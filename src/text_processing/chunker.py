from openai import OpenAI
from enum import Enum
from typing import Dict, Tuple
from pydantic import BaseModel
import os
import json

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

class BodySystem():
    body_system_list = [
    "neurological",
    "EENT",
    "cardiovascular",
    "respiratory",
    "gastrointestinal",
    "genitourinary",
    "musculoskeletal",
    "integumentary",
    "KUPIDS"
]

class Chunk(BaseModel):
    is_referred_to_in_summary: bool
    exceptions_to_within_defined_limits: str

Chunk.model_rebuild()

chunker_schema_path = 'utils/chunker_schema.json'
with open(chunker_schema_path, 'r') as file:
    chunker_schema = json.load(file)

system_prompt = "You are an medical expert for the placeholder system. You will be given an unstructured medical summary and you should extract information about the placeholder system."

user_base_prompt = "Extract information about placeholder system from this summary"

assistant_base_prompt = """
    1. "is_referred_to_in_summary": If the summary refers to the placeholder system or any subject matter related to it, explicitly or implicitly, set this to True. If not, set to False. Look for short-forms like CV for cardiovascular, GI for gastrointestinal, GU for gastro urinary.

    2. "exceptions_to_within_defined_limits": If the summary refers to any to exceptions to within defined limits (WDL) in context of the placeholder system, add that infortmation here. Else set to false. There can be multiple of exceptions or abonormalities. This could include dates/numbers. Any additional information relevant to the placeholder system should be added here. 
    ---
    Examples
    input summary:
    "Pt Neuro WDL, EENT WDl except impaired vision bilaterally, CV WDL except left lower extremity pedal pulse present only with doppler, Respiratory WDL except lung sounds coarse throughout, GI/GU WDL, except urinary incontinence, musculoskeletal with partial and passive range of motion in all extremities, integumentary is WDL"

    output:
    {
        "neurological":
            {
            "is_referred_to_in_summary": True,
            "exceptions_to_within_defined_limits": None
            },
        "EENT":
            {
            "is_referred_to_in_summary": True,
            "exceptions_to_within_defined_limits": "impaired vision bilaterally"
            },
        "cardiovascular":
            {
            "is_referred_to_in_summary": True
            "exceptions_to_within_defined_limits": "left lower extremity pedal pulse present only with doppler"
            },
        "respiratory":
            {
            "is_referred_to_in_summary": True
            "exceptions_to_within_defined_limits": "lung sounds coarse throughout"
            },
        "gastrointestinal":
            {
            "is_referred_to_in_summary": True
            "exceptions_to_within_defined_limits": None
            },
        "gastrourinary":
            {
            "is_referred_to_in_summary": True
            "exceptions_to_within_defined_limits": "urinary incontinence"
            },
        "musculoskeletal":
            {
            "is_referred_to_in_summary": True
            "exceptions_to_within_defined_limits": "partial and passive range of motion in all extremities"
            },
        "integumentary":
            {
            "is_referred_to_in_summary": True
            "exceptions_to_within_defined_limits": None
            },
        "KUPIDS":
            {
            "is_referred_to_in_summary": False
            "exceptions_to_within_defined_limits": None
            }
    }"""


def chunk_transcription(transcription_text):
    """
    Chunk the transcription text into modules using GPT-4 API.
    
    Args:
    - transcription_text (str): The transcription text of a nurse summary.
    - api_key (str): The API key to authenticate with OpenAI.

    Returns:
    - list: A list of JSON objects with "system," "WDL," and "exceptions" fields.
    """
    if not api_key:
        raise ValueError("OpenAI API key not found in environment variables. Please set 'OPENAI_API_KEY'.")
    
    response = {}
    try:
        print("Chunking the transcription into modules...")
        for body_system in BodySystem.body_system_list:
            system_specific_information = client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": system_prompt.replace("placeholder", body_system)},
                    {"role": "user", "content": f"{user_base_prompt} {transcription_text}".replace("placeholder", body_system)},
                    {"role": "assistant", "content": assistant_base_prompt.replace("placeholder", body_system)}
                ],
                response_format=Chunk
            )
            response[body_system]=(system_specific_information.choices[0].message.parsed).__dict__
        return response

    except Exception as e:
        print(f"An error occurred while processing the transcription: {e}")
        return None
    
def save_chunks(chunked_output:Dict, json_file_path: str):
    """
    Save the JSON content to a file.
    
    Args:
        json_text (dict): The JSON content to save.
        json_file_path (str): Path to the output JSON file.
    """
    with open(json_file_path, 'w') as file:
        json.dump(chunked_output, file, indent=4)
    print(f"JSON content saved to {json_file_path}")


if __name__ == "__main__":
    # Example usage:
    transcription_text =  "PT neuro WDL, EENT WDL except impaired vision bilaterally, CV WDL except left lower extremity pedal pulse present only with Doppler, respiratory WDL except lung sounds coarse throughout, GI GU WDL except urinary incontinence, musculoskeletal with partial and passive range of motion in all extremities, and integumentary is WDL. Thank you."
    chunked_output = chunk_transcription(transcription_text)
    [print(i, v) for i, v in chunked_output.items()]
