#!/usr/bin/env python3
"""
Demo script for Resume Keyword Optimizer
Demonstrates the tool's capabilities with sample data
"""

import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from resume_optimizer import ResumeKeywordOptimizer
from file_processors import FileProcessor
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

console = Console()

def run_demo():
    """Run a demonstration of the Resume Keyword Optimizer"""
    
    # Welcome message
    welcome_text = """
🎯 [bold blue]Resume Keyword Optimizer Demo[/bold blue]

This demo will analyze a sample resume against a sample job description
to show you how the tool works and what insights it provides.

Sample scenario:
• Resume: Software Engineer with 5 years experience
• Job: Senior Full Stack Developer position at a fintech company

Let's see how well the resume matches the job requirements!
    """
    
    console.print(Panel(welcome_text, title="Demo", border_style="blue"))
    
    # Initialize components
    console.print("\n🔧 [bold]Initializing Resume Keyword Optimizer...[/bold]")
    optimizer = ResumeKeywordOptimizer()
    file_processor = FileProcessor()
    
    # Load sample files
    console.print("📁 [bold]Loading sample resume and job description...[/bold]")
    
    try:
        # Load sample resume
        with open("sample_resume.txt", "r", encoding="utf-8") as f:
            resume_text = f.read()
        
        # Load sample job description
        with open("sample_job_description.txt", "r", encoding="utf-8") as f:
            job_description = f.read()
        
        console.print("✅ Sample files loaded successfully!")
        
    except FileNotFoundError as e:
        console.print(f"[red]Error: Sample file not found: {e}[/red]")
        console.print("Please make sure sample_resume.txt and sample_job_description.txt exist.")
        return
    
    # Run analysis
    console.print("\n🧠 [bold]Analyzing resume against job description...[/bold]")
    
    try:
        result = optimizer.analyze_resume_against_job(resume_text, job_description)
        console.print("✅ Analysis complete!")
        
        # Display results summary
        display_demo_results(result)
        
        # Generate full report
        console.print("\n📄 [bold]Generating detailed report...[/bold]")
        report = optimizer.generate_keyword_report(result)
        
        # Save report
        report_filename = "demo_analysis_report.txt"
        with open(report_filename, "w", encoding="utf-8") as f:
            f.write(report)
        
        console.print(f"✅ Detailed report saved to: [green]{report_filename}[/green]")
        
        # Show next steps
        show_next_steps()
        
    except Exception as e:
        console.print(f"[red]Error during analysis: {e}[/red]")
        return

def display_demo_results(result):
    """Display a summary of demo results"""
    
    console.print("\n" + "="*60)
    console.print("📊 [bold blue]DEMO ANALYSIS RESULTS[/bold blue]", justify="center")
    console.print("="*60)
    
    # Score overview table
    score_table = Table(title="📈 Score Overview", show_header=True, header_style="bold magenta")
    score_table.add_column("Metric", style="cyan", no_wrap=True)
    score_table.add_column("Score", justify="right")
    score_table.add_column("Interpretation", justify="center")
    
    # Add scores
    overall_status = get_score_status(result.overall_score)
    ats_status = get_score_status(result.ats_score)
    
    score_table.add_row("Overall Match", f"{result.overall_score}%", overall_status)
    score_table.add_row("ATS Compatibility", f"{result.ats_score}%", ats_status)
    score_table.add_row("Readability", f"{result.readability_score:.1f}", "📖 Good" if result.readability_score > 60 else "📖 Needs Work")
    score_table.add_row("Keyword Density", f"{result.keyword_density}%", "🎯 Good" if 1 <= result.keyword_density <= 3 else "⚠️ Adjust")
    
    console.print(score_table)
    
    # Top missing keywords
    if result.missing_keywords:
        console.print(f"\n❌ [bold red]Top Missing Keywords ({len(result.missing_keywords)} total):[/bold red]")
        for i, kw in enumerate(result.missing_keywords[:5], 1):
            impact = get_impact_indicator(kw.importance_score)
            console.print(f"  {i}. [white]{kw.keyword}[/white] ({kw.keyword_type.value.replace('_', ' ').title()}) - {impact}")
    
    # Top matched keywords
    if result.matched_keywords:
        console.print(f"\n✅ [bold green]Top Matched Keywords ({len(result.matched_keywords)} total):[/bold green]")
        for i, kw in enumerate(result.matched_keywords[:5], 1):
            freq = f"({kw.resume_frequency}x)" if kw.resume_frequency > 1 else ""
            console.print(f"  {i}. [white]{kw.keyword}[/white] {freq}")
    
    # Key suggestions
    if result.suggestions:
        console.print(f"\n💡 [bold yellow]Key Optimization Suggestions:[/bold yellow]")
        for i, suggestion in enumerate(result.suggestions[:3], 1):
            console.print(f"  {i}. {suggestion}")

def get_score_status(score):
    """Get status emoji/text for score"""
    if score >= 80:
        return "🌟 Excellent"
    elif score >= 60:
        return "👍 Good"
    elif score >= 40:
        return "⚠️ Needs Work"
    else:
        return "🚨 Poor"

def get_impact_indicator(score):
    """Get impact indicator for keyword importance"""
    if score > 0.1:
        return "🔴 Critical"
    elif score > 0.05:
        return "🟡 Important"
    else:
        return "⚪ Moderate"

def show_next_steps():
    """Show next steps for using the tool"""
    
    next_steps = """
🚀 [bold blue]Next Steps - Try It Yourself![/bold blue]

Now that you've seen the demo, here's how to use the tool with your own resume:

[bold yellow]1. Web Interface (Easiest):[/bold yellow]
   streamlit run web_app.py
   Then open http://localhost:8501 in your browser

[bold yellow]2. Command Line Interface:[/bold yellow]
   python cli.py --resume your_resume.pdf --job job_description.txt

[bold yellow]3. Interactive Mode:[/bold yellow]
   python cli.py
   Follow the prompts to upload your files

[bold yellow]Supported File Formats:[/bold yellow]
   • Resume: PDF, DOCX, TXT
   • Job Description: TXT, or paste directly

[bold yellow]Pro Tips:[/bold yellow]
   • Use exact keywords from job descriptions
   • Aim for 60-80% ATS compatibility score
   • Focus on the "Critical" missing keywords first
   • Keep keyword density between 1-3%

Happy job hunting! 🎯
    """
    
    console.print(Panel(next_steps, title="What's Next?", border_style="green"))

if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")