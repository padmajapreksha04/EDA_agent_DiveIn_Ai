"""
ML/DL enhancements for research agent
Adds intelligent ranking and analysis
"""

from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class RelevanceScorer:
    """ML-based relevance scoring for search results"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=100, 
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    def score_results(self, query: str, results: List[str]) -> List[Tuple[str, float]]:
        """Score and rank search results by relevance to query"""
        
        if not results or len(results) == 0:
            return []
        
        try:
            # Combine query and results
            all_texts = [query] + results
            
            # Vectorize
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            
            # Calculate similarity scores
            query_vector = tfidf_matrix[0:1]
            result_vectors = tfidf_matrix[1:]
            
            similarities = cosine_similarity(query_vector, result_vectors)[0]
            
            # Rank results
            ranked = sorted(
                zip(results, similarities),
                key=lambda x: x[1],
                reverse=True
            )
            
            return ranked
            
        except Exception as e:
            print(f"Error in relevance scoring: {e}")
            return [(r, 1.0) for r in results]
    
    def extract_key_terms(self, text: str, top_n: int = 5) -> List[str]:
        """Extract key terms from text using TF-IDF"""
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform([text])
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Get top terms
            tfidf_scores = tfidf_matrix.toarray()[0]
            top_indices = tfidf_scores.argsort()[-top_n:][::-1]
            
            key_terms = [feature_names[i] for i in top_indices if tfidf_scores[i] > 0]
            return key_terms
            
        except Exception as e:
            print(f"Error extracting key terms: {e}")
            return []


class TopicAnalyzer:
    """Analyze topics and themes in research"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=50, stop_words='english')
    
    def identify_themes(self, texts: List[str]) -> List[str]:
        """Identify main themes across multiple texts"""
        
        if not texts:
            return []
        
        try:
            # Vectorize all texts
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Get feature names (terms)
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Calculate average TF-IDF scores
            avg_scores = np.mean(tfidf_matrix.toarray(), axis=0)
            
            # Get top terms
            top_indices = avg_scores.argsort()[-10:][::-1]
            themes = [feature_names[i] for i in top_indices if avg_scores[i] > 0]
            
            return themes
            
        except Exception as e:
            print(f"Error identifying themes: {e}")
            return []
