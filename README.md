# 🎯 Resume Keyword Optimizer

A powerful tool that analyzes resumes against job descriptions to identify missing keywords, calculate ATS compatibility scores, and provide actionable optimization suggestions. Built with advanced NLP techniques and designed to help job seekers improve their resume's performance with Applicant Tracking Systems (ATS).

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![NLP](https://img.shields.io/badge/NLP-spaCy%20%7C%20NLTK-orange.svg)

## 🌟 Features

### 🔍 **Advanced Keyword Analysis**
- **Smart Keyword Extraction**: Uses TF-IDF and spaCy NLP for intelligent keyword identification
- **Categorical Classification**: Automatically categorizes keywords into technical skills, soft skills, tools, etc.
- **Importance Scoring**: Assigns relevance scores to help prioritize optimization efforts
- **Context Analysis**: Shows where keywords appear in job descriptions for better understanding

### 📊 **Comprehensive Scoring System**
- **ATS Compatibility Score**: Simulates how well your resume performs with ATS systems
- **Overall Match Score**: Calculates alignment between resume and job description
- **Readability Assessment**: Evaluates resume readability using established metrics
- **Keyword Density Analysis**: Measures optimal keyword usage without over-optimization

### 💡 **Actionable Insights**
- **Missing Keywords Identification**: Highlights critical keywords absent from your resume
- **Optimization Suggestions**: Provides specific, actionable recommendations
- **Strength Highlighting**: Identifies your existing advantages to emphasize
- **Industry-Specific Guidance**: Tailored advice based on job requirements

### 🎨 **Multiple Interfaces**
- **Web Application**: Beautiful Streamlit interface with interactive visualizations
- **Command Line Tool**: Powerful CLI with rich formatting and batch processing
- **File Format Support**: Handles PDF, DOCX, and TXT files seamlessly

## 🚀 Quick Start

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/resume-keyword-optimizer.git
cd resume-keyword-optimizer
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Download spaCy model**
```bash
python -m spacy download en_core_web_sm
```

### Usage Options

#### 🌐 Web Interface (Recommended)
```bash
streamlit run web_app.py
```
Then open your browser to `http://localhost:8501`

#### 💻 Command Line Interface
```bash
# Interactive mode
python cli.py

# Direct analysis
python cli.py --resume sample_resume.txt --job sample_job_description.txt

# With output file
python cli.py -r resume.pdf -j job.txt -o analysis_report.txt

# JSON output
python cli.py -r resume.docx -jt "Job description text..." -f json
```

#### 🐍 Python API
```python
from resume_optimizer import ResumeKeywordOptimizer
from file_processors import FileProcessor

# Initialize
optimizer = ResumeKeywordOptimizer()
processor = FileProcessor()

# Process files
resume_text = processor.extract_text_from_file("resume.pdf")
job_description = open("job.txt").read()

# Analyze
result = optimizer.analyze_resume_against_job(resume_text, job_description)

# Generate report
report = optimizer.generate_keyword_report(result)
print(report)
```

## 📈 Understanding Your Results

### Score Interpretation

| Score Range | ATS Compatibility | Recommendation |
|-------------|------------------|----------------|
| 80-100% | 🌟 Excellent | Ready to submit! |
| 60-79% | 👍 Good | Minor tweaks needed |
| 40-59% | ⚠️ Needs Work | Significant improvements required |
| 0-39% | 🚨 Poor | Major overhaul needed |

### Keyword Impact Levels
- **🔴 Critical**: Must-have keywords for ATS success
- **🟡 Important**: Highly recommended additions
- **⚪ Moderate**: Nice-to-have improvements

## 🛠️ Technical Architecture

### Core Components

```
├── resume_optimizer.py      # Main analysis engine
├── file_processors.py       # Document parsing utilities
├── cli.py                   # Command-line interface
├── web_app.py              # Streamlit web application
├── requirements.txt         # Python dependencies
└── README.md               # Documentation
```

### Key Technologies
- **NLP Processing**: spaCy, NLTK for text analysis
- **Machine Learning**: scikit-learn for TF-IDF vectorization
- **File Processing**: PyPDF2, python-docx for document parsing
- **Web Interface**: Streamlit with Plotly visualizations
- **CLI Interface**: Rich library for beautiful terminal output

### Algorithm Overview

1. **Text Preprocessing**: Clean and normalize resume and job description text
2. **Keyword Extraction**: Use TF-IDF and NLP techniques to identify important terms
3. **Categorization**: Classify keywords into types using regex patterns and linguistic analysis
4. **Matching Algorithm**: Compare resume keywords against job requirements with fuzzy matching
5. **Scoring**: Calculate multiple metrics including ATS compatibility and overall alignment
6. **Suggestions**: Generate actionable recommendations based on analysis results

## 📊 Sample Analysis Output

```
============================================================
📊 RESUME KEYWORD OPTIMIZATION REPORT
============================================================

🎯 Overall Match Score: 72%
🤖 ATS Compatibility: 68%
📖 Readability Score: 75.2
🔍 Keyword Density: 2.3%

👍 Good: Your resume has good alignment, but there's room for improvement.

❌ MISSING HIGH-IMPACT KEYWORDS
----------------------------------------
 1. typescript (technical_skill) - 🟡 Important
 2. microservices (technical_skill) - 🟡 Important
 3. kubernetes (tool_technology) - 🔴 Critical
 4. terraform (tool_technology) - 🟡 Important
 5. graphql (technical_skill) - ⚪ Moderate

✅ SUCCESSFULLY MATCHED KEYWORDS
----------------------------------------
1. react (mentioned 2x)
2. node.js (mentioned 1x)
3. aws (mentioned 3x)
4. python (mentioned 4x)
5. agile (mentioned 2x)

💡 OPTIMIZATION SUGGESTIONS
----------------------------------------
1. 📋 Technical Skills Gap: Add these key technical skills: typescript, microservices, kubernetes
2. 🔧 Tools & Technologies: Mention experience with: terraform, graphql
3. 🤖 ATS Optimization: Your resume may not pass initial ATS screening. Focus on exact keyword matches.
```

## 🎨 Web Interface Features

### Interactive Dashboard
- **Real-time Analysis**: Instant feedback as you upload documents
- **Visual Charts**: Gauge charts, bar graphs, and word clouds
- **Tabbed Interface**: Organized results across multiple views
- **Export Options**: Download detailed reports in text or JSON format

### Visualizations
- **Score Gauges**: Intuitive circular progress indicators
- **Keyword Charts**: Comparative analysis by category
- **Word Clouds**: Visual representation of missing vs. matched keywords
- **Context Highlighting**: Show where keywords appear in job descriptions

## 🔧 Advanced Usage

### Batch Processing
```bash
# Process multiple resumes against the same job
for resume in resumes/*.pdf; do
    python cli.py -r "$resume" -j job_description.txt -o "analysis_$(basename "$resume").txt"
done
```

### Custom Keyword Patterns
Extend the tool by modifying keyword patterns in `resume_optimizer.py`:

```python
self.keyword_patterns = {
    KeywordType.TECHNICAL_SKILL: [
        r'\b(?:your_custom_pattern)\b',
        # Add more patterns...
    ]
}
```

### Integration with Other Tools
```python
# Example: Integration with job scraping
import requests
from resume_optimizer import ResumeKeywordOptimizer

def analyze_job_posting(job_url, resume_path):
    # Scrape job description
    job_text = scrape_job_description(job_url)
    
    # Analyze
    optimizer = ResumeKeywordOptimizer()
    result = optimizer.analyze_resume_against_job(resume_path, job_text)
    
    return result
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests** for new functionality
5. **Submit a pull request**

### Development Setup
```bash
# Clone your fork
git clone https://github.com/yourusername/resume-keyword-optimizer.git

# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Run tests
pytest tests/

# Format code
black .
```

### Areas for Contribution
- Additional file format support (e.g., ODT, RTF)
- More sophisticated NLP models
- Industry-specific keyword databases
- Multi-language support
- Enhanced visualization options
- Performance optimizations

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **spaCy**: For advanced NLP capabilities
- **NLTK**: For text processing utilities
- **Streamlit**: For the beautiful web interface
- **Rich**: For enhanced CLI experience
- **scikit-learn**: For machine learning algorithms

## 📞 Support

- **Issues**: Report bugs on [GitHub Issues](https://github.com/yourusername/resume-keyword-optimizer/issues)
- **Documentation**: Check our [Wiki](https://github.com/yourusername/resume-keyword-optimizer/wiki)
- **Discussions**: Join conversations in [GitHub Discussions](https://github.com/yourusername/resume-keyword-optimizer/discussions)

## 🚗 Roadmap

### Upcoming Features
- [ ] **AI-Powered Suggestions**: GPT integration for natural language recommendations
- [ ] **Resume Builder**: Generate optimized resumes based on analysis
- [ ] **Industry Templates**: Pre-built optimization templates for different sectors
- [ ] **Version Tracking**: Track resume improvements over time
- [ ] **Collaborative Features**: Team resume review and feedback
- [ ] **Mobile App**: Native mobile application
- [ ] **Browser Extension**: Analyze job postings directly from job boards

---

**Built with ❤️ for job seekers everywhere. Help us make job hunting more fair and accessible!**