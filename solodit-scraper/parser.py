import json
import time
import logging
import re
import os
from dotenv import load_dotenv
from openai import OpenAI
import tiktoken

# Load environment variables from .env file
load_dotenv()

# Setting up logging configuration with file output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('parser.log'),
        logging.StreamHandler()  # Also print to console
    ]
)

# Cost tracking variables
total_tokens_used = 0
total_cost = 0.0
total_requests = 0

# Initialize tiktoken for token counting
encoding = tiktoken.encoding_for_model("gpt-4o")

def get_model_pricing():
    """Get current pricing for GPT-4o model"""
    # GPT-4o pricing (as of 2024) - you can update these or fetch from API
    pricing = {
        "gpt-4o": {
            "input_cost_per_1k": 0.005,   # $0.005 per 1K input tokens
            "output_cost_per_1k": 0.015,  # $0.015 per 1K output tokens
        }
    }
    return pricing["gpt-4o"]

def calculate_cost(prompt_tokens, completion_tokens, model="gpt-4o"):
    """Calculate cost based on token usage using current pricing"""
    pricing = get_model_pricing()
    input_cost = (prompt_tokens / 1000) * pricing["input_cost_per_1k"]
    output_cost = (completion_tokens / 1000) * pricing["output_cost_per_1k"]
    return input_cost + output_cost

def count_tokens(text, model="gpt-4o"):
    """Count tokens in text using tiktoken"""
    try:
        return len(encoding.encode(text))
    except Exception as e:
        logging.warning(f"Error counting tokens: {e}")
        # Fallback: rough estimation (1 token ≈ 4 characters)
        return len(text) // 4

def log_cost_info(prompt_tokens, completion_tokens, cost, audit_count):
    """Log cost information"""
    global total_tokens_used, total_cost, total_requests
    
    total_tokens_used += prompt_tokens + completion_tokens
    total_cost += cost
    total_requests += 1
    
    pricing = get_model_pricing()
    
    logging.info(f"Token usage - Input: {prompt_tokens}, Output: {completion_tokens}, Total: {prompt_tokens + completion_tokens}")
    logging.info(f"Pricing - Input: ${pricing['input_cost_per_1k']:.3f}/1K, Output: ${pricing['output_cost_per_1k']:.3f}/1K")
    logging.info(f"Request cost: ${cost:.4f}")
    logging.info(f"Cumulative - Requests: {total_requests}, Tokens: {total_tokens_used:,}, Cost: ${total_cost:.4f}")
    
    # Estimate remaining cost
    if audit_count > 0:
        avg_cost_per_audit = total_cost / audit_count
        estimated_remaining_cost = avg_cost_per_audit * (len(json_data) - audit_count)
        logging.info(f"Estimated remaining cost: ${estimated_remaining_cost:.4f}")

# Initializing OpenAI client
try:
    client = OpenAI()
except Exception as e:
    logging.error(f"Error initializing OpenAI client: {e}")
    logging.warning("Please ensure your OPENAI_API_KEY environment variable is set correctly.")
    client = None

