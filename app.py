import fitz  # PyMuPDF
import os
import streamlit as st
from concurrent.futures import ThreadPoolExecutor

# Function to split PDF based on specific text and remove the separating pages
def split_pdf_based_on_text_and_remove_separator(pdf, output_folder, split_text):
    document = fitz.open(stream=pdf.read(), filetype="pdf")
    current_document = None
    documents = []
    output_files = []

    def process_page(page_number):
        nonlocal current_document
        page = document.load_page(page_number)

        # Extract text directly from the PDF
        text = page.get_text().strip()

        # Check if the split text is in the extracted text
        if split_text in text:
            # Save the current document if it exists
            if current_document is not None:
                documents.append(current_document)
                current_document = None
            # Skip adding this page (do not include it in any document)
            return

        # Start a new document or add the page to the current document
        if current_document is None:
            current_document = fitz.open()  # Create a new document
        current_document.insert_pdf(document, from_page=page_number, to_page=page_number)

    # Process all pages in parallel
    with ThreadPoolExecutor() as executor:
        executor.map(process_page, range(len(document)))

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
st.markdown("""
<div style="text-align: center; line-height: 2; font-size: 20px; direction: rtl;">
    <strong>تطبيق تقسيم ملفات PDF</strong><br>
    بناءً على ورقة تحتوي على نص فاصل: <span style="color: navy;">warakafaselasamirhetawy</span><br>
    <span style="color: maroon;">تصميم: المستشار سمير عبد العظيم حيطاوي</span>
</div>
""", unsafe_allow_html=True)

uploaded_files = st.file_uploader("Upload one or more PDF files", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    # Define the text to split the PDF by
    split_text = "warakafaselasamirhetawy"  # النص الفاصل الثابت

    # Base folder for all outputs
    base_folder = "E:\\الملفات_المقسمة"
    os.makedirs(base_folder, exist_ok=True)

    for uploaded_file in uploaded_files:
        # Create a specific folder for each uploaded file
        output_folder = os.path.join(base_folder, uploaded_file.name.replace(".pdf", ""))
        os.makedirs(output_folder, exist_ok=True)

        st.write(f"جاري معالجة الملف: {uploaded_file.name}...")
        output_files = split_pdf_based_on_text_and_remove_separator(uploaded_file, output_folder, split_text)

        # Provide download buttons for individual PDF files
        for idx, file in enumerate(output_files):
            unique_key = f"{uploaded_file.name}_{os.path.basename(file)}_{idx}"  # Unique key for each button
            with open(file, "rb") as f:
                st.download_button(
                    label=f"تحميل {os.path.basename(file)}",
                    data=f,
                    file_name=os.path.basename(file),
                    mime="application/pdf",
                    key=unique_key  # Use unique key for each button
                )

    st.success("تم معالجة جميع الملفات بنجاح!")
