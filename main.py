#!/usr/bin/env python3
import os
import json
from process_pdfs import PDFOutlineExtractor

def main():
    input_dir = "/app/input"
    output_dir = "/app/output"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Process all PDF files in input directory
    extractor = PDFOutlineExtractor()
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(input_dir, filename)
            output_filename = filename.replace('.pdf', '.json')
            output_path = os.path.join(output_dir, output_filename)
            
            try:
                result = extractor.extract_outline(pdf_path)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                print(f"Successfully processed: {filename}")
                
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                # Create empty result for failed files
                empty_result = {"title": "", "outline": []}
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(empty_result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
