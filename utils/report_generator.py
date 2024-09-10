import os
import re
import random
import json
import base64
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from typing import List, Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class ReportGenerator:
    """
    generates layman report based on uploaded report
    """

    def __init__(self):
        """
        constructor
        """
        load_dotenv()
        
        self.llm_3  = ChatOpenAI(
            api_key= os.getenv('OPENAI_API_KEY'),
            model=os.getenv('MODEL_GPT_3.5'), 
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )

        self.llm_4  = ChatOpenAI(
            api_key= os.getenv('OPENAI_API_KEY'),
            model=os.getenv('MODEL_GPT_4'), 
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )

        self.llm_4_mini  = ChatOpenAI(
            api_key= os.getenv('OPENAI_API_KEY'),
            model=os.getenv('MODEL_GPT_4_MINI'), 
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )




    def get_formatted_report(self, report):
        """
        get formatted report from input text
        """
        # if len(report)<100:
        #     return "Invalid Report"
        
        format_template = """
           You are a medical expert who is provided with a Medical Report delimited by triple quotes. You are suppose to perform following operations:
            - Read out of the given report carefully and decide wheather its a medical report or raw text. Your decision should be based on the content of the report. If it has patient's information, diagnoses or any medical information, then it must be a medical report.
            - Classify the medical report as medical diagnoses or random text. It's random text just return 'report_satatus' as 'Invalid Report', otherwise perfrom below tasks.
            - Place the 'report_status' as 'medical diagnoses' inside the JSON output first.
            - Structure the report into patient-centered interactive report.
            - Extract the name of the patient from the given report and place it under key 'patient_name'.
            - IMPORTANT ! Becasue its medical report so don't try to change the wording of report, just structure it in readable manner.
            - Don't miss any section of the report.
            - Your final response should only be in following JSON format.
            - Extract the headings from the report and their values as well.
            - Finally make object of JSON having multiple key value pairs e.g heading as key and its value.
           Here's is the medical report : '''{report}'''
        """
    

        format_prompt = PromptTemplate(
            template= format_template,
            input_variables=["report"]
        )
        output_parser = JsonOutputParser()

        format_chain = format_prompt | self.llm_4_mini | output_parser
        formatted_report = format_chain.invoke({"report": report})

        return formatted_report
    
    def get_medical_terms(self, report):
        """
        returns the dictionary of the medical terminologies
        """

        class Term(BaseModel):
            term: str = Field(description="medical term or complex term")
            definition: str  = Field(description="plain layman english explaination or definition of the medical term or complex term")

        terms_template = """
           You are a medical expert who is provided whose task is to provide detailed explaination of each and every terms used in provided Medical Report delimited by triple quotes. You are suppose to perform following operations:
            - Extract each and every medical term or complex term seperately which is used inside the report. Make sure you don't miss any medical term.
            - CARFULL! Don't miss any medical word, medical term, or medical jorgan used inside the report. Its super important to cover all terms or words.
            - Prepare plain layman english explaination or definition of these terms.
            - Definition or explaination of medical term or complex term must be detailed not 1 liners.
            - Don't miss any term of the report. But avoid adding explaination for too obvious terms e.g name date etc.
            - Consider case senstivity for medical terms as keys of dictionary must exactly match with terms used in medical report.
            - IMPORTANT!! As this is medical report so please don't miss any complex term or medical term or even a single medical word.
            - Finally return the list of terms and definitions dictionary and remember your final response must be according to the below instructions.
                \n{format_instructions}
            Here's is the medical report : '''{report}'''
        """
        output_parser = JsonOutputParser(pydantic_object=Term)
        terms_prompt = PromptTemplate(
            template= terms_template,
            input_variables=["report"],
            partial_variables={"format_instructions": output_parser.get_format_instructions()},
        )

        terms_chain = terms_prompt | self.llm_4_mini | output_parser
        terms_response = terms_chain.invoke({"report": report})
        return terms_response
    
    @staticmethod
    def convert_image_to_base64(image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    @staticmethod
    def transform_dicts(list_of_dicts):
        responses = list()
        for item in list_of_dicts:
            if (item["organ_system"] is not None) and (item["organ_system_portion"] is not None):
                # image = (os.path.join(str(Path(__file__).resolve().parent.parent), "images", item["organ_system"], f'{item["organ_system_portion"]}.jpg'))
                # with open(image, "rb") as image_file:
                #     image = base64.b64encode(image_file.read()).decode('utf-8')

                image = os.path.join(os.getenv('HOST_URL'),"images", item["organ_system"], f'{item["organ_system_portion"]}.jpg')
            else:
                image = None

            responses.append({"term":item['term'],
                              "image": image})
        return responses        
    
    def identify_images(self, medical_terms: list, human_organ_system: dict):
        """
        extracts relevant images with respect to medical term used
        """
        class OrganSystem(BaseModel):
            term: str = Field(description="medical term from the list")
            organ_system: str = Field(description="identified item from given organ system JSON object")
            organ_system_portion: str = Field(description="identified portion from given organ system list inside JSON object")

        organ_system_template = """
        You are medical expert who is provided following information.
            - A list of medical terms which mostly used in diagnoses process below. 
                \n{medical_terms}\n
            - A JSON object having keys as Human Organ System and values as the list of items inside each organ system below.
                \n{human_organ_system}\n
        Now you are supposed to perform following operations:
            - Read out each of the medical term from the list and figure out which item of Human Organ System it belongs to.
            - If medical term is not related to any of the item of any organ system, simply place None.
            - IMPORTANT! Don't go outside the scope of provided JSON object of human Organ system.
            - As this is about medical diagnoses so, please be deadly accurate in mapping
            - Once each medical term mapped with relevant item of human organ system, make a final JSON object with following instructions.
            - Final Json object must have one key as properties and values as JSON object

                \n{format_instructions}
        """

        output_parser = JsonOutputParser(pydantic_object=OrganSystem)
        organ_system_prompt = PromptTemplate(
            template= organ_system_template,
            input_variables=["medical_terms", "human_organ_system"],
            partial_variables={"format_instructions": output_parser.get_format_instructions()},
        )

        organ_system_chain = organ_system_prompt | self.llm_4_mini | output_parser
        organ_system_response = organ_system_chain.invoke({"medical_terms": medical_terms, "human_organ_system": human_organ_system})
        organ_system_response = self.transform_dicts(organ_system_response['properties'])
        return organ_system_response
        
    def report_formatting_from_dictionary(self, report_dictionary, indent=0):
        """
        converts dictionary to string format
        """

        result = []
        indent_str = '  ' * indent
        for key, value in report_dictionary.items():
            if isinstance(value, dict):
                result.append(f"{indent_str}{key}:")
                result.append(self.report_formatting_from_dictionary(value, indent + 1))
            else:
                result.append(f"{indent_str}{key}: {value}")
        return "\n".join(result)
    def generate_unique_code(self):
        """Generate a 4-digit unique code."""
        return random.randint(1000, 9999)

    def get_llm_response(self, report):
        """
        generates query to chat gpt
        """

        formatted_report = self.get_formatted_report(report)
        print(" -------------------- report formatting done --------------------")
        if "invalid report" in formatted_report['report_status'].lower():
            return {
                "report_code": 0,
                "patient_name": None,
                "report": "Invalid Report",
                "medical_terms": [],
                "images": []
            }
        
        try:
            medical_terms = self.get_medical_terms(self.report_formatting_from_dictionary(formatted_report['report']))
            if len(medical_terms)==1: 
                if type(medical_terms)==dict:
                    _, medical_terms = next(iter(medical_terms.items()))

            terms = [dictionary['term'] for dictionary in medical_terms]
            print("-------------------- medical terms extraction done --------------------")
            human_organ_system = None
            with open( os.path.join(SCRIPT_DIR, os.getenv("ORGAN_SYSTEM_MAPPING_JSON")), 'r') as file:
                human_organ_system = json.load(file)

            images_path = self.identify_images(terms, human_organ_system)
            print("-------------------- images generation done --------------------")

            return {
                "report_code": self.generate_unique_code(),
                "patient_name": formatted_report['patient_name'],
                "report": formatted_report['report'],
                "medical_terms": medical_terms,
                "images": images_path
            }


        except:
            return{
                "report_code": 0,
                "patient_name": None,
                "report": "Invalid Report",
                "medical_terms":  [],
                "images": []
            }
            
        
        


    
