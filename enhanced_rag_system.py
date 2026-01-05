"""
enhanced_rag_system.py
Complete RAG knowledge base that combines JSON files + conversational AI
Optimized for AI Therapist with emotional support
"""

import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer

class EnhancedRAGSystem:
    def __init__(self, rag_directory="rag_knowledges"):
        self.rag_dir = rag_directory
        self.knowledge_base = []
        self.embedder = None
        self.index = None
        
        # Load all knowledge
        self.load_all_knowledge()
        self.build_index()
    
    def load_all_knowledge(self):
        """Load all JSON files from rag_knowledges folder"""
        if not os.path.exists(self.rag_dir):
            print(f"Warning: {self.rag_dir} folder not found!")
            return
        
        for file in os.listdir(self.rag_dir):
            if file.endswith('.json'):
                filepath = os.path.join(self.rag_dir, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # Add emotion category from filename
                        emotion_category = file.replace('.json', '')
                        
                        for item in data:
                            self.knowledge_base.append({
                                'user_input': item.get('user_input', ''),
                                'bot_response': item.get('bot_response', ''),
                                'bot_followup': item.get('bot_followup', ''),
                                'emotion_category': emotion_category,
                                'combined_response': f"{item.get('bot_response', '')} {item.get('bot_followup', '')}"
                            })
                    
                    print(f"✅ Loaded {len(data)} entries from {file}")
                except Exception as e:
                    print(f"❌ Error loading {file}: {e}")
    
    def build_index(self):
        """Build FAISS index for semantic search"""
        if not self.knowledge_base:
            print("No knowledge base loaded!")
            return
        
        try:
            import faiss
            
            # Initialize embedder
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Create embeddings for all user inputs
            user_inputs = [item['user_input'] for item in self.knowledge_base]
            embeddings = self.embedder.encode(user_inputs, convert_to_numpy=True)
            
            # Build FAISS index
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings)
            
            print(f"✅ Built FAISS index with {len(self.knowledge_base)} entries")
        except Exception as e:
            print(f"❌ Error building index: {e}")
    
    def retrieve_response(self, query, emotion=None, top_k=3):
        """
        Retrieve best response from RAG knowledge base
        
        Args:
            query: User's question/input
            emotion: Detected emotion (optional, for filtering)
            top_k: Number of top results to consider
        
        Returns:
            dict with response and metadata
        """
        if not self.index or not self.embedder:
            return None
        
        try:
            # Encode query
            query_embedding = self.embedder.encode([query], convert_to_numpy=True)
            
            # Search in FAISS index
            distances, indices = self.index.search(query_embedding, top_k * 2)  # Get more to filter
            
            # Filter by emotion if provided
            candidates = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx < len(self.knowledge_base):
                    item = self.knowledge_base[idx]
                    
                    # If emotion matches category, prioritize it
                    if emotion and emotion.lower() in item['emotion_category'].lower():
                        candidates.insert(0, {
                            'distance': dist,
                            'item': item
                        })
                    else:
                        candidates.append({
                            'distance': dist,
                            'item': item
                        })
            
            # Get best match
            if candidates:
                best = candidates[0]['item']
                
                return {
                    'response': best['bot_response'],
                    'followup': best['bot_followup'],
                    'combined': best['combined_response'],
                    'emotion_category': best['emotion_category'],
                    'distance': float(candidates[0]['distance']),
                    'confidence': self._calculate_confidence(candidates[0]['distance'])
                }
            
        except Exception as e:
            print(f"Error retrieving response: {e}")
        
        return None
    
    def _calculate_confidence(self, distance):
        """Calculate confidence score from distance (0-1)"""
        # Lower distance = higher confidence
        # Typical distances range from 0 to 2
        confidence = max(0, min(1, 1 - (distance / 2)))
        return confidence


# ==================== INTEGRATION WITH MAIN APP ====================

def get_enhanced_response(user_input, emotion, rag_system):
    """
    Main function to get response - tries RAG first, then fallback
    
    Args:
        user_input: User's message
        emotion: Detected emotion
        rag_system: EnhancedRAGSystem instance
    
    Returns:
        Chatbot response string
    """
    
    # Try RAG knowledge base first
    rag_result = rag_system.retrieve_response(user_input, emotion, top_k=3)
    
    if rag_result and rag_result['confidence'] > 0.6:  # Good match
        # Use RAG response
        return rag_result['combined']
    
    # Fallback to contextual responses (from chatbot_responses.py)
    from chatbot_responses import get_response
    return get_response(user_input, emotion)


# ==================== USAGE EXAMPLE ====================

if __name__ == "__main__":
    # Initialize RAG system
    rag = EnhancedRAGSystem(rag_directory="rag_knowledges")
    
    # Test queries
    test_queries = [
        ("I passed my exam today!", "joy"),
        ("I'm feeling really sad and lonely", "sadness"),
        ("I got promoted at work", "happiness"),
        ("Hey, what's up?", "neutral"),
        ("I'm so stressed about my exams", "anxiety"),
        ("I came from school and got hurt through bus", "sadness")
    ]
    
    print("\n" + "="*80)
    print("TESTING ENHANCED RAG SYSTEM")
    print("="*80 + "\n")
    
    for query, emotion in test_queries:
        print(f"USER ({emotion}): {query}")
        
        # Get response
        response = get_enhanced_response(query, emotion, rag)
        
        print(f"BOT: {response[:200]}...")
        print("-" * 80 + "\n")
