# GenAI PYQ Assistant - Complete Guide

## 🎯 Project Overview

**GenAI PYQ Assistant** is a full-stack AI-powered learning platform for MCA students. It uses **Retrieval-Augmented Generation (RAG)** to answer exam questions and generate AI-powered quizzes based on Previous Year Question Papers.

### Key Features
- 📚 **Smart Q&A**: Get exam-focused answers using RAG technology
- 🧪 **AI Quiz Generator**: Generate MCQ quizzes with instant feedback
- 📊 **Progress Tracking**: Monitor performance and learning metrics
- 🔒 **Complete Privacy**: All data stays local - no cloud dependency
- ⚡ **Fast & Reliable**: Optimized vector search with FAISS

## 🏗️ Architecture

### Tech Stack
```
Frontend:  HTML5 + CSS3 + JavaScript (Bootstrap 5)
Backend:   Flask (Python 3.9+)
Vector DB: FAISS
Embeddings: Sentence Transformers (all-MiniLM-L6-v2)
LLM:       Mistral 7B (via Ollama)
Database:  SQLite3
```

### Project Structure
```
GenAI-PYQ-Assistant/
├── app.py                    # Main Flask application
├── config.py                 # Configuration management
├── rag_engine.py             # RAG implementation
├── database.py               # Database operations
├── utils.py                  # Utility functions
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
├── data/
│   ├── pyq_data.txt         # Sample PYQ data
│   ├── vector_store.faiss   # FAISS index
│   ├── db.sqlite            # SQLite database
│   └── uploads/             # Uploaded files
├── static/
│   ├── css/                 # Stylesheets
│   │   ├── style.css        # Global styles
│   │   ├── dashboard.css    # Dashboard styles
│   │   ├── query.css        # Query page styles
│   │   └── quiz.css         # Quiz page styles
│   └── js/                  # JavaScript files
│       ├── main.js          # Main logic
│       ├── dashboard.js     # Dashboard logic
│       ├── query.js         # Query page logic
│       └── quiz.js          # Quiz logic
└── templates/               # HTML templates
    ├── base.html            # Base template
    ├── home.html            # Home page
    ├── dashboard.html       # Dashboard
    ├── query.html           # Question interface
    └── quiz.html            # Quiz interface
```

## 🚀 Installation & Setup

### Step 1: Install Ollama

**Windows:**
1. Download from https://ollama.com/download
2. Run the installer
3. Open Command Prompt and verify:
   ```bash
   ollama --version
   ```

**macOS:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Step 2: Download Mistral Model

```bash
ollama pull mistral
```

This downloads ~4GB Mistral 7B model. Do this on your development machine before deployment.

### Step 3: Start Ollama Server

```bash
ollama serve
```

Keep this terminal open. Ollama runs on `http://localhost:11434`

### Step 4: Setup Python Project

```bash
# Clone/extract project
cd GenAI-PYQ-Assistant

# Create virtual environment
python -m venv venv

# Activate venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download embedding model (first time only - ~500MB)
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

### Step 5: Initialize Application

```bash
# Create directories
mkdir -p data static/css static/js templates

# Initialize database and vector store
python app.py --init
```

This:
- Creates SQLite database with tables
- Loads sample PYQ data
- Generates embeddings
- Builds FAISS index

### Step 6: Run Application

```bash
python app.py
```

Access at: **http://localhost:5000**

## 📖 Usage Guide

### 1. Home Page
- Overview of the platform
- Feature highlights
- Quick navigation

### 2. Dashboard
- View statistics (total PYQs, quiz attempts, scores)
- Select subject
- View recent queries
- Access quick actions

### 3. Ask Question
- Select subject
- Type your exam question
- Get AI-powered answer
- View source documents
- Confidence score

### 4. Take Quiz
- Select subject and number of questions (1-10)
- Answer MCQ questions with timer
- Submit and view results
- Review answers with explanations

## 🔌 API Endpoints

### POST /api/ask
**Request:**
```json
{
  "question": "What is ACID?",
  "subject": "DBMS",
  "top_k": 3
}
```

**Response:**
```json
{
  "answer": "ACID stands for...",
  "sources": ["chunk1", "chunk2"],
  "confidence": 0.85
}
```

### POST /api/quiz
**Request:**
```json
{
  "subject": "DBMS",
  "num_questions": 5
}
```

**Response:**
```json
{
  "quiz_id": "uuid",
  "subject": "DBMS",
  "questions": [
    {
      "question": "What is...",
      "options": {"A": "...", "B": "..."},
      "correct": "A",
      "explanation": "..."
    }
  ]
}
```

### POST /api/submit-quiz
**Request:**
```json
{
  "quiz_id": "uuid",
  "subject": "DBMS",
  "answers": ["A", "B", "C"],
  "correct_answers": ["A", "B", "D"],
  "time_taken": 300
}
```

### GET /api/stats
**Response:**
```json
{
  "total_pyqs": 15,
  "subjects": {"DBMS": 5, "DS": 4},
  "quiz_attempts": 3,
  "avg_score": 72.5,
  "recent_queries": [...]
}
```

## 📚 Adding Real PYQs

### Method 1: Text File (Simplest)

1. Create `data/pyq_data.txt`:
```
[DBMS] What is normalization?
Normalization is the process of organizing data...

