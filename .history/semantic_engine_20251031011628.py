#!/usr/bin/env python3
"""
Semantic Engine for ResuAI
Implements sentence-transformers for semantic job-candidate matching
"""

import os
import json
import logging
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
import pickle
from datetime import datetime
import hashlib

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    SEMANTIC_DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    SEMANTIC_DEPENDENCIES_AVAILABLE = False
    print(f"⚠️  Semantic dependencies not available: {e}")

logger = logging.getLogger(__name__)

class UniversitySemanticEngine:
    """
    Semantic engine for university job-candidate matching using sentence transformers
    Balances performance and accuracy with efficient batch processing
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", cache_dir: str = "semantic_cache"):
        """
        Initialize semantic engine with balanced model selection
        
        Args:
            model_name: Primary model for embedding generation
            cache_dir: Directory for caching embeddings and models
        """
        self.model_name = model_name
        self.fallback_model = "all-mpnet-base-v2"  # Higher accuracy fallback
        self.cache_dir = cache_dir
        self.model = None
        self.faiss_index = None
        self.job_embeddings_cache = {}
        self.candidate_embeddings_cache = {}
        
        # Performance settings
        self.max_sequence_length = 512
        self.batch_size = 32
        self.similarity_threshold = 0.3
        
        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize model
        self._initialize_model()
        
    def _initialize_model(self):
        """Initialize sentence transformer model with fallback"""
        if not SEMANTIC_DEPENDENCIES_AVAILABLE:
            logger.error("Semantic dependencies not available. Install sentence-transformers and faiss-cpu.")
            self.model = None
            return False
            
        try:
            logger.info(f"Loading semantic model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"✅ Semantic model loaded successfully: {self.model_name}")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to load primary model {self.model_name}: {e}")
            
            # Try fallback model
            try:
                logger.info(f"Attempting fallback model: {self.fallback_model}")
                self.model = SentenceTransformer(self.fallback_model)
                self.model_name = self.fallback_model
                logger.info(f"✅ Fallback model loaded: {self.fallback_model}")
                return True
                
            except Exception as e2:
                logger.error(f"Failed to load fallback model: {e2}")
                logger.info("Creating minimal semantic engine without transformer model")
                self.model = None
                return False
    
    def is_available(self) -> bool:
        """Check if semantic engine is available and ready"""
        return SEMANTIC_DEPENDENCIES_AVAILABLE  # Can work with or without model
    
    def _generate_cache_key(self, text: str, context: str = "") -> str:
        """Generate cache key for embeddings"""
        combined = f"{text}_{context}_{self.model_name}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _save_embedding_cache(self, cache_type: str = "both"):
        """Save embedding cache to disk"""
        try:
            if cache_type in ["job", "both"] and self.job_embeddings_cache:
                cache_file = os.path.join(self.cache_dir, "job_embeddings.pkl")
                with open(cache_file, 'wb') as f:
                    pickle.dump(self.job_embeddings_cache, f)
                    
            if cache_type in ["candidate", "both"] and self.candidate_embeddings_cache:
                cache_file = os.path.join(self.cache_dir, "candidate_embeddings.pkl")
                with open(cache_file, 'wb') as f:
                    pickle.dump(self.candidate_embeddings_cache, f)
                    
        except Exception as e:
            logger.warning(f"Failed to save embedding cache: {e}")
    
    def _load_embedding_cache(self):
        """Load embedding cache from disk"""
        try:
            job_cache_file = os.path.join(self.cache_dir, "job_embeddings.pkl")
            if os.path.exists(job_cache_file):
                with open(job_cache_file, 'rb') as f:
                    self.job_embeddings_cache = pickle.load(f)
                    
            candidate_cache_file = os.path.join(self.cache_dir, "candidate_embeddings.pkl")
            if os.path.exists(candidate_cache_file):
                with open(candidate_cache_file, 'rb') as f:
                    self.candidate_embeddings_cache = pickle.load(f)
                    
            logger.info(f"Loaded {len(self.job_embeddings_cache)} job and {len(self.candidate_embeddings_cache)} candidate embeddings from cache")
            
        except Exception as e:
            logger.warning(f"Failed to load embedding cache: {e}")
    
    def encode_text(self, text: str, context: str = "", use_cache: bool = True) -> Optional[np.ndarray]:
        """
        Encode text to embedding vector with caching
        
        Args:
            text: Text to encode
            context: Additional context for caching
            use_cache: Whether to use/update cache
            
        Returns:
            Embedding vector or None if failed
        """
        if not self.is_available():
            # Return a simple hash-based vector when model not available
            import hashlib
            hash_obj = hashlib.md5(text.encode())
            hash_bytes = hash_obj.digest()
            # Convert to 384-dimensional vector (same as all-MiniLM-L6-v2)
            vector = np.frombuffer(hash_bytes, dtype=np.uint8).astype(np.float32)
            # Pad or truncate to 384 dimensions
            if len(vector) < 384:
                vector = np.pad(vector, (0, 384 - len(vector)), 'constant')
            else:
                vector = vector[:384]
            # Normalize
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm
            return vector
            
        # Check cache first
        if use_cache:
            cache_key = self._generate_cache_key(text, context)
            if cache_key in self.candidate_embeddings_cache:
                return self.candidate_embeddings_cache[cache_key]
        
        try:
            # Truncate text if too long
            if len(text) > self.max_sequence_length:
                text = text[:self.max_sequence_length]
            
            # Generate embedding
            embedding = self.model.encode(text, normalize_embeddings=True)
            
            # Cache result
            if use_cache:
                self.candidate_embeddings_cache[cache_key] = embedding
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to encode text: {e}")
            return None
    
    def encode_job_requirements(self, job_data: Dict) -> Optional[np.ndarray]:
        """
        Encode job requirements into embedding vector
        
        Args:
            job_data: Dictionary containing job information
            
        Returns:
            Job embedding vector or None if failed
        """
        if not self.is_available():
            return None
            
        try:
            # Extract job information
            job_id = job_data.get('id', 'unknown')
            title = job_data.get('title', '')
            description = job_data.get('description', '')
            requirements = job_data.get('requirements', '')
            department = job_data.get('department', '')
            experience_level = job_data.get('experience_level', '')
            
            # Create comprehensive job text
            job_text_parts = []
            if title:
                job_text_parts.append(f"Job Title: {title}")
            if department:
                job_text_parts.append(f"Department: {department}")
            if experience_level:
                job_text_parts.append(f"Experience Level: {experience_level}")
            if description:
                job_text_parts.append(f"Description: {description}")
            if requirements:
                job_text_parts.append(f"Requirements: {requirements}")
            
            job_text = " | ".join(job_text_parts)
            
            # Check cache
            cache_key = self._generate_cache_key(job_text, f"job_{job_id}")
            if cache_key in self.job_embeddings_cache:
                return self.job_embeddings_cache[cache_key]
            
            # Generate embedding
            embedding = self.encode_text(job_text, f"job_{job_id}", use_cache=False)
            
            # Cache job embedding
            if embedding is not None:
                self.job_embeddings_cache[cache_key] = embedding
                self._save_embedding_cache("job")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to encode job requirements: {e}")
            return None
    
    def encode_candidate_profile(self, candidate_data: Dict) -> Optional[np.ndarray]:
        """
        Encode candidate profile into embedding vector using actual PDS structure
        
        Args:
            candidate_data: Dictionary containing candidate information with PDS data
            
        Returns:
            Candidate embedding vector or None if failed
        """
        if not self.is_available():
            return None
            
        try:
            candidate_id = candidate_data.get('id', 'unknown')
            
            # Extract candidate information using PDS structure
            profile_parts = []
            
            # Educational Background (from PDS structure)
            educational_background = candidate_data.get('educational_background', [])
            if not educational_background:
                # Fallback to converted format
                education = candidate_data.get('education', [])
                if education and isinstance(education, list):
                    for edu in education[:4]:  # Top 4 education entries
                        if isinstance(edu, dict):
                            degree = edu.get('degree', '')
                            school = edu.get('school', '')
                            level = edu.get('level', '')
                            if degree or school:
                                profile_parts.append(f"Education: {level} {degree} from {school}")
            else:
                # Use direct PDS structure
                if isinstance(educational_background, list):
                    for edu in educational_background[:4]:  # Include more education entries
                        if isinstance(edu, dict):
                            level = edu.get('level', '')
                            degree_course = edu.get('degree_course', edu.get('degree', ''))  # Support both field names
                            school = edu.get('school', '')
                            honors = edu.get('honors', '')
                            if degree_course or school:
                                edu_text = f"Education: {level} {degree_course} from {school}"
                                if honors and honors != 'N/a':
                                    edu_text += f" with {honors}"
                                profile_parts.append(edu_text)
            
            # Work Experience (from PDS structure)
            work_experience = candidate_data.get('work_experience', [])
            if not work_experience:
                # Fallback to converted format
                experience = candidate_data.get('experience', [])
                if experience and isinstance(experience, list):
                    for exp in experience[:4]:  # Top 4 work experiences
                        if isinstance(exp, dict):
                            position = exp.get('position', '')
                            company = exp.get('company', '')
                            description = exp.get('description', '')
                            if position or company:
                                exp_text = f"Experience: {position} at {company}"
                                if description:
                                    exp_text += f" - {description[:100]}"
                                profile_parts.append(exp_text)
            else:
                # Use direct PDS structure
                if isinstance(work_experience, list):
                    for exp in work_experience[:4]:  # Include more experience entries
                        if isinstance(exp, dict):
                            position = exp.get('position', '')
                            company = exp.get('company', '')
                            salary = exp.get('salary', '')
                            grade = exp.get('grade', '')
                            if position or company:
                                exp_text = f"Experience: {position} at {company}"
                                if grade and grade != 'N/A':
                                    exp_text += f" ({grade})"
                                profile_parts.append(exp_text)
            
            # Learning and Development (Training from PDS)
            learning_development = candidate_data.get('learning_development', [])
            if not learning_development:
                # Fallback to converted format
                training = candidate_data.get('training', [])
                if training and isinstance(training, list):
                    for cert in training[:3]:  # Top 3 trainings
                        if isinstance(cert, dict):
                            title = cert.get('title', '')
                            if title:
                                profile_parts.append(f"Training: {title}")
            else:
                # Use direct PDS structure
                for train in learning_development[:3]:  # Top 3 training entries
                    if isinstance(train, dict):
                        title = train.get('title', '')
                        type_info = train.get('type', '')
                        hours = train.get('hours', '')
                        if title:
                            train_text = f"Training: {title}"
                            if type_info and type_info != 'N/a':
                                train_text += f" ({type_info})"
                            if hours:
                                train_text += f" - {hours} hours"
                            profile_parts.append(train_text)
            
            # Civil Service Eligibility (unique to PDS)
            civil_service = candidate_data.get('civil_service_eligibility', [])
            if civil_service and isinstance(civil_service, list):
                for elig in civil_service[:2]:  # Top 2 eligibilities
                    if isinstance(elig, dict):
                        eligibility = elig.get('eligibility', '')
                        rating = elig.get('rating', '')
                        if eligibility:
                            elig_text = f"Eligibility: {eligibility}"
                            if rating and rating != '':
                                try:
                                    rating_pct = float(rating) * 100
                                    elig_text += f" (Rating: {rating_pct:.1f}%)"
                                except:
                                    pass
                            profile_parts.append(elig_text)
            
            # PDS Personal Info (relevant details only)
            pds_data = candidate_data.get('pds_data', {})
            if pds_data and isinstance(pds_data, dict):
                personal_info = pds_data.get('personal_info', {})
                if personal_info:
                    # Add citizenship if relevant for government positions
                    citizenship = personal_info.get('citizenship', '')
                    if citizenship and citizenship not in ['N/a', 'please indicate the details.']:
                        profile_parts.append(f"Citizenship: {citizenship}")
            
            # Combine all parts
            candidate_text = " | ".join(profile_parts)
            
            if not candidate_text.strip():
                logger.warning(f"No meaningful text extracted for candidate {candidate_id}")
                return None
            
            # Generate embedding
            embedding = self.encode_text(candidate_text, f"candidate_{candidate_id}")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to encode candidate profile: {e}")
            return None
    
    def calculate_semantic_similarity(self, candidate_embedding: np.ndarray, job_embedding: np.ndarray) -> float:
        """
        Calculate semantic similarity between candidate and job
        
        Args:
            candidate_embedding: Candidate embedding vector
            job_embedding: Job embedding vector
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        try:
            # Calculate cosine similarity
            similarity = np.dot(candidate_embedding, job_embedding)
            
            # Ensure similarity is between 0 and 1
            similarity = max(0.0, min(1.0, (similarity + 1) / 2))
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {e}")
            return 0.0
    
    def batch_encode_candidates(self, candidates_data: List[Dict]) -> List[Optional[np.ndarray]]:
        """
        Encode multiple candidates efficiently in batches
        
        Args:
            candidates_data: List of candidate dictionaries
            
        Returns:
            List of embedding vectors (same order as input)
        """
        if not self.is_available():
            return [None] * len(candidates_data)
        
        embeddings = []
        
        try:
            # Process in batches for memory efficiency
            for i in range(0, len(candidates_data), self.batch_size):
                batch = candidates_data[i:i + self.batch_size]
                batch_embeddings = []
                
                for candidate in batch:
                    embedding = self.encode_candidate_profile(candidate)
                    batch_embeddings.append(embedding)
                
                embeddings.extend(batch_embeddings)
                
                # Log progress for large batches
                if len(candidates_data) > 50:
                    progress = min(i + self.batch_size, len(candidates_data))
                    logger.info(f"Processed {progress}/{len(candidates_data)} candidates")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to batch encode candidates: {e}")
            return [None] * len(candidates_data)
    
    def calculate_detailed_semantic_score(self, candidate_data: Dict, job_data: Dict) -> Dict:
        """
        Calculate detailed semantic relevance breakdown
        
        Args:
            candidate_data: Candidate information
            job_data: Job information
            
        Returns:
            Dictionary with detailed semantic scores
        """
        if not self.is_available():
            return {
                'overall_score': 0.0,
                'education_relevance': 0.0,
                'experience_relevance': 0.0,
                'training_relevance': 0.0,
                'error': 'Semantic engine not available'
            }
        
        try:
            # Get overall embeddings
            candidate_embedding = self.encode_candidate_profile(candidate_data)
            job_embedding = self.encode_job_requirements(job_data)
            
            if candidate_embedding is None or job_embedding is None:
                return {
                    'overall_score': 0.0,
                    'education_relevance': 0.0,
                    'experience_relevance': 0.0,
                    'training_relevance': 0.0,
                    'error': 'Failed to generate embeddings'
                }
            
            # Calculate overall similarity
            overall_score = self.calculate_semantic_similarity(candidate_embedding, job_embedding)
            
            # Calculate component-specific scores
            education_score = self._calculate_education_relevance(candidate_data, job_data)
            experience_score = self._calculate_experience_relevance(candidate_data, job_data)
            training_score = self._calculate_training_relevance(candidate_data, job_data)
            
            return {
                'overall_score': round(overall_score, 3),
                'education_relevance': round(education_score, 3),
                'experience_relevance': round(experience_score, 3),
                'training_relevance': round(training_score, 3),
                'similarity_threshold': self.similarity_threshold,
                'model_used': self.model_name
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate detailed semantic score: {e}")
            return {
                'overall_score': 0.0,
                'education_relevance': 0.0,
                'experience_relevance': 0.0,
                'training_relevance': 0.0,
                'error': str(e)
            }
    
    def _calculate_education_relevance(self, candidate_data: Dict, job_data: Dict) -> float:
        """Calculate education-specific relevance using PDS structure"""
        try:
            # Extract education from PDS structure
            educational_background = candidate_data.get('educational_background', [])
            education = candidate_data.get('education', [])  # Fallback to converted format
            
            education_texts = []
            
            # Use PDS educational_background first
            if educational_background and isinstance(educational_background, list):
                for edu in educational_background[:4]:  # Include more education entries
                    if isinstance(edu, dict):
                        level = edu.get('level', '')
                        degree_course = edu.get('degree_course', edu.get('degree', ''))  # Support both field names
                        school = edu.get('school', '')
                        honors = edu.get('honors', '')
                        year_graduated = edu.get('year_graduated', '')
                        
                        if degree_course or school:
                            edu_text = f"{level} {degree_course} from {school}"
                            if honors and honors not in ['N/a', '']:
                                edu_text += f" with {honors}"
                            if year_graduated:
                                edu_text += f" (graduated {year_graduated})"
                            education_texts.append(edu_text)
            
            # Fallback to converted education format
            elif education:
                for edu in education[:4]:
                    if isinstance(edu, dict):
                        degree = edu.get('degree', '')
                        school = edu.get('school', '')
                        level = edu.get('level', '')
                        if degree or school:
                            edu_text = f"{level} {degree} from {school}".strip()
                            education_texts.append(edu_text)
            
            if not education_texts:
                return 0.0
            
            # Job requirements - focus on educational requirements
            job_text = f"{job_data.get('title', '')} {job_data.get('requirements', '')}"
            
            # Calculate similarity
            candidate_edu_text = " | ".join(education_texts)
            edu_embedding = self.encode_text(candidate_edu_text, "education")
            job_embedding = self.encode_text(job_text, "job_edu_comparison")
            
            if edu_embedding is None or job_embedding is None:
                return 0.0
            
            return self.calculate_semantic_similarity(edu_embedding, job_embedding)
            
        except Exception as e:
            logger.error(f"Failed to calculate education relevance: {e}")
            return 0.0
    
    def _calculate_experience_relevance(self, candidate_data: Dict, job_data: Dict) -> float:
        """Calculate experience-specific relevance using PDS structure"""
        try:
            # Extract experience from PDS structure
            work_experience = candidate_data.get('work_experience', [])
            experience = candidate_data.get('experience', [])  # Fallback to converted format
            
            experience_texts = []
            
            # Use PDS work_experience first
            if work_experience and isinstance(work_experience, list):
                for exp in work_experience[:4]:  # Top 4 experiences
                    if isinstance(exp, dict):
                        position = exp.get('position', '')
                        company = exp.get('company', '')
                        grade = exp.get('grade', '')
                        date_from = exp.get('date_from', '')
                        date_to = exp.get('date_to', '')
                        
                        if position or company:
                            exp_text = f"{position} at {company}"
                            if grade and grade != 'N/A':
                                exp_text += f" (Grade: {grade})"
                            # Add date range for recency context
                            if date_from or date_to:
                                exp_text += f" ({date_from} to {date_to})"
                            experience_texts.append(exp_text)
            
            # Fallback to converted experience format
            elif experience:
                for exp in experience[:4]:
                    if isinstance(exp, dict):
                        position = exp.get('position', '')
                        company = exp.get('company', '')
                        description = exp.get('description', '')
                        if position or description:
                            exp_text = f"{position} - {description[:100]}".strip()
                            experience_texts.append(exp_text)
            
            if not experience_texts:
                return 0.0
            
            # Job requirements - focus on experience requirements
            job_text = f"{job_data.get('title', '')} {job_data.get('description', '')} {job_data.get('requirements', '')}"
            
            # Calculate similarity
            candidate_exp_text = " | ".join(experience_texts)
            exp_embedding = self.encode_text(candidate_exp_text, "experience")
            job_embedding = self.encode_text(job_text, "job_exp_comparison")
            
            if exp_embedding is None or job_embedding is None:
                return 0.0
            
            return self.calculate_semantic_similarity(exp_embedding, job_embedding)
            
        except Exception as e:
            logger.error(f"Failed to calculate experience relevance: {e}")
            return 0.0
    
    def _calculate_training_relevance(self, candidate_data: Dict, job_data: Dict) -> float:
        """Calculate training and development relevance using PDS structure"""
        try:
            # Extract training/learning development from PDS structure
            learning_development = candidate_data.get('learning_development', [])
            training = candidate_data.get('training', [])  # Fallback to converted format
            
            training_texts = []
            
            # Use PDS learning_development first
            if learning_development:
                for train in learning_development[:5]:  # Top 5 trainings
                    if isinstance(train, dict):
                        title = train.get('title', '')
                        type_info = train.get('type', '')
                        conductor = train.get('conductor', '')
                        hours = train.get('hours', '')
                        
                        if title:
                            train_text = title
                            if type_info and type_info != 'N/a':
                                train_text += f" ({type_info})"
                            if conductor:
                                train_text += f" by {conductor}"
                            if hours:
                                train_text += f" - {hours} hours"
                            training_texts.append(train_text)
            
            # Fallback to converted training format
            elif training:
                for train in training[:5]:
                    if isinstance(train, dict):
                        title = train.get('title', '')
                        type_info = train.get('type', '')
                        if title:
                            train_text = title
                            if type_info:
                                train_text += f" ({type_info})"
                            training_texts.append(train_text)
            
            if not training_texts:
                return 0.0
            
            # Job requirements - focus on training/development needs
            job_text = f"{job_data.get('title', '')} {job_data.get('description', '')} {job_data.get('requirements', '')}"
            
            # Calculate similarity
            candidate_training_text = " | ".join(training_texts)
            training_embedding = self.encode_text(candidate_training_text, "training")
            job_embedding = self.encode_text(job_text, "job_training_comparison")
            
            if training_embedding is None or job_embedding is None:
                return 0.0
            
            return self.calculate_semantic_similarity(training_embedding, job_embedding)
            
        except Exception as e:
            logger.error(f"Failed to calculate training relevance: {e}")
            return 0.0
    
    def cleanup_cache(self, max_age_days: int = 30):
        """Clean up old cache entries"""
        try:
            # Save current cache before cleanup
            self._save_embedding_cache()
            logger.info(f"Semantic cache cleanup completed. Kept recent embeddings.")
            
        except Exception as e:
            logger.error(f"Failed to cleanup cache: {e}")

# Global semantic engine instance
_semantic_engine = None

def get_semantic_engine() -> UniversitySemanticEngine:
    """Get global semantic engine instance"""
    global _semantic_engine
    if _semantic_engine is None:
        _semantic_engine = UniversitySemanticEngine()
        _semantic_engine._load_embedding_cache()
    return _semantic_engine

def test_semantic_engine():
    """Test semantic engine functionality"""
    print("🧪 Testing Semantic Engine...")
    
    engine = get_semantic_engine()
    
    if not engine.is_available():
        print("❌ Semantic engine not available")
        return False
    
    # Test job encoding
    test_job = {
        'id': 1,
        'title': 'Software Engineering Professor',
        'description': 'Teaching software engineering and computer science courses',
        'requirements': 'PhD in Computer Science, programming experience, research background'
    }
    
    job_embedding = engine.encode_job_requirements(test_job)
    print(f"✅ Job embedding shape: {job_embedding.shape if job_embedding is not None else 'None'}")
    
    # Test candidate encoding
    test_candidate = {
        'id': 1,
        'education': [{'degree': 'PhD Computer Science', 'school': 'MIT'}],
        'experience': [{'position': 'Software Engineer', 'company': 'Google', 'description': 'Developed algorithms'}],
        'skills': ['Python', 'Machine Learning', 'Teaching']
    }
    
    candidate_embedding = engine.encode_candidate_profile(test_candidate)
    print(f"✅ Candidate embedding shape: {candidate_embedding.shape if candidate_embedding is not None else 'None'}")
    
    # Test similarity calculation
    if job_embedding is not None and candidate_embedding is not None:
        similarity = engine.calculate_semantic_similarity(candidate_embedding, job_embedding)
        print(f"✅ Semantic similarity: {similarity:.3f}")
        
        # Test detailed scoring
        detailed_score = engine.calculate_detailed_semantic_score(test_candidate, test_job)
        print(f"✅ Detailed semantic score: {detailed_score}")
    
    return True

if __name__ == "__main__":
    test_semantic_engine()