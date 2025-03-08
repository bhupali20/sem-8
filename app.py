import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to extract text from a PDF
def input_pdf_text(uploaded_file):
    try:
        reader = pdf.PdfReader(uploaded_file)
        text = " ".join([page.extract_text() or "" for page in reader.pages])
        return text.strip()
    except Exception as e:
        return None

# Function to get Gemini AI response
def get_gemini_response(input_text, jd):
    model = genai.GenerativeModel('gemini-1.5-flash')
    input_prompt = f"""
    Act like an advanced ATS (Application Tracking System) specializing in tech roles:
    software engineering, data science, data analytics, and big data engineering.

    Evaluate the resume based on the given job description.
    - Provide a percentage match score.
    - Identify missing keywords from the job description.
    - Generate a concise profile summary.

    Resume: {input_text}
    Job Description: {jd}

    Respond in JSON format:
    {{
        "JD Match": "percentage",
        "MissingKeywords": ["keyword1", "keyword2"],
        "Profile Summary": "summary"
    }}
    """
    response = model.generate_content(input_prompt)
    
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return None  # Return None if response is not valid JSON

# Streamlit App Configuration
st.set_page_config(page_title="Smart ATS", layout="wide")

# CSS for better UI
st.markdown("""
    <style>
    .main-title { text-align: center; color: #2c3e50; padding: 20px; }
    .result-card { padding: 20px; border-radius: 10px; margin: 10px 0; background-color: #f8f9fa; border: 1px solid #dee2e6; }
    .match-percentage { font-size: 24px; font-weight: bold; color: #28a745; }
    .keywords-section { margin: 20px 0; }
    .keyword-pill { display: inline-block; padding: 5px 10px; margin: 5px; background-color: #e9ecef; border-radius: 15px; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

# App Title
st.markdown("<h1 class='main-title'>Smart ATS Resume Analyzer</h1>", unsafe_allow_html=True)

# Input Sections
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Job Description")
    jd = st.text_area("Paste the Job Description", height=200)

with col2:
    st.markdown("### Upload Resume")
    uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"], help="Only PDF files are supported.")

submit = st.button("Analyze Resume")

# Resume Analysis Logic
if submit:
    if not uploaded_file:
        st.warning("⚠️ Please upload a resume before analyzing.")
    elif not jd.strip():
        st.warning("⚠️ Please enter a job description before analyzing.")
    else:
        with st.spinner("🔍 Analyzing your resume..."):
            resume_text = input_pdf_text(uploaded_file)
            if resume_text:
                response = get_gemini_response(resume_text, jd)
                
                if response and isinstance(response, dict):
                    st.markdown("<div class='result-card'>", unsafe_allow_html=True)

                    # Display JD Match Percentage
                    col1, col2, col3 = st.columns([1,2,1])
                    with col2:
                        st.markdown(f"<h2 style='text-align: center;'>JD Match: <span class='match-percentage'>{response['JD Match']}</span></h2>", unsafe_allow_html=True)

                    # Missing Keywords
                    if response['MissingKeywords']:
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
                    st.error("⚠️ Failed to analyze the resume. Please try again.")
            else:
                st.error("⚠️ Error reading the PDF. Ensure it's a valid document.")
