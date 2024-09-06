import streamlit as st
import json
import base64
import requests
import fitz  # PyMuPDF
import tempfile
from functools import partial
from multiprocessing import Pool

# Define constants
api_key = "487dbbf0df454ee6be002a5f77b0d04f"
endpoint = "https://weev.openai.azure.com/"

# Function to encode image to base64
def encode_image(image):
    return base64.b64encode(image).decode('utf-8')

# Function to call GPT-Vision API
def gpt_vision(api_key, image_data):
    base64_image = encode_image(image_data)

    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
    }

    payload = {
        "messages": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "You analyze documents by finding the main points of the document in each section and in each paragraph with proper formatting in md format, converting tables into md format as well and convert the equations into latex. If there is a flowchart then write in an understandable and readable format .You are known for your accuracy and speed."
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    },
                    {
                        "type": "text",
                        "text": "Write whatever is written in this image in English in proper markdown formatting and do not write anything else. If there are equations then write it in latex form. If the image has another language, convert it into english."
                    }
                ]
            }
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 4096,
    }

    gpt4v_endpoint = f"{endpoint}openai/deployments/gptomni/chat/completions?api-version=2024-02-15-preview"

    try:
        response = requests.post(gpt4v_endpoint, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.RequestException as e:
        st.error(f"Error: {e}")
        return None

# Function to process individual page
def process_page(api_key, pdf_file_path, page_number):
    doc = fitz.open(pdf_file_path)
    page = doc[page_number]
    pix = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72))
    image_data = pix.tobytes("jpg")
    doc.close()
    return gpt_vision(api_key, image_data)

# Streamlit app
def main():
    st.title("PDF to Markdown with GPT-Vision")
    
    # Upload PDF file
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
    
    if uploaded_file is not None:
        # Use a temporary file to save the uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(uploaded_file.read())
            pdf_file_path = temp_pdf.name

        # Display the PDF preview
        with fitz.open(pdf_file_path) as doc:
            num_pages = len(doc)
            st.write(f"Total Pages: {num_pages}")
        
        if st.button("Process PDF"):
            progress_bar = st.progress(0)

            results = []
            with Pool(processes=10) as pool:  # Adjust the number of processes
                func = partial(process_page, api_key, pdf_file_path)
                for i in range(num_pages):
                    result = pool.apply_async(func, args=(i,)).get()
                    if result is not None:
                        results.append(f"# Page {i + 1}\n\n{result}\n\n---\n\n")
                        progress_bar.progress((i + 1) / num_pages)

            if results:
                markdown_output = "\n".join(results)
                st.markdown(markdown_output, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
