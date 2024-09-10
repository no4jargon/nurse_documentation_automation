completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "You are medical professional who is well versed with reading patient status summaries. You have to corre"},
                {"role": "user", "content": f"{user_base_prompt} {transcription_text}"},
                {"role": "assistant", "content": assistant_prompt}
            ],
            response_format={
                "corrected_summary" : str
            },
        )