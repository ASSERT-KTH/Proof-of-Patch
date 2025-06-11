# SHOULD ALSO INCLUDE AUDIT CONTENT IN THE FINAL THING
import json

def process_and_remove_duplicates(data):
    """
    Finds duplicate links, removes them, and adds a consolidated "Also in:" 
    reference to the original entry, excluding the original's own category.

    Args:
        data (dict): The JSON data loaded as a Python dictionary.

    Returns:
        dict: The new, cleaned dictionary with duplicates removed and originals annotated.
    """
    # The tracker now also stores the original category to prevent self-referencing.
    seen_links = {}
    
    # This will be the new, clean data structure we build.
    processed_data = {}

    # --- Phase 1: Filter duplicates and rebuild the data structure ---
    print("Phase 1: Removing duplicates and collecting info...")
    for category, items in data.items():
        # Start each new category list with its header row.
        new_items_list = [items[0]] if items else []

        for item in items[0:]:
            try:
                link = item[1]
            except IndexError:
                continue # Skip malformed rows

            if link in seen_links:
                # --- This is a DUPLICATE item ---
                duplicate_category = category
                original_info = seen_links[link]
                original_category = original_info['original_category']

                # THE CRUCIAL FIX: Only proceed if the duplicate is in a DIFFERENT category.
                if duplicate_category != original_category:
                    # And ensure we don't add the same category name more than once.
                    if duplicate_category not in original_info['also_in_categories']:
                        original_info['also_in_categories'].append(duplicate_category)
                
                # In all cases of duplication, the item is NOT added to the new list,
                # effectively deleting it.

            else:
                # --- This is the ORIGINAL item ---
                # 1. Add it to our new list of items to keep.
                new_items_list.append(item)
                
                # 2. Register it, now including its own category.
                seen_links[link] = {
                    'item': item,
                    'original_category': category, 
                    'also_in_categories': []
                }
        
        # Replace the old category data with our newly constructed list.
        processed_data[category] = new_items_list

    # --- Phase 2: Annotate the remaining original items ---
    print("Phase 2: Annotating original items...")
    for link_info in seen_links.values():
        if link_info['also_in_categories']:
            categories_string = ", ".join(link_info['also_in_categories'])
            original_item = link_info['item']
            original_item.append(f"Also in: {categories_string}")
                
    return processed_data

def main():
    input_filename = 'results.json'
    output_filename = 'result_no_dupe.json'

    try:
        # Open and read the source JSON file
        with open(input_filename, 'r', encoding='utf-8') as f:
            print(f"Reading data from '{input_filename}'...")
            json_data = json.load(f)

        # Process the data in memory
        modified_data = process_and_remove_duplicates(json_data)

        # Write the modified data to a new JSON file
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(modified_data, f, indent=4, ensure_ascii=False)
        
        print(f"Success! Processed data has been saved to '{output_filename}'.")

    except FileNotFoundError:
        print(f"Error: The input file '{input_filename}' was not found.")
        print("Please make sure the file exists in the same directory as the script.")

    except json.JSONDecodeError:
        print(f"Error: The file '{input_filename}' is not a valid JSON file.")
        print("Please check the file for syntax errors.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()