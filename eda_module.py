import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import io
from datetime import datetime
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.preprocessing import LabelEncoder


class EDAAnalyzer:
    def __init__(self, data):
        """Initialize with uploaded data"""
        self.data = data
        self.numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = data.select_dtypes(include=['object']).columns.tolist()
        
    def get_basic_info(self):
        """Get basic dataset information"""
        info = {
            'shape': self.data.shape,
            'columns': self.data.columns.tolist(),
            'dtypes': self.data.dtypes.to_dict(),
            'missing_values': self.data.isnull().sum().to_dict(),
            'missing_percentage': (self.data.isnull().sum() / len(self.data) * 100).to_dict(),
            'duplicates': self.data.duplicated().sum(),
            'memory_usage': self.data.memory_usage(deep=True).sum() / 1024**2  # MB
        }
        return info
    
    def get_statistical_summary(self):
        """Get statistical summary for numeric columns"""
        if len(self.numeric_cols) > 0:
            return self.data[self.numeric_cols].describe()
        return pd.DataFrame()
    
    def detect_outliers(self):
        """Detect outliers using IQR method"""
        outliers_info = {}
        for col in self.numeric_cols:
            Q1 = self.data[col].quantile(0.25)
            Q3 = self.data[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = self.data[(self.data[col] < lower_bound) | (self.data[col] > upper_bound)]
            outliers_info[col] = {
                'count': len(outliers),
                'percentage': (len(outliers) / len(self.data)) * 100,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound
            }
        return outliers_info
    
    def get_correlation_matrix(self):
        """Calculate correlation matrix for numeric columns"""
        if len(self.numeric_cols) > 1:
            return self.data[self.numeric_cols].corr()
        return pd.DataFrame()
    
    def create_distribution_plots(self):
        """Create distribution plots for numeric columns"""
        plots = []
        for col in self.numeric_cols[:6]:  # Limit to first 6 columns
            fig = px.histogram(self.data, x=col, marginal="box", 
                             title=f'Distribution of {col}',
                             color_discrete_sequence=['#636EFA'])
            plots.append(fig)
        return plots
    
    def create_correlation_heatmap(self):
        """Create correlation heatmap"""
        if len(self.numeric_cols) > 1:
            corr_matrix = self.get_correlation_matrix()
            fig = px.imshow(corr_matrix, 
                          text_auto='.2f',
                          color_continuous_scale='RdBu_r',
                          title='Correlation Heatmap',
                          aspect='auto')
            return fig
        return None
    
    def create_boxplots(self):
        """Create boxplots for outlier visualization"""
        plots = []
        for col in self.numeric_cols[:6]:
            fig = px.box(self.data, y=col, 
                        title=f'Box Plot - {col}',
                        color_discrete_sequence=['#EF553B'])
            plots.append(fig)
        return plots
    
    def create_categorical_plots(self):
        """Create plots for categorical columns"""
        plots = []
        for col in self.categorical_cols[:6]:
            value_counts = self.data[col].value_counts().head(10)
            fig = px.bar(x=value_counts.index, y=value_counts.values,
                        title=f'Top 10 Values in {col}',
                        labels={'x': col, 'y': 'Count'},
                        color_discrete_sequence=['#00CC96'])
            plots.append(fig)
        return plots
    
    def prepare_excel_export(self):
        """Prepare comprehensive Excel export with multiple sheets"""
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Sheet 1: Raw Data
            self.data.to_excel(writer, sheet_name='Raw Data', index=False)
            
            # Sheet 2: Statistical Summary
            if len(self.numeric_cols) > 0:
                summary = self.get_statistical_summary()
                summary.to_excel(writer, sheet_name='Statistical Summary')
            
            # Sheet 3: Missing Values Analysis
            missing_df = pd.DataFrame({
                'Column': self.data.columns,
                'Missing Count': self.data.isnull().sum().values,
                'Missing Percentage': (self.data.isnull().sum() / len(self.data) * 100).values
            })
            missing_df.to_excel(writer, sheet_name='Missing Values', index=False)
            
            # Sheet 4: Outliers Analysis
            if len(self.numeric_cols) > 0:
                outliers_info = self.detect_outliers()
                outliers_df = pd.DataFrame(outliers_info).T
                outliers_df.to_excel(writer, sheet_name='Outliers Analysis')
            
            # Sheet 5: Correlation Matrix
            if len(self.numeric_cols) > 1:
                corr_matrix = self.get_correlation_matrix()
                corr_matrix.to_excel(writer, sheet_name='Correlation Matrix')
            
            # Sheet 6: Data Types
            dtypes_df = pd.DataFrame({
                'Column': self.data.columns,
                'Data Type': self.data.dtypes.values
            })
            dtypes_df.to_excel(writer, sheet_name='Data Types', index=False)
        
        output.seek(0)
        return output

# Add these methods to the EDAAnalyzer class

    def generate_data_profile(self):
        """Generate comprehensive data profile"""
        profile = {
            'dataset_info': self.get_basic_info(),
            'statistical_summary': self.get_statistical_summary().to_dict() if len(self.numeric_cols) > 0 else {},
            'outliers': self.detect_outliers(),
            'correlations': self.get_correlation_matrix().to_dict() if len(self.numeric_cols) > 1 else {},
            'data_types': self.data.dtypes.to_dict(),
            'unique_counts': {col: self.data[col].nunique() for col in self.data.columns},
            'value_counts': {col: self.data[col].value_counts().head(10).to_dict() 
                           for col in self.categorical_cols[:5]}
        }
        return profile
    
    def get_recommendations(self):
        """Generate automated recommendations based on analysis"""
        recommendations = []
        info = self.get_basic_info()
        
        # Check for missing values
        missing_cols = [col for col, count in info['missing_values'].items() if count > 0]
        if missing_cols:
            recommendations.append({
                'type': 'Missing Data',
                'severity': 'High' if len(missing_cols) > len(self.data.columns) * 0.3 else 'Medium',
                'message': f"Found missing values in {len(missing_cols)} columns. Consider imputation strategies.",
                'columns': missing_cols[:5]
            })
        
        # Check for duplicates
        if info['duplicates'] > 0:
            recommendations.append({
                'type': 'Data Quality',
                'severity': 'Medium',
                'message': f"Found {info['duplicates']} duplicate rows. Consider removing or investigating.",
                'action': 'Remove duplicates with df.drop_duplicates()'
            })
        
        # Check for high correlation
        if len(self.numeric_cols) > 1:
            corr_matrix = self.get_correlation_matrix()
            high_corr = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    if abs(corr_matrix.iloc[i, j]) > 0.8:
                        high_corr.append((corr_matrix.columns[i], corr_matrix.columns[j]))
            
            if high_corr:
                recommendations.append({
                    'type': 'Multicollinearity',
                    'severity': 'Medium',
                    'message': f"Found {len(high_corr)} pairs of highly correlated variables (|r| > 0.8).",
                    'pairs': high_corr[:3]
                })
        
        # Check for outliers
        if len(self.numeric_cols) > 0:
            outliers_info = self.detect_outliers()
            high_outlier_cols = [col for col, info in outliers_info.items() 
                               if info['percentage'] > 5]
            
            if high_outlier_cols:
                recommendations.append({
                    'type': 'Outliers',
                    'severity': 'Low',
                    'message': f"Found significant outliers (>5%) in {len(high_outlier_cols)} columns.",
                    'columns': high_outlier_cols[:5]
                })
        
        return recommendations


class MissingValueHandler:
    """
    Comprehensive missing value handling with multiple imputation strategies
    """
    
    def __init__(self, data):
        self.data = data.copy()
        self.original_data = data.copy()
        self.numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
        self.imputation_summary = {}
    
    def analyze_missing_patterns(self):
        """Analyze missing data patterns"""
        missing_info = {}
        
        for col in self.data.columns:
            missing_count = self.data[col].isnull().sum()
            if missing_count > 0:
                missing_info[col] = {
                    'count': missing_count,
                    'percentage': (missing_count / len(self.data)) * 100,
                    'dtype': str(self.data[col].dtype),
                    'unique_values': self.data[col].nunique(),
                    'recommended_method': self._recommend_imputation_method(col)
                }
        
        return missing_info
    
    def _recommend_imputation_method(self, column):
        """Recommend best imputation method based on data characteristics"""
        col_data = self.data[column]
        missing_pct = (col_data.isnull().sum() / len(col_data)) * 100
        
        if col_data.dtype in ['object', 'category']:
            return 'mode' if missing_pct < 50 else 'constant'
        else:
            # For numeric columns
            skewness = col_data.skew()
            
            if missing_pct < 5:
                return 'mean' if abs(skewness) < 1 else 'median'
            elif missing_pct < 20:
                return 'knn'
            elif missing_pct < 40:
                return 'iterative'
            else:
                return 'median'
    
    def impute_mean(self, columns=None):
        """Impute missing values with mean (for numeric columns)"""
        if columns is None:
            columns = self.numeric_cols
        
        imputed_data = self.data.copy()
        
        for col in columns:
            if col in self.numeric_cols and self.data[col].isnull().any():
                mean_value = self.data[col].mean()
                imputed_data[col].fillna(mean_value, inplace=True)
                self.imputation_summary[col] = {
                    'method': 'mean',
                    'value': mean_value,
                    'filled_count': self.data[col].isnull().sum()
                }
        
        return imputed_data
    
    def impute_median(self, columns=None):
        """Impute missing values with median (robust to outliers)"""
        if columns is None:
            columns = self.numeric_cols
        
        imputed_data = self.data.copy()
        
        for col in columns:
            if col in self.numeric_cols and self.data[col].isnull().any():
                median_value = self.data[col].median()
                imputed_data[col].fillna(median_value, inplace=True)
                self.imputation_summary[col] = {
                    'method': 'median',
                    'value': median_value,
                    'filled_count': self.data[col].isnull().sum()
                }
        
        return imputed_data
    
    def impute_mode(self, columns=None):
        """Impute missing values with mode (most frequent value)"""
        if columns is None:
            columns = self.categorical_cols
        
        imputed_data = self.data.copy()
        
        for col in columns:
            if self.data[col].isnull().any():
                mode_value = self.data[col].mode()[0] if not self.data[col].mode().empty else 'Unknown'
                imputed_data[col].fillna(mode_value, inplace=True)
                self.imputation_summary[col] = {
                    'method': 'mode',
                    'value': mode_value,
                    'filled_count': self.data[col].isnull().sum()
                }
        
        return imputed_data
    
    def impute_forward_fill(self, columns=None):
        """Forward fill - use previous value (good for time series)"""
        if columns is None:
            columns = self.data.columns.tolist()
        
        imputed_data = self.data.copy()
        
        for col in columns:
            if self.data[col].isnull().any():
                imputed_data[col].fillna(method='ffill', inplace=True)
                # If still has NaN (at the beginning), backfill
                imputed_data[col].fillna(method='bfill', inplace=True)
                self.imputation_summary[col] = {
                    'method': 'forward_fill',
                    'filled_count': self.data[col].isnull().sum()
                }
        
        return imputed_data
    
    def impute_backward_fill(self, columns=None):
        """Backward fill - use next value"""
        if columns is None:
            columns = self.data.columns.tolist()
        
        imputed_data = self.data.copy()
        
        for col in columns:
            if self.data[col].isnull().any():
                imputed_data[col].fillna(method='bfill', inplace=True)
                # If still has NaN (at the end), forward fill
                imputed_data[col].fillna(method='ffill', inplace=True)
                self.imputation_summary[col] = {
                    'method': 'backward_fill',
                    'filled_count': self.data[col].isnull().sum()
                }
        
        return imputed_data
    
    def impute_knn(self, n_neighbors=5, columns=None):
        """KNN Imputation - uses k-nearest neighbors"""
        if columns is None:
            columns = self.numeric_cols
        
        imputed_data = self.data.copy()
        
        if len(columns) > 0:
            # Only impute numeric columns with KNN
            numeric_data = imputed_data[columns]
            
            imputer = KNNImputer(n_neighbors=n_neighbors)
            imputed_array = imputer.fit_transform(numeric_data)
            
            imputed_data[columns] = imputed_array
            
            for col in columns:
                if self.data[col].isnull().any():
                    self.imputation_summary[col] = {
                        'method': f'knn (k={n_neighbors})',
                        'filled_count': self.data[col].isnull().sum()
                    }
        
        return imputed_data
    
    def impute_iterative(self, max_iter=10, columns=None):
        """Iterative Imputation - MICE (Multiple Imputation by Chained Equations)"""
        if columns is None:
            columns = self.numeric_cols
        
        imputed_data = self.data.copy()
        
        if len(columns) > 0:
            numeric_data = imputed_data[columns]
            
            imputer = IterativeImputer(max_iter=max_iter, random_state=42)
            imputed_array = imputer.fit_transform(numeric_data)
            
            imputed_data[columns] = imputed_array
            
            for col in columns:
                if self.data[col].isnull().any():
                    self.imputation_summary[col] = {
                        'method': f'iterative (MICE, iter={max_iter})',
                        'filled_count': self.data[col].isnull().sum()
                    }
        
        return imputed_data
    
    def impute_constant(self, constant_value='Missing', columns=None):
        """Impute with a constant value"""
        if columns is None:
            columns = self.data.columns.tolist()
        
        imputed_data = self.data.copy()
        
        for col in columns:
            if self.data[col].isnull().any():
                imputed_data[col].fillna(constant_value, inplace=True)
                self.imputation_summary[col] = {
                    'method': 'constant',
                    'value': constant_value,
                    'filled_count': self.data[col].isnull().sum()
                }
        
        return imputed_data
    
    def impute_interpolate(self, method='linear', columns=None):
        """Interpolate missing values (good for time series)"""
        if columns is None:
            columns = self.numeric_cols
        
        imputed_data = self.data.copy()
        
        for col in columns:
            if col in self.numeric_cols and self.data[col].isnull().any():
                imputed_data[col] = imputed_data[col].interpolate(method=method)
                self.imputation_summary[col] = {
                    'method': f'interpolate ({method})',
                    'filled_count': self.data[col].isnull().sum()
                }
        
        return imputed_data
    
    def auto_impute(self):
        """Automatically impute using recommended methods for each column"""
        imputed_data = self.data.copy()
        missing_info = self.analyze_missing_patterns()
        
        for col, info in missing_info.items():
            recommended = info['recommended_method']
            
            if recommended == 'mean':
                mean_val = imputed_data[col].mean()
                imputed_data[col].fillna(mean_val, inplace=True)
            elif recommended == 'median':
                median_val = imputed_data[col].median()
                imputed_data[col].fillna(median_val, inplace=True)
            elif recommended == 'mode':
                mode_val = imputed_data[col].mode()[0] if not imputed_data[col].mode().empty else 'Unknown'
                imputed_data[col].fillna(mode_val, inplace=True)
            elif recommended == 'knn':
                if col in self.numeric_cols:
                    knn_imputer = KNNImputer(n_neighbors=5)
                    imputed_data[[col]] = knn_imputer.fit_transform(imputed_data[[col]])
            elif recommended == 'iterative':
                if col in self.numeric_cols:
                    iter_imputer = IterativeImputer(max_iter=10, random_state=42)
                    imputed_data[[col]] = iter_imputer.fit_transform(imputed_data[[col]])
            elif recommended == 'constant':
                imputed_data[col].fillna('Missing', inplace=True)
            
            self.imputation_summary[col] = {
                'method': recommended,
                'filled_count': self.data[col].isnull().sum()
            }
        
        return imputed_data
    
    def drop_missing_rows(self, threshold=None):
        """Drop rows with missing values"""
        if threshold is not None:
            # Drop rows where more than threshold% of values are missing
            return self.data.dropna(thresh=int((1 - threshold/100) * len(self.data.columns)))
        else:
            return self.data.dropna()
    
    def drop_missing_columns(self, threshold=50):
        """Drop columns with missing values above threshold%"""
        missing_pct = (self.data.isnull().sum() / len(self.data)) * 100
        cols_to_drop = missing_pct[missing_pct > threshold].index.tolist()
        return self.data.drop(columns=cols_to_drop), cols_to_drop
    
    def get_imputation_report(self):
        """Get detailed report of imputation performed"""
        return pd.DataFrame(self.imputation_summary).T
