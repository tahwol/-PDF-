import fitz  # PyMuPDF
import os
import streamlit as st
import pytesseract
from PIL import Image
import zipfile

# Function to split PDF based on specific separator text
def split_pdf_with_specific_text(pdf, output_folder):
    document = fitz.open(stream=pdf.read(), filetype="pdf")

    current_document = None
    documents = []
    output_files = []

    for page_number in range(len(document)):
        page = document.load_page(page_number)

        # Convert page to image for OCR
        pix = page.get_pixmap()
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Use OCR to extract text from the image
        ocr_text = pytesseract.image_to_string(image).strip()

        # Check if the specific separator text is present
        if "warakafaselasamirhetawy" in ocr_text:
            # If current document exists, add it to the list and reset
            if current_document is not None:
                documents.append(current_document)
                current_document = None
            continue

        # Start or add the page to the current document
        if current_document is None:
            current_document = fitz.open()  # Create a new document
        current_document.insert_pdf(document, from_page=page_number, to_page=page_number)

    # Add the last document if any
    if current_document is not None:
        documents.append(current_document)

    # Save individual documents to the desired folder
    for idx, doc in enumerate(documents):
        doc_name = os.path.join(output_folder, f"document_{idx + 1}.pdf")
        doc.save(doc_name)
        output_files.append(doc_name)
        doc.close()

    return output_files

# Streamlit Interface
st.title("PDF Splitter by Specific Text - by: Samir Hettawy")
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None:
    # Define the output folder path as specified
    output_folder = "E:\\الملفات_المقسمة"
    os.makedirs(output_folder, exist_ok=True)

    st.write("Processing...")
    output_files = split_pdf_with_specific_text(uploaded_file, output_folder)

    # Create a ZIP file to compress the output files without extra folders
    zip_filename = os.path.join(output_folder, uploaded_file.name.replace(".pdf", ".zip"))
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in output_files:
            zipf.write(file, os.path.basename(file))

    # Delete individual PDF files after adding them to ZIP
    for file in output_files:
        os.remove(file)

    # Provide download button for the ZIP file
    with open(zip_filename, "rb") as f:
        st.download_button(
            label="Download All as ZIP",
            data=f,
            file_name=os.path.basename(zip_filename),
            mime="application/zip"
        )

    st.success("PDF splitting and ZIP compression completed successfully!")
