import streamlit as st
import fitz  # PyMuPDF for PDF parsing
from google import genai

st.set_page_config(page_title="📄 Resume & Job Matcher", layout="centered")
st.title("📄 Resume & Job Matcher")

st.sidebar.info("""
This app uses **Google GenAI SDK** with **Gemini 2.5 Flash** model.
1. Get your API key from: https://aistudio.google.com/app/apikey
2. Enter your API key in the sidebar field below.
3. Upload a Resume + Job Description to get a fit score and suggestions.
""")

# API Key input in sidebar
api_key = st.sidebar.text_input("🔑 Enter your Google API Key:", type="password", key="api_key_input")

if not api_key:
    st.warning("⚠️ Please enter your Google API Key in the sidebar to proceed.")
    st.stop()

# Initialize client with API key
client = genai.Client(api_key=api_key)

# Helper: Extract text from PDF
def extract_pdf_text(file):
    text = ""
    try:
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        st.error(f"Error extracting PDF: {str(e)}")
        return None
    return text

# File uploaders
st.subheader("📤 Upload Documents")
col1, col2 = st.columns(2)

with col1:
    resume_file = st.file_uploader("Upload Resume (PDF/TXT)", type=["pdf", "txt"], key="resume_upload")

with col2:
    job_file = st.file_uploader("Upload Job Description (PDF/TXT)", type=["pdf", "txt"], key="job_upload")

if st.button("🔍 Match Resume with Job Description", use_container_width=True):
    if resume_file and job_file:
        # Extract Resume text
        if resume_file.type == "application/pdf":
            resume_text = extract_pdf_text(resume_file)
        else:
            resume_text = resume_file.read().decode("utf-8")
        
        if resume_text is None:
            st.stop()
        
        # Extract Job text
        if job_file.type == "application/pdf":
            job_text = extract_pdf_text(job_file)
        else:
            job_text = job_file.read().decode("utf-8")
        
        if job_text is None:
            st.stop()
        
        # Prompt
        prompt = f"""
You are an expert AI career advisor and resume analyst.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_text}

Please provide a comprehensive analysis with the following:

1. **Fit Score** (0-100%): Rate how well this resume matches the job description with a clear percentage.
2. **Key Strengths**: List 3-5 resume areas that align well with the job requirements.
3. **Gaps & Weaknesses**: Identify 2-3 areas where the resume falls short of the job requirements.
4. **Specific Recommendations**: Provide 3-5 actionable recommendations to improve the resume for this specific role.

Format your response clearly in Markdown with sections and bullet points for easy reading.
        """
        
        try:
            with st.spinner("⏳ Analyzing Resume vs Job Description with Gemini 2.5 Flash..."):
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                output = response.text
            
            # Show Results
            st.subheader("📌 Match Analysis Results")
            st.markdown(output)
            
            # Save in session for download
            st.session_state["resume_match"] = output
            
        except Exception as e:
            st.error(f"❌ Error occurred: {str(e)}")
            st.info("Please ensure your API key is valid and you have internet connection.")
    else:
        st.warning("⚠️ Please upload both Resume and Job Description files.")

# Download button
if "resume_match" in st.session_state:
    st.divider()
    st.download_button(
        label="💾 Download Match Report (Markdown)",
        data=st.session_state["resume_match"],
        file_name="resume_match_report.md",
        mime="text/markdown",
        use_container_width=True
    )
    
