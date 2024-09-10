import json

def print_json_structure(data, indent=0):
    """
    Recursively prints the structure of a JSON object.
    
    Args:
    - data: The JSON object (dict or list) to print the structure of.
    - indent: The current indentation level (for pretty printing).
    """
    if isinstance(data, dict):
        for key in data:
            print(' ' * indent + str(key))
            print_json_structure(data[key], indent + 2)
    elif isinstance(data, list):
        if data:  # If the list is not empty
            print(' ' * indent + '[list]')
            # Recursively print the structure of the first element as a representative
            print_json_structure(data[0], indent + 2)
    else:
        print(' ' * indent + str(type(data).__name__))

# Load the JSON file
with open('/Users/anujshah/Downloads/nurse-summary-automation/form.json', 'r') as file:
    json_data = json.load(file)

# Print the structure
print_json_structure(json_data)