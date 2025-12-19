"""
Advanced Research Agent with Multi-Step Analysis
Conducts comprehensive research like a professional analyst
"""

import google.generativeai as genai
from typing import List, Dict
import json
from datetime import datetime
import re
# Import at the top of your file

class ResearchAgent:
    """Deep research agent with multi-step comprehensive analysis"""
    
    def __init__(self, model, search_tool):
        self.model = model
        self.search_tool = search_tool
        self.research_history = []
    
    def conduct_research(self, query: str) -> str:
        """
        Multi-step research process:
        1. Decompose query into sub-questions
        2. Research each aspect
        3. Synthesize findings
        4. Generate comprehensive report
        """
        
        # Step 1: Break down the query
        sub_questions = self._decompose_query(query)
        
        # Step 2: Research each sub-question
        findings = []
        for question in sub_questions:
            result = self._research_single_question(question)
            findings.append(result)
        
        # Step 3: Synthesize all findings
        final_report = self._synthesize_report(query, sub_questions, findings)
        
        return final_report
    
    def _decompose_query(self, query: str) -> List[str]:
        """Break down complex query into specific research questions"""
        
        prompt = f"""You are a research analyst. Break down this topic into 4-5 specific research questions.

Topic: "{query}"

Create questions that cover:
1. Background and history
2. Key facts and statistics
3. Current developments
4. Impact and significance
5. Related topics or future outlook

Provide ONLY the questions, one per line, numbered 1-5:"""
        
        try:
            response = self.model.generate_content(prompt)
            # Extract questions
            questions = []
            for line in response.text.split('\n'):
                # Match numbered questions
                match = re.match(r'\d+[\.\)]\s*(.+)', line.strip())
                if match:
                    questions.append(match.group(1))
            
            return questions[:5] if questions else [query]
        except:
            return [query]  # Fallback to original query
    
    def _research_single_question(self, question: str) -> Dict:
        """Research a specific question using web search"""
        
        try:
            # Perform web search
            search_results = self.search_tool.func(question)
            
            # Analyze and extract key information
            analysis_prompt = f"""Analyze these search results for: "{question}"

Search Results:
{search_results}

Extract and summarize:
1. Key facts and figures
2. Important dates or events
3. Notable sources or experts
4. Relevant statistics

Provide a clear, factual summary:"""
            
            analysis = self.model.generate_content(analysis_prompt)
            
            return {
                'question': question,
                'findings': analysis.text,
                'sources': 'Web search results'
            }
        except Exception as e:
            return {
                'question': question,
                'findings': f'Could not retrieve information: {str(e)}',
                'sources': 'N/A'
            }
    
    def _synthesize_report(self, original_query: str, questions: List[str], findings: List[Dict]) -> str:
        """Synthesize all findings into a comprehensive research report"""
        
        # Combine all findings
        combined_findings = "\n\n".join([
            f"**Research Area {i+1}:** {f['question']}\n{f['findings']}"
            for i, f in enumerate(findings)
        ])
        
        synthesis_prompt = f"""You are a professional research analyst creating a comprehensive report.

Original Topic: "{original_query}"

Research Findings:
{combined_findings}

Create a well-structured research report with:

# {original_query}

## Executive Summary
[2-3 sentence overview]

## Background
[Historical context and origins]

## Key Findings
[Main facts, statistics, and developments organized by themes]

## Analysis
[Significance, impact, and implications]

## Current Status
[Latest developments and current state]

## Conclusion
[Summary of key points]

---
*Research completed on {datetime.now().strftime('%B %d, %Y')}*

Write in a professional, academic tone with specific facts and details:"""
        
        try:
            final_report = self.model.generate_content(synthesis_prompt)
            return final_report.text
        except Exception as e:
            return f"Error generating report: {str(e)}"


class MLQueryAnalyzer:
    """ML-based query understanding and classification"""
    
    def __init__(self, model):
        self.model = model
    
    def analyze_query_intent(self, query: str) -> Dict:
        """Classify query type and determine research strategy"""
        
        analysis_prompt = f"""Analyze this query and classify it:

Query: "{query}"

Classify:
1. Type: [factual/analytical/comparative/historical/technical]
2. Complexity: [simple/moderate/complex]
3. Depth Required: [quick answer/detailed research/comprehensive analysis]

Respond in this exact format:
Type: [your answer]
Complexity: [your answer]
Depth: [your answer]"""
        
        try:
            response = self.model.generate_content(analysis_prompt)
            text = response.text
            
            # Parse response
            query_type = 'analytical'
            complexity = 'moderate'
            depth = 'detailed research'
            
            if 'Type:' in text:
                query_type = text.split('Type:')[1].split('\n')[0].strip()
            if 'Complexity:' in text:
                complexity = text.split('Complexity:')[1].split('\n')[0].strip()
            if 'Depth:' in text:
                depth = text.split('Depth:')[1].split('\n')[0].strip()
            
            return {
                'query_type': query_type,
                'complexity': complexity,
                'depth': depth
            }
        except:
            return {
                'query_type': 'analytical',
                'complexity': 'moderate',
                'depth': 'detailed research'
            }
class CitationTracker:
    """Track and manage citations in research"""
    
    def __init__(self):
        self.citations = []
        self.citation_count = 0
    
    def add_citation(self, source: str, url: str = None, snippet: str = None):
        """Add a citation"""
        self.citation_count += 1
        citation = {
            'id': self.citation_count,
            'source': source,
            'url': url,
            'snippet': snippet,
            'timestamp': datetime.now().isoformat()
        }
        self.citations.append(citation)
        return self.citation_count
    
    def get_citation_text(self, citation_id: int) -> str:
        """Get formatted citation text"""
        for cit in self.citations:
            if cit['id'] == citation_id:
                text = f"[{cit['id']}] {cit['source']}"
                if cit['url']:
                    text += f"\n    URL: {cit['url']}"
                return text
        return ""
    
    def format_bibliography(self) -> str:
        """Format all citations as bibliography"""
        if not self.citations:
            return ""
        
        bib = "\n## References\n\n"
        for cit in self.citations:
            bib += f"[{cit['id']}] {cit['source']}"
            if cit['url']:
                bib += f"\n    {cit['url']}"
            bib += "\n\n"
        
        return bib

