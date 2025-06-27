import json
import time
import logging
import re
from openai import OpenAI

# Setting up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initializing OpenAI client
try:
    client = OpenAI()
except Exception as e:
    logging.error(f"Error initializing OpenAI client: {e}")
    logging.warning("Please ensure your OPENAI_API_KEY environment variable is set correctly.")
    client = None

def parse_results(file):
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

    count = 0
    for audit, details in json_data.items():
        count = count + 1
        audit_content = details['audit_content']
        example_prompt = f"""You are a blockchain security analyst reviewing a report. Here is the content of a 
        smart contract security audit between '|' brackets: |{audit_content}|. Analyze the report and answer the 
        following questions. Only provide your answer in the specified format. 
        1.  Does the report appear to contain a functional code snippet or test case demonstrating a proof-of-concept for a vulnerability? 
        2.  Does the report clearly explain the reasoning behind its findings and provide specific evidence (like code references or 
        transaction examples)? 
        3.  Do the findings appear technically sound and accurate upon inspection?
        Answer format: has_poc_code: yes/no, is_well_reasoned: yes/mostly/no, is_correct: yes/uncertain/no"""
            
        try:
            logging.info(f"Processing audit: {count}")
                
                # --- Make the API call to OpenAI ---
            response = client.chat.completions.create(
                model="gpt-4o", 
                messages=[
                    {"role": "system", "content": "You are a helpful security analyst assistant."},
                    {"role": "user", "content": example_prompt}
                ]
            )

            llm_answer = response.choices[0].message.content
            logging.info(f"  -> Viable LLM Answer")

                # --- Parse the response and add new parameters ---
            poc_match = re.search(r"has_poc_code:\s*(yes|no)", llm_answer)
            reasoned_match = re.search(r"is_well_reasoned:\s*(yes|mostly|no)", llm_answer)
            correct_match = re.search(r"is_correct:\s*(yes|uncertain|no)", llm_answer)

                # --- Add the parsed values to the details dictionary ---
            details['has_poc_code'] = poc_match.group(1) if poc_match else "parse_error"
            details['is_well_reasoned'] = reasoned_match.group(1) if reasoned_match else "parse_error"
            details['is_correct'] = correct_match.group(1) if correct_match else "parse_error"

                # --- Add delay to mitgate RPM limit ---
            time.sleep(0.2)

        except Exception as e:
            logging.error(f"An unexpected error occurred while processing: {e}")

    return json_data

def main():
    enriched_data = parse_results('results.json')

    # Save the updated data to a new file
    output_file = 'enriched_data.json'
    if enriched_data:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enriched_data, f, indent=4)
        logging.info(f"Successfully enriched audits and saved the result to '{output_file}'")

if __name__ == "__main__":
    main()