import os
import re
import glob
import json

def extract_name(file_basename):
    return '_'.join(tmp.split('_')[:-1])

def find_ground_truth_file_if_exists(filled_form_file_path, type):
    directory = f"./data/test/{type}"
    tmp, extension = os.path.splitext(filled_form_file_path)
    foundation_name = os.path.basename('_'.join(tmp.split('_')[:-1]))
    pattern = os.path.join(directory, '**', f'*{extension}')
    all_files = glob.glob(pattern, recursive=True)
    matching_files = [file for file in all_files if foundation_name in os.path.basename(file)]
    if matching_files:
        return matching_files[0]
    else:
        return None    

def compare_json_files(pred_file_path, gt_file_path):
    """
    Compare two JSON files and list:
    1. Keys missed (present in ground truth but not in prediction)
    2. Keys overfilled (present in prediction but not in ground truth)
    3. Keys filled incorrectly (present in both but with different values)
    
    :param gt_file_path: str, file path for the ground truth JSON file
    :param pred_file_path: str, file path for the predicted JSON file
    :return: dict, a dictionary containing the counts and lists of keys for each category
    """
    with open(gt_file_path, 'r') as gt_file:
        ground_truth = json.load(gt_file)
    
    with open(pred_file_path, 'r') as pred_file:
        prediction = json.load(pred_file)
    
    gt_keys = set(ground_truth.keys())
    pred_keys = set(prediction.keys())
    
    keys_missed = gt_keys - pred_keys
    
    keys_overfilled = pred_keys - gt_keys
    
    keys_filled_incorrectly = {
        key for key in gt_keys & pred_keys 
        if ground_truth[key] != prediction[key]
    }
    
    # Result dictionary with counts and lists of keys
    result = {
        "number_of_keys_missed": len(keys_missed),
        "keys_missed": list(keys_missed),
        "number_of_keys_overfilled": len(keys_overfilled),
        "keys_overfilled": list(keys_overfilled),
        "number_of_keys_filled_incorrectly": len(keys_filled_incorrectly),
        "keys_filled_incorrectly": list(keys_filled_incorrectly),
    }
    
    return result

def compare_txt_files(pred_file_path, gt_file_path):
    def compute_similarity(text1, text2):
        vectorizer = TfidfVectorizer().fit_transform([text1, text2])
        vectors = vectorizer.toarray()
        return cosine_similarity(vectors)[0, 1]
    with open(pred_file_path, 'r') as file:
        pred_text = file.read()
    with open(gt_file_path, 'r') as file:
        gt_text = file.read()
    return compute_similarity(pred_text, gt_text)

def compare(file_path, type):
    gt_file_path = find_ground_truth_file_if_exists(file_path, type)
    if gt_file_path:
        match type:
            case "filled_forms":
                return compare_json_files(file_path, gt_file_path)
            case "chunks":
                return compare_json_files(file_path, gt_file_path)
            case "transcriptions":
                return compare_txt_files(file_path, gt_file_path)

    else:
        print("Comparision could not be because gt does not exist")

if __name__=="__main__":
    compare('/Users/anujshah/Downloads/nurse-summary-automation/data/trials/filled_forms/Tanay 3_3.json', 'filled_forms')