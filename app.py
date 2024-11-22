import fitz  # PyMuPDF
import os
import streamlit as st
import shutil

# Function to split PDF based on user-provided text and remove separator pages
def split_pdf_based_on_text_and_remove_separator(pdf, output_folder, split_text):
    document = fitz.open(stream=pdf.read(), filetype="pdf")
    current_document = None
    documents = []
    output_files = []

    for page_number in range(len(document)):
        page = document.load_page(page_number)

        # Extract text from the page
        text = page.get_text("text").strip()

        # Check if the split text is in the extracted text
        if split_text in text:
            # Save the current document if it exists
            if current_document is not None:
                documents.append(current_document)
                current_document = None
            # Skip adding this page (do not include it in any document)
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

# File uploader for multiple PDF files
uploaded_files = st.file_uploader("Upload one or more PDF files", type=["pdf"], accept_multiple_files=True)

# User input for the separator text
split_text = st.text_input("Enter the separator text:", value="warakafaselasamirhetawy")

if uploaded_files and split_text:
    # Use a safe folder path
    output_folder = "./temp_output"
    os.makedirs(output_folder, exist_ok=True)

    try:
        for uploaded_file in uploaded_files:
            # Save the uploaded file
            file_path = os.path.join(output_folder, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.write(f"جاري معالجة الملف: {uploaded_file.name}...")
            output_files = split_pdf_based_on_text_and_remove_separator(uploaded_file, output_folder, split_text)

            if output_files:
                # Provide download buttons for individual PDF files
                for idx, file in enumerate(output_files):
                    unique_key = f"{uploaded_file.name}_{idx}"
                    with open(file, "rb") as f:
                        st.download_button(
                            label=f"تحميل {os.path.basename(file)}",
                            data=f,
                            file_name=os.path.basename(file),
                            mime="application/pdf",
                            key=unique_key
                        )
            else:
                st.warning(f"No output files generated for {uploaded_file.name}. Please check the separator text.")

        # Zip all the processed files for batch download
        zip_path = os.path.join(output_folder, "processed_files.zip")
        shutil.make_archive(zip_path.replace(".zip", ""), 'zip', output_folder)

        with open(zip_path, "rb") as zf:
            st.download_button(
                label="Download All Processed Files as ZIP",
                data=zf,
                file_name="processed_files.zip",
                mime="application/zip"
            )

        st.success("تم معالجة جميع الملفات بنجاح!")
    except Exception as e:
        st.error(f"An error occurred: {e}")
