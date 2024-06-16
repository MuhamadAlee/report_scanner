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

    @staticmethod
    def filter_text(text):
        """"
        using regular expression extract useful information only
        """
        # Define the pattern to match content between {RADIOLOGY} and {~~End of report~~}
        pattern = re.compile(r'RADIOLOGY(.*?)~~End of report~~', re.DOTALL)
        match = re.search(pattern, text)
    
        # If a match is found, return the matched group
        if match:
            return match.group(1).strip()
        else:
            return None

    def content_extraction(self, file_path):
        """
        extracts the actual textual meaningful content from the reports
        """
        report_content = ""
        pages = convert_from_path(file_path, 300)
        for page in pages:
            report_content += pytesseract.image_to_string(page)

        report_content = Extractor.filter_text(report_content)
        return report_content
    
if __name__=="__main__":
    ext = Extractor()
    file_path = "/home/alee/Documents/projects/report_scanner/sample_reports/ultrasound-abdo.pdf"

    content = ext.content_extraction(file_path)
    print(content)

            