def parse_results(file):
    global json_data  # Make json_data global for cost estimation
    if not client:
        logging.error("OpenAI client is not available. Exiting.")
        return None

    try:
        with open(file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        logging.error(f"Error: The file '{file}' was not found.")
        return None
    except json.JSONDecodeError:
        logging.error(f"Error: The file '{file}' is not a valid JSON file.")
        return None

    total_audits = len(json_data)
    logging.info(f"Starting to parse {total_audits} audits")
    
    # Estimate cost based on sample audit content
    if total_audits > 0:
        sample_audit = list(json_data.values())[0]
        sample_content = sample_audit.get('audit_content', '')
        sample_tokens = count_tokens(sample_content)
        
        # Estimate tokens per audit (content + prompt overhead)
        estimated_tokens_per_audit = sample_tokens + 500  # Add overhead for prompt
        estimated_cost_per_audit = calculate_cost(estimated_tokens_per_audit, 200)  # Assume 200 output tokens
        
        total_estimated_cost = estimated_cost_per_audit * total_audits
        
        logging.info(f"Sample audit tokens: {sample_tokens}")
        logging.info(f"Estimated tokens per audit: {estimated_tokens_per_audit}")
        logging.info(f"Estimated cost per audit: ${estimated_cost_per_audit:.4f}")
        logging.info(f"Total estimated cost: ${total_estimated_cost:.2f}")
    
    count = 0
    for audit, details in json_data.items():
        count = count + 1
        audit_content = details['audit_content']
        example_prompt = f"""You are a blockchain security analyst reviewing a smart contract audit report. 
        Here is the content of the audit between '|' brackets: |{audit_content}|. 
        
        Analyze the report and answer the following questions. Only provide your answer in the specified format.
        
        1. Does the report contain a clear Proof of Concept (PoC)? Look for:
           - Code examples demonstrating the vulnerability
           - Step-by-step exploitation instructions
           - Specific attack scenarios or test cases
        
        2. Does the report contain a clear mitigation proposal or solution? Look for:
           - Specific recommendations, fixes, or corrective measures
           - Code examples showing how to fix the vulnerability
           - Implementation guidance or best practices
        
        3. Does the report include a reference to an actual patch implementation? This could be:
           - A GitHub commit hash or link
           - A GitHub pull request (PR) number or link
           - A specific code fix or implementation
           - A reference to deployed fixes
        
        4. Is the audit technically sound and well-explained? Evaluate if the audit:
           - Clearly explains the vulnerability and its impact
           - Provides specific evidence (code references, transaction examples)
           - Uses proper technical terminology and analysis
           - Demonstrates deep understanding of the smart contract mechanics
           - Presents findings in a clear, logical manner
        
        Answer format: 
        has_poc: yes/no, 
        has_mitigation_proposal: yes/no, 
        has_patch_reference: yes/uncertain/no, 
        audit_quality: excellent/good/fair/poor"""
            
        try:
            logging.info(f"Processing audit {count}/{total_audits}")
                
            # --- Make the API call to OpenAI ---
            response = client.chat.completions.create(
                model="gpt-4o", 
                messages=[
                    {"role": "system", "content": "You are a helpful blockchain security analyst assistant specializing in patch and mitigation analysis."},
                    {"role": "user", "content": example_prompt}
                ]
            )

            llm_answer = response.choices[0].message.content
            
            # Extract token usage information
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            cost = calculate_cost(prompt_tokens, completion_tokens)
            
            # Log cost information
            log_cost_info(prompt_tokens, completion_tokens, cost, count)
            
            logging.info(f"  -> Received LLM Answer")

            # --- Parse the response and add new parameters ---
            poc_match = re.search(r"has_poc:\s*(yes|no)", llm_answer)
            mitigation_match = re.search(r"has_mitigation_proposal:\s*(yes|no)", llm_answer)
            patch_match = re.search(r"has_patch_reference:\s*(yes|uncertain|no)", llm_answer)
            quality_match = re.search(r"audit_quality:\s*(excellent|good|fair|poor)", llm_answer)

            # --- Add the parsed values to the details dictionary ---
            details['has_poc'] = poc_match.group(1) if poc_match else "parse_error"
            details['has_mitigation_proposal'] = mitigation_match.group(1) if mitigation_match else "parse_error"
            details['has_patch_reference'] = patch_match.group(1) if patch_match else "parse_error"
            details['audit_quality'] = quality_match.group(1) if quality_match else "parse_error"
            
            # --- Calculate patch score based on multiple factors ---
            patch_score = calculate_patch_score(details)
            details['patch_score'] = patch_score

                # --- Add delay to mitgate RPM limit ---
            time.sleep(0.2)

        except Exception as e:
            logging.error(f"An unexpected error occurred while processing: {e}")

    return json_data

def calculate_patch_score(details):
    """Calculate a comprehensive patch score based on various indicators"""
    score = 0
    
    # Base score from LLM analysis
    has_poc = details.get('has_poc', 'no')
    mitigation_proposal = details.get('has_mitigation_proposal', 'no')
    patch_reference = details.get('has_patch_reference', 'no')
    audit_quality = details.get('audit_quality', 'poor')
    
    # PoC scoring (important for understanding the vulnerability)
    if has_poc == 'yes':
        score += 8  # PoC is valuable for understanding the issue
    
    # Mitigation proposal scoring
    if mitigation_proposal == 'yes':
        score += 10
    elif mitigation_proposal == 'no':
        score += 0
    
    # Patch reference scoring (highest priority)
    if patch_reference == 'yes':
        score += 15  # Highest weight for actual patch references
    elif patch_reference == 'uncertain':
        score += 5
    elif patch_reference == 'no':
        score += 0
    
    # Audit quality scoring
    quality_scores = {
        'excellent': 10,
        'good': 7,
        'fair': 4,
        'poor': 1
    }
    score += quality_scores.get(audit_quality, 0)
    
    # Additional scoring based on detected indicators
    if details.get('github_commit', False):
        score += 8
    if details.get('github_pr', False):
        score += 8
    if details.get('patch_link', False):
        score += 5
    if details.get('fix_commit', False):
        score += 6
    if details.get('mitigation_code', False):
        score += 7
    
    # Mitigation content types bonus
    mitigation_content = details.get('mitigation_content_types', [])
    if 'code' in mitigation_content:
        score += 5
    if 'github_link' in mitigation_content:
        score += 6
    if 'text' in mitigation_content:
        score += 2
    
    # Impact level bonus
    impact = details.get('impact', 'Low')
    if impact == 'High':
        score += 5
    elif impact == 'Medium':
        score += 3
    elif impact == 'Low':
        score += 1
    
    # GitHub link presence bonus
    if details.get('contains_github_link') == 'yes':
        score += 3
    
    return score

def main():
    enriched_data = parse_results('results/results.json')

    # Save the updated data to a new file
    import os
    os.makedirs("results", exist_ok=True)
    output_file = 'results/enriched_data.json'
    if enriched_data:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enriched_data, f, indent=4)
        logging.info(f"Successfully enriched audits and saved the result to '{output_file}'")
        
        # Final cost summary
        pricing = get_model_pricing()
        logging.info(f"\n{'='*60}")
        logging.info(f"PARSING COMPLETED - COST SUMMARY")
        logging.info(f"{'='*60}")
        logging.info(f"Model: GPT-4o")
        logging.info(f"Pricing - Input: ${pricing['input_cost_per_1k']:.3f}/1K, Output: ${pricing['output_cost_per_1k']:.3f}/1K")
        logging.info(f"Total audits processed: {len(enriched_data)}")
        logging.info(f"Total API requests: {total_requests}")
        logging.info(f"Total tokens used: {total_tokens_used:,}")
        logging.info(f"Total cost: ${total_cost:.4f}")
        logging.info(f"Average cost per audit: ${total_cost/len(enriched_data):.4f}")
        logging.info(f"Average tokens per audit: {total_tokens_used/len(enriched_data):.0f}")
        logging.info(f"{'='*60}")
        
        # Save cost summary to file
        cost_summary = {
            "model": "gpt-4o",
            "pricing": pricing,
            "total_audits": len(enriched_data),
            "total_requests": total_requests,
            "total_tokens": total_tokens_used,
            "total_cost": total_cost,
            "avg_cost_per_audit": total_cost/len(enriched_data),
            "avg_tokens_per_audit": total_tokens_used/len(enriched_data)
        }
        
        with open("results/cost_summary.json", "w") as f:
            json.dump(cost_summary, f, indent=4)
        logging.info("Cost summary saved to 'results/cost_summary.json'")

if __name__ == "__main__":
    main()