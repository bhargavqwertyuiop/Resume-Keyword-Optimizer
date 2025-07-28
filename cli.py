#!/usr/bin/env python3
"""
Resume Keyword Optimizer - Command Line Interface
A tool to analyze resumes against job descriptions and provide optimization suggestions.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional
import json

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.layout import Layout
from rich.columns import Columns
from rich import print as rprint

from resume_optimizer import ResumeKeywordOptimizer, OptimizationResult
from file_processors import FileProcessor

console = Console()

class ResumeOptimizerCLI:
    def __init__(self):
        self.optimizer = ResumeKeywordOptimizer()
        self.file_processor = FileProcessor()
        
    def main(self):
        """Main CLI entry point"""
        parser = self.create_parser()
        args = parser.parse_args()
        
        if len(sys.argv) == 1:
            # No arguments provided, run interactive mode
            self.interactive_mode()
        else:
            # Run with command line arguments
            self.run_with_args(args)
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create command line argument parser"""
        parser = argparse.ArgumentParser(
            description="Resume Keyword Optimizer - Analyze and optimize your resume for ATS systems",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s --resume resume.pdf --job job_description.txt
  %(prog)s --resume resume.docx --job-text "Software Engineer with Python experience..."
  %(prog)s --interactive
            """
        )
        
        parser.add_argument(
            '--resume', '-r',
            type=str,
            help='Path to resume file (PDF, DOCX, or TXT)'
        )
        
        parser.add_argument(
            '--job', '-j',
            type=str,
            help='Path to job description file (TXT)'
        )
        
        parser.add_argument(
            '--job-text', '-jt',
            type=str,
            help='Job description as text (alternative to --job)'
        )
        
        parser.add_argument(
            '--output', '-o',
            type=str,
            help='Output file for the analysis report (optional)'
        )
        
        parser.add_argument(
            '--format', '-f',
            choices=['text', 'json'],
            default='text',
            help='Output format (default: text)'
        )
        
        parser.add_argument(
            '--interactive', '-i',
            action='store_true',
            help='Run in interactive mode'
        )
        
        parser.add_argument(
            '--verbose', '-v',
            action='store_true',
            help='Verbose output'
        )
        
        return parser
    
    def interactive_mode(self):
        """Run the tool in interactive mode"""
        self.show_welcome()
        
        # Get resume file
        resume_path = self.get_resume_file()
        if not resume_path:
            return
        
        # Get job description
        job_description = self.get_job_description()
        if not job_description:
            return
        
        # Run analysis
        result = self.run_analysis(resume_path, job_description)
        if result:
            self.display_results(result)
            self.offer_save_report(result)
    
    def run_with_args(self, args):
        """Run analysis with command line arguments"""
        # Validate arguments
        if not args.resume:
            console.print("[red]Error: Resume file is required[/red]")
            return False
        
        if not args.job and not args.job_text:
            console.print("[red]Error: Job description is required (--job or --job-text)[/red]")
            return False
        
        # Get job description
        if args.job:
            try:
                with open(args.job, 'r', encoding='utf-8') as f:
                    job_description = f.read()
            except Exception as e:
                console.print(f"[red]Error reading job description file: {e}[/red]")
                return False
        else:
            job_description = args.job_text
        
        # Run analysis
        result = self.run_analysis(args.resume, job_description, verbose=args.verbose)
        if result:
            if args.format == 'json':
                self.output_json(result, args.output)
            else:
                self.display_results(result)
                if args.output:
                    self.save_report(result, args.output)
        
        return True
    
    def show_welcome(self):
        """Display welcome message"""
        welcome_text = """
🎯 [bold blue]Resume Keyword Optimizer[/bold blue]

This tool analyzes your resume against job descriptions to:
• Identify missing keywords that ATS systems look for
• Provide optimization suggestions
• Calculate your ATS compatibility score
• Highlight your existing strengths

Let's optimize your resume for better job application success!
        """
        
        console.print(Panel(welcome_text, title="Welcome", border_style="blue"))
    
    def get_resume_file(self) -> Optional[str]:
        """Get resume file from user"""
        while True:
            file_path = Prompt.ask("\n📄 Enter path to your resume file (PDF, DOCX, or TXT)")
            
            if not file_path:
                if Confirm.ask("Exit the application?"):
                    return None
                continue
            
            # Expand user path and resolve relative paths
            file_path = os.path.expanduser(file_path)
            file_path = os.path.abspath(file_path)
            
            if not os.path.exists(file_path):
                console.print(f"[red]File not found: {file_path}[/red]")
                continue
            
            # Check file extension
            ext = Path(file_path).suffix.lower()
            if ext not in ['.pdf', '.docx', '.doc', '.txt']:
                console.print(f"[red]Unsupported file format: {ext}[/red]")
                console.print("Supported formats: PDF, DOCX, TXT")
                continue
            
            return file_path
    
    def get_job_description(self) -> Optional[str]:
        """Get job description from user"""
        console.print("\n💼 How would you like to provide the job description?")
        console.print("1. Paste text directly")
        console.print("2. Load from file")
        
        choice = Prompt.ask("Choose option", choices=["1", "2"], default="1")
        
        if choice == "1":
            console.print("\n📝 Paste the job description below (press Ctrl+D when finished):")
            lines = []
            try:
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                pass
            
            job_description = '\n'.join(lines).strip()
            if not job_description:
                console.print("[red]No job description provided[/red]")
                return None
            
            return job_description
        
        else:
            while True:
                file_path = Prompt.ask("📁 Enter path to job description file")
                
                if not file_path:
                    return None
                
                file_path = os.path.expanduser(file_path)
                file_path = os.path.abspath(file_path)
                
                if not os.path.exists(file_path):
                    console.print(f"[red]File not found: {file_path}[/red]")
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return f.read()
                except Exception as e:
                    console.print(f"[red]Error reading file: {e}[/red]")
                    continue
    
    def run_analysis(self, resume_path: str, job_description: str, verbose: bool = False) -> Optional[OptimizationResult]:
        """Run the resume analysis"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            # Extract resume text
            task = progress.add_task("📄 Extracting text from resume...", total=None)
            try:
                resume_text = self.file_processor.extract_text_from_file(resume_path)
                resume_text = self.file_processor.clean_extracted_text(resume_text)
                
                if not self.file_processor.validate_resume_content(resume_text):
                    console.print("[red]Warning: The file doesn't appear to contain a valid resume[/red]")
                    if not Confirm.ask("Continue anyway?"):
                        return None
                
            except Exception as e:
                console.print(f"[red]Error processing resume file: {e}[/red]")
                return None
            
            progress.update(task, description="🧠 Analyzing keywords and content...")
            
            # Run analysis
            try:
                result = self.optimizer.analyze_resume_against_job(resume_text, job_description)
                progress.update(task, description="✅ Analysis complete!")
                
                if verbose:
                    console.print(f"\n[dim]Resume length: {len(resume_text.split())} words[/dim]")
                    console.print(f"[dim]Job description length: {len(job_description.split())} words[/dim]")
                
                return result
                
            except Exception as e:
                console.print(f"[red]Error during analysis: {e}[/red]")
                return None
    
    def display_results(self, result: OptimizationResult):
        """Display analysis results in a formatted way"""
        console.print("\n" + "="*80)
        console.print("📊 [bold blue]RESUME ANALYSIS RESULTS[/bold blue]", justify="center")
        console.print("="*80)
        
        # Score overview
        self.display_score_overview(result)
        
        # Missing keywords
        if result.missing_keywords:
            self.display_missing_keywords(result)
        
        # Matched keywords
        if result.matched_keywords:
            self.display_matched_keywords(result)
        
        # Suggestions
        if result.suggestions:
            self.display_suggestions(result)
    
    def display_score_overview(self, result: OptimizationResult):
        """Display score overview table"""
        score_table = Table(title="📈 Score Overview", show_header=True, header_style="bold magenta")
        score_table.add_column("Metric", style="cyan", no_wrap=True)
        score_table.add_column("Score", justify="right")
        score_table.add_column("Status", justify="center")
        
        # Overall score
        overall_status = self.get_score_status(result.overall_score)
        score_table.add_row("Overall Match", f"{result.overall_score}%", overall_status)
        
        # ATS score
        ats_status = self.get_score_status(result.ats_score)
        score_table.add_row("ATS Compatibility", f"{result.ats_score}%", ats_status)
        
        # Readability
        readability_status = "📖 Good" if result.readability_score > 60 else "📖 Needs Work"
        score_table.add_row("Readability", f"{result.readability_score:.1f}", readability_status)
        
        # Keyword density
        density_status = "🎯 Good" if 1 <= result.keyword_density <= 3 else "⚠️ Adjust"
        score_table.add_row("Keyword Density", f"{result.keyword_density}%", density_status)
        
        console.print(score_table)
        console.print()
    
    def get_score_status(self, score: float) -> str:
        """Get status emoji/text for score"""
        if score >= 80:
            return "🌟 Excellent"
        elif score >= 60:
            return "👍 Good"
        elif score >= 40:
            return "⚠️ Needs Work"
        else:
            return "🚨 Poor"
    
    def display_missing_keywords(self, result: OptimizationResult):
        """Display missing keywords table"""
        missing_table = Table(title="❌ Missing Keywords (Top 10)", show_header=True, header_style="bold red")
        missing_table.add_column("#", justify="right", style="cyan", no_wrap=True)
        missing_table.add_column("Keyword", style="white")
        missing_table.add_column("Type", style="yellow")
        missing_table.add_column("Impact", justify="center")
        
        for i, kw in enumerate(result.missing_keywords[:10], 1):
            impact = self.get_impact_indicator(kw.importance_score)
            missing_table.add_row(
                str(i),
                kw.keyword,
                kw.keyword_type.value.replace('_', ' ').title(),
                impact
            )
        
        console.print(missing_table)
        console.print()
    
    def display_matched_keywords(self, result: OptimizationResult):
        """Display matched keywords table"""
        matched_table = Table(title="✅ Successfully Matched Keywords", show_header=True, header_style="bold green")
        matched_table.add_column("#", justify="right", style="cyan", no_wrap=True)
        matched_table.add_column("Keyword", style="white")
        matched_table.add_column("Frequency", justify="center", style="green")
        
        for i, kw in enumerate(result.matched_keywords[:5], 1):
            freq_text = f"{kw.resume_frequency}x" if kw.resume_frequency > 1 else "1x"
            matched_table.add_row(str(i), kw.keyword, freq_text)
        
        console.print(matched_table)
        console.print()
    
    def display_suggestions(self, result: OptimizationResult):
        """Display optimization suggestions"""
        suggestions_panel = Panel(
            "\n".join(f"{i}. {suggestion}" for i, suggestion in enumerate(result.suggestions, 1)),
            title="💡 Optimization Suggestions",
            border_style="yellow"
        )
        console.print(suggestions_panel)
        console.print()
    
    def get_impact_indicator(self, score: float) -> str:
        """Get impact indicator for keyword importance"""
        if score > 0.1:
            return "🔴 Critical"
        elif score > 0.05:
            return "🟡 Important"
        else:
            return "⚪ Moderate"
    
    def offer_save_report(self, result: OptimizationResult):
        """Offer to save the detailed report"""
        if Confirm.ask("\n💾 Would you like to save a detailed report?"):
            default_name = f"resume_analysis_{result.ats_score:.0f}pct.txt"
            filename = Prompt.ask("Enter filename", default=default_name)
            self.save_report(result, filename)
    
    def save_report(self, result: OptimizationResult, filename: str):
        """Save detailed report to file"""
        try:
            report = self.optimizer.generate_keyword_report(result)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            console.print(f"[green]✅ Report saved to {filename}[/green]")
        except Exception as e:
            console.print(f"[red]Error saving report: {e}[/red]")
    
    def output_json(self, result: OptimizationResult, output_file: Optional[str] = None):
        """Output results in JSON format"""
        # Convert result to JSON-serializable format
        data = {
            "overall_score": result.overall_score,
            "ats_score": result.ats_score,
            "readability_score": result.readability_score,
            "keyword_density": result.keyword_density,
            "missing_keywords": [
                {
                    "keyword": kw.keyword,
                    "type": kw.keyword_type.value,
                    "importance": kw.importance_score,
                    "job_frequency": kw.job_frequency
                }
                for kw in result.missing_keywords
            ],
            "matched_keywords": [
                {
                    "keyword": kw.keyword,
                    "type": kw.keyword_type.value,
                    "resume_frequency": kw.resume_frequency
                }
                for kw in result.matched_keywords
            ],
            "suggestions": result.suggestions
        }
        
        json_output = json.dumps(data, indent=2)
        
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(json_output)
                console.print(f"[green]✅ JSON report saved to {output_file}[/green]")
            except Exception as e:
                console.print(f"[red]Error saving JSON: {e}[/red]")
        else:
            console.print(json_output)

def main():
    """Main entry point"""
    cli = ResumeOptimizerCLI()
    cli.main()

if __name__ == "__main__":
    main()