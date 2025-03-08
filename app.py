import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json

# Load environment variables from the .env file
load_dotenv()  # This loads the Google API key from the .env file

# Configure Google Generative AI API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get response from the Generative AI model
def get_gemini_response(input_text, jd):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')  # You can try other models available based on your API version
        response = model.generate_content(input_text=input_text, prompt=jd)
        return json.loads(response.text)  # Parse the response into a JSON object
    except Exception as e:
        return f"Error in generating response: {e}"

# Function to extract text from a PDF file
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += str(page.extract_text())  # Extract text from each page
    return text

# Prompt template to analyze resume and job description
input_prompt = """
Hey Act Like a skilled or very experienced ATS (Application Tracking System)
with a deep understanding of tech fields, software engineering, data science, data analysis,
and big data engineering. Your task is to evaluate the resume based on the given job description.
You must consider that the job market is very competitive, and you should provide 
the best assistance for improving the resumes. Assign the percentage Matching based 
on JD and the missing keywords with high accuracy.

Resume: {text}
Job Description: {jd}

Provide the response in the following JSON format:
{{"JD Match": "percentage", "MissingKeywords": ["keyword1", "keyword2"], "Profile Summary": "summary"}}
"""

# Streamlit App Configuration
st.set_page_config(page_title="Smart ATS Resume Analyzer", layout="wide")

# Custom CSS for Streamlit UI
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #2c3e50;
        padding: 20px;
    }
    .result-card {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
    }
    .match-percentage {
        font-size: 24px;
        font-weight: bold;
        color: #28a745;
    }
    .keywords-section {
        margin: 20px 0;
    }
    .keyword-pill {
        display: inline-block;
        padding: 5px 10px;
        margin: 5px;
        background-color: #e9ecef;
        border-radius: 15px;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

# Page title
st.markdown("<h1 class='main-title'>Smart ATS Resume Analyzer</h1>", unsafe_allow_html=True)

# Create two columns for input
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Job Description")
    jd = st.text_area("Paste the Job Description", height=200)

with col2:
    st.markdown("### Upload Resume")
    uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type="pdf", help="Please upload a PDF")

submit = st.button("Analyze Resume")

# When the user clicks the submit button
if submit:
    if uploaded_file is not None and jd:
        with st.spinner("Analyzing your resume..."):
            # Extract text from the uploaded resume
            text = input_pdf_text(uploaded_file)
            
            # Get the response from the Generative AI model
            response = get_gemini_response(text, jd)
            
            if isinstance(response, dict):
                # Display results in the result card
                st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                
                # Match percentage
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.markdown(f"<h2 style='text-align: center;'>JD Match: <span class='match-percentage'>{response['JD Match']}</span></h2>", unsafe_allow_html=True)
                
                # Missing Keywords
                st.markdown("### 🎯 Missing Keywords")
                st.markdown("<div class='keywords-section'>", unsafe_allow_html=True)
                for keyword in response['MissingKeywords']:
                    st.markdown(f"<span class='keyword-pill'>{keyword}</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Profile Summary
                st.markdown("### 📋 Profile Summary")
                st.markdown(f"<div style='padding: 20px; background-color: white; border-radius: 5px; border: 1px solid #dee2e6;'>{response['Profile Summary']}</div>", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Recommendations
                st.markdown("### 💡 Next Steps")
                st.info("""
                1. Add the missing keywords to your resume where applicable.
                2. Quantify your achievements with metrics.
                3. Tailor your resume summary to better match the job description.
                4. Use action verbs and industry-specific terminology.
                """)
                
            else:
                st.error("Failed to analyze the resume. Please try again.")
    else:
        st.warning("Please upload both a resume and a job description before analyzing.")
