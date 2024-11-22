import fitz  # PyMuPDF
import os
import streamlit as st
import shutil

# Function to detect if a page contains text
def page_contains_text(page):
    text = page.get_text("text").strip()  # Check if there is any text
    return bool(text)  # Returns True if text exists, False otherwise

# Function to split PDF based on text presence or absence
def split_pdf_based_on_text_and_remove_separator(pdf, output_folder, split_text):
    document = fitz.open(stream=pdf.read(), filetype="pdf")
    current_document = None
    documents = []
    output_files = []

    for page_number in range(len(document)):
        page = document.load_page(page_number)

        # Check if the page contains the split text
        text = page.get_text("text").strip()
        if split_text in text:
            # Save the current document if it exists
            if current_document is not None:
                documents.append(current_document)
                current_document = None
            # Skip the separator page
            continue

        # Start a new document or add the page to the current document
        if current_document is None:
            current_document = fitz.open()  # Create a new document
        current_document.insert_pdf(document, from_page=page_number, to_page=page_number)

    # Add the last document if any
    if current_document is not None:
        documents.append(current_document)

    # Save the split documents to the output folder
    for idx, doc in enumerate(documents):
        doc_name = os.path.join(output_folder, f"document_{idx + 1}.pdf")
        doc.save(doc_name)
        output_files.append(doc_name)
        doc.close()

    return output_files

# Streamlit Interface

# Arabic Title with custom styles
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
    split_text = st.text_input("Enter the separator text:", value="warakafaselasamirhetawy")  # النص الفاصل الثابت

    if st.button("Start Processing"):
        # Base folder for all outputs
        base_folder = "output"
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

        # Zip all the processed files for batch download
        zip_path = os.path.join(base_folder, "processed_files.zip")
        shutil.make_archive(base_folder, 'zip', base_folder)

        with open(zip_path, "rb") as zf:
            st.download_button(
                label="Download All Processed Files as ZIP",
                data=zf,
                file_name="processed_files.zip",
                mime="application/zip"
            )

        st.success("تم معالجة جميع الملفات بنجاح!")
