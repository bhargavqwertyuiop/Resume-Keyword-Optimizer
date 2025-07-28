import re
import nltk
import spacy
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import textstat
from typing import Dict, List, Tuple, Set
import json
from dataclasses import dataclass
from enum import Enum

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
from nltk.stem import WordNetLemmatizer

class KeywordType(Enum):
    TECHNICAL_SKILL = "technical_skill"
    SOFT_SKILL = "soft_skill"
    CERTIFICATION = "certification"
    TOOL_TECHNOLOGY = "tool_technology"
    INDUSTRY_TERM = "industry_term"
    ACTION_VERB = "action_verb"
    QUALIFICATION = "qualification"

@dataclass
class KeywordMatch:
    keyword: str
    keyword_type: KeywordType
    importance_score: float
    found_in_resume: bool
    resume_frequency: int
    job_frequency: int
    context: List[str]

@dataclass
class OptimizationResult:
    overall_score: float
    missing_keywords: List[KeywordMatch]
    matched_keywords: List[KeywordMatch]
    suggestions: List[str]
    ats_score: float
    readability_score: float
    keyword_density: float

class ResumeKeywordOptimizer:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy English model not found. Installing...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
        
        # Industry-specific keyword patterns
        self.keyword_patterns = {
            KeywordType.TECHNICAL_SKILL: [
                r'\b(?:python|java|javascript|c\+\+|sql|html|css|react|angular|vue|node\.?js|django|flask|spring|docker|kubernetes|aws|azure|gcp|git|jenkins|terraform|ansible)\b',
                r'\b(?:machine learning|artificial intelligence|data science|deep learning|neural networks|nlp|computer vision|algorithms|data structures)\b',
                r'\b(?:agile|scrum|devops|ci/cd|microservices|api|rest|graphql|nosql|mongodb|postgresql|mysql|redis|elasticsearch)\b'
            ],
            KeywordType.SOFT_SKILL: [
                r'\b(?:leadership|communication|teamwork|problem.solving|analytical|creative|adaptable|collaborative|mentoring|coaching)\b',
                r'\b(?:project management|time management|critical thinking|decision making|conflict resolution|negotiation)\b'
            ],
            KeywordType.CERTIFICATION: [
                r'\b(?:aws certified|azure certified|google cloud|cissp|cisa|pmp|scrum master|six sigma|itil|comptia)\b',
                r'\b(?:certification|certified|credential|license)\b'
            ],
            KeywordType.TOOL_TECHNOLOGY: [
                r'\b(?:jira|confluence|slack|teams|zoom|tableau|power bi|salesforce|sap|oracle|workday|servicenow)\b',
                r'\b(?:photoshop|illustrator|figma|sketch|autocad|solidworks|matlab|r studio|jupyter|visual studio)\b'
            ],
            KeywordType.ACTION_VERB: [
                r'\b(?:developed|implemented|designed|created|built|managed|led|coordinated|optimized|improved)\b',
                r'\b(?:analyzed|researched|collaborated|mentored|trained|presented|delivered|achieved|increased|reduced)\b'
            ]
        }
        
        # Common ATS-friendly keywords by industry
        self.industry_keywords = {
            'technology': ['software development', 'programming', 'debugging', 'testing', 'deployment', 'scalability', 'performance optimization'],
            'marketing': ['digital marketing', 'seo', 'sem', 'social media', 'content creation', 'brand management', 'analytics'],
            'finance': ['financial analysis', 'budgeting', 'forecasting', 'risk management', 'compliance', 'audit', 'investment'],
            'healthcare': ['patient care', 'medical records', 'hipaa', 'clinical research', 'healthcare regulations', 'quality assurance'],
            'education': ['curriculum development', 'lesson planning', 'student assessment', 'classroom management', 'educational technology']
        }

    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for analysis"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s\.\-\+\#]', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def extract_keywords_with_importance(self, text: str, min_freq: int = 1) -> Dict[str, float]:
        """Extract keywords using TF-IDF and assign importance scores"""
        # Preprocess text
        processed_text = self.preprocess_text(text)
        
        # Use spaCy for better tokenization and NER
        doc = self.nlp(processed_text)
        
        # Extract meaningful tokens
        tokens = []
        for token in doc:
            if (not token.is_stop and 
                not token.is_punct and 
                len(token.text) > 2 and
                token.pos_ in ['NOUN', 'ADJ', 'VERB', 'PROPN']):
                tokens.append(token.lemma_)
        
        # Extract phrases (bigrams and trigrams)
        sentences = sent_tokenize(text)
        all_phrases = []
        
        for sentence in sentences:
            sentence_doc = self.nlp(sentence)
            # Extract noun phrases
            for chunk in sentence_doc.noun_chunks:
                if len(chunk.text.split()) > 1:
                    all_phrases.append(chunk.text.lower())
        
        # Combine tokens and phrases
        combined_text = ' '.join(tokens + all_phrases)
        
        # Use TF-IDF for importance scoring
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),
            max_features=1000,
            stop_words='english'
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform([combined_text])
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
            
            # Create keyword importance dictionary
            keyword_scores = {}
            for i, score in enumerate(scores):
                if score > 0:
                    keyword_scores[feature_names[i]] = score
            
            return keyword_scores
        except:
            # Fallback to simple frequency counting
            word_freq = Counter(tokens + all_phrases)
            total_words = sum(word_freq.values())
            return {word: freq/total_words for word, freq in word_freq.items() if freq >= min_freq}

    def categorize_keywords(self, keywords: Dict[str, float]) -> Dict[KeywordType, List[Tuple[str, float]]]:
        """Categorize keywords by type using pattern matching"""
        categorized = defaultdict(list)
        
        for keyword, score in keywords.items():
            categorized_keyword = False
            
            # Check against patterns for each category
            for keyword_type, patterns in self.keyword_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, keyword, re.IGNORECASE):
                        categorized[keyword_type].append((keyword, score))
                        categorized_keyword = True
                        break
                if categorized_keyword:
                    break
            
            # If not categorized, classify as industry term
            if not categorized_keyword:
                categorized[KeywordType.INDUSTRY_TERM].append((keyword, score))
        
        return categorized

    def extract_job_requirements(self, job_description: str) -> Dict[str, any]:
        """Extract structured requirements from job description"""
        doc = self.nlp(job_description)
        
        requirements = {
            'required_skills': [],
            'preferred_skills': [],
            'experience_years': None,
            'education_level': None,
            'certifications': [],
            'tools': []
        }
        
        # Extract years of experience
        exp_pattern = r'(\d+)[\+\-\s]*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)'
        exp_match = re.search(exp_pattern, job_description.lower())
        if exp_match:
            requirements['experience_years'] = int(exp_match.group(1))
        
        # Extract education requirements
        education_patterns = [
            r'bachelor[\'s]*\s*(?:degree)?',
            r'master[\'s]*\s*(?:degree)?',
            r'phd|doctorate',
            r'high school|diploma'
        ]
        
        for pattern in education_patterns:
            if re.search(pattern, job_description.lower()):
                requirements['education_level'] = pattern
                break
        
        # Extract required vs preferred skills
        required_section = re.search(r'(?:required|must have|essential).*?(?:preferred|nice to have|plus|bonus)', job_description, re.IGNORECASE | re.DOTALL)
        preferred_section = re.search(r'(?:preferred|nice to have|plus|bonus).*', job_description, re.IGNORECASE | re.DOTALL)
        
        return requirements

    def calculate_ats_score(self, resume_text: str, job_description: str) -> float:
        """Calculate ATS-friendly score based on keyword matching"""
        # Extract keywords from both texts
        job_keywords = self.extract_keywords_with_importance(job_description)
        resume_keywords = self.extract_keywords_with_importance(resume_text)
        
        # Calculate keyword overlap
        job_keyword_set = set(job_keywords.keys())
        resume_keyword_set = set(resume_keywords.keys())
        
        # Weighted matching score
        matched_keywords = job_keyword_set.intersection(resume_keyword_set)
        
        if not job_keyword_set:
            return 0.0
        
        # Calculate weighted score
        total_job_importance = sum(job_keywords.values())
        matched_importance = sum(job_keywords[kw] for kw in matched_keywords)
        
        base_score = (matched_importance / total_job_importance) * 100 if total_job_importance > 0 else 0
        
        # Bonus points for keyword density and variety
        keyword_density = len(matched_keywords) / len(resume_text.split()) * 1000
        density_bonus = min(keyword_density * 5, 15)  # Max 15% bonus
        
        # Format and structure bonus
        format_bonus = 0
        if any(section in resume_text.lower() for section in ['experience', 'education', 'skills']):
            format_bonus += 5
        if re.search(r'\b\d{4}\b', resume_text):  # Has years
            format_bonus += 3
        if re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', resume_text):  # Has email
            format_bonus += 2
        
        final_score = min(base_score + density_bonus + format_bonus, 100)
        return round(final_score, 1)

    def analyze_resume_against_job(self, resume_text: str, job_description: str) -> OptimizationResult:
        """Main analysis function that compares resume against job description"""
        
        # Extract keywords from both texts
        job_keywords = self.extract_keywords_with_importance(job_description)
        resume_keywords = self.extract_keywords_with_importance(resume_text)
        
        # Categorize job keywords
        categorized_job_keywords = self.categorize_keywords(job_keywords)
        
        # Find matches and gaps
        matched_keywords = []
        missing_keywords = []
        
        for keyword_type, keywords in categorized_job_keywords.items():
            for keyword, importance in keywords:
                # Check if keyword exists in resume (fuzzy matching)
                found_in_resume = any(
                    keyword.lower() in resume_kw.lower() or resume_kw.lower() in keyword.lower()
                    for resume_kw in resume_keywords.keys()
                )
                
                resume_freq = sum(1 for resume_kw in resume_keywords.keys() 
                                if keyword.lower() in resume_kw.lower() or resume_kw.lower() in keyword.lower())
                
                job_freq = job_description.lower().count(keyword.lower())
                
                # Extract context where keyword appears in job description
                context = self._extract_keyword_context(job_description, keyword)
                
                keyword_match = KeywordMatch(
                    keyword=keyword,
                    keyword_type=keyword_type,
                    importance_score=importance,
                    found_in_resume=found_in_resume,
                    resume_frequency=resume_freq,
                    job_frequency=job_freq,
                    context=context
                )
                
                if found_in_resume:
                    matched_keywords.append(keyword_match)
                else:
                    missing_keywords.append(keyword_match)
        
        # Sort by importance
        missing_keywords.sort(key=lambda x: x.importance_score, reverse=True)
        matched_keywords.sort(key=lambda x: x.importance_score, reverse=True)
        
        # Calculate scores
        ats_score = self.calculate_ats_score(resume_text, job_description)
        overall_score = self._calculate_overall_score(matched_keywords, missing_keywords)
        readability_score = textstat.flesch_reading_ease(resume_text)
        keyword_density = self._calculate_keyword_density(resume_text, job_keywords)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(missing_keywords, matched_keywords, ats_score)
        
        return OptimizationResult(
            overall_score=overall_score,
            missing_keywords=missing_keywords[:20],  # Top 20 missing
            matched_keywords=matched_keywords[:10],   # Top 10 matched
            suggestions=suggestions,
            ats_score=ats_score,
            readability_score=readability_score,
            keyword_density=keyword_density
        )

    def _extract_keyword_context(self, text: str, keyword: str, window: int = 30) -> List[str]:
        """Extract context around keyword occurrences"""
        contexts = []
        text_lower = text.lower()
        keyword_lower = keyword.lower()
        
        start = 0
        while True:
            pos = text_lower.find(keyword_lower, start)
            if pos == -1:
                break
            
            # Extract surrounding context
            context_start = max(0, pos - window)
            context_end = min(len(text), pos + len(keyword) + window)
            context = text[context_start:context_end].strip()
            
            # Clean context
            context = re.sub(r'\s+', ' ', context)
            contexts.append(f"...{context}...")
            
            start = pos + 1
        
        return contexts[:3]  # Return up to 3 contexts

    def _calculate_overall_score(self, matched: List[KeywordMatch], missing: List[KeywordMatch]) -> float:
        """Calculate overall optimization score"""
        if not matched and not missing:
            return 0.0
        
        total_importance = sum(kw.importance_score for kw in matched + missing)
        matched_importance = sum(kw.importance_score for kw in matched)
        
        if total_importance == 0:
            return 0.0
        
        return round((matched_importance / total_importance) * 100, 1)

    def _calculate_keyword_density(self, text: str, keywords: Dict[str, float]) -> float:
        """Calculate keyword density as percentage"""
        total_words = len(text.split())
        keyword_count = sum(text.lower().count(kw.lower()) for kw in keywords.keys())
        
        if total_words == 0:
            return 0.0
        
        return round((keyword_count / total_words) * 100, 2)

    def _generate_suggestions(self, missing: List[KeywordMatch], matched: List[KeywordMatch], ats_score: float) -> List[str]:
        """Generate actionable suggestions for resume improvement"""
        suggestions = []
        
        # Suggestions based on missing keywords
        if missing:
            # Group by type
            missing_by_type = defaultdict(list)
            for kw in missing[:15]:  # Top 15 missing
                missing_by_type[kw.keyword_type].append(kw)
            
            for keyword_type, keywords in missing_by_type.items():
                if keyword_type == KeywordType.TECHNICAL_SKILL:
                    top_skills = [kw.keyword for kw in keywords[:5]]
                    suggestions.append(f"📋 **Technical Skills Gap**: Add these key technical skills: {', '.join(top_skills)}")
                
                elif keyword_type == KeywordType.SOFT_SKILL:
                    top_soft = [kw.keyword for kw in keywords[:3]]
                    suggestions.append(f"🤝 **Soft Skills**: Incorporate these soft skills in your experience descriptions: {', '.join(top_soft)}")
                
                elif keyword_type == KeywordType.ACTION_VERB:
                    top_verbs = [kw.keyword for kw in keywords[:5]]
                    suggestions.append(f"💪 **Action Words**: Use stronger action verbs like: {', '.join(top_verbs)}")
                
                elif keyword_type == KeywordType.TOOL_TECHNOLOGY:
                    top_tools = [kw.keyword for kw in keywords[:4]]
                    suggestions.append(f"🔧 **Tools & Technologies**: Mention experience with: {', '.join(top_tools)}")
        
        # ATS-specific suggestions
        if ats_score < 70:
            suggestions.append("🤖 **ATS Optimization**: Your resume may not pass initial ATS screening. Focus on exact keyword matches from the job description.")
        
        if ats_score < 50:
            suggestions.append("⚠️ **Critical**: Consider restructuring your resume to include more relevant keywords. Use the exact terms from the job posting.")
        
        # Format suggestions
        if not any('email' in s.lower() for s in suggestions):
            suggestions.append("📧 **Contact Info**: Ensure your email and phone number are clearly visible at the top.")
        
        # Experience suggestions
        if matched:
            strong_areas = [kw.keyword for kw in matched[:3]]
            suggestions.append(f"✅ **Strengths to Emphasize**: You're strong in {', '.join(strong_areas)}. Make sure these are prominent in your summary.")
        
        return suggestions

    def generate_keyword_report(self, result: OptimizationResult) -> str:
        """Generate a detailed text report"""
        report = []
        report.append("="*60)
        report.append("📊 RESUME KEYWORD OPTIMIZATION REPORT")
        report.append("="*60)
        report.append("")
        
        # Overall scores
        report.append(f"🎯 **Overall Match Score**: {result.overall_score}%")
        report.append(f"🤖 **ATS Compatibility**: {result.ats_score}%")
        report.append(f"📖 **Readability Score**: {result.readability_score:.1f}")
        report.append(f"🔍 **Keyword Density**: {result.keyword_density}%")
        report.append("")
        
        # Score interpretation
        if result.overall_score >= 80:
            report.append("🌟 **Excellent**: Your resume is well-aligned with the job description!")
        elif result.overall_score >= 60:
            report.append("👍 **Good**: Your resume has good alignment, but there's room for improvement.")
        elif result.overall_score >= 40:
            report.append("⚠️ **Needs Work**: Your resume needs significant improvements to match the job.")
        else:
            report.append("🚨 **Poor Match**: Your resume doesn't align well with this job description.")
        
        report.append("")
        
        # Missing keywords section
        if result.missing_keywords:
            report.append("❌ **MISSING HIGH-IMPACT KEYWORDS**")
            report.append("-" * 40)
            
            for i, kw in enumerate(result.missing_keywords[:10], 1):
                impact = "🔴 Critical" if kw.importance_score > 0.1 else "🟡 Important" if kw.importance_score > 0.05 else "⚪ Moderate"
                report.append(f"{i:2d}. {kw.keyword} ({kw.keyword_type.value}) - {impact}")
                
                if kw.context:
                    report.append(f"    Context: {kw.context[0][:100]}...")
            report.append("")
        
        # Matched keywords section
        if result.matched_keywords:
            report.append("✅ **SUCCESSFULLY MATCHED KEYWORDS**")
            report.append("-" * 40)
            
            for i, kw in enumerate(result.matched_keywords[:5], 1):
                frequency_note = f"(mentioned {kw.resume_frequency}x)" if kw.resume_frequency > 1 else ""
                report.append(f"{i}. {kw.keyword} {frequency_note}")
            report.append("")
        
        # Suggestions section
        if result.suggestions:
            report.append("💡 **OPTIMIZATION SUGGESTIONS**")
            report.append("-" * 40)
            
            for i, suggestion in enumerate(result.suggestions, 1):
                report.append(f"{i}. {suggestion}")
            report.append("")
        
        # Action plan
        report.append("📋 **IMMEDIATE ACTION PLAN**")
        report.append("-" * 40)
        
        if result.missing_keywords:
            top_missing = result.missing_keywords[:5]
            report.append("1. **Add these critical keywords to your resume:**")
            for kw in top_missing:
                report.append(f"   • {kw.keyword}")
            report.append("")
        
        report.append("2. **Review job description again** and ensure you're using exact terminology")
        report.append("3. **Quantify your achievements** with numbers and metrics")
        report.append("4. **Tailor your summary** to include top missing keywords")
        report.append("5. **Test your resume** with different ATS systems if possible")
        
        return "\n".join(report)