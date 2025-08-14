import logging
import json
import pandas as pd

# Setting up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_data(file):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            logging.info("Starting to parse json file")
    except FileNotFoundError:
        logging.error(f"Error: The file '{file}' was not found.")
        return None
    except json.JSONDecodeError:
        logging.error(f"Error: The file '{file}' is not a valid JSON file.")
        return None
    
    for audit, details in json_data.items():
        priority_score = 0

        poc_content_types = details['poc_content_types']
        impact = details['impact']
        year = int(details['publication_date'].split()[-1])
        n_authors = details['n_authors']
        contains_github_link = details['contains_github_link']
        has_poc_code = details['has_poc_code']
        is_well_reasoned = details['is_well_reasoned']
        is_correct = details['is_correct']

        #text = f"impact: {impact}"
        #logging.info(text)
        # --- Large impact parameters ---
        if has_poc_code == 'yes':
            priority_score = priority_score + 5
        if is_well_reasoned == 'yes':
            priority_score = priority_score + 5
        elif is_well_reasoned == 'mostly':
            priority_score = priority_score + 2
        if is_correct == 'yes':
            priority_score = priority_score + 5
        if contains_github_link == 'yes':
            priority_score = priority_score + 5

        # --- Smaller impact parameters ---
        priority_score = priority_score + len(poc_content_types) + 0.5 * (year - 2025)
        if impact == 'High':
            priority_score = priority_score + 2
        elif impact == 'Medium':
            priority_score = priority_score + 1
        if 1 < n_authors < 5:
            priority_score = priority_score + 1
        elif 5 <= n_authors < 10:
            priority_score = priority_score + 2
        elif 9 < n_authors:
            priority_score = priority_score + 3
        
        # --- Append new priority score ---
        details['priority_score'] = priority_score
        details['verification'] = 'not_attempted'
        details['correctness'] = 'not_evaluated'
    
    return json_data

"""
def main():
    prioritized_data = parse_data('my_result/enriched_data.json')

    # Save the updated data to a new file
    output_file = 'prioritized_data.json'
    if prioritized_data:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(prioritized_data, f, indent=4)
        logging.info(f"Successfully prioritized audits and saved the result to '{output_file}'")
    

    data = prioritized_data
    df = pd.DataFrame.from_dict(data, orient='index')
    df.sort_values(by='priority_score', ascending=False, inplace=True)
    output_file_path = "data.html"
    df['rank'] = range(1, len(df) + 1)
    df['rank'] = df['rank'].astype(str).str.zfill(4)
    cols = ['rank'] + [col for col in df.columns if col != 'rank']
    df = df[cols]
    html_output = df.to_html(index=True)
    with open(output_file_path, "w") as file:
        file.write(html_output)"""

def main():
    prioritized_data = parse_data('enriched_data.json')

    # Save the updated data to a JSON file (optional)
    output_json = 'prioritized_data.json'
    if prioritized_data:
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(prioritized_data, f, indent=4)
        logging.info(f"Successfully prioritized audits and saved the result to '{output_json}'")

    # Convert to DataFrame
    df = pd.DataFrame.from_dict(prioritized_data, orient='index')

    # Sort by priority_score (highest first)
    df.sort_values(by='priority_score', ascending=False, inplace=True)

    # Create rank column
    df['rank'] = range(1, len(df) + 1)
    df['rank'] = df['rank'].astype(str).str.zfill(4)
    df['rank'] = "'" + df['rank']

    # Reorder columns so rank is first
    cols = ['rank'] + [col for col in df.columns if col != 'rank']
    df = df[cols]

    # Save to CSV instead of HTML
    output_csv_path = "prioritized_data.csv"
    df.to_csv(output_csv_path, index=True)  
    logging.info(f"CSV file saved to '{output_csv_path}'")

if __name__ == "__main__":
    main()