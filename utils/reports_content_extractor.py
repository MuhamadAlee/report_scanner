import re
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

class Extractor:
    """
    extracts the text from the report
    """

    def __init__(self):
        """
        constructor
        """

    def content_extraction(self, file_path):
        """
        extracts the actual textual meaningful content from the reports
        """
        report_content = ""
        pages = convert_from_path(file_path, 300)
        for page in pages:
            report_content += pytesseract.image_to_string(page)
        return report_content
    


            

