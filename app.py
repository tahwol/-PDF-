import fitz  # PyMuPDF
import os
import numpy as np
import streamlit as st
import easyocr
from PIL import Image
import shutil
import zipfile

# Function to split PDF based on blank pages and OCR
def split_pdf_with_ocr(pdf, output_folder):
    document = fitz.open(stream=pdf.read(), filetype="pdf")

    # Initialize EasyOCR reader
    reader = easyocr.Reader(['en'], gpu=False)

    current_document = None
    documents = []
    output_files = []

    for page_number in range(len(document)):
        page = document.load_page(page_number)

        # Check if the page is blank based on text, OCR, and luminance level
        text = page.get_text().strip()
        pix = page.get_pixmap()
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Use EasyOCR to extract text
        ocr_result = reader.readtext(np.array(image))
        ocr_text = " ".join([res[1] for res in ocr_result]).strip()

        # Combine extracted text from page and OCR
        combined_text = text + ocr_text

        # Convert page image to array to analyze luminance
        image_data = np.frombuffer(pix.samples, dtype=np.uint8)
        average_luminance = image_data.mean()

        # If the page is considered blank, skip to the next page
        if len(combined_text) == 0 and average_luminance > 245:
            # Close the current document if any
            if current_document is not None:
                documents.append(current_document)
                current_document = None
            continue

        # Start or add the page to the document
        if current_document is None:
            current_document = fitz.open()  # Create a new document
        current_document.insert_pdf(document, from_page=page_number, to_page=page_number)

    # Add the last document if any
    if current_document is not None:
        documents.append(current_document)

    # Save files to the desired folder
    for idx, doc in enumerate(documents):
        doc_name = os.path.join(output_folder, f"document_{idx + 1}.pdf")
        doc.save(doc_name)
        output_files.append(doc_name)
        doc.close()

    return output_files

# Streamlit Interface
st.title("PDF Splitter by Blank Page and OCR")
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None:
    # Create a new folder with the uploaded file's name
    base_folder = "E:\\الملفات_المقسمة"
    os.makedirs(base_folder, exist_ok=True)
    output_folder = os.path.join(base_folder, uploaded_file.name.replace(".pdf", ""))
    os.makedirs(output_folder, exist_ok=True)

    st.write("Processing...")
    output_files = split_pdf_with_ocr(uploaded_file, output_folder)

    # Create a ZIP file to compress the output folder
    zip_filename = f"{output_folder}.zip"
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for file in output_files:
            zipf.write(file, os.path.basename(file))

    # Provide download button for the ZIP file
    with open(zip_filename, "rb") as f:
        st.download_button(
            label=f"Download All as ZIP",
            data=f,
            file_name=os.path.basename(zip_filename),
            mime="application/zip"
        )

    st.success("PDF splitting and compression completed successfully!")
