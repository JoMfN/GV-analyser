import json
import os
import zipfile
from io import BytesIO
from PIL import Image
import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

# Handle API key storage
KEY_FOLDER = "."

def get_latest_api_key():
    keys = [f for f in os.listdir(KEY_FOLDER) if f.startswith(".env_")]
    if keys:
        latest_key_file = sorted(keys)[-1]
        with open(os.path.join(KEY_FOLDER, latest_key_file)) as f:
            return f.read().strip()
    return GOOGLE_API_KEY  # fallback to hardcoded key

# Function to reconfigure the Gemini model with new key
def update_api_key(new_key):
    key_files = [f for f in os.listdir(KEY_FOLDER) if f.startswith(".env_")]
    key_id = len(key_files) + 1
    key_path = os.path.join(KEY_FOLDER, f".env_{key_id}")
    with open(key_path, "w") as f:
        f.write(new_key.strip())
    genai.configure(api_key=new_key)
    return new_key

# Update the model with latest key at launch
GOOGLE_API_KEY = get_latest_api_key()
genai.configure(api_key=GOOGLE_API_KEY)

# Load models
text_model = genai.GenerativeModel("gemini-2.0-flash-exp")
vision_model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")
# Default OCR prompt
# default_prompt = """Transcribe all printed and handwritten text on this label of a specimen from a collection of a museum for natural history, being especially careful to preserve any scientific names, dates, and location information. Maintain the original formatting and line breaks with exception of the NURI (an URL starting with http://coll.mfn-berlin.de/u/{HEXhash} ) the label with QR-code should have the full URL displayed in the output."""

default_prompt = """You are given an image containing multiple specimen labels from a natural history museum collection.

Transcribe all printed and handwritten text on this label of a specimen from a collection of a museum for natural history, being especially careful to preserve any scientific names, dates, and location information. Maintain the original formatting and line breaks with exception of the NURI (an URL starting with http://coll.mfn-berlin.de/u/{HEXhash}) — the label with QR-code should have the full URL displayed in the output.

Please extract the text from each distinct label individually, and return the output as a list of labeled code blocks.

Use this format:

```label 1
<text from the first label> 
```

```label 2
<text from the second label>
```

and so on... 

aim to segment all the labels correctly
"""

# Function to get Gemini response for text queries
def get_text_response(question):
    response = text_model.generate_content(question)
    return response.text

# Function to get Gemini response for images
def get_vision_response(input_text, image):
    if input_text.strip():
        response = vision_model.generate_content([input_text, image])
    else:
        response = vision_model.generate_content(image)
    return response.text

# Initialize Streamlit app
st.set_page_config(page_title="Gemini AI Analyzer")
st.title("🔍 Gemini AI Vision & Q&A")

# Tabs for Q&A and Image Analysis
tab1, tab2 = st.tabs(["📖 Text Q&A", "🖼️ Image Analysis"])
# Tabs for Q&A, Image Analysis, and Embedded App
# tab1, tab2, tab3 = st.tabs(["📖 Text Q&A", "🖼️ Image Analysis", "🌐 Ollama"])


# Text-Based Q&A
with tab1:
    st.header("💬 Ask Gemini Anything!")
    question = st.text_input("Enter your question:", key="text_input")
    if st.button("Ask Gemini"):
        if question.strip():
            response = get_text_response(question)
            st.subheader("Response:")
            st.write(response)
        else:
            st.warning("Please enter a valid question!")

# Image Analysis


with tab2:
    st.header("🖼️ Upload Images for OCR & Analysis")
    input_prompt = st.text_area("Optional Prompt (editable):", value=default_prompt, height=150)

    # Secure input for new API key
    new_key_input = st.text_input("🔐 (Optional) Enter new API Key (hidden)", type="password")
    if st.button("Update API Key"):
        if new_key_input:
            update_api_key(new_key_input)
            st.success("API Key updated and saved for this session.")
        else:
            st.warning("Please enter a valid key.")

    uploaded_files = st.file_uploader("Choose one or more images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    if uploaded_files:
        if st.button("Analyze All Images"):
            zip_buffer = BytesIO()
            errors = []

            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zipf:
                for uploaded_file in uploaded_files:
                    try:
                        image = Image.open(uploaded_file)
                        st.image(image, caption=f"Uploaded: {uploaded_file.name}", use_container_width=True)

                        response_text = get_vision_response(input_prompt, image)

                        st.subheader(f"Text Extracted from {uploaded_file.name}:")
                        st.write(response_text)

                        json_data = {
                            "filename": uploaded_file.name,
                            "extracted_text": response_text
                        }
                        json_filename = uploaded_file.name.replace(".", "__Text.") + ".json"
                        zipf.writestr(json_filename, json.dumps(json_data, indent=2).encode("utf-8"))

                    except ResourceExhausted as e:
                        st.error(f"❌ API limit hit while processing {uploaded_file.name}. Skipped.")
                        errors.append(uploaded_file.name)

                    except Exception as e:
                        st.error(f"⚠️ Unexpected error with {uploaded_file.name}: {str(e)}")
                        errors.append(uploaded_file.name)

            zip_buffer.seek(0)

            if zip_buffer.getbuffer().nbytes > 0:
                st.download_button(
                    label="📦 Download All Extracted JSONs as ZIP",
                    data=zip_buffer,
                    file_name="ocr_results.zip",
                    mime="application/zip"
                )
            else:
                st.warning("No files were processed due to errors or quota limits.")

            if errors:
                st.info("The following files had issues and were not included in the ZIP:")
                st.write(errors)
				

# Embedded iframe App
# with tab3:
#     st.header("🌐 Embedded Textgenerateion App")
#     components.html(
#         """
#         <iframe
#             src="http://localhost:7860"
#             frameborder="0"
#             width="850"
#             height="850"
#         ></iframe>
#         """,
#         height=850,
#     )
