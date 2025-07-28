import streamlit as st
import io
import tempfile
import os
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt

from resume_optimizer import ResumeKeywordOptimizer, KeywordType
from file_processors import FileProcessor

# Page configuration
st.set_page_config(
    page_title="Resume Keyword Optimizer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .score-metric {
        text-align: center;
        padding: 1rem;
        background-color: #f0f2f6;
        border-radius: 10px;
        margin: 0.5rem;
    }
    .missing-keyword {
        background-color: #ffebee;
        padding: 0.5rem;
        border-left: 4px solid #f44336;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
    .matched-keyword {
        background-color: #e8f5e8;
        padding: 0.5rem;
        border-left: 4px solid #4caf50;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_optimizer():
    """Load and cache the optimizer instance"""
    return ResumeKeywordOptimizer()

@st.cache_resource  
def load_file_processor():
    """Load and cache the file processor instance"""
    return FileProcessor()

def create_score_gauge(score, title):
    """Create a gauge chart for scores"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title},
        delta = {'reference': 70},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 40], 'color': "lightgray"},
                {'range': [40, 70], 'color': "yellow"},
                {'range': [70, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    fig.update_layout(height=300)
    return fig

def create_keyword_chart(missing_keywords, matched_keywords):
    """Create a bar chart comparing keyword types"""
    # Count keywords by type
    missing_counts = {}
    matched_counts = {}
    
    for kw in missing_keywords:
        kw_type = kw.keyword_type.value.replace('_', ' ').title()
        missing_counts[kw_type] = missing_counts.get(kw_type, 0) + 1
    
    for kw in matched_keywords:
        kw_type = kw.keyword_type.value.replace('_', ' ').title()
        matched_counts[kw_type] = matched_counts.get(kw_type, 0) + 1
    
    # Prepare data for plotting
    all_types = set(list(missing_counts.keys()) + list(matched_counts.keys()))
    
    data = []
    for kw_type in all_types:
        data.append({
            'Keyword Type': kw_type,
            'Missing': missing_counts.get(kw_type, 0),
            'Matched': matched_counts.get(kw_type, 0)
        })
    
    df = pd.DataFrame(data)
    
    fig = px.bar(df, x='Keyword Type', y=['Missing', 'Matched'], 
                 title='Keyword Analysis by Type',
                 color_discrete_map={'Missing': '#ff7f7f', 'Matched': '#7fbf7f'})
    
    fig.update_layout(height=400)
    return fig

def create_wordcloud(keywords, title):
    """Create a word cloud from keywords"""
    if not keywords:
        return None
    
    # Prepare text for word cloud
    text = ' '.join([kw.keyword for kw in keywords[:20]])
    
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        colormap='viridis'
    ).generate(text)
    
    # Create matplotlib figure
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title(title, fontsize=16, fontweight='bold')
    
    return fig

def process_uploaded_file(uploaded_file):
    """Process uploaded file and extract text"""
    file_processor = load_file_processor()
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name
    
    try:
        # Extract text from file
        text = file_processor.extract_text_from_file(tmp_file_path)
        text = file_processor.clean_extracted_text(text)
        
        # Validate content
        if not file_processor.validate_resume_content(text):
            st.warning("⚠️ The uploaded file doesn't appear to contain a typical resume format. Results may be less accurate.")
        
        return text
    finally:
        # Clean up temporary file
        os.unlink(tmp_file_path)

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🎯 Resume Keyword Optimizer</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    **Optimize your resume for Applicant Tracking Systems (ATS) and improve your job application success rate!**
    
    This tool analyzes your resume against job descriptions to identify missing keywords, 
    calculate ATS compatibility scores, and provide actionable optimization suggestions.
    """)
    
    # Sidebar for inputs
    st.sidebar.header("📋 Input Your Documents")
    
    # Resume upload
    st.sidebar.subheader("1. Upload Your Resume")
    resume_file = st.sidebar.file_uploader(
        "Choose your resume file",
        type=['pdf', 'docx', 'txt'],
        help="Supported formats: PDF, DOCX, TXT"
    )
    
    # Job description input
    st.sidebar.subheader("2. Job Description")
    input_method = st.sidebar.radio(
        "How would you like to provide the job description?",
        ["Paste text", "Upload file"]
    )
    
    job_description = None
    
    if input_method == "Paste text":
        job_description = st.sidebar.text_area(
            "Paste the job description here",
            height=200,
            placeholder="Paste the complete job description including requirements, responsibilities, and qualifications..."
        )
    else:
        job_file = st.sidebar.file_uploader(
            "Upload job description file",
            type=['txt'],
            help="Upload a text file containing the job description"
        )
        if job_file:
            job_description = str(job_file.read(), "utf-8")
    
    # Analysis button
    analyze_button = st.sidebar.button("🚀 Analyze Resume", type="primary")
    
    # Main content area
    if resume_file is None:
        st.info("👆 Please upload your resume file in the sidebar to get started.")
        
        # Show demo information
        st.subheader("🌟 What This Tool Does")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🔍 Keyword Analysis**
            - Identifies missing keywords from job descriptions
            - Categorizes keywords by type (technical, soft skills, etc.)
            - Shows keyword importance scores
            """)
        
        with col2:
            st.markdown("""
            **📊 ATS Scoring**
            - Calculates ATS compatibility score
            - Measures keyword density
            - Assesses readability
            """)
        
        with col3:
            st.markdown("""
            **💡 Smart Suggestions**
            - Provides actionable optimization tips
            - Highlights your existing strengths
            - Suggests specific improvements
            """)
        
        return
    
    if not job_description:
        st.warning("📝 Please provide a job description in the sidebar.")
        return
    
    if not analyze_button:
        st.info("✅ Resume and job description loaded. Click 'Analyze Resume' in the sidebar to start analysis.")
        return
    
    # Process files and run analysis
    with st.spinner("🔄 Processing your resume and analyzing keywords..."):
        try:
            # Extract resume text
            resume_text = process_uploaded_file(resume_file)
            
            # Load optimizer and run analysis
            optimizer = load_optimizer()
            result = optimizer.analyze_resume_against_job(resume_text, job_description)
            
            # Display results
            display_results(result, resume_text, job_description)
            
        except Exception as e:
            st.error(f"❌ Error during analysis: {str(e)}")
            st.error("Please check your files and try again.")

def display_results(result, resume_text, job_description):
    """Display the analysis results"""
    
    # Overview section
    st.header("📊 Analysis Results")
    
    # Score metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Overall Match",
            value=f"{result.overall_score}%",
            delta=f"{result.overall_score - 70:.1f}%" if result.overall_score != 70 else None
        )
    
    with col2:
        st.metric(
            label="ATS Score", 
            value=f"{result.ats_score}%",
            delta=f"{result.ats_score - 70:.1f}%" if result.ats_score != 70 else None
        )
    
    with col3:
        st.metric(
            label="Readability",
            value=f"{result.readability_score:.1f}",
            delta=f"{result.readability_score - 60:.1f}" if result.readability_score != 60 else None
        )
    
    with col4:
        st.metric(
            label="Keyword Density",
            value=f"{result.keyword_density}%",
            delta=f"{result.keyword_density - 2:.1f}%" if result.keyword_density != 2 else None
        )
    
    # Score interpretation
    if result.overall_score >= 80:
        st.success("🌟 **Excellent!** Your resume is well-aligned with the job description.")
    elif result.overall_score >= 60:
        st.info("👍 **Good alignment** with room for improvement.")
    elif result.overall_score >= 40:
        st.warning("⚠️ **Needs work** - significant improvements recommended.")
    else:
        st.error("🚨 **Poor match** - major optimization needed.")
    
    # Detailed analysis tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Missing Keywords", "✅ Matched Keywords", "💡 Suggestions", "📈 Visual Analysis"])
    
    with tab1:
        display_missing_keywords(result.missing_keywords)
    
    with tab2:
        display_matched_keywords(result.matched_keywords)
    
    with tab3:
        display_suggestions(result.suggestions)
    
    with tab4:
        display_visual_analysis(result)
    
    # Download section
    st.header("💾 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Download Detailed Report"):
            report = load_optimizer().generate_keyword_report(result)
            st.download_button(
                label="Download Report",
                data=report,
                file_name=f"resume_analysis_{result.ats_score:.0f}pct.txt",
                mime="text/plain"
            )
    
    with col2:
        if st.button("📊 Download JSON Data"):
            import json
            
            data = {
                "overall_score": result.overall_score,
                "ats_score": result.ats_score,
                "readability_score": result.readability_score,
                "keyword_density": result.keyword_density,
                "missing_keywords": [
                    {
                        "keyword": kw.keyword,
                        "type": kw.keyword_type.value,
                        "importance": kw.importance_score
                    }
                    for kw in result.missing_keywords
                ],
                "matched_keywords": [
                    {
                        "keyword": kw.keyword,
                        "type": kw.keyword_type.value,
                        "frequency": kw.resume_frequency
                    }
                    for kw in result.matched_keywords
                ],
                "suggestions": result.suggestions
            }
            
            st.download_button(
                label="Download JSON",
                data=json.dumps(data, indent=2),
                file_name=f"resume_analysis_{result.ats_score:.0f}pct.json",
                mime="application/json"
            )

def display_missing_keywords(missing_keywords):
    """Display missing keywords analysis"""
    if not missing_keywords:
        st.success("🎉 Great! No critical keywords are missing from your resume.")
        return
    
    st.subheader(f"❌ Missing Keywords ({len(missing_keywords)} found)")
    st.write("These keywords from the job description are not found in your resume:")
    
    # Create dataframe for display
    data = []
    for i, kw in enumerate(missing_keywords[:15], 1):  # Show top 15
        impact = "🔴 Critical" if kw.importance_score > 0.1 else "🟡 Important" if kw.importance_score > 0.05 else "⚪ Moderate"
        data.append({
            "#": i,
            "Keyword": kw.keyword,
            "Type": kw.keyword_type.value.replace('_', ' ').title(),
            "Impact": impact,
            "Importance Score": f"{kw.importance_score:.3f}"
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
    
    # Show context for top missing keywords
    st.subheader("🔍 Context Analysis")
    for kw in missing_keywords[:5]:
        if kw.context:
            with st.expander(f"Context for '{kw.keyword}'"):
                for context in kw.context[:2]:  # Show up to 2 contexts
                    st.write(f"*{context}*")

def display_matched_keywords(matched_keywords):
    """Display successfully matched keywords"""
    if not matched_keywords:
        st.warning("⚠️ No keywords were successfully matched. Consider reviewing your resume content.")
        return
    
    st.subheader(f"✅ Successfully Matched Keywords ({len(matched_keywords)} found)")
    st.write("These keywords from the job description are present in your resume:")
    
    # Create dataframe for display
    data = []
    for i, kw in enumerate(matched_keywords[:10], 1):  # Show top 10
        data.append({
            "#": i,
            "Keyword": kw.keyword,
            "Type": kw.keyword_type.value.replace('_', ' ').title(),
            "Frequency": f"{kw.resume_frequency}x",
            "Importance": f"{kw.importance_score:.3f}"
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

def display_suggestions(suggestions):
    """Display optimization suggestions"""
    if not suggestions:
        st.success("🎉 No specific suggestions - your resume looks good!")
        return
    
    st.subheader("💡 Optimization Suggestions")
    st.write("Here are actionable recommendations to improve your resume:")
    
    for i, suggestion in enumerate(suggestions, 1):
        st.markdown(f"**{i}.** {suggestion}")

def display_visual_analysis(result):
    """Display visual analysis charts"""
    st.subheader("📈 Visual Analysis")
    
    # Score gauges
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = create_score_gauge(result.overall_score, "Overall Match Score")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = create_score_gauge(result.ats_score, "ATS Compatibility Score")
        st.plotly_chart(fig2, use_container_width=True)
    
    # Keyword analysis chart
    if result.missing_keywords or result.matched_keywords:
        fig3 = create_keyword_chart(result.missing_keywords, result.matched_keywords)
        st.plotly_chart(fig3, use_container_width=True)
    
    # Word clouds
    col1, col2 = st.columns(2)
    
    with col1:
        if result.missing_keywords:
            fig4 = create_wordcloud(result.missing_keywords, "Missing Keywords")
            if fig4:
                st.pyplot(fig4)
    
    with col2:
        if result.matched_keywords:
            fig5 = create_wordcloud(result.matched_keywords, "Matched Keywords")
            if fig5:
                st.pyplot(fig5)

if __name__ == "__main__":
    main()