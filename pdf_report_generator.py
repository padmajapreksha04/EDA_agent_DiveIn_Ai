from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from datetime import datetime
import io

class PDFReportGenerator:
    def __init__(self, data, eda_analyzer):
        self.data = data
        self.eda = eda_analyzer
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='TheoryText',
            parent=self.styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        ))
    
    def generate_report(self):
        """Generate comprehensive PDF report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        story = []
        
        # Title Page
        story.append(Paragraph("Exploratory Data Analysis Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y %H:%M')}", 
                              self.styles['Normal']))
        story.append(Spacer(1, 12))
        story.append(Paragraph("DiveIn AI - Executive Research Companion", 
                              self.styles['Normal']))
        story.append(PageBreak())
        
        # Table of Contents
        story.append(Paragraph("Table of Contents", self.styles['CustomHeading']))
        toc_items = [
            "1. Executive Summary",
            "2. Theoretical Background",
            "3. Dataset Overview",
            "4. Statistical Analysis",
            "5. Missing Values Analysis",
            "6. Outlier Detection",
            "7. Correlation Analysis",
            "8. Conclusions and Recommendations"
        ]
        for item in toc_items:
            story.append(Paragraph(item, self.styles['Normal']))
            story.append(Spacer(1, 6))
        story.append(PageBreak())
        
        # 1. Executive Summary
        story.extend(self._add_executive_summary())
        
        # 2. Theoretical Background
        story.extend(self._add_theoretical_background())
        
        # 3. Dataset Overview
        story.extend(self._add_dataset_overview())
        
        # 4. Statistical Analysis
        story.extend(self._add_statistical_analysis())
        
        # 5. Missing Values Analysis
        story.extend(self._add_missing_values_analysis())
        
        # 6. Outlier Detection
        story.extend(self._add_outlier_analysis())
        
        # 7. Correlation Analysis
        story.extend(self._add_correlation_analysis())
        
        # 8. Conclusions
        story.extend(self._add_conclusions())
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _add_executive_summary(self):
        """Add executive summary section"""
        content = []
        content.append(Paragraph("1. Executive Summary", self.styles['CustomHeading']))
        
        info = self.eda.get_basic_info()
        summary_text = f"""
        This report presents a comprehensive exploratory data analysis of the dataset containing 
        {info['shape'][0]:,} observations across {info['shape'][1]} variables. The analysis reveals 
        key patterns, distributions, and relationships within the data, providing actionable insights 
        for data-driven decision making.
        """
        content.append(Paragraph(summary_text, self.styles['TheoryText']))
        content.append(Spacer(1, 12))
        content.append(PageBreak())
        return content
    
    def _add_theoretical_background(self):
        """Add theoretical background section"""
        content = []
        content.append(Paragraph("2. Theoretical Background", self.styles['CustomHeading']))
        
        theory_sections = [
            {
                'title': '2.1 Exploratory Data Analysis (EDA)',
                'text': """
                Exploratory Data Analysis is an approach to analyzing datasets to summarize their main 
                characteristics using statistical graphics and other data visualization methods. Pioneered 
                by statistician John Tukey in the 1970s, EDA emphasizes the use of visual methods to 
                understand data patterns, spot anomalies, test hypotheses, and check assumptions before 
                formal modeling.
                """
            },
            {
                'title': '2.2 Descriptive Statistics',
                'text': """
                Descriptive statistics provide simple summaries about the sample and measures of the data. 
                Key measures include central tendency (mean, median, mode), dispersion (variance, standard 
                deviation, range), and shape (skewness, kurtosis). These statistics form the foundation 
                for understanding data distribution and variability.
                """
            },
            {
                'title': '2.3 Outlier Detection',
                'text': """
                Outliers are data points that differ significantly from other observations. The Interquartile 
                Range (IQR) method is a robust statistical technique for outlier detection. Values falling 
                below Q1 - 1.5×IQR or above Q3 + 1.5×IQR are considered potential outliers. Identifying 
                outliers is crucial as they can significantly impact statistical analyses and model performance.
                """
            },
            {
                'title': '2.4 Correlation Analysis',
                'text': """
                Correlation measures the strength and direction of the linear relationship between two 
                variables. The Pearson correlation coefficient ranges from -1 to +1, where values close to 
                ±1 indicate strong relationships and values near 0 suggest weak relationships. Understanding 
                correlations helps identify multicollinearity and feature relationships for predictive modeling.
                """
            }
        ]
        
        for section in theory_sections:
            content.append(Paragraph(section['title'], self.styles['Heading3']))
            content.append(Paragraph(section['text'], self.styles['TheoryText']))
            content.append(Spacer(1, 12))
        
        content.append(PageBreak())
        return content
    
    def _add_dataset_overview(self):
        """Add dataset overview section"""
        content = []
        content.append(Paragraph("3. Dataset Overview", self.styles['CustomHeading']))
        
        info = self.eda.get_basic_info()
        
        overview_data = [
            ['Metric', 'Value'],
            ['Number of Observations', f"{info['shape'][0]:,}"],
            ['Number of Variables', str(info['shape'][1])],
            ['Numeric Columns', str(len(self.eda.numeric_cols))],
            ['Categorical Columns', str(len(self.eda.categorical_cols))],
            ['Duplicate Rows', str(info['duplicates'])],
            ['Memory Usage', f"{info['memory_usage']:.2f} MB"]
        ]
        
        table = Table(overview_data, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        content.append(table)
        content.append(Spacer(1, 20))
        
        # Column Information
        content.append(Paragraph("3.1 Column Information", self.styles['Heading3']))
        col_text = f"The dataset contains {len(self.eda.numeric_cols)} numeric variables and {len(self.eda.categorical_cols)} categorical variables."
        content.append(Paragraph(col_text, self.styles['TheoryText']))
        content.append(Spacer(1, 12))
        content.append(PageBreak())
        
        return content
    
    def _add_statistical_analysis(self):
        """Add statistical analysis section"""
        content = []
        content.append(Paragraph("4. Statistical Analysis", self.styles['CustomHeading']))
        
        theory_text = """
        Statistical analysis provides quantitative measures of central tendency, dispersion, and shape 
        of the dataset's distribution. These measures are essential for understanding the underlying 
        patterns and characteristics of the data.
        """
        content.append(Paragraph(theory_text, self.styles['TheoryText']))
        content.append(Spacer(1, 12))
        
        if len(self.eda.numeric_cols) > 0:
            summary = self.eda.get_statistical_summary()
            
            # Convert summary to table format
            summary_data = [['Statistic'] + self.eda.numeric_cols[:5]]  # Limit to 5 columns for space
            
            for stat in ['mean', 'std', 'min', '25%', '50%', '75%', 'max']:
                if stat in summary.index:
                    row = [stat.capitalize()]
                    for col in self.eda.numeric_cols[:5]:
                        value = summary.loc[stat, col]
                        row.append(f"{value:.2f}")
                    summary_data.append(row)
            
            table = Table(summary_data, colWidths=[1.2*inch] + [1*inch]*min(5, len(self.eda.numeric_cols)))
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            
            content.append(table)
            content.append(Spacer(1, 12))
        else:
            content.append(Paragraph("No numeric columns available for statistical analysis.", 
                                   self.styles['Normal']))
        
        content.append(PageBreak())
        return content
    
    def _add_missing_values_analysis(self):
        """Add missing values analysis section"""
        content = []
        content.append(Paragraph("5. Missing Values Analysis", self.styles['CustomHeading']))
        
        theory_text = """
        Missing data is a common issue in real-world datasets. Understanding the pattern and extent of 
        missing values is crucial for data quality assessment and determining appropriate imputation 
        strategies. Missing data can occur randomly (MAR), completely at random (MCAR), or not at random (MNAR).
        """
        content.append(Paragraph(theory_text, self.styles['TheoryText']))
        content.append(Spacer(1, 12))
        
        info = self.eda.get_basic_info()
        missing_data = []
        
        for col, missing_count in info['missing_values'].items():
            if missing_count > 0:
                missing_pct = info['missing_percentage'][col]
                missing_data.append([col, str(missing_count), f"{missing_pct:.2f}%"])
        
        if missing_data:
            missing_data.insert(0, ['Column', 'Missing Count', 'Percentage'])
            table = Table(missing_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            content.append(table)
        else:
            content.append(Paragraph("✓ No missing values detected in the dataset.", 
                                   self.styles['Normal']))
        
        content.append(Spacer(1, 12))
        content.append(PageBreak())
        return content
    
    def _add_outlier_analysis(self):
        """Add outlier analysis section"""
        content = []
        content.append(Paragraph("6. Outlier Detection", self.styles['CustomHeading']))
        
        theory_text = """
        Outliers are observations that deviate significantly from the overall pattern of the data. 
        The Interquartile Range (IQR) method defines outliers as values that fall below Q1 - 1.5×IQR 
        or above Q3 + 1.5×IQR. These points may represent data errors, rare events, or genuinely 
        extreme values that require special attention.
        """
        content.append(Paragraph(theory_text, self.styles['TheoryText']))
        content.append(Spacer(1, 12))
        
        if len(self.eda.numeric_cols) > 0:
            outliers_info = self.eda.detect_outliers()
            
            outlier_data = [['Column', 'Outlier Count', 'Percentage']]
            for col, info in list(outliers_info.items())[:10]:  # Limit to 10 columns
                outlier_data.append([
                    col,
                    str(info['count']),
                    f"{info['percentage']:.2f}%"
                ])
            
            table = Table(outlier_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f39c12')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            
            content.append(table)
        else:
            content.append(Paragraph("No numeric columns available for outlier analysis.", 
                                   self.styles['Normal']))
        
        content.append(Spacer(1, 12))
        content.append(PageBreak())
        return content
    
    def _add_correlation_analysis(self):
        """Add correlation analysis section"""
        content = []
        content.append(Paragraph("7. Correlation Analysis", self.styles['CustomHeading']))
        
        theory_text = """
        Correlation analysis examines the strength and direction of relationships between variables. 
        The Pearson correlation coefficient (r) ranges from -1 (perfect negative correlation) to +1 
        (perfect positive correlation), with 0 indicating no linear relationship. Strong correlations 
        (|r| > 0.7) may indicate multicollinearity in predictive modeling contexts.
        """
        content.append(Paragraph(theory_text, self.styles['TheoryText']))
        content.append(Spacer(1, 12))
        
        if len(self.eda.numeric_cols) > 1:
            corr_matrix = self.eda.get_correlation_matrix()
            
            # Find top correlations
            content.append(Paragraph("7.1 Strong Correlations", self.styles['Heading3']))
            
            # Get correlation pairs
            correlations = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    col1 = corr_matrix.columns[i]
                    col2 = corr_matrix.columns[j]
                    corr_value = corr_matrix.iloc[i, j]
                    if abs(corr_value) > 0.5:  # Only strong correlations
                        correlations.append((col1, col2, corr_value))
            
            # Sort by absolute correlation
            correlations.sort(key=lambda x: abs(x[2]), reverse=True)
            
            if correlations[:10]:  # Top 10
                corr_data = [['Variable 1', 'Variable 2', 'Correlation']]
                for col1, col2, corr_val in correlations[:10]:
                    corr_data.append([col1, col2, f"{corr_val:.3f}"])
                
                table = Table(corr_data, colWidths=[2*inch, 2*inch, 1.5*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                ]))
                
                content.append(table)
            else:
                content.append(Paragraph("No strong correlations (|r| > 0.5) detected.", 
                                       self.styles['Normal']))
        else:
            content.append(Paragraph("Insufficient numeric columns for correlation analysis.", 
                                   self.styles['Normal']))
        
        content.append(Spacer(1, 12))
        content.append(PageBreak())
        return content
    
    def _add_conclusions(self):
        """Add conclusions section"""
        content = []
        content.append(Paragraph("8. Conclusions and Recommendations", self.styles['CustomHeading']))
        
        info = self.eda.get_basic_info()
        
        # Data Quality Assessment
        content.append(Paragraph("8.1 Data Quality Assessment", self.styles['Heading3']))
        
        missing_total = sum(1 for v in info['missing_values'].values() if v > 0)
        quality_text = f"""
        The dataset demonstrates {'good' if missing_total < len(self.data.columns) * 0.2 else 'moderate'} 
        data quality with {missing_total} columns containing missing values out of {len(self.data.columns)} 
        total variables. The dataset contains {info['duplicates']} duplicate rows which {'should be addressed' if info['duplicates'] > 0 else 'indicates good data integrity'}.
        """
        content.append(Paragraph(quality_text, self.styles['TheoryText']))
        content.append(Spacer(1, 12))
        
        # Recommendations
        content.append(Paragraph("8.2 Recommendations", self.styles['Heading3']))
        
        # Continuing from previous section...

        recommendations = [
            "1. <b>Missing Data Treatment:</b> Consider appropriate imputation methods (mean/median for numeric, mode for categorical) or removal strategies based on the missing data mechanism.",
            "2. <b>Outlier Handling:</b> Investigate outliers to determine if they are genuine extreme values or data errors. Consider robust statistical methods or transformation techniques.",
            "3. <b>Feature Engineering:</b> Leverage correlation insights to create derived features or reduce multicollinearity through feature selection.",
            "4. <b>Data Transformation:</b> For skewed distributions, consider logarithmic or Box-Cox transformations to improve normality.",
            "5. <b>Further Analysis:</b> Conduct domain-specific analysis and hypothesis testing based on the insights from this exploratory analysis."
        ]
        
        for rec in recommendations:
            content.append(Paragraph(rec, self.styles['TheoryText']))
            content.append(Spacer(1, 8))
        
        content.append(Spacer(1, 12))
        
        # Footer
        footer_text = f"""
        <i>This report was automatically generated by DiveIn AI - Executive Research Companion. 
        For more information, visit Pace University Data Science Program.</i>
        """
        content.append(Paragraph(footer_text, self.styles['Normal']))
        
        return content

