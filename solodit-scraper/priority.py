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

        # Get basic information
        poc_content_types = details.get('poc_content_types', [])
        impact = details.get('impact', 'Low')
        
        # Handle publication date parsing (could be "2 days ago", "Jan 2023", etc.)
        publication_date = details.get('publication_date', 'no_date')
        try:
            # Try to ex
            # tract year from date string
            if 'ago' in publication_date.lower():
                # For relative dates like "2 days ago", mark as no_date
                year = 0  # Use 0 to indicate no specific date
            else:
                # Try to extract year from date string
                year_str = publication_date.split()[-1]
                year = int(year_str)
        except (ValueError, IndexError):
            # Fallback to 0 if parsing fails
            year = 0
        
        n_authors = details.get('n_authors', 1)
        contains_github_link = details.get('contains_github_link', 'no')
        
        # Get patch-focused analysis results
        has_poc = details.get('has_poc', 'no')
        has_mitigation_proposal = details.get('has_mitigation_proposal', 'no')
        has_patch_reference = details.get('has_patch_reference', 'no')
        audit_quality = details.get('audit_quality', 'poor')
        
        # Get technical indicators
        github_commit = details.get('github_commit', False)
        github_pr = details.get('github_pr', False)
        patch_link = details.get('patch_link', False)
        fix_commit = details.get('fix_commit', False)
        mitigation_code = details.get('mitigation_code', False)
        mitigation_content_types = details.get('mitigation_content_types', [])

        # --- HIGH PRIORITY: Patch-related scoring ---
        # Patch references get the highest priority
        if has_patch_reference == 'yes':
            priority_score += 20  # Highest weight for actual patch references
        elif has_patch_reference == 'uncertain':
            priority_score += 8
        elif has_patch_reference == 'no':
            priority_score += 0
        
        # Mitigation proposals are also very important
        if has_mitigation_proposal == 'yes':
            priority_score += 15
        elif has_mitigation_proposal == 'no':
            priority_score += 0
        
        # PoC is important for understanding the vulnerability
        if has_poc == 'yes':
            priority_score += 12
        elif has_poc == 'no':
            priority_score += 0
        
        # Audit quality scoring
        quality_scores = {
            'excellent': 15,
            'good': 10,
            'fair': 6,
            'poor': 2
        }
        priority_score += quality_scores.get(audit_quality, 0)
        
        # --- TECHNICAL INDICATORS ---
        if github_commit:
            priority_score += 12
        if github_pr:
            priority_score += 12
        if patch_link:
            priority_score += 8
        if fix_commit:
            priority_score += 10
        if mitigation_code:
            priority_score += 10
        
        # Mitigation content types bonus
        if 'code' in mitigation_content_types:
            priority_score += 8
        if 'github_link' in mitigation_content_types:
            priority_score += 10
        if 'text' in mitigation_content_types:
            priority_score += 3
        
        # --- MEDIUM PRIORITY: PoC content scoring ---
        if 'code' in poc_content_types:
            priority_score += 6
        if 'link' in poc_content_types:
            priority_score += 4
        if 'text' in poc_content_types:
            priority_score += 3
        
        # --- LOWER PRIORITY: General factors ---
        # Impact level bonus
        if impact == 'High':
            priority_score += 8
        elif impact == 'Medium':
            priority_score += 5
        elif impact == 'Low':
            priority_score += 2
        
        # GitHub link presence bonus
        if contains_github_link == 'yes':
            priority_score += 4
        
        # Author count bonus (collaborative work often higher quality)
        if 1 < n_authors < 5:
            priority_score += 2
        elif 5 <= n_authors < 10:
            priority_score += 4
        elif n_authors >= 10:
            priority_score += 6
        
        # Recency bonus (more recent audits might be more relevant)
        if year > 0:  # Only apply recency bonus if we have a valid year
            priority_score += max(0, (year - 2020) * 0.5)
        
        # --- Append new priority score ---
        details['priority_score'] = priority_score
        details['verification'] = 'not_attempted'
        details['correctness'] = 'not_evaluated'
        
        # Add categorization for easy filtering
        if has_patch_reference == 'yes' and has_poc == 'yes':
            details['category'] = 'patch_and_poc'
        elif has_patch_reference == 'yes':
            details['category'] = 'patch_only'
        elif has_poc == 'yes':
            details['category'] = 'poc_only'
        else:
            details['category'] = 'other'
    
    return json_data

def main():
    prioritized_data = parse_data('results/enriched_data.json')

    # Save the updated data to a JSON file (optional)
    import os
    os.makedirs("results", exist_ok=True)
    output_json = 'results/prioritized_data.json'
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

    # Reorder columns so rank is first, then key metrics
    key_columns = ['rank', 'priority_score', 'category', 'has_patch_reference', 'has_mitigation_proposal', 'has_poc', 'audit_quality', 'impact']
    other_columns = [col for col in df.columns if col not in key_columns]
    cols = key_columns + other_columns
    df = df[cols]

    # Save to CSV
    output_csv_path = "results/prioritized_data.csv"
    df.to_csv(output_csv_path, index=True)  
    logging.info(f"CSV file saved to '{output_csv_path}'")
    
    # Print summary statistics
    print("\n" + "="*60)
    print("PATCH PRIORITIZATION SUMMARY")
    print("="*60)
    print(f"Total audits prioritized: {len(df)}")
    print(f"Average priority score: {df['priority_score'].mean():.1f}")
    print(f"Highest priority score: {df['priority_score'].max()}")
    print(f"Lowest priority score: {df['priority_score'].min()}")
    
    print("\n--- CATEGORY BREAKDOWN ---")
    category_counts = df['category'].value_counts()
    for category, count in category_counts.items():
        percentage = (count / len(df)) * 100
        print(f"{category}: {count} ({percentage:.1f}%)")
    
    print("\n--- TOP 10 HIGHEST PRIORITY AUDITS ---")
    top_10 = df.head(10)[['rank', 'priority_score', 'category', 'has_patch_reference', 'has_mitigation_proposal', 'has_poc', 'audit_quality', 'impact']]
    print(top_10.to_string(index=False))
    print("="*60)

if __name__ == "__main__":
    main()