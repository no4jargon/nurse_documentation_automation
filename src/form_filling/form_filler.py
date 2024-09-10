# form_filler.py
import os
import re
import time
import json 

from openai import OpenAI
from enum import Enum
from pydantic import BaseModel, create_model
from typing import Optional
from tqdm import tqdm

import import_ipynb

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

system_prompt = "You are an medical expert in the assessment_placeholder assessment. You will be given an unstructured medical information and you can try to honestly extract information about a specific line-item in assessment_placeholder assessment. It is completely alright to not fill in any information, if unsure or unclear."

user_prompt = """For line item 'row_name_placeholder' with respect to the assessment_placeholder assessment, use the following structured information to fill in the values: "chunk_information_placeholder". This line item is within the 'group_name_placeholder' subgroup of a larger form """

assistant_prompt = """The following information about the line item can help you fill in the line item 

1. row_information_placeholder
2. additional_notes_placeholder

If the information is not explicitly clear choose, "Line item cannot be filled with the provided information".
If unsure or unclear, choose "Line item cannot be filled with the provided information".
"""


def find_relevant_rows(form_dataframe, assessment_name):
    return form_dataframe[assessment_name.lower() in form_dataframe['assessment_names'].str.lower()]

def fill_row(row, chunked_output):
    try:
        relevant_assessments = [assessment_name for assessment_name in row["assessment_names"] if chunked_output[assessment_name]['is_referred_to_in_summary']]
        if relevant_assessments:
            relevant_information = {assessment_name: chunked_output[assessment_name] for assessment_name in relevant_assessments}
            relevant_assessments = ' '.join(relevant_assessments)
            group_name : str = row["group_name"]
            row_name : str = row["row_name"]
            row_information : str = row["row_information"]
            additional_notes : str = row["additional_notes"]
            options : dict = {string.replace('"', ''): string.replace('"', '') for string in row["options"]}
            options["Line item cannot be filled with the provided information"] = "Line item cannot be filled with the provided information"
            if options:
                Options_class = Enum('Options',options)
                Response_class = create_model(
                    'Response',
                    line_item_cannot_be_filled_with_the_provided_information=(bool, ...),
                    line_item_entry_if_sufficient_information=(Options_class, ...)
                )
                Response_class.model_rebuild()
            else:
                Response_class = create_model(
                    'Response',
                    line_item_cannot_be_filled_with_the_provided_information=(bool, ...),
                    line_item_entry_if_sufficient_information=(Optional[str], None)
                )
            try:
                answer = client.beta.chat.completions.parse(
                        model="gpt-4o-2024-08-06",
                        messages=[
                            {"role": "system", "content": system_prompt.replace("assessment_placeholder", relevant_assessments)},
                            {"role": "user", "content": user_prompt.replace("assessment_placeholder", relevant_assessments).replace("row_name_placeholder", row_name).replace("chunk_information_placeholder", str(relevant_information)).replace("group_name_placeholder", group_name)},
                            {"role": "assistant", "content": assistant_prompt.replace("row_information_placeholder", row_information).replace("additional_notes_placeholder", additional_notes)}
                        ],
                        response_format=Response_class
                    ).choices[0].message.parsed
                number_of_tokens_called = (4/3)*len(f"""
                    {system_prompt.replace("assessment_placeholder", relevant_assessments)} 
                    {user_prompt.replace("assessment_placeholder", relevant_assessments).replace("row_name_placeholder", row_name).replace("chunk_information_placeholder", str(relevant_information))} {assistant_prompt.replace("row_information_placeholder", row_information).replace("additional_notes_placeholder", additional_notes)}
                                            """.split())
                if answer:
                    answer = answer.__dict__
                else:
                    return None, None, 0
            except:
                print(f"This {row_name} errored. Try to figure why?")
                return None, None, 0
            
            if answer["line_item_cannot_be_filled_with_the_provided_information"] or not answer["line_item_entry_if_sufficient_information"] or answer["line_item_entry_if_sufficient_information"].value=="Line item cannot be filled with the provided information":
                return None, None, 0
            else:
                return row_name, answer["line_item_entry_if_sufficient_information"].value, number_of_tokens_called
            
        return None, None, 0
    except:
        return None, None, 0

            
def fill_form_from_chunks(form_dataframe, chunked_output):
    filled_rows = {}
    assessment_names = [i for i,v in chunked_output.items()]
    total_number_of_tokens_called = 0
    t = time.time()
    for index, row in tqdm(form_dataframe.iterrows()):
        row_name, answer, number_of_tokens_called = fill_row(row, chunked_output)
        total_number_of_tokens_called += number_of_tokens_called
        if row_name and answer:
            filled_rows[re.sub(r'\[\d+\]', '', row_name).strip()] = answer
        if index % 100 == 0:
            print(f"Total tokens used = {total_number_of_tokens_called} \n Avarage tokens per call = {total_number_of_tokens_called/(index+1)}")
            print(f"Total time {time.time()-t} for {index+1} rows \n Avarage time per call = {(time.time()-t)/(index+1)}")
    return filled_rows

def save_filled_form(filled_form:dict, json_file_path: str):
    with open(json_file_path, 'w') as file:
        json.dump(filled_form, file, indent=4)
    print(f"JSON content saved to {json_file_path}")

if __name__ == "__main__":
    chunked_output = {
        'neurological': {'is_referred_to_in_summary': True, 'exceptions_to_within_defined_limits': 'patient is anxious but cooperative, intubated, tract strengths are 4s in uppers and 3s in lowers'}, 'EENT': {'is_referred_to_in_summary': True, 'exceptions_to_within_defined_limits': 'bilateral hearing and vision impairments, tongue and oral mucosa is dry, teeth are decayed and missing'}, 'cardiovascular': {'is_referred_to_in_summary': True, 'exceptions_to_within_defined_limits': 'click present'}, 'respiratory': {'is_referred_to_in_summary': True, 'exceptions_to_within_defined_limits': 'diseased lungs, decreased lung sounds in the right base'}, 'gastrointestinal': {'is_referred_to_in_summary': True, 'exceptions_to_within_defined_limits': 'abdomen is distended, patient with diarrhea and incontinence'}, 'genitourinary': {'is_referred_to_in_summary': True, 'exceptions_to_within_defined_limits': 'foliocytosis'}, 'musculoskeletal': {'is_referred_to_in_summary': True, 'exceptions_to_within_defined_limits': ''}, 'integumentary': {'is_referred_to_in_summary': True, 'exceptions_to_within_defined_limits': 'skin over trunk, back and upper extremities is bruised, dry and flaking.'}, 'KUPIDS': {'is_referred_to_in_summary': False, 'exceptions_to_within_defined_limits': ''}
        }
    form_dataframe = exploratory_analysis.df
    filled_rows = fill_form_from_chunks(form_dataframe, chunked_output)
    print(filled_rows)
    breakpoint()