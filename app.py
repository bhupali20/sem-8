# import streamlit as st
# import google.generativeai as genai
# import os
# import PyPDF2 as pdf
# from dotenv import load_dotenv
# import json

# load_dotenv() ## load all our environment variables

# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# def get_gemini_repsonse(input):
#     model=genai.GenerativeModel('gemini-1.5-flash')
#     response=model.generate_content(input)
#     return response.text

# def input_pdf_text(uploaded_file):
#     reader=pdf.PdfReader(uploaded_file)
#     text=""
#     for page in range(len(reader.pages)):
#         page=reader.pages[page]
#         text+=str(page.extract_text())
#     return text

# #Prompt Template

# input_prompt="""
# Hey Act Like a skilled or very experience ATS(Application Tracking System)
# with a deep understanding of tech field,software engineering,data science ,data analyst
# and big data engineer. Your task is to evaluate the resume based on the given job description.
# You must consider the job market is very competitive and you should provide 
# best assistance for improving thr resumes. Assign the percentage Matching based 
# on Jd and
# the missing keywords with high accuracy
# resume:{text}
# description:{jd}

# I want the response in one single string having the structure
# {{"JD Match":"%","MissingKeywords:[]","Profile Summary":""}}
# """

# ## streamlit app
# st.title("Smart ATS")
# st.text("Improve Your Resume ATS")
# jd=st.text_area("Paste the Job Description")
# uploaded_file=st.file_uploader("Upload Your Resume",type="pdf",help="Please uplaod the pdf")

# submit = st.button("Submit")

# if submit:
#     if uploaded_file is not None:
#         text=input_pdf_text(uploaded_file)
#         response=get_gemini_repsonse(input_prompt)
#         st.subheader(response)

import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json

load_dotenv()  # load all our environment variables

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input_text, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt.format(text=input_text, jd=jd))
    try:
        return json.loads(response.text)
    except:
        return response.text

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += str(page.extract_text())
    return text

# Prompt Template
input_prompt = """
Hey Act Like a skilled or very experience ATS(Application Tracking System)
with a deep understanding of tech field, software engineering, data science, data analyst
and big data engineer. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide 
best assistance for improving the resumes. Assign the percentage Matching based 
on JD and the missing keywords with high accuracy.

Resume: {text}
Job Description: {jd}

Provide the response in the following JSON format:
{{"JD Match": "percentage", "MissingKeywords": ["keyword1", "keyword2"], "Profile Summary": "summary"}}
"""

# Page configuration
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

# Create two columns
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Job Description")
    jd = st.text_area("Paste the Job Description", height=200)

with col2:
    st.markdown("### Upload Resume")
    uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type="pdf", help="Please upload the pdf")

submit = st.button("Analyze Resume")

if submit:
    if uploaded_file is not None and jd:
        with st.spinner("Analyzing your resume..."):
            text = input_pdf_text(uploaded_file)
            response = get_gemini_response(text, input_prompt)
            
            if isinstance(response, dict):
                # Results section
                st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                
                # Match percentage
                col1, col2, col3 = st.columns([1,2,1])
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
                1. Add the missing keywords to your resume where applicable
                2. Quantify your achievements with metrics
                3. Tailor your resume summary to better match the job description
                4. Use action verbs and industry-specific terminology
                """)
                
            else:
                st.error("Failed to analyze the resume. Please try again.")
    else:
        st.warning("Please upload both a resume and job description before analyzing.")
