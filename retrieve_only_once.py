import csv

def get_unique_elements_from_csvs(file1_path, file2_path, output_csv_path="unique_elements.csv"):
    """
    Retrieves unique elements from all rows of two CSV files and writes them to an output CSV file.

    Args:
        file1_path (str): The path to the first CSV file.
        file2_path (str): The path to the second CSV file.
        output_csv_path (str): The path to the output CSV file.

    Returns:
        int: The number of unique elements written to the output CSV file.
    """
    unique_elements = set()

    def process_file(filepath, element_set):
        try:
            with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    for element in row:
                        element_set.add(element.strip())  # Remove leading/trailing whitespace
        except FileNotFoundError:
            print(f"Error: File not found at {filepath}")
        except Exception as e:
            print(f"An error occurred while processing {filepath}: {e}")

    process_file(file1_path, unique_elements)
    process_file(file2_path, unique_elements)

    if unique_elements:
        try:
            with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                for item in sorted(unique_elements):
                    writer.writerow([item])
            print(f"\n✅ {len(unique_elements)} unique elements written to '{output_csv_path}'")
        except Exception as e:
            print(f"❌ Failed to write output CSV: {e}")
    else:
        print("⚠️ No unique elements found or files were empty/could not be read.")

    return len(unique_elements)

# --- How to use the function ---

file1 = 'field_csv.csv'
file2 = 'sites_to_crawl.csv'
output_file = 'unique_elements.csv'

get_unique_elements_from_csvs(file1, file2, output_file)
