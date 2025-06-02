import json
import argparse

def mark_duplicates_in_file(duplicates_filepath, in_scope_filepath, output_filepath):
    """
    Args:
        duplicates_filepath (str): Path to the JSON file containing a list of duplicate links.
        in_scope_filepath (str): Path to the JSON file to be processed (e.g., in_scope.json).
        output_filepath (str): Path to save the modified in_scope data.
    """
    try:
        with open(duplicates_filepath, 'r', encoding='utf-8') as f:
            duplicate_links_list = json.load(f)
        duplicate_links_set = set(duplicate_links_list)
    except FileNotFoundError:
        print(f"Error: Duplicates file not found at {duplicates_filepath}")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {duplicates_filepath}.")
        return
    except Exception as e:
        print(f"An unexpected error occurred while reading {duplicates_filepath}: {e}")
        return

    try:
        with open(in_scope_filepath, 'r', encoding='utf-8') as f:
            in_scope_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: In-scope file not found at {in_scope_filepath}")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {in_scope_filepath}.")
        return
    except Exception as e:
        print(f"An unexpected error occurred while reading {in_scope_filepath}: {e}")
        return

    if not isinstance(in_scope_data, dict):
        print(f"Error: Root of {in_scope_filepath} is not an object/dictionary. Skipping marking.")
        try:
            with open(output_filepath, 'w', encoding='utf-8') as outfile:
                json.dump(in_scope_data, outfile, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error writing original data to {output_filepath}: {e}")
        return

    modified_in_scope_data = {}
    dupe_prefix = "#dupe "

    for category, links_or_value in in_scope_data.items():
        if not isinstance(links_or_value, list):
            modified_in_scope_data[category] = links_or_value
            continue

        marked_links_for_category = []
        for link_item in links_or_value:
            if not isinstance(link_item, str):
                marked_links_for_category.append(link_item)
                continue

            current_link_str = link_item
            base_link = current_link_str

            if current_link_str.startswith(dupe_prefix):
                base_link = current_link_str[len(dupe_prefix):]

            if base_link in duplicate_links_set:
                # It's a duplicate. Mark it if not already marked.
                if not current_link_str.startswith(dupe_prefix):
                    marked_links_for_category.append(dupe_prefix + current_link_str)
                else:
                    # Already marked, keep it as is
                    marked_links_for_category.append(current_link_str)
            else:
                # Not a duplicate, keep it as is (it might have been marked previously
                # for a reason not in the current duplicates_file, so we preserve that)
                marked_links_for_category.append(current_link_str)

        modified_in_scope_data[category] = marked_links_for_category

    try:
        with open(output_filepath, 'w', encoding='utf-8') as outfile:
            json.dump(modified_in_scope_data, outfile, indent=4, ensure_ascii=False)
        print(f"Successfully processed {in_scope_filepath}. Marked data saved to: {output_filepath}")
    except Exception as e:
        print(f"An unexpected error occurred while writing to {output_filepath}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Marks links in an 'in-scope' JSON file if they appear in a 'duplicates' JSON file.")
    parser.add_argument("duplicates_file", help="Path to the JSON file containing the list of duplicate links.")
    parser.add_argument("in_scope_file", help="Path to the JSON file to be processed and have links marked (e.g., in_scope.json).")
    parser.add_argument("output_file", help="Path to save the modified 'in-scope' data with marked duplicates.")

    args = parser.parse_args()

    mark_duplicates_in_file(args.duplicates_file, args.in_scope_file, args.output_file)