[DS] Explain binary search
Binary search is an efficient algorithm...
```

2. Rebuild index:
```bash
python app.py --rebuild-index
```

### Method 2: CSV File

1. Create CSV with columns: `subject`, `question`, `answer`, `year`

2. Load data:
```python
# Create load_csv.py in project root
import pandas as pd
from app import app, rag_engine

df = pd.read_csv('your_file.csv')
texts = []
metadata = []

for _, row in df.iterrows():
    text = f"[{row['subject']}] {row['question']}\n{row['answer']}"
    texts.append(text)
    metadata.append({
        'subject': row['subject'],
        'year': row['year'],
        'text': text
    })

rag_engine.add_documents(texts, metadata)
```

Run: `python load_csv.py`

### Method 3: PDF Files

```python
# Create load_pdf.py
from pathlib import Path
import PyPDF2
from app import app, rag_engine

pdf_dir = Path('data/pdfs')

texts = []
for pdf_file in pdf_dir.glob('*.pdf'):
    with open(pdf_file, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text = page.extract_text()
            texts.append(text)

metadata = [{'text': t, 'subject': 'Mixed'} for t in texts]
rag_engine.add_documents(texts, metadata)
```

## ⚙️ Configuration

Edit `.env` to customize:

```
# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# RAG Settings
RAG_TOP_K=3              # Number of documents to retrieve
RAG_CHUNK_SIZE=500       # Size of text chunks
RAG_CHUNK_OVERLAP=50     # Overlap between chunks

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## 🐛 Troubleshooting

### Error: "Ollama connection refused"
```bash
# Check if Ollama is running
ollama serve

# Verify on different terminal
curl http://localhost:11434/api/tags
```

### Error: "Sentence Transformers not found"
```bash
pip install sentence-transformers
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

### Error: "FAISS index not found"
```bash
python app.py --init
```

### Error: "Database locked"
- Close all other Flask instances
- Delete `data/db.sqlite` and reinitialize

### Slow Response Times
- Increase `RAG_TOP_K` in `.env`
- Reduce `RAG_CHUNK_SIZE` for faster retrieval
- Ensure Ollama has enough memory

## 📊 Performance Optimization

### Vector Store Size
- FAISS handles 100K+ vectors efficiently
- Current sample: 15 vectors
- Scale: 1M+ vectors possible with proper hardware

### Batch Processing
```python
# Add multiple documents at once
texts = [doc1, doc2, doc3, ...]
metadata = [meta1, meta2, meta3, ...]
rag_engine.add_documents(texts, metadata)
```

### Caching
- Recent queries cached in memory
- Database indexed for fast retrieval
- FAISS provides O(log n) similarity search

## 🚢 Deployment

### Using Gunicorn (Production)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download embedding model
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Copy application
COPY . .

# Expose port
EXPOSE 5000

# Run with gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:
```bash
docker build -t genai-pyq .
docker run -p 5000:5000 genai-pyq
```

## 🎓 Educational Notes

### How RAG Works
1. **Retrieval**: Find similar documents using embeddings
2. **Augmentation**: Add retrieved documents to prompt
3. **Generation**: LLM generates answer using augmented context

### Why FAISS?
- Fast similarity search
- Handles millions of vectors
- Memory efficient
- Supports GPU acceleration

### Embedding Model Choice
- **all-MiniLM-L6-v2**: Fast, 384 dimensions, good for education
- Alternatives: DistilBERT, MPNet (for higher quality)

## 🔒 Security Notes

- All data stays local
- No API keys needed (Ollama runs locally)
- SQLite is simple but not for multi-user production
- For production: upgrade to PostgreSQL

## 📝 Sample Questions

**DBMS:**
- What are ACID properties?
- Explain normalization
- What is indexing?

**Data Structures:**
- Explain binary search complexity
- Compare sorting algorithms
- What are balanced BSTs?

**Machine Learning:**
- Define overfitting
- Explain gradient descent
- What is cross-validation?

**Networks:**
- Explain TCP handshake
- What is sliding window protocol?
- Compare routing protocols

**OS:**
- What is deadlock?
- Explain page replacement
- What is virtual memory?

## 📞 Support & Updates

- Check console logs for errors
- Verify Ollama is running
- Ensure vector store is built
- Check database integrity

## 📄 License

MIT License - Free for educational and commercial use

## 🎉 Getting Started Checklist

- [ ] Install Ollama
- [ ] Pull Mistral model
- [ ] Start Ollama server
- [ ] Create virtual environment
- [ ] Install Python dependencies
- [ ] Download embedding model
- [ ] Run `python app.py --init`
- [ ] Run `python app.py`
- [ ] Access http://localhost:5000
- [ ] Ask a question
- [ ] Take a quiz
- [ ] Add your own PYQs

**Happy Learning! 🚀**
