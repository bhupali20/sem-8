import json
import time
import streamlit as st
from google.generativeai import generate_content

# Function to fetch gemini response
def get_gemini_response(input_text, prompt):
    formatted_prompt = prompt.format(text=input_text, jd=jd)
    
    print(f"Formatted prompt: {formatted_prompt}")  # Debugging: log formatted prompt

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")  # Use a supported model
        response = model.generate_content(formatted_prompt)
        
        print(f"API Response: {response.text}")  # Log the raw response
        
        # Try parsing the response as JSON
        try:
            return json.loads(response.text)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {str(e)}")
            return response.text  # Return raw response if parsing fails
    except Exception as e:
        print(f"Error fetching API response: {str(e)}")
        st.error(f"Failed to analyze the resume. Please try again. Error: {str(e)}")
        return None

# Wrapper function with retry logic
def get_gemini_response_with_retry(input_text, prompt, retries=3):
    attempt = 0
    while attempt < retries:
        try:
            return get_gemini_response(input_text, prompt)
        except Exception as e:
            attempt += 1
            print(f"Attempt {attempt} failed: {e}")
            if attempt == retries:
                st.error("Failed to analyze after multiple attempts.")
            time.sleep(2)  # Wait for a couple of seconds before retrying
            return None

# Function to display the parsed response
def display_response(response):
    if isinstance(response, dict):
        # Proceed with the usual flow if response is valid JSON
        if 'JD Match' in response:
            st.subheader(f"JD Match: {response['JD Match']}")
            st.write(f"Missing Keywords: {', '.join(response['MissingKeywords'])}")
            st.write(f"Profile Summary: {response['Profile Summary']}")
        else:
            st.error(f"API response is not structured as expected: {response}")
    else:
        # If the response is not in JSON format, show the raw response
        st.error(f"Failed to parse the response. Raw response: {response}")

# Main function to analyze the resume
def analyze_resume(input_text, jd):
    prompt = """
    You are an AI assistant designed to analyze resumes and match them to job descriptions.
    Based on the following job description (jd) and resume text (text), provide a JD match score, a list of missing keywords, and a profile summary:
    
    Job Description: {jd}
    Resume: {text}
    """
    
    response = get_gemini_response_with_retry(input_text, prompt)
    
    if response:
        display_response(response)

# Example of using the analyze_resume function
if __name__ == "__main__":
    input_text = st.text_area("Enter Resume Text")
    jd = st.text_area("Enter Job Description")
    
    if st.button("Analyze"):
        analyze_resume(input_text, jd)
