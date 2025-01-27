import os
import requests
import argparse
from collections import defaultdict

# Gemini API details
GEMINI_API_URL = "https://gemini.googleapis.com/v1/models/gemini-3.5-flash:generateDocumentation"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def extract_code(file_path):
    """Reads and returns the content of the given source file."""
    with open(file_path, "r") as file:
        return file.read()

def generate_documentation(source_code, file_name):
    """Generates documentation for a file using Gemini API."""
    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = f"Generate documentation for the file '{file_name}' with the following code:\n\n{source_code}"
    payload = {"prompt": prompt, "language": "python", "output_format": "markdown"}
    response = requests.post(GEMINI_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json().get("content", "")
    else:
        raise Exception(f"Gemini API Error: {response.status_code}, {response.text}")

def read_existing_readme():
    """Reads the existing README.md content."""
    if os.path.exists("README.md"):
        with open("README.md", "r") as file:
            return file.read()
    return ""

def update_readme_content(readme_content, new_sections):
    """Integrates new sections into the existing README.md."""
    updated_content = readme_content.split("\n")
    updated_content.append("\n## Updated Documentation\n")
    for section_title, section_content in new_sections.items():
        updated_content.append(f"### {section_title}\n")
        updated_content.append(section_content)
        updated_content.append("\n")
    return "\n".join(updated_content)

def main(changed_files_path):
    """Main function to update README.md based on changed files."""
    # Read the list of changed files
    with open(changed_files_path, "r") as file:
        changed_files = [line.strip() for line in file if line.strip().endswith(".py")]

    if not changed_files:
        print("No Python files were modified. Skipping README update.")
        return

    # Generate documentation for changed files
    new_sections = defaultdict(str)
    for file in changed_files:
        try:
            print(f"Processing {file}...")
            code = extract_code(file)
            documentation = generate_documentation(code, file)
            new_sections[file] = documentation
            print(f"Documentation generated for {file}.")
        except Exception as e:
            print(f"Error processing {file}: {e}")

    # Read the existing README.md
    existing_readme = read_existing_readme()

    # Update README.md content
    updated_readme = update_readme_content(existing_readme, new_sections)

    # Save updated README.md
    with open("README.md", "w") as file:
        file.write(updated_readme)

    print("README.md updated successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update README.md with new documentation.")
    parser.add_argument("--changed-files", required=True, help="Path to the file containing the list of changed files.")
    args = parser.parse_args()

    main(args.changed_files)
