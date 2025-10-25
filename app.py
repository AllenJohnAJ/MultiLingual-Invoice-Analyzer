from dotenv import load_dotenv

load_dotenv() 

import streamlit as st
import os
import pathlib
import textwrap
from PIL import Image
import google.generativeai as genai

# Configure Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("models/gemini-2.5-flash")

# Function to setup image for Gemini
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Function to get Gemini response
def get_gemini_response(input_text, image, prompt):
    if image:
        response = model.generate_content([input_text, image[0], prompt])
    else:
        response = model.generate_content([input_text, prompt])
    return response.text

# Page configuration
st.set_page_config(
    page_title="Invoice Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #4a5568;
        text-align: center;
        margin-bottom: 2rem;
    }
    .response-section {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-top: 1rem;
    }
    .language-badge {
        background-color: #48bb78;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">📄 Invoice Analyzer Pro</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-Powered Invoice Analysis & Language Detection</p>', unsafe_allow_html=True)

# Sidebar for additional information
with st.sidebar:
    st.markdown("### 🔧 Features")
    st.markdown("""
    - **Smart Invoice Analysis**: Extract key information from invoices
    - **Language Detection**: Automatically detect invoice language
    - **Multi-format Support**: JPG, JPEG, PNG files
    - **AI-Powered**: Powered by Google Gemini 2.5 flash model
    """)
    
    st.markdown("### 📋 Supported Languages")
    st.markdown("""
    - English
    - Spanish
    - French
    - German
    - Italian
    - Portuguese
    - And many more...
    """)

# Main content area - arranged vertically
st.markdown("### 📤 Upload Invoice")
uploaded_file = st.file_uploader(
    "Choose an invoice image...", 
    type=["jpg", "jpeg", "png"],
    help="Upload a clear image of your invoice for analysis"
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="📄 Uploaded Invoice", use_container_width=True)

st.markdown("### ❓ Ask Questions")
input_text = st.text_area(
    "What would you like to know about this invoice?", 
    key="input",
    height=100,
    placeholder="e.g., What is the total amount? Who is the vendor? What is the invoice date?"
)

submit = st.button("🔍 Analyze Invoice", type="primary", use_container_width=True)

# Language detection prompt
language_prompt = """
You are a language detection expert. Analyze the uploaded invoice image and determine the primary language used in the document. 
Respond with only the language name in English (e.g., "English", "Spanish", "French", "German", etc.).
If multiple languages are present, identify the dominant language.
"""

# Main analysis prompt
input_prompt = """
You are an expert invoice analyst with extensive knowledge of financial documents and international business practices.
You will receive input images as invoices and you will have to answer questions based on the input image.

Please provide:
1. Clear and accurate answers to the user's questions
2. Professional and detailed analysis
3. Relevant financial information extraction
4. Contextual insights about the invoice

Be thorough but concise in your responses.
"""

# Process the analysis
if submit:
    if not api_key:
        st.error("⚠️ Please set up your Google API key first to use this feature")
    elif not input_text.strip():
        st.error("⚠️ Please enter a question about the invoice")
    elif uploaded_file is None:
        st.error("⚠️ Please upload an invoice image first")
    else:
        try:
            with st.spinner("🔍 Analyzing invoice..."):
                # Setup image data
                image_data = input_image_setup(uploaded_file)
                
                # Detect language first
                language_response = get_gemini_response("", image_data, language_prompt)
                
                # Get main analysis
                analysis_response = get_gemini_response(input_text, image_data, input_prompt)
                
                # Display language detection
                st.markdown(f'<div class="language-badge">🌍 Detected Language: {language_response.strip()}</div>', unsafe_allow_html=True)
                
                # Display analysis results
                st.markdown('<div class="response-section">', unsafe_allow_html=True)
                st.markdown("### 📊 Analysis Results")
                st.write(analysis_response)
                st.markdown('</div>', unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.info("💡 Please ensure your image is clear and try again.")