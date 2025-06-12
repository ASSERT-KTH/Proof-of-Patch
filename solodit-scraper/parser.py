import json
import time
import logging

def parse_results(file):
    # Process URLs from JSON
    try:
        with open(file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        count = 0
        for audit, details in json_data.items():
                count = count + 1
                audit_content = details['audit_content']
                print(audit_content)
        print(count)
    
    except FileNotFoundError:
        print(f"Error: The file '{file}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred during URL processing: {e}")

def main():
    parse_results("my_result/results.json")

if __name__ == "__main__":
    main()