"""
RAG Engine - Retrieval Augmented Generation implementation
"""
import requests
import numpy as np
from typing import List, Tuple, Dict
from sentence_transformers import SentenceTransformer
import faiss
import json


class RAGEngine:
    def __init__(self, config):
        """Initialize RAG Engine with embeddings and vector store"""
        self.config = config
        
        # Load embedding model
        print("Loading embedding model...")
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        
        # Initialize FAISS index
        self.vector_store = None
        self.metadata = []
        self.load_vector_store()
        
        print("RAG Engine initialized successfully")
    
    def load_vector_store(self):
        """Load FAISS vector store from disk"""
        try:
            import pickle
            import os
            
            if os.path.exists(self.config.FAISS_INDEX_PATH):
                self.vector_store = faiss.read_index(self.config.FAISS_INDEX_PATH)
                
                if os.path.exists(self.config.VECTOR_METADATA_PATH):
                    with open(self.config.VECTOR_METADATA_PATH, 'rb') as f:
                        self.metadata = pickle.load(f)
                print(f"Loaded vector store with {self.vector_store.ntotal} vectors")
            else:
                print("Vector store not found. Initialize with data first.")
        except Exception as e:
            print(f"Error loading vector store: {e}")
    
    def save_vector_store(self):
        """Save FAISS vector store to disk"""
        try:
            import pickle
            import os
            
            os.makedirs(os.path.dirname(self.config.FAISS_INDEX_PATH), exist_ok=True)
            
            faiss.write_index(self.vector_store, self.config.FAISS_INDEX_PATH)
            
            with open(self.config.VECTOR_METADATA_PATH, 'wb') as f:
                pickle.dump(self.metadata, f)
            print("Vector store saved successfully")
        except Exception as e:
            print(f"Error saving vector store: {e}")
    
    def add_documents(self, texts: List[str], metadata: List[Dict]):
        """Add documents to vector store"""
        print(f"Generating embeddings for {len(texts)} chunks...")
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts, batch_size=32, show_progress_bar=True)
        embeddings = embeddings.astype('float32')
        
        # Create or update FAISS index
        dimension = embeddings.shape[1]
        
        if self.vector_store is None:
            self.vector_store = faiss.IndexFlatL2(dimension)
        
        # Add embeddings to index
        self.vector_store.add(embeddings)
        
        # Store metadata
        self.metadata.extend(metadata)
        
        # Save to disk
        self.save_vector_store()
        print(f"Added {len(texts)} documents. Total vectors: {self.vector_store.ntotal}")
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """Retrieve top-k similar documents for query"""
        if self.vector_store is None or self.vector_store.ntotal == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query], convert_to_tensor=False)
        query_embedding = query_embedding.astype('float32')
        
        # Search in FAISS
        distances, indices = self.vector_store.search(query_embedding, min(top_k, self.vector_store.ntotal))
        
        # Retrieve documents
        results = []
        for i, idx in enumerate(indices[0]):
            if idx >= 0 and idx < len(self.metadata):
                distance = distances[0][i]
                # Convert L2 distance to similarity score (0-1)
                # Smaller distance = higher similarity
                similarity = 1 / (1 + distance)
                
                doc_text = self.metadata[idx].get('text', '')
                results.append((doc_text, similarity))
        
        return results
    
    def generate_answer(self, query: str, top_k: int = 3) -> Dict:
        """Generate answer using RAG pipeline"""
        # Retrieve relevant documents
        retrieved_docs = self.retrieve(query, top_k)
        
        if not retrieved_docs:
            return {
                'answer': 'No relevant information found in the database.',
                'sources': [],
                'confidence': 0.0
            }
        
        # Prepare context
        context = "\n\n".join([doc[0] for doc in retrieved_docs])
        
        # Create prompt
        prompt = self.create_prompt(query, context)
        
        # Call Ollama
        answer = self.call_ollama(prompt)
        
        # Calculate confidence
        confidence = sum([doc[1] for doc in retrieved_docs]) / len(retrieved_docs)
        
        return {
            'answer': answer,
            'sources': [doc[0][:100] + "..." for doc in retrieved_docs],
            'confidence': float(confidence)
        }
    
    def create_prompt(self, query: str, context: str) -> str:
        """Create prompt for LLM"""
        prompt = f"""You are an expert MCA exam assistant. Answer the following question based on the provided context.

Context from Previous Year Questions:
{context}

Question: {query}

Instructions:
1. Provide a clear, concise answer suitable for MCA exam preparation
2. Use simple language
3. Structure your answer with key points if needed
4. Avoid hallucination - only use information from context
5. If context doesn't contain relevant information, say so explicitly
6. Maximum 200 words

Answer:"""
        return prompt
    
    def call_ollama(self, prompt: str) -> str:
        """Call Ollama LLM API"""
        try:
            url = f"{self.config.OLLAMA_BASE_URL}/api/generate"
            
            payload = {
                "model": self.config.OLLAMA_MODEL,
                "prompt": prompt,
                "temperature": 0.1,  # Low temperature for factual answers
                "num_predict": 200,
                "stream": False
            }
            
            response = requests.post(
                url,
                json=payload,
                timeout=self.config.OLLAMA_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'Error: No response from model')
            else:
                return f"Error: {response.status_code} - {response.text}"
        
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to Ollama. Ensure Ollama is running on localhost:11434"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def generate_mcq(self, topic: str, num_questions: int = 5) -> List[Dict]:
        """Generate MCQ questions for a topic"""
        prompt = f"""Generate {num_questions} multiple choice questions on {topic} for MCA exam preparation.

Format each question as:
Question: [Question text]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
Answer: [Correct option letter]
Explanation: [Brief explanation]

Generate {num_questions} questions now:"""
        
        response = self.call_ollama(prompt)
        
        # Parse questions
        questions = self.parse_mcq_response(response)
        
        return questions
    
    def parse_mcq_response(self, response: str) -> List[Dict]:
        """Parse MCQ questions from LLM response"""
        questions = []
        
        # Simple parsing - can be improved
        blocks = response.split('Question:')[1:]  # Skip first empty split
        
        for block in blocks[:5]:  # Get up to 5 questions
            try:
                lines = block.strip().split('\n')
                
                if len(lines) < 5:
                    continue
                
                question_text = lines[0].strip()
                
                options = {}
                answer_key = None
                explanation = ""
                
                for line in lines[1:]:
                    if line.startswith('A)'):
                        options['A'] = line[2:].strip()
                    elif line.startswith('B)'):
                        options['B'] = line[2:].strip()
                    elif line.startswith('C)'):
                        options['C'] = line[2:].strip()
                    elif line.startswith('D)'):
                        options['D'] = line[2:].strip()
                    elif line.startswith('Answer:'):
                        answer_key = line.split(':')[1].strip()[0]
                    elif line.startswith('Explanation:'):
                        explanation = line.split(':', 1)[1].strip()
                
                if len(options) == 4 and answer_key:
                    questions.append({
                        'question': question_text,
                        'options': options,
                        'correct': answer_key,
                        'explanation': explanation
                    })
            except:
                continue
        
        return questions
