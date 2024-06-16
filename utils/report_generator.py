import os
import re
import json
from dotenv import load_dotenv
from openai import OpenAI

class ReportGenerator:
    """
    generates layman report based on uploaded report
    """

    def __init__(self):
        """
        constructor
        """
        load_dotenv()
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('MODEL')
        self.client = OpenAI()

    def get_llm_response(self, report):
        """
        generates query to chat gpt
        """




        persona = """
        You are a medical expert who is provided with a Medical Report delimited by triple quotes. You are suppose to perform following operations:
        - Structure the report into patient-centered interactive report with plain language explanations.
        - Reports should have headings and precise explainations for each heading.
        - Make a dictionary of all terms used in report along with thier plain english explaination.
        - Your final response should only be in following format.

        Format:
        - Generated report should be in following format.
        - Don't miss any section of the report.
        ```
            Something: The Something of the Something
            Something: The Something
            .
            .
            .
            Somethings: The Something
        ```
        - Generated report is placed in JSON object with key "response".
        - Another key "medical_terms" should have nested JSON object (having "medical_terms" as key and its "plain explainable definition" as value).
        ```JSON
           { {"response": "generated report", "medical_terms": {"term 1": "definition", "term2": "definition"}}}
        ```
        - Your final response must be a single JSON object.


        """

        messages=[
            {
            "role": "system",
            "content": [
                {
                "type": "text",
                "text": persona
                }
            ]
            },
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": f'"""Medical Report : {report}"""'
                }
            ]
            },
            {
            "role": "assistant",
            "content": [
                {
                "type": "text",
                "text": ""
                }
            ]
            }
        ]
    
        response = self.client.chat.completions.create(
            model=self.model,
            messages= messages,
            temperature=0, 
            max_tokens=4095
        )
        response = response.choices[0].message.content
        response = response.replace("\n", " ")
        return json.loads(response)
        


    
