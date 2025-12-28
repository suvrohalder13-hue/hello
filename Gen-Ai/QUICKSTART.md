# Quick Start Guide - GenAI PYQ Assistant

## ⚡ 5-Minute Setup

### Prerequisites
- Python 3.9+
- 4GB+ RAM
- Internet connection (first time only)

### Step 1: Install Ollama (2 minutes)
```bash
# Windows: Download from https://ollama.com/download
# macOS: curl -fsSL https://ollama.com/install.sh | sh
# Linux: curl -fsSL https://ollama.com/install.sh | sh
```

### Step 2: Download Mistral Model (Wait 5-10 min)
```bash
ollama pull mistral
```

### Step 3: Start Ollama Server
```bash
ollama serve
# Keep this running in background!
```

### Step 4: Setup Python (2 minutes)
```bash
# Clone/extract the project
cd GenAI-PYQ-Assistant

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Initialize (3 minutes)
```bash
# Download embedding model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Initialize database and vector store
python app.py --init
```

### Step 6: Run! (30 seconds)
```bash
python app.py
```

**Open browser: http://localhost:5000**

## 🎯 First Actions

1. **Dashboard**: View statistics
2. **Ask Question**: Type "What is ACID in databases?"
3. **Take Quiz**: Select DBMS, generate 5 questions
4. **View Results**: Check your score and review

## ❌ Common Issues

### "Connection refused" (Ollama)
- Ensure `ollama serve` is running in another terminal
- Windows: Check firewall settings

### "Model not found"
```bash
ollama pull mistral
```

### "Python module not found"
```bash
pip install -r requirements.txt
```

### "Database error"
```bash
python app.py --init
```

## 📂 File Structure Quick Reference

```
GenAI-PYQ-Assistant/
├── app.py              ← Run this to start server
├── requirements.txt    ← Install dependencies
├── .env               ← Configuration
├── rag_engine.py      ← RAG implementation
├── database.py        ← Database logic
├── data/
│   ├── pyq_data.txt   ← Add your questions here
│   ├── db.sqlite      ← Auto-created
│   └── vector_store.* ← Auto-created
├── static/
│   ├── css/           ← Styles
│   └── js/            ← Frontend logic
└── templates/         ← HTML pages
```

## 🔧 Customization

### Change Default Subject
Edit `query.html` line with `<option value="">`

### Adjust Quiz Difficulty
Modify `RAG_TOP_K` in `.env` (1-5 recommended)

### Add Your PYQs
1. Edit `data/pyq_data.txt`
2. Run: `python app.py --rebuild-index`

### Change Port (if 5000 busy)
Edit last line of `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8000)  # Changed to 8000
```

## 📊 Architecture at a Glance

```
Question Input
    ↓
Embedding (Sentence Transformers)
    ↓
FAISS Vector Search
    ↓
Retrieve Top-K Documents
    ↓
Add to LLM Prompt
    ↓
Generate Answer (Mistral via Ollama)
    ↓
Return with Confidence Score
```

## 🚀 What's Working

✅ Question answering with RAG
✅ Quiz generation and scoring
✅ Progress tracking
✅ Multi-subject support
✅ Local-only processing
✅ Responsive UI
✅ SQLite persistence

## 📈 Next Steps

1. **Add PYQs**: Replace sample data with real questions
2. **Customize**: Adjust prompts in `rag_engine.py`
3. **Deploy**: Use Gunicorn or Docker
4. **Monitor**: Track usage and adjust parameters

## 🆘 Help

**Issue not listed?**

1. Check console output for error messages
2. Verify Ollama is running: `curl http://localhost:11434/api/tags`
3. Check database: `sqlite3 data/db.sqlite ".tables"`
4. Review `setup-instructions.md` for detailed guide

## 💡 Tips

- First query/quiz takes longer (model warm-up)
- Keep Ollama running throughout session
- Batch process large PYQ datasets for efficiency
- Use Firefox/Chrome for best compatibility

## 📞 Support

- **Ollama Issues**: https://github.com/ollama/ollama
- **Sentence Transformers**: https://www.sbert.net/
- **Flask**: https://flask.palletsprojects.com/

---

**You're all set! Start learning with AI-powered questions. Good luck! 🎓**
