"""
Main Flask Application - GenAI PYQ Assistant
"""
from flask import Flask, render_template, request, jsonify
import sys
import os
from datetime import datetime
import uuid

from config import config_by_name, Config
from rag_engine import RAGEngine
from database import Database
from utils import load_sample_pyqs, chunk_text


def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    config = config_by_name.get(config_name, config_by_name['development'])
    app.config.from_object(config)
    
    # Initialize database
    db = Database(os.path.join(config.DATA_DIR, 'db.sqlite'))
    app.db = db
    
    # Initialize RAG Engine
    try:
        rag_engine = RAGEngine(config)
        app.rag_engine = rag_engine
    except Exception as e:
        print(f"Warning: RAG Engine initialization failed: {e}")
        app.rag_engine = None
    
    # Store config
    app.config_obj = config
    
    return app, db


app, db = create_app()


# ============ Routes ============

@app.route('/')
def home():
    """Home page"""
    return render_template('home.html')


@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    stats = db.get_stats()
    return render_template('dashboard.html', stats=stats)


@app.route('/query')
def query_page():
    """Query page"""
    subjects = app.config_obj.SUBJECTS
    return render_template('query.html', subjects=subjects)


@app.route('/quiz')
def quiz_page():
    """Quiz page"""
    subjects = app.config_obj.SUBJECTS
    return render_template('quiz.html', subjects=subjects)


# ============ API Endpoints ============

