import csv

def get_unique_elements_from_csvs(file1_path, file2_path):
    """
    Retrieves unique elements from all rows of two CSV files.

    Args:
        file1_path (str): The path to the first CSV file.
        file2_path (str): The path to the second CSV file.

    Returns:
        set: A set containing all unique elements from both CSV files.
             Returns an empty set if files cannot be read or are empty.
    """
    unique_elements = set()

    def process_file(filepath, element_set):
        try:
            with open(filepath, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    for element in row:
                        element_set.add(element.strip()) # .strip() removes leading/trailing whitespace
        except FileNotFoundError:
            print(f"Error: File not found at {filepath}")
        except Exception as e:
            print(f"An error occurred while processing {filepath}: {e}")

    process_file(file1_path, unique_elements)
    process_file(file2_path, unique_elements)

    return unique_elements

# --- How to use the function ---

file1 = 'field_csv.csv'
file2 = 'your_file2.csv'

unique_items = get_unique_elements_from_csvs(file1, file2)

if unique_items:
    print("Unique elements found in both CSV files:")
    for item in sorted(list(unique_items)): # Print sorted list for better readability
        print(item)
else:
    print("No unique elements found or files were empty/could not be read.")