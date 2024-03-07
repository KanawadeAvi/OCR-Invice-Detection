from flask import Flask, request, jsonify
from PIL import Image
from pytesseract import pytesseract
import re
from dateutil.parser import parse
import spacy

app = Flask(__name__)

pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class OCR:
    def extract_text(self, image):
        try:
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            print(e)
            return "Error"

    def extract_date_and_time(self, text):
        dates = re.findall(r'\b\d{1,4}[-/]\d{1,2}[-/]\d{1,4}\b', text)
        times = re.findall(r'\b(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d)?\b', text)
        parsed_dates = [parse(date).strftime('%Y-%m-%d') for date in dates]

        return {'dates': parsed_dates, 'times': times}

    def extract_email_addresses(self, text):
        email_addresses = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', text)
        return {'email_addresses': email_addresses}

    def extract_phone_numbers(self, text):
        phone_numbers = re.findall(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', text)
        return {'phone_numbers': phone_numbers}


    def extract_addresses(self, text):
       addresses = re.findall(r'\b\d+\s+\S[^,]*,\s*\S[^,]*,\s*\S.*?\b', text)
       return {'addresses': addresses}


    def extract_supplier_names(self, text):
        supplier_names = re.findall(r'Supplier:\s*([^\n\r]+)', text)
        return {'supplier_names': supplier_names}

    def extract_gst_numbers(self, text):
        gst_numbers = re.findall(r'\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}\d[Z]{1}\d{1}\b', text)
        return {'gst_numbers': gst_numbers}

   

    def extract_supplier_names(self, text):
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)

        supplier_names = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
        return {'supplier_names': supplier_names}

    def extract_names(self, text):
        # Regular expression to capture common name patterns
        name_patterns = re.findall(r'\b(?:Mr\.|Ms\.|Mrs\.|Dr\.|Miss)?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', text)

        # spaCy named entity recognition for additional names
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        ner_names = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']

        # Combine results from regular expression and spaCy
        names = list(set(name_patterns + ner_names))

        return {'names': names}

ocr = OCR()

@app.route('/extract_image', methods=['POST'])
def extract_date_and_time_api():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        image = request.files['image']

        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if '.' not in image.filename or image.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return jsonify({'error': 'Invalid file format'}), 400

        img = Image.open(image)

        extracted_text = ocr.extract_text(img)
        extracted_date_time = ocr.extract_date_and_time(extracted_text)
        extracted_email_addresses = ocr.extract_email_addresses(extracted_text)
        extracted_phone_numbers = ocr.extract_phone_numbers(extracted_text)
        extracted_addresses = ocr.extract_addresses(extracted_text)
        extracted_supplier_names = ocr.extract_supplier_names(extracted_text)
        extracted_gst_numbers = ocr.extract_gst_numbers(extracted_text)
        
        return jsonify({'date_and_time': extracted_date_time, 
                        'email_addresses': extracted_email_addresses,
                        'phone_numbers': extracted_phone_numbers,
                        'addresses': extracted_addresses,
                        'supplier_names': extracted_supplier_names,
                        'gst_numbers': extracted_gst_numbers}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
