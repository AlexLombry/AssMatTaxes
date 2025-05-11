import os
import re
import argparse
from decimal import Decimal
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import io

def debug_print(*args, debug=False):
    if debug:
        for arg in args:
            print(f"Debug: {arg}")

def extract_amounts_from_text(text, debug=False):
    # Pattern to match amounts in French format (e.g., 1 234,56 or 1234,56)
    amount_pattern = re.compile(r'[0-9]+[ ,]*[0-9]*\.[0-9]+')
    amounts = []
    
    lines = text.split('\n')
    for line in lines:
        if 'Mont' in line:
            debug_print(f"Found line with 'Mont': {line}", debug=debug)
            matches = amount_pattern.findall(line)
            for match in matches:
                # Remove spaces and replace comma with dot
                clean_value = match.replace(' ', '').replace(',', '.')
                debug_print(f"Found amount: {clean_value}", debug=debug)
                try:
                    amount = Decimal(clean_value)
                    amounts.append(amount)
                except Exception as e:
                    debug_print(f"Error converting amount {clean_value}: {str(e)}", debug=debug)
    
    return amounts

def process_pdf(file_path, debug=False):
    debug_print(f"Processing PDF file: {file_path}", debug=debug)
    amounts_found = []
    
    try:
        # Convert PDF pages to images
        images = convert_from_path(file_path)
        
        for page_num, image in enumerate(images):
            debug_print(f"Processing page {page_num + 1}", debug=debug)
            
            # Extract text using OCR
            text = pytesseract.image_to_string(image, lang='fra')
            
            # Extract amounts from the text
            page_amounts = extract_amounts_from_text(text, debug)
            for amount in page_amounts:
                amounts_found.append((page_num + 1, amount))
            
            debug_print(f"Found {len(page_amounts)} amounts on page {page_num + 1}", debug=debug)
    
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return None
    
    total_amount = sum(amount for _, amount in amounts_found)
    
    return {
        'file_name': os.path.basename(file_path),
        'total_amount': total_amount,
        'amounts_found': amounts_found
    }

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Process PDF files to find tax deduction amounts using OCR.')
    parser.add_argument('--debug', '-v', action='store_true', help='Enable debug mode to show detailed processing information')
    args = parser.parse_args()
    
    # Get all PDF files in the current directory
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found in the current directory.")
        return
    
    print("Processing PDF files...")
    print("-" * 50)
    
    grand_total = Decimal('0')
    
    for pdf_file in pdf_files:
        print(f"\nProcessing: {pdf_file}")
        result = process_pdf(pdf_file, args.debug)
        
        if result:
            print(f"Total amount found: {result['total_amount']:,.2f} €")
            print("Amounts found by page:")
            for page_num, amount in result['amounts_found']:
                print(f"  Page {page_num}: {amount:,.2f} €")
            grand_total += result['total_amount']
    
    print("\n" + "=" * 50)
    print(f"Grand total across all files: {grand_total:,.2f} €")

if __name__ == "__main__":
    main() 