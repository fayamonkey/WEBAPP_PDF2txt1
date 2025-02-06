import streamlit as st
import fitz  # PyMuPDF
import base64
import json
import os
from io import BytesIO

def extract_pdf_content(pdf_bytes):
    """Extract text and images from PDF bytes"""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    output = {"pages": []}
    
    for page_num, page in enumerate(doc, start=1):
        # Extract text
        text = page.get_text()
        
        # Extract images
        images = []
        for img in page.get_images(full=True):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            images.append(image_base64)
        
        output["pages"].append({
            "page_number": page_num,
            "text": text,
            "images": images
        })
    
    return output

def generate_json(output):
    """Convert extracted content to JSON format"""
    return json.dumps(output, indent=2)

def generate_markdown(output):
    """Convert extracted content to Markdown format"""
    md_content = ""
    for page in output["pages"]:
        md_content += f"## Page {page['page_number']}\n\n"
        md_content += page["text"] + "\n\n"
        
        for idx, img_base64 in enumerate(page["images"], start=1):
            md_content += f"![Image {idx}](data:image/png;base64,{img_base64})\n\n"
    
    return md_content

# Streamlit UI
st.title("PDF to JSON/Markdown Converter")
st.write("Upload PDF files and convert them to structured JSON and Markdown formats with embedded images.")

uploaded_files = st.file_uploader(
    "Choose PDF files",
    type=["pdf"],
    accept_multiple_files=True
)

if st.button("Process Files"):
    if uploaded_files:
        results = []
        for uploaded_file in uploaded_files:
            try:
                pdf_bytes = uploaded_file.read()
                extracted_data = extract_pdf_content(pdf_bytes)
                
                results.append({
                    "filename": uploaded_file.name,
                    "json": generate_json(extracted_data),
                    "markdown": generate_markdown(extracted_data)
                })
            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {str(e)}")
        
        st.session_state.results = results
        st.success("Processing completed!")
    else:
        st.warning("Please upload at least one PDF file first.")

if "results" in st.session_state:
    st.subheader("Download Converted Files")
    for result in st.session_state.results:
        base_name = os.path.splitext(result["filename"])[0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label=f"Download JSON - {base_name}",
                data=result["json"],
                file_name=f"{base_name}.json",
                mime="application/json"
            )
        with col2:
            st.download_button(
                label=f"Download Markdown - {base_name}",
                data=result["markdown"],
                file_name=f"{base_name}.md",
                mime="text/markdown"
            )