import os
import google.generativeai as genai
import argparse
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY =  os.getenv('GEMINI_API_KEY')

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def response_generatior(headers, payload):
    response = model.generate_content([headers, payload])
    return response.text

def extract_code(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def generate_test_cases(source_code, file_name):
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "prompt" : f"Generate pytest test cases for the Flask application code in '{file_name}':\n\n{source_code}", 
        "language": "python", 
        "output_format": "python"
    }
    
    return response_generatior(headers, payload)

def save_test_cases(file_name, test_code):
    test_file_path = Path(f"tests/test_{file_name.replace('/', '_')}.py")
    os.makedirs(test_file_path.parent, exist_ok=True)
    with open(test_file_path, 'w') as file:
        file.write(test_code)
        
def main(changed_file_path):
    with open(changed_file_path, "r") as file:
        changed_files = [line.strip() for line in file if line.strip().endswith(".py")]
        
    if not changed_files:
        print("No Python files were modified. Skipping test case generation.")
        return
    
    for file in changed_files:
        try:
            print(f"Processing {file}...")
            code = extract_code(file)
            test_case = generate_test_cases(code, file)
            print("Generated test case:", test_case)
            save_test_cases(file.replace('/', '_').replace('.py', ''), test_case)
            print(f"Test generated for {file}")
        except Exception as e:
            print(f"Error processing {file}: {e}")
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate test cases for modified files.")
    parser.add_argument("--changed-files", required=True, help="Path to the file containing the list of changed files.")
    args = parser.parse_args()

    main(args.changed_files)