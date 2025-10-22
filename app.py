import streamlit as st
import fitz  # PyMuPDF for PDF parsing
from google import genai

st.set_page_config(page_title="📄 Resume & Job Matcher", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .hero-section h1 {
        font-size: 2.5rem;
        margin: 0;
        font-weight: 700;
    }
    .hero-section p {
        font-size: 1.1rem;
        margin-top: 0.5rem;
        opacity: 0.95;
    }
    .card-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        border-left: 4px solid #667eea;
    }
    .tab-section {
        padding: 1.5rem;
        background: white;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
    .results-container {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="hero-section">
    <h1>📄 Resume & Job Matcher Pro</h1>
    <p>Powered by Google Gemini 2.5 Flash | AI-Driven Career Intelligence</p>
</div>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    api_key = st.text_input("🔑 Enter your Google API Key:", type="password", key="api_key_input")
    
    st.divider()
    
    st.markdown("""
    ### 🚀 How to Use:
    1. Get API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
    2. Upload or paste your job description
    3. Upload your resume
    4. Click "Analyze" to get insights
    
    ### ✨ Features:
    - Resume matching analysis
    - CV generation
    - Interview preparation guide
    - Download reports
    """)

if not api_key:
    st.warning("⚠️ Please enter your Google API Key in the sidebar to proceed.")
    st.stop()

# Initialize client
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"❌ Invalid API Key: {str(e)}")
    st.stop()

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

# Helper: Generate content with Gemini
def generate_content(prompt):
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None

# Section 1: Document Input
st.markdown("""
<div class="card-section">
    <h2>📤 Step 1: Provide Your Documents</h2>
    <p>Upload or paste your resume and job description below.</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Resume Upload")
    resume_file = st.file_uploader("Upload Resume (PDF/TXT)", type=["pdf", "txt"], key="resume_upload")
    
    if resume_file:
        if resume_file.type == "application/pdf":
            resume_text = extract_pdf_text(resume_file)
        else:
            resume_text = resume_file.read().decode("utf-8")
        st.success(f"✅ Resume loaded ({len(resume_text)} characters)")
    else:
        resume_text = None

with col2:
    st.subheader("💼 Job Description")
    job_input_method = st.radio("Choose input method:", ["Upload File", "Paste Text"], horizontal=True, key="job_method")
    
    if job_input_method == "Upload File":
        job_file = st.file_uploader("Upload Job Description (PDF/TXT)", type=["pdf", "txt"], key="job_upload")
        if job_file:
            if job_file.type == "application/pdf":
                job_text = extract_pdf_text(job_file)
            else:
                job_text = job_file.read().decode("utf-8")
            st.success(f"✅ Job description loaded ({len(job_text)} characters)")
        else:
            job_text = None
    else:
        job_text = st.text_area("Paste job description here:", height=200, placeholder="Paste the job description text...", key="job_paste")
        if job_text:
            st.success(f"✅ Job description loaded ({len(job_text)} characters)")

# Section 2: Analysis & Results
st.markdown("""
<div class="card-section">
    <h2>🔍 Step 2: Analyze & Generate</h2>
    <p>Click the button below to get personalized insights based on your resume and job description.</p>
</div>
""", unsafe_allow_html=True)

if st.button("🚀 Analyze Resume & Generate Insights", use_container_width=True, key="analyze_btn"):
    if not resume_text or not job_text:
        st.warning("⚠️ Please provide both resume and job description.")
    else:
        # Initialize session state for results
        if "analysis_result" not in st.session_state:
            st.session_state.analysis_result = None
        if "cv_result" not in st.session_state:
            st.session_state.cv_result = None
        if "interview_result" not in st.session_state:
            st.session_state.interview_result = None
        
        # Tab 1: Resume Matching Analysis
        with st.spinner("⏳ Generating Resume Matching Analysis..."):
            matching_prompt = f"""
You are an expert AI career advisor and resume analyst.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_text}

Please provide a comprehensive resume matching analysis with the following:

1. **Fit Score** (0-100%): Rate how well this resume matches the job description with a clear percentage.
2. **Key Strengths**: List 3-5 resume areas that align well with the job requirements.
3. **Gaps & Weaknesses**: Identify 2-3 areas where the resume falls short of the job requirements.
4. **Specific Recommendations**: Provide 3-5 actionable recommendations to improve the resume for this specific role.
5. **Keywords to Include**: List important keywords from the job description that should be added to the resume.

Format your response clearly in Markdown with sections and bullet points for easy reading.
            """
            analysis_result = generate_content(matching_prompt)
            st.session_state.analysis_result = analysis_result

        # Tab 2: CV Generation
        with st.spinner("⏳ Generating Customized CV..."):
            cv_prompt = f"""
Based on the following resume and job description, create an optimized CV/Resume that highlights relevant skills and experiences for this specific position.

ORIGINAL RESUME:
{resume_text}

TARGET JOB DESCRIPTION:
{job_text}

Create a professional, tailored resume that:
1. Reorganizes the resume to emphasize relevant skills first
2. Uses keywords from the job description naturally
3. Highlights achievements that match job requirements
4. Maintains professional formatting
5. Is ATS-friendly (Applicant Tracking System compatible)

Generate the complete customized CV with proper sections (Summary, Experience, Skills, Education, etc.).
            """
            cv_result = generate_content(cv_prompt)
            st.session_state.cv_result = cv_result

        # Tab 3: Interview Preparation Guide
        with st.spinner("⏳ Generating Interview Preparation Guide..."):
            interview_prompt = f"""
Based on the job description and resume, create a comprehensive interview preparation guide.

JOB DESCRIPTION:
{job_text}

RESUME:
{resume_text}

Create a detailed interview preparation guide that includes:

1. **Top 10 Questions You'll Likely Be Asked**: Based on the job description and your experience
2. **How to Answer Them**: Provide strategic answers for each question
3. **Questions to Ask the Interviewer**: 5-7 intelligent questions that show your interest
4. **Key Talking Points**: Main achievements and skills to highlight
5. **Potential Concerns & How to Address Them**: Address any gaps between resume and job requirements
6. **Technical Skills to Prepare**: If applicable, technical areas to brush up on
7. **Company Research Tips**: What to research about the company
8. **STAR Method Examples**: 3-4 examples using Situation-Task-Action-Result format

Make it comprehensive, strategic, and personalized to this specific role.
            """
            interview_result = generate_content(interview_prompt)
            st.session_state.interview_result = interview_result

        st.success("✅ Analysis Complete! Check the tabs below for results.")

# Section 3: Results Display
if st.session_state.get("analysis_result") or st.session_state.get("cv_result") or st.session_state.get("interview_result"):
    st.markdown("""
    <div class="card-section">
        <h2>📊 Step 3: Your Personalized Results</h2>
        <p>Review your analysis, customized CV, and interview guide below.</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📈 Resume Analysis", "📝 Customized CV", "🎤 Interview Guide"])
    
    with tab1:
        if st.session_state.analysis_result:
            st.markdown("<div class='results-container'>", unsafe_allow_html=True)
            st.markdown(st.session_state.analysis_result)
            st.markdown("</div>", unsafe_allow_html=True)
            st.download_button(
                "⬇️ Download Analysis Report",
                st.session_state.analysis_result,
                file_name="resume_analysis_report.md",
                mime="text/markdown",
                use_container_width=True
            )
    
    with tab2:
        if st.session_state.cv_result:
            st.markdown("<div class='results-container'>", unsafe_allow_html=True)
            st.markdown(st.session_state.cv_result)
            st.markdown("</div>", unsafe_allow_html=True)
            st.download_button(
                "⬇️ Download Customized CV",
                st.session_state.cv_result,
                file_name="customized_resume.md",
                mime="text/markdown",
                use_container_width=True
            )
    
    with tab3:
        if st.session_state.interview_result:
            st.markdown("<div class='results-container'>", unsafe_allow_html=True)
            st.markdown(st.session_state.interview_result)
            st.markdown("</div>", unsafe_allow_html=True)
            st.download_button(
                "⬇️ Download Interview Guide",
                st.session_state.interview_result,
                file_name="interview_preparation_guide.md",
                mime="text/markdown",
                use_container_width=True
            )

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p>🚀 Resume & Job Matcher Pro | Powered by Google Gemini 2.5 Flash</p>
    <p style="font-size: 0.9rem;">Built to help you land your dream job!</p>
</div>
""", unsafe_allow_html=True)
