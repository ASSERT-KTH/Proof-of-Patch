import json
import argparse

def remove_duplicates(input_filepath, output_filepath, duplicates_filepath):
    try:
        with open(input_filepath, 'r', encoding='utf-8') as infile:
            data = json.load(infile)
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_filepath}")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {input_filepath}. Make sure it's a valid JSON file.")
        return
    except Exception as e:
        print(f"An unexpected error occurred while reading: {e}")
        return

    if not isinstance(data, dict):
        print("Error: JSON root is not an object/dictionary. Expected format: {'category': ['link1', ...], ...}")
        return

    seen_links_globally = set()
    result_data = {}
    collected_duplicates = []

    for category, links in data.items():
        if not isinstance(links, list):
            result_data[category] = links
            continue

        unique_links_for_this_category = []
        for link in links:
            if not isinstance(link, (str, int, float, bool, type(None))):
                 link_key = str(link)
            else:
                 link_key = link

            if link_key not in seen_links_globally:
                seen_links_globally.add(link_key)
                unique_links_for_this_category.append(link) 
            else:
                # This link is a duplicate in the current context
                collected_duplicates.append(link) # Add the original link item to duplicates list

        result_data[category] = unique_links_for_this_category

    # Write the main output file with unique links per category
    try:
        with open(output_filepath, 'w', encoding='utf-8') as outfile:
            json.dump(result_data, outfile, indent=4, ensure_ascii=False)
        print(f"Successfully removed cross-category duplicate links. Main output saved to: {output_filepath}")
    except Exception as e:
        print(f"An unexpected error occurred while writing main output file: {e}")
        return # Exit if we can't write the main output

    # Write the file containing all identified duplicate links
    try:
        with open(duplicates_filepath, 'w', encoding='utf-8') as dup_file:
            json.dump(collected_duplicates, dup_file, indent=4, ensure_ascii=False)
        print(f"List of all identified duplicate links saved to: {duplicates_filepath}")
    except Exception as e:
        print(f"An unexpected error occurred while writing duplicates file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove duplicate links across categories in a JSON file and save duplicates to a separate file.")
    parser.add_argument("input_file", help="Path to the input JSON file.")
    parser.add_argument("output_file", help="Path to the output JSON file where results (with unique links per category) will be saved.")
    parser.add_argument("duplicates_out_file", help="Path to the JSON file where the list of all identified duplicate links will be saved.")

    args = parser.parse_args()

    remove_duplicates(args.input_file, args.output_file, args.duplicates_out_file)