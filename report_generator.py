"""
Report Generation Module
Exports research reports in PDF, DOCX, and Markdown formats
"""

import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import re


class ReportGenerator:
    """Generate professional research reports in multiple formats"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles for PDF generation"""
        if 'CustomTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1e88e5'),
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            ))
        
        if 'CustomSubtitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomSubtitle',
                parent=self.styles['Normal'],
                fontSize=14,
                textColor=colors.HexColor('#666666'),
                spaceAfter=20,
                alignment=TA_CENTER,
                fontName='Helvetica-Oblique'
            ))
        
        if 'SectionHeading' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SectionHeading',
                parent=self.styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#2196f3'),
                spaceAfter=12,
                spaceBefore=12,
                fontName='Helvetica-Bold'
            ))
        
        if 'CustomBodyText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomBodyText',
                parent=self.styles['Normal'],
                fontSize=11,
                alignment=TA_JUSTIFY,
                spaceAfter=12,
                leading=14
            ))
    
    def _clean_text(self, text):
        """Clean text for PDF generation (remove markdown, special chars)"""
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^\*]+)\*', r'\1', text)
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        return text
    
    def _parse_report_sections(self, report_text):
        """Parse report text into structured sections"""
        sections = []
        current_section = None
        current_content = []
        
        lines = report_text.split('\n')
        
        for line in lines:
            if line.strip().startswith('##'):
                if current_section:
                    sections.append({
                        'title': current_section,
                        'content': '\n'.join(current_content).strip()
                    })
                current_section = line.strip().replace('#', '').strip()
                current_content = []
            else:
                if line.strip():
                    current_content.append(line.strip())
        
        if current_section:
            sections.append({
                'title': current_section,
                'content': '\n'.join(current_content).strip()
            })
        
        return sections
    
    def generate_pdf(self, query, report_text, metadata=None):
        """Generate PDF report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        story = []
        
        title = Paragraph(f"Research Report: {query}", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        if metadata:
            date_str = metadata.get('date', datetime.now().strftime('%B %d, %Y'))
            subtitle = Paragraph(f"Generated on {date_str}", self.styles['CustomSubtitle'])
            story.append(subtitle)
            story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("Executive Summary", self.styles['SectionHeading']))
        story.append(Spacer(1, 0.1*inch))
        
        sections = self._parse_report_sections(report_text)
        
        for section in sections:
            story.append(Paragraph(section['title'], self.styles['SectionHeading']))
            story.append(Spacer(1, 0.1*inch))
            
            cleaned_content = self._clean_text(section['content'])
            paragraphs = cleaned_content.split('\n\n')
            
            for para in paragraphs:
                if para.strip():
                    p = Paragraph(para.strip(), self.styles['CustomBodyText'])
                    story.append(p)
                    story.append(Spacer(1, 0.1*inch))
            
            story.append(Spacer(1, 0.2*inch))
        
        story.append(Spacer(1, 0.5*inch))
        footer_style = ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        footer = Paragraph(
            "Generated by DiveIn AI Research Assistant | Built with Google Gemini API",
            footer_style
        )
        story.append(footer)
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_docx(self, query, report_text, metadata=None):
        """Generate DOCX report"""
        doc = Document()
        
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Calibri'
        font.size = Pt(11)
        
        title = doc.add_heading(f"Research Report: {query}", level=0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_run = title.runs[0]
        title_run.font.color.rgb = RGBColor(30, 136, 229)
        
        if metadata:
            date_str = metadata.get('date', datetime.now().strftime('%B %d, %Y'))
            subtitle = doc.add_paragraph(f"Generated on {date_str}")
            subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
            subtitle_run = subtitle.runs[0]
            subtitle_run.italic = True
            subtitle_run.font.color.rgb = RGBColor(128, 128, 128)
        
        doc.add_paragraph()
        doc.add_heading("Executive Summary", level=1)
        
        sections = self._parse_report_sections(report_text)
        
        for section in sections:
            heading = doc.add_heading(section['title'], level=2)
            heading_run = heading.runs[0]
            heading_run.font.color.rgb = RGBColor(33, 150, 243)
            
            cleaned_content = self._clean_text(section['content'])
            paragraphs = cleaned_content.split('\n\n')
            
            for para in paragraphs:
                if para.strip():
                    p = doc.add_paragraph(para.strip())
                    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        
        doc.add_paragraph()
        footer = doc.add_paragraph(
            "Generated by DiveIn AI Research Assistant | Built with Google Gemini API"
        )
        footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        footer_run = footer.runs[0]
        footer_run.font.size = Pt(9)
        footer_run.font.color.rgb = RGBColor(128, 128, 128)
        
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer
    
    def generate_markdown(self, query, report_text, metadata=None):
        """Generate Markdown report"""
        md_content = []
        
        md_content.append(f"# Research Report: {query}\n")
        
        if metadata:
            date_str = metadata.get('date', datetime.now().strftime('%B %d, %Y'))
            md_content.append(f"*Generated on {date_str}*\n")
        
        md_content.append("---\n")
        md_content.append("## Executive Summary\n")
        md_content.append(report_text)
        md_content.append("\n---\n")
        md_content.append("*Generated by DiveIn AI Research Assistant | Built with Google Gemini API*\n")
        
        return '\n'.join(md_content)


def create_download_button(report_generator, query, report_text, format_type='pdf'):
    """
    Helper function to create download buttons in Streamlit
    
    Args:
        report_generator: ReportGenerator instance
        query: Research query string
        report_text: Generated report content
        format_type: 'pdf', 'docx', or 'md'
    
    Returns:
        tuple: (file_data, file_name, mime_type)
    """
    metadata = {'date': datetime.now().strftime('%B %d, %Y')}
    
    if format_type == 'pdf':
        buffer = report_generator.generate_pdf(query, report_text, metadata)
        file_name = f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        mime_type = "application/pdf"
        return buffer.getvalue(), file_name, mime_type
    
    elif format_type == 'docx':
        buffer = report_generator.generate_docx(query, report_text, metadata)
        file_name = f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        return buffer.getvalue(), file_name, mime_type
    
    elif format_type == 'md':
        md_content = report_generator.generate_markdown(query, report_text, metadata)
        file_name = f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        mime_type = "text/markdown"
        return md_content.encode('utf-8'), file_name, mime_type
    
    else:
        raise ValueError(f"Unsupported format: {format_type}")
