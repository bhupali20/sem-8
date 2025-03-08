import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure Gemini AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to extract text from PDF
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        extracted_text = page.extract_text() or ""  # Handle None case
        text += extracted_text
    return text.strip()

# Function to get AI response
def get_gemini_response(input_text, jd):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Hey, act like a highly experienced ATS (Applicant Tracking System) specializing in software engineering,
    data science, data analytics, and big data roles. Evaluate the resume against the provided job description.
    Consider that the job market is competitive and provide insights for improvement.

    Resume: {input_text}
    Job Description: {jd}

    Respond in JSON format:
    {{"JD Match": "percentage", "MissingKeywords": ["keyword1", "keyword2"], "Profile Summary": "summary"}}
    """
    
    response = model.generate_content(prompt)
    
    try:
        return json.loads(response.text)  # Convert AI response to JSON
    except:
        return {"error": "Failed to process the response. Please try again."}

# Page settings
st.set_page_config(page_title="Smart ATS", layout="wide")

# Custom CSS
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

# App title
st.markdown("<h1 class='main-title'>Smart ATS Resume Analyzer</h1>", unsafe_allow_html=True)

# Input fields
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Job Description")
    jd = st.text_area("Paste the Job Description", height=200)

with col2:
    st.markdown("### Upload Resume")
    uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type="pdf", help="Please upload a PDF")

# Submit button
if st.button("Analyze Resume"):
    if uploaded_file is not None and jd.strip():
        with st.spinner("Analyzing your resume..."):
            text = input_pdf_text(uploaded_file)
            response = get_gemini_response(text, jd)

            if "error" in response:
                st.error(response["error"])
            else:
                # Display results
                st.markdown("<div class='result-card'>", unsafe_allow_html=True)

                # JD Match percentage
                st.markdown(f"<h2 style='text-align: center;'>JD Match: <span class='match-percentage'>{response['JD Match']}</span></h2>", unsafe_allow_html=True)

                # Missing Keywords
                st.markdown("### 🎯 Missing Keywords")
                st.markdown("<div class='keywords-section'>", unsafe_allow_html=True)
                for keyword in response.get("MissingKeywords", []):
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
        st.warning("Please upload a resume and enter a job description before analyzing.")