@app.route('/api/ask', methods=['POST'])
def api_ask():
    """Answer a question using RAG"""
    data = request.json
    
    question = data.get('question', '').strip()
    subject = data.get('subject', 'DBMS')
    
    if not question:
        return jsonify({'error': 'Question cannot be empty'}), 400
    
    if not app.rag_engine:
        return jsonify({'error': 'RAG Engine not initialized'}), 500
    
    try:
        # Generate answer
        result = app.rag_engine.generate_answer(question, top_k=3)
        
        # Store query
        db.add_query(
            question=question,
            subject=subject,
            answer=result['answer'],
            confidence=result['confidence'],
            sources=result['sources']
        )
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@app.route('/api/quiz', methods=['POST'])
def api_quiz():
    """Generate quiz questions"""
    data = request.json
    
    subject = data.get('subject', 'DBMS')
    num_questions = min(int(data.get('num_questions', 5)), 10)
    
    if not app.rag_engine:
        return jsonify({'error': 'RAG Engine not initialized'}), 500
    
    try:
        quiz_id = str(uuid.uuid4())
        
        # Generate MCQ questions
        questions = app.rag_engine.generate_mcq(subject, num_questions)
        
        # Ensure we have enough questions
        if len(questions) < num_questions:
            # Fallback: generate sample questions
            questions = generate_sample_questions(subject, num_questions)
        
        return jsonify({
            'quiz_id': quiz_id,
            'subject': subject,
            'questions': questions
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@app.route('/api/submit-quiz', methods=['POST'])
def api_submit_quiz():
    """Submit quiz and calculate score"""
    data = request.json
    
    quiz_id = data.get('quiz_id', '')
    subject = data.get('subject', 'DBMS')
    answers = data.get('answers', [])
    correct_answers = data.get('correct_answers', [])
    time_taken = int(data.get('time_taken', 0))
    
    # Calculate score
    score = sum(1 for a, c in zip(answers, correct_answers) if a == c)
    total = len(correct_answers)
    
    try:
        # Store attempt
        db.add_quiz_attempt(
            quiz_id=quiz_id,
            subject=subject,
            num_questions=total,
            answers=answers,
            score=score,
            total=total,
            time_taken=time_taken
        )
        
        percentage = (score / total * 100) if total > 0 else 0
        
        return jsonify({
            'quiz_id': quiz_id,
            'score': score,
            'total': total,
            'percentage': round(percentage, 2),
            'time_taken': time_taken
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@app.route('/api/stats', methods=['GET'])
def api_stats():
    """Get dashboard statistics"""
    try:
        stats = db.get_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@app.route('/api/recent-queries', methods=['GET'])
def api_recent_queries():
    """Get recent queries"""
    subject = request.args.get('subject', None)
    limit = int(request.args.get('limit', 10))
    
    try:
        queries = db.get_recent_queries(subject, limit)
        return jsonify({'queries': queries}), 200
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@app.route('/api/quiz-history', methods=['GET'])
def api_quiz_history():
    """Get quiz history"""
    subject = request.args.get('subject', None)
    limit = int(request.args.get('limit', 10))
    
    try:
        history = db.get_quiz_history(subject, limit)
        return jsonify({'history': history}), 200
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


# ============ Utility Functions ============

def generate_sample_questions(subject, num_questions):
    """Generate sample MCQ questions for fallback"""
    sample_questions = {
        'DBMS': [
            {
                'question': 'What is the primary key in a database?',
                'options': {'A': 'A key that uniquely identifies each record', 'B': 'First key in table', 'C': 'Key stored in primary memory', 'D': 'Key used for sorting'},
                'correct': 'A',
                'explanation': 'Primary key is a constraint that uniquely identifies each record in a table.'
            },
            {
                'question': 'What does ACID stand for?',
                'options': {'A': 'Accuracy, Consistency, Integrity, Durability', 'B': 'Atomicity, Consistency, Isolation, Durability', 'C': 'Availability, Concurrency, Integration, Data', 'D': 'Authentication, Confidentiality, Integrity, Durability'},
                'correct': 'B',
                'explanation': 'ACID properties ensure reliable database transactions.'
            },
        ],
        'DS': [
            {
                'question': 'Time complexity of binary search is?',
                'options': {'A': 'O(n)', 'B': 'O(log n)', 'C': 'O(n²)', 'D': 'O(1)'},
                'correct': 'B',
                'explanation': 'Binary search has logarithmic time complexity as it divides search space in half.'
            },
        ],
        'ML': [
            {
                'question': 'What is overfitting in machine learning?',
                'options': {'A': 'Model generalizes well', 'B': 'Model memorizes training data', 'C': 'Model has high bias', 'D': 'Model underfits data'},
                'correct': 'B',
                'explanation': 'Overfitting occurs when a model learns training data too well including noise.'
            },
        ],
        'CN': [
            {
                'question': 'What layer is TCP in OSI model?',
                'options': {'A': 'Layer 2', 'B': 'Layer 3', 'C': 'Layer 4', 'D': 'Layer 5'},
                'correct': 'C',
                'explanation': 'TCP operates at Transport Layer (Layer 4) of the OSI model.'
            },
        ],
        'OS': [
            {
                'question': 'What is a deadlock?',
                'options': {'A': 'Process waiting indefinitely', 'B': 'Process that never starts', 'C': 'Mutual waiting of processes', 'D': 'Process running indefinitely'},
                'correct': 'C',
                'explanation': 'Deadlock is a situation where processes wait for each other indefinitely.'
            },
        ]
    }
    
    questions = sample_questions.get(subject, [])
    return questions[:num_questions]


# ============ CLI Commands ============

@app.cli.command('init')
def init_db():
    """Initialize database and vector store with sample data"""
    print("Initializing database and vector store...")
    
    # Load sample PYQs
    print("Loading sample PYQ data...")
    texts, metadata = load_sample_pyqs()
    
    if app.rag_engine:
        # Add documents to vector store
        print(f"Adding {len(texts)} chunks to vector store...")
        app.rag_engine.add_documents(texts, metadata)
        print("Vector store initialized successfully!")
    
    print("Database and vector store initialization complete!")


@app.cli.command('rebuild-index')
def rebuild_index():
    """Rebuild vector store index"""
    print("Rebuilding vector store...")
    
    if app.rag_engine:
        texts, metadata = load_sample_pyqs()
        app.rag_engine.add_documents(texts, metadata)
        print("Vector store rebuilt successfully!")
    else:
        print("Error: RAG Engine not initialized")


# ============ Error Handlers ============

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--init':
            with app.app_context():
                init_db()
        elif sys.argv[1] == '--rebuild-index':
            with app.app_context():
                rebuild_index()
    else:
        # Run Flask app
        app.run(debug=True, host='0.0.0.0', port=5000)
