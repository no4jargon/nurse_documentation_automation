import pandas as pd
import json

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

def flatten_json(json_data):
    """
    Flattens the JSON structure to extract relevant information and returns a DataFrame.
    """
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

    # Convert the list of rows to a DataFrame
    df = pd.DataFrame(rows)
    return df


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

def process_json_file(json_path):
    """
    Reads a JSON file, flattens it, categorizes the data, and returns a processed DataFrame.
    """
    with open(json_path, 'r') as file:
        json_data = json.load(file)

    # Flatten the JSON data
    df = flatten_json(json_data)
    
    # Determine categories for each group name
    df['assessment_names'] = df['group_name'].apply(determine_categories)
    return df

