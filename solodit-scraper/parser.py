import json
import time
import logging
import tiktoken

def parse_results(file):
    # Process URLs from JSON
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

    try:
        with open(file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        count = 0
        total_tokens = 0
        most_tokens = 0
        least_tokens = 1000000000

        for audit, details in json_data.items():
                count = count + 1
                audit_content = details['audit_content']
                if details['ai_summary']:
                    ai_summary = details['ai_summary']
                else:
                    ai_summary = ""
                # HERE I HAVE TO ADD THE AI SUMMARY
                example_prompt = f"""You are a blockchain security analyst reviewing a report. Here is the content of a 
                smart contract security audit between '|' brackets:|{audit_content}|. Analyze the report and answer the 
                following questions. Only provide your answer in the specified format. 
                1.  Does the report appear to contain a functional code snippet or test case demonstrating a proof-of-concept for a vulnerability? 
                2.  Does the report clearly explain the reasoning behind its findings and provide specific evidence (like code references or 
                transaction examples)? 
                Answer format: (has_poc_code: yes/no, is_well_reasoned: yes/mostly/no)"""

                tokens = encoding.encode(example_prompt)
                token_count = len(tokens)
                total_tokens = total_tokens + token_count
                if most_tokens < token_count:
                     most_tokens = token_count
                if least_tokens > token_count:
                     least_tokens = token_count

        average_tokens = total_tokens/count
        #print(audit_content)
        print(f"Number of audits: {count}")
        print(f"Average tokens: {average_tokens:.2f}")
        print(f"Highest number of tokens: {most_tokens}")
        print(f"Least value of tokens: {least_tokens}")
    
    except FileNotFoundError:
        print(f"Error: The file '{file}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred during URL processing: {e}")

def main():
    parse_results("my_result/results.json")

if __name__ == "__main__":
    main()