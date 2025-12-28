"""
Database models and operations
"""
from datetime import datetime
import sqlite3
import json
import os


class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                pyq_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS queries (
                id INTEGER PRIMARY KEY,
                question TEXT NOT NULL,
                subject TEXT NOT NULL,
                answer TEXT,
                confidence REAL,
                sources TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (subject) REFERENCES subjects(name)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id INTEGER PRIMARY KEY,
                quiz_id TEXT NOT NULL,
                subject TEXT NOT NULL,
                num_questions INTEGER,
                answers TEXT,
                score INTEGER,
                total INTEGER,
                time_taken INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (subject) REFERENCES subjects(name)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pyqs (
                id INTEGER PRIMARY KEY,
                subject TEXT NOT NULL,
                year INTEGER,
                question TEXT,
                answer TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (subject) REFERENCES subjects(name)
            )
        ''')
        
        # Insert default subjects
        subjects = ['DBMS', 'DS', 'ML', 'CN', 'OS']
        for subject in subjects:
            try:
                cursor.execute('INSERT INTO subjects (name) VALUES (?)', (subject,))
            except sqlite3.IntegrityError:
                pass  # Subject already exists
        
        conn.commit()
        conn.close()
    
    def add_query(self, question: str, subject: str, answer: str, confidence: float, sources: list):
        """Store a query"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO queries (question, subject, answer, confidence, sources)
            VALUES (?, ?, ?, ?, ?)
        ''', (question, subject, answer, confidence, json.dumps(sources)))
        
        conn.commit()
        conn.close()
    
    def add_quiz_attempt(self, quiz_id: str, subject: str, num_questions: int, 
                        answers: list, score: int, total: int, time_taken: int):
        """Store a quiz attempt"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO quiz_attempts (quiz_id, subject, num_questions, answers, score, total, time_taken)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (quiz_id, subject, num_questions, json.dumps(answers), score, total, time_taken))
        
        conn.commit()
        conn.close()
    
    def get_stats(self):
        """Get dashboard statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total PYQs
        cursor.execute('SELECT COUNT(*) as count FROM pyqs')
        total_pyqs = cursor.fetchone()['count']
        
        # PYQs by subject
        cursor.execute('SELECT subject, COUNT(*) as count FROM pyqs GROUP BY subject')
        subject_counts = {row['subject']: row['count'] for row in cursor.fetchall()}
        
        # Quiz attempts
        cursor.execute('SELECT COUNT(*) as count FROM quiz_attempts')
        quiz_attempts = cursor.fetchone()['count']
        
        # Average score
        cursor.execute('SELECT AVG(CAST(score AS FLOAT) / total * 100) as avg FROM quiz_attempts WHERE total > 0')
        avg_score = cursor.fetchone()['avg'] or 0
        
        # Recent queries
        cursor.execute('SELECT question, subject, created_at FROM queries ORDER BY created_at DESC LIMIT 10')
        recent_queries = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'total_pyqs': total_pyqs,
            'subjects': subject_counts,
            'quiz_attempts': quiz_attempts,
            'avg_score': round(avg_score, 2),
            'recent_queries': recent_queries
        }
    
    def get_recent_queries(self, subject: str = None, limit: int = 10):
        """Get recent queries"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if subject:
            cursor.execute('''
                SELECT question, subject, answer, confidence, created_at 
                FROM queries 
                WHERE subject = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (subject, limit))
        else:
            cursor.execute('''
                SELECT question, subject, answer, confidence, created_at 
                FROM queries 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_quiz_history(self, subject: str = None, limit: int = 10):
        """Get quiz history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if subject:
            cursor.execute('''
                SELECT quiz_id, subject, score, total, time_taken, created_at
                FROM quiz_attempts
                WHERE subject = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (subject, limit))
        else:
            cursor.execute('''
                SELECT quiz_id, subject, score, total, time_taken, created_at
                FROM quiz_attempts
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
