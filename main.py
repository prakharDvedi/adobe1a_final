#!/usr/bin/env python3
import os
import json
from process_pdfs import PDFOutlineExtractor

def main():
    input_dir = "/app/input"
    output_dir = "/app/output"
    
    if not os.path.exists(input_dir):
        print(f"Error: Input directory {input_dir} does not exist or is not mounted")
        return
    
    if not os.access(input_dir, os.R_OK):
        print(f"Error: Input directory {input_dir} is not readable")
        return
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        if not os.access(output_dir, os.W_OK):
            print(f"Error: Output directory {output_dir} is not writable")
            return
    except Exception as e:
        print(f"Error creating output directory {output_dir}: {str(e)}")
        return
    
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s) to process")
    
    extractor = PDFOutlineExtractor()
    processed_count = 0
    
    for filename in pdf_files:
        pdf_path = os.path.join(input_dir, filename)
        output_filename = filename.replace('.pdf', '.json')
        output_path = os.path.join(output_dir, output_filename)
        
        try:
            result = extractor.extract_outline(pdf_path)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"Successfully processed: {filename}")
            processed_count += 1
            
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            empty_result = {"title": "", "outline": []}
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(empty_result, f, indent=2, ensure_ascii=False)
                print(f"Created empty result for: {filename}")
            except Exception as write_error:
                print(f"Failed to create output file for {filename}: {str(write_error)}")
    
    print(f"\nProcessing complete: {processed_count}/{len(pdf_files)} files processed successfully")

if __name__ == "__main__":
    main()
