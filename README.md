# 🤖 AI Data Analyst

Upload a dataset, ask questions in plain English, and get SQL queries, insights, results, and charts.

## 🚀 Features

- Upload any CSV file and query it instantly
- Natural language to SQL conversion using LLM
- Semantic understanding — say "kitchen appliance" and it maps to "Kitchen Appliances"
- Case-insensitive matching
- Auto-generated insights from query results
- Chart generation from results
- RAG-based schema retrieval using ChromaDB

## 🛠️ Tech Stack

**Backend**
- FastAPI
- SQLite + SQLAlchemy
- LangChain
- Ollama (qwen2.5:14b)
- ChromaDB
- HuggingFace Embeddings (all-MiniLM-L6-v2)

**Frontend**
- HTML, CSS, JavaScript

## 📁 Project Structure

```
text-2-sql/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── rag.py               # LLM chain, interpret + SQL generation
│   ├── database.py          # DB init and SQL execution
│   ├── schema_generator.py  # Schema + sample values extraction
│   ├── schema_docs.py       # Default schema docs
│   ├── service.py           # Core query pipeline
│   ├── insights.py          # Insight generation
│   ├── chart.py             # Chart config generation
│   └── requirements.txt
├── frontend/
│   └── index.html
└── README.md
```

## ⚙️ Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/text-2-sql.git
cd text-2-sql
```

### 2. Install Ollama and pull the model

```bash
# Install Ollama from https://ollama.com
ollama pull qwen2.5:14b
```

### 3. Set up Python environment

```bash
cd backend
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

### 4. Run the backend

```bash
python main.py
```

Backend runs at `http://localhost:8000`

### 5. Open the frontend

Open `frontend/index.html` in your browser.

## 📖 Usage

1. Upload a CSV file using the **Upload CSV** button
2. Type your question in plain English
3. Click **Analyze**
4. View the generated SQL, results, insights, and chart

## 💡 Example Questions

- "Show all kitchen appliances"
- "What are the top 5 most expensive products?"
- "Show me all large size items"
- "How many products are out of stock?"
- "Show all items under 500 dollars"

## 📝 Notes

- Ollama must be running locally before starting the backend
- `store.db` and `chroma_db/` are auto-generated and excluded from the repo
- Re-upload your CSV after restarting the server
