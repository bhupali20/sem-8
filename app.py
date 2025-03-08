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

def get_gemini_response(resume_text, jd_text):
    """Generate AI-based ATS analysis using Gemini API."""
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    input_prompt = f"""
    Hey, act like a highly experienced ATS (Application Tracking System) 
    with deep expertise in tech roles like Software Engineering, Data Science, 
    Data Analysis, and Big Data Engineering. Your task is to evaluate a given 
    resume based on the provided job description.

    Please ensure high accuracy in:
    - **JD Match (%)**
    - **Missing Keywords**
    - **Profile Summary Suggestions**
    
    Resume:
    ```
    {resume_text}
    ```
    Job Description:
    ```
    {jd_text}
    ```

    Provide the response **ONLY** in this JSON format:
    {{
        "JD Match": "XX%",
        "MissingKeywords": ["keyword1", "keyword2"],
        "Profile Summary": "Your improved profile summary..."
    }}
    """

    response = model.generate_content(input_prompt)

    try:
        return json.loads(response.text)  # Parse response as JSON
    except json.JSONDecodeError:
        return {"error": "Failed to parse AI response. Try again!"}  # Handle errors

def extract_text_from_pdf(uploaded_file):
    """Extract text from uploaded PDF resume."""
    reader = pdf.PdfReader(uploaded_file)
    text = "\n".join([page.extract_text() or "" for page in reader.pages])  # Handle NoneType
    return text.strip()

# Streamlit UI
st.set_page_config(page_title="Smart ATS", layout="wide")

# Custom Styling
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

# UI Title
st.markdown("<h1 class='main-title'>📄 Smart ATS Resume Analyzer</h1>", unsafe_allow_html=True)

# Two-column Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📝 Paste Job Description")
    job_description = st.text_area("Enter the Job Description", height=200)

with col2:
    st.markdown("### 📂 Upload Resume (PDF)")
    uploaded_file = st.file_uploader("Upload your resume", type="pdf", help="Only PDF files are supported.")

submit = st.button("Analyze Resume")

# Handle Submission
if submit:
    if uploaded_file and job_description:
        with st.spinner("🔍 Analyzing resume..."):
            resume_text = extract_text_from_pdf(uploaded_file)
            response = get_gemini_response(resume_text, job_description)

            if "error" in response:
                st.error(response["error"])
            else:
                st.markdown("<div class='result-card'>", unsafe_allow_html=True)

                # JD Match Percentage
                st.markdown(f"<h2 style='text-align: center;'>✅ JD Match: <span class='match-percentage'>{response['JD Match']}</span></h2>", unsafe_allow_html=True)

                # Missing Keywords Section
                st.markdown("### 🎯 Missing Keywords")
                st.markdown("<div class='keywords-section'>", unsafe_allow_html=True)
                for keyword in response.get("MissingKeywords", []):
                    st.markdown(f"<span class='keyword-pill'>{keyword}</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

                # Profile Summary
                st.markdown("### 📋 Suggested Profile Summary")
                st.markdown(f"<div style='padding: 20px; background-color: white; border-radius: 5px; border: 1px solid #dee2e6;'>{response['Profile Summary']}</div>", unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

                # Recommendations
                st.markdown("### 💡 Next Steps")
                st.info("""
                - Include missing keywords naturally in your resume
                - Quantify achievements with numbers and impact
                - Improve your profile summary for better alignment
                - Use action verbs and industry-specific language
                """)
    else:
        st.warning("⚠️ Please upload a resume and enter a job description before proceeding.")
