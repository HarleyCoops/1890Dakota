import os
import google.generativeai as genai
from pathlib import Path

# Configure the API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(str(path), mime_type=mime_type)
    print(f"Processing file: {path.name}")
    return file

def save_latex_output(latex_content, output_path):
    """Saves the LaTeX content to a file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    print(f"Saved LaTeX output to: {output_path}")

# Set up paths
images_dir = Path("C:/Users/admin/1890Dakota/Data/sources/Images")
latex_dir = Path("C:/Users/admin/1890Dakota/Data/sources/Latex")
latex_dir.mkdir(exist_ok=True)

# Configure Gemini model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-pro-exp-02-05",
    generation_config=generation_config,
)

# Process all jpg files in the directory
for image_path in sorted(images_dir.glob("*.jpg")):
    # Create output filename
    latex_filename = image_path.stem + ".tex"
    output_path = latex_dir / latex_filename
    
    # Skip if output file already exists
    if output_path.exists():
        print(f"Skipping {image_path.name} - output already exists")
        continue
    
    try:
        # Upload image to Gemini
        file = upload_to_gemini(image_path, mime_type="image/jpeg")
        
        # Start chat session and request LaTeX output
        chat = model.start_chat()
        response = chat.send_message([
            file,
            "Extract the text from this image and return it in fully formatted LaTeX using article class with amsmath package. Include proper formatting for dictionary entries including italics for part of speech markers."
        ])
        
        # Save the LaTeX output
        latex_content = response.text
        if latex_content.startswith("```latex"):
            latex_content = latex_content[7:-3]  # Remove markdown code block markers
        save_latex_output(latex_content, output_path)
        
    except Exception as e:
        print(f"Error processing {image_path.name}: {str(e)}")

print("Processing complete!")