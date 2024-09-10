#!/usr/bin/env python
# coding: utf-8

# In[4]:


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


# In[5]:


# Load the JSON file
with open('/Users/anujshah/Downloads/nurse-summary-automation/form.json', 'r') as file:
    json_data = json.load(file)

# Print the structure
# print_json_structure(json_data)


# In[6]:


import pandas as pd

def flatten_json(json_data):
    # List to store the flattened rows
    rows = []

    # Iterate over templates
    for template in json_data.get('templates', []):
        template_id = template.get('id')
        template_name = template.get('name')
        template_version_id = template.get('version_id')
        
        # Iterate over groups within each template
        for group in template.get('groups', []):
            group_id = group.get('id')
            group_topic_id = group.get('topic_id')
            group_name = group.get('name')
            group_start_removed = group.get('start_removed')
            
            # Iterate over rows within each group
            for row in group.get('rows', []):
                row_id = row.get('id')
                row_name = row.get('name')
                row_start_removed = row.get('start_removed')
                row_information = row.get('row_information')
                additional_notes = row.get('additional_notes')

                # Extract options if they exist
                options = row.get('options', [])
                options_list = [option.get('option', '') for option in options]

                # Append the flattened row to the list
                rows.append({
                    'template_id': template_id,
                    'template_name': template_name,
                    'template_version_id': template_version_id,
                    'group_id': group_id,
                    'group_topic_id': group_topic_id,
                    'group_name': group_name,
                    'group_start_removed': group_start_removed,
                    'row_id': row_id,
                    'row_name': row_name,
                    'row_start_removed': row_start_removed,
                    'row_information': row_information,
                    'additional_notes': additional_notes,
                    'options': options_list
                })
        break

    # Convert the list of rows to a DataFrame
    df = pd.DataFrame(rows)
    return df
df = flatten_json(json_data)
# print(df)


# In[7]:


categories = {
    'neurological': [
        'Neurological', 'BiSpectral Index Monitoring', 'Onset', 'Focused Stroke Assessment',
        'Stroke Dysphagia Screen Part I', 'Stroke Dysphagia Screen Part II', 'Stroke Dysphagia Screen Part III',
        'NIH Stroke Scale Scores', 'Neurovascular Check Right Upper Extremity', 'Neurovascular Check Right Lower Extremity',
        'Neurovascular Check Left Upper Extremity', 'Neurovascular Check Left Lower Extremity', 'Alcohol Withdrawal Assessment Scale',
        'Pupillometer Checks', 'Glasgow Coma Scale', 'Glasgow Coma Scale (2 months - 2 years)', 'Glasgow Coma Scale (2-5 years)',
        'Brain Injury Assessment'
    ],
    'EENT': ['EENT', 'Mucositis Assessment', 'Stroke Dysphagia Screen Part I', 'Stroke Dysphagia Screen Part II', 'Stroke Dysphagia Screen Part III', 'Pupillometer Checks'],
    'cardiovascular': ['Cardiac', 'Temporary Pacemaker', 'Permanent Pacemaker'],
    'respiratory': ['Respiratory', 'Subcutaneous Emphysema'],
    'gastrointestinal': ['Gastrointestinal', 'Mucositis Assessment'],
    'genitourinary': ['Genitourinary'],
    'musculoskeletal': [
        'Musculoskeletal', 'Skeletal Traction', 'Halo Traction', 'Bucks Traction', 'CPM Machine', 'Musculoskeletal Brace',
        'Musculoskeletal Brace 2', 'Musculoskeletal Brace 3', 'Musculoskeletal Cast', 'Musculoskeletal Cast 2', 'Musculoskeletal Cast 3',
        'C-Collar', 'Immobilizer', 'Immobilizer 2', 'Immobilizer 3', 'Sling', 'Sling 2', 'Splint', 'Splint 2', 'Splint 3', 'Trough',
        'Trough 2', 'TLSO Brace', 'External Fixator 1', 'External Fixator 2', 'Neurovascular Check Right Upper Extremity', 'Neurovascular Check Right Lower Extremity','Neurovascular Check Left Upper Extremity', 'Neurovascular Check Left Lower Extremity',
    ],
    'integumentary': ['Integumentary', 'Leech Therapy', 'Flap', 'Flap 2', 'Flap 3'],
    'KUPIDS': ['KUPIDS Assessment', 'Part I, KUPIDS Diagnosis and History', 'Part II, KUPIDS Patient Evaluation', 'Part III, KUPIDS Swallow Screening']
}

def determine_categories(group_name):
    """
    Determines the category of the given group name.
    """
    group_name = group_name.strip()
    relevant_categories = []
    for category, group_names in categories.items():
        if group_name in group_names:
            relevant_categories.append(category)
    return relevant_categories

df['assessment_names'] = df['group_name'].apply(determine_categories)


# In[8]:


# print(df.sample(n=1))


# In[9]:


import json
import os
from zipfile import ZipFile

# Helper function to escape LaTeX special characters
def escape_latex_special_chars(text):
    if not text:
        return ''
    replacements = {
        '\\': r'\textbackslash{}',
        '{': r'\{',
        '}': r'\}',
        '#': r'\#',
        '%': r'\%',
        '&': r'\&',
        '_': r'\_',
        '$': r'\$',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        '<': r'\textless{}',
        '>': r'\textgreater{}',
    }
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text

# Helper function to check if all options have a maximum of 2 words
def all_options_short(options):
    return all(len(option.split()) <= 2 for option in options)

def create_latex_from_json(json_file_path):
    # Read the JSON file
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    # Start writing LaTeX content
    latex_content = r'''
\documentclass{article}
\usepackage{lmodern}
\usepackage{geometry}
\geometry{margin=1in}
\begin{document}
'''

    # Initialize question counter
    question_counter = 1

    # Process the JSON data
    templates = data.get('templates', [])
    for template in templates:
        template_name = escape_latex_special_chars(template.get('name', 'Unnamed Template'))
        latex_content += f"\\section*{{Template: {template_name}}}\n"

        groups = template.get('groups', [])
        for group in groups:
            group_name = escape_latex_special_chars(group.get('name', 'Unnamed Group'))
            latex_content += f"\\subsection*{{Group: {group_name}}}\n"

            rows = group.get('rows', [])
            for row in rows:
                row_name = escape_latex_special_chars(row.get('name', 'Unnamed Row'))
                
                # Add question number
                latex_content += f"\\textbf{{Q{question_counter}: {row_name}}}\n\n"
                question_counter += 1  # Increment question counter

                # Gather options and check their length
                options = [escape_latex_special_chars(option.get('option', 'Unnamed Option')) for option in row.get('options', [])]

                if options:
                    if all_options_short(options):  # If all options are short, place them next to each other
                        latex_content += "A: \\parbox{\\textwidth}{\n"
                        for option in options:
                            latex_content += f"{option} \\quad "  # Use \\quad for spacing between options
                        latex_content += "}\n\n"
                    else:  # If any option is longer than 2 words, use itemize
                        latex_content += "A: \\begin{itemize}\n"
                        for option in options:
                            latex_content += f"  \\item {option}\n"
                        latex_content += "\\end{itemize}\n\n"
                else:
                    latex_content += "A: No options provided.\n\n"

                # Additional tiny font information under each question
                row_information = escape_latex_special_chars(row.get('row_information', ''))
                additional_notes = escape_latex_special_chars(row.get('additional_notes', ''))
                if row_information:
                    latex_content += f"\\textit{{\\tiny Row Information: {row_information}}}\n\n"
                if additional_notes:
                    latex_content += f"\\textit{{\\tiny Additional Notes: {additional_notes}}}\n\n"

    # End the document
    latex_content += r'\end{document}'

    # Write LaTeX content to file
    latex_file_path = 'output.tex'
    with open(latex_file_path, 'w') as latex_file:
        latex_file.write(latex_content)

    # Compress the LaTeX file into a zip file
    zip_file_path = 'latex_output.zip'
    with ZipFile(zip_file_path, 'w') as zip_file:
        zip_file.write(latex_file_path, os.path.basename(latex_file_path))
    
    # Clean up the intermediate .tex file
    os.remove(latex_file_path)

    return zip_file_path

# Example usage:
# json_file_path = 'path/to/your/json_file.json'
# output_zip_path = create_latex_from_json(json_file_path)
# print(f"LaTeX file is compressed and saved at: {output_zip_path}")


# In[21]:


# create_latex_from_json('/Users/anujshah/Downloads/nurse-summary-automation/form.json')


# In[ ]:




