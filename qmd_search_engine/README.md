# qmd-search-engine

# QMD – Hybrid Markdown Document Search Engine

A Python-based hybrid search engine that searches Markdown documents using **BM25 keyword retrieval, semantic search and Reciprocal Rank Fusion (RRF)**.

QMD (Query Markup Documents) is designed to help users find relevant information from a collection of Markdown documents using both keyword matching and meaning-based retrieval.

The project combines traditional information retrieval with vector-based semantic search to provide ranked and relevant document chunks.

---

## 1. Project Overview

Searching large documents manually can be time-consuming, especially when information is distributed across multiple files and sections.

This project provides a document search system that:

- Loads and processes Markdown documents.
- Extracts document metadata, headings and content.
- Splits documents into smaller searchable chunks.
- Creates keyword indexes using SQLite FTS5.
- Generates vector embeddings using Sentence Transformers.
- Performs keyword-based and semantic search.
- Combines search results using Reciprocal Rank Fusion.
- Supports incremental indexing of new, modified and deleted documents.
- Provides a REST API using FastAPI.
- Displays search results through a web-based interface.

The system is designed to work locally without requiring an LLM API for search.

## 2. Key Features

### Document Processing
- Automatically discovers Markdown files.
- Extracts document titles, headings and metadata.
- Splits large documents into smaller chunks.
- Maintains document and chunk relationships.

### Keyword Search
- Uses SQLite FTS5 for full-text indexing.
- Uses BM25 for keyword relevance scoring.
- Supports matching multiple query terms.
- Supports collection-based filtering.

### Semantic Search
- Uses the `sentence-transformers/all-MiniLM-L6-v2` embedding model.
- Converts queries and document chunks into numerical vectors.
- Uses cosine similarity to identify meaning-related content.
- Retrieves relevant chunks even when the exact query wording differs from the document.

### Hybrid Search
- Combines keyword and semantic search.
- Uses Reciprocal Rank Fusion (RRF).
- Combines ranking positions rather than directly adding BM25 and cosine similarity scores.
- Produces a unified ranking of search results.

### Incremental Indexing
- Detects newly added documents.
- Identifies modified documents using SHA-256 file hashes.
- Skips unchanged documents.
- Removes deleted documents from the index.
- Updates keyword and embedding indexes when required.

### Web Interface
- Search documents through a browser.
- Select keyword, semantic or hybrid search.
- Filter results by collection.
- Configure the number of results.
- View relevance scores.
- Open complete documents and navigate back to search results.

### REST API
- Built using FastAPI.
- Provides search, document retrieval and collection endpoints.
- Supports API testing through Swagger UI.

## 3. Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python 3.12 |
| Backend Framework | FastAPI |
| Database | SQLite |
| Full-Text Search | SQLite FTS5 |
| Keyword Ranking | BM25 |
| Embedding Model | Sentence Transformers |
| Pretrained Model | all-MiniLM-L6-v2 |
| Vector Operations | NumPy |
| Semantic Ranking | Cosine Similarity |
| Hybrid Ranking | Reciprocal Rank Fusion (RRF) |
| Frontend | HTML, CSS, JavaScript |
| API Server | Uvicorn |
| Testing | Pytest |
| Version Control | Git and GitHub |

## 4. Project Architecture

The project consists of two major workflows:

1. Document ingestion and indexing.
2. Query processing and document retrieval.

### A. Document Ingestion and Indexing

Markdown documents are processed and indexed before users perform searches.

```text
Markdown Documents
        |
        v
    loader.py
        |
        v
    parser.py
        |
        v
   chunking.py
        |
        v
  index_manager.py
        |
        +-------------------------+
        |                         |
        v                         v
 keyword_index.py          embedding_index.py
        |                         |
        v                         v
 SQLite FTS5 Index         Vector Embeddings
        |                         |
        +------------+------------+
                     |
                     v
                 qmd.db
```

**Processing steps:**

1. `loader.py` discovers and reads Markdown documents.
2. `parser.py` extracts document metadata, headings and content.
3. `chunking.py` splits documents into smaller sections.
4. `index_manager.py` coordinates indexing and incremental updates.
5. `keyword_index.py` creates the full-text search index.
6. `embedding_index.py` generates and stores document embeddings.
7. `database.py` manages the SQLite database.

### B. Search and Retrieval Workflow

When a user enters a query, the search system retrieves relevant document chunks.

```text
                User Query
                     |
                     v
              FastAPI Search API
                     |
                     v
               Search Selection
                     |
          +----------+----------+
          |                     |
          v                     v
    Keyword Search        Semantic Search
          |                     |
          v                     v
         BM25             Cosine Similarity
          |                     |
          +----------+----------+
                     |
                     v
               Hybrid Search
                     |
                     v
                    RRF
                     |
                     v
              Ranked Results
                     |
                     v
              FastAPI Response
                     |
                     v
               Web Interface
```

## 5. Search Algorithms

### 5.1 Keyword Search – BM25

Keyword search uses SQLite FTS5 and its built-in BM25 ranking function.

BM25 evaluates:
- Term frequency.
- Inverse document frequency.
- Document length.
- Configured column weights.

The project assigns different weights to indexed fields:

| Indexed Field | Weight |
|---|---:|
| Chunk ID | 0.0 |
| Document Title | 1.0 |
| Collection | 0.5 |
| Heading | 2.0 |
| Content | 1.0 |

SQLite FTS5 returns negative BM25 scores. More negative scores indicate stronger keyword relevance.

### 5.2 Semantic Search – Cosine Similarity

Semantic search uses the pretrained Sentence Transformer model:

`sentence-transformers/all-MiniLM-L6-v2`

The model converts queries and document chunks into 384-dimensional embedding vectors.

The project calculates cosine similarity using the dot product of normalized vectors.

Formula:

\[
Similarity(A,B)=\frac{A\cdot B}{\|A\|\|B\|}
\]

Higher cosine similarity indicates greater semantic similarity.

### 5.3 Hybrid Search – Reciprocal Rank Fusion

Hybrid search combines the ranked results from keyword and semantic search.

The project uses Reciprocal Rank Fusion with a constant of 60.

Formula:

\[
RRF(d)=\sum_{r\in rankings(d)}\frac{1}{60+r}
\]

Where:

- `d` represents a document chunk.
- `r` represents its rank in an individual search result list.
- `60` is the RRF constant.

Chunks appearing in both result lists receive contributions from both rankings.

The final results are sorted in descending order of the RRF score.

**Note:** The hybrid score is a ranking value, not a relevance probability or percentage.

## 6. Project Folder Structure

```text
qmd_search_engine/
│
├── app/
│   │
│   ├── api/
│   │   ├── search_routes.py
│   │   └── document_routes.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   ├── parser.py
│   │   └── chunking.py
│   │
│   ├── indexing/
│   │   ├── __init__.py
│   │   ├── keyword_index.py
│   │   ├── embedding_index.py
│   │   └── index_manager.py
│   │
│   ├── search/
│   │   ├── keyword_search.py
│   │   ├── semantic_search.py
│   │   └── hybrid_search.py
│   │
│   └── main.py
│
├── frontend/
│   ├── index.html
│   ├── css/
│   └── js/
│       └── app.js
│
├── documents/
│   ├── python/
│   ├── machine_learning/
│   └── medical/
│
├── data/
│   └── qmd.db
│
├── tests/
│
├── requirements.txt
├── README.md
└── .gitignore
```

## 7. Installation and Setup

### Prerequisites

- Python 3.12
- pip
- Git
- Visual Studio Code (recommended)

### Step 1: Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Navigate to the project directory:

```bash
cd qmd_search_engine
```

### Step 2: Create a Virtual Environment

```bash
python -m venv .venv
```

### Step 3: Activate the Virtual Environment

For Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Index Markdown Documents

Run the indexing manager:

```bash
python -m app.indexing.index_manager
```

This command:

- Discovers Markdown files.
- Processes document content.
- Generates chunks.
- Creates keyword indexes.
- Generates and stores embeddings.
- Detects new, modified, unchanged and deleted documents.

The Sentence Transformer model is downloaded when needed if it is not already available locally. An internet connection may be required for the initial download.

### Step 6: Start the FastAPI Server

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Step 7: Open the Application

Web interface:

http://127.0.0.1:8000/ui

Swagger API documentation:

http://127.0.0.1:8000/docs

Health check:

http://127.0.0.1:8000/health

## 8. How to Use the Application

1. Start the FastAPI server.
2. Open the web interface in your browser.
3. Enter a search query.
4. Select the search mode:
   - Keyword
   - Semantic
   - Hybrid
5. Select a document collection if required.
6. Choose the number of results.
7. Click Search.
8. Review the retrieved document chunks and their scores.
9. Click View Full Document to read the complete document.

## 9. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/search` | Search Markdown documents |
| GET | `/documents` | Retrieve indexed documents |
| GET | `/documents/{document_id}` | Retrieve a complete document |
| GET | `/collections` | Retrieve available collections |
| GET | `/health` | Check API health |

### Example Search Request

**Endpoint:**

```text
POST /search
```

**Request Body:**

```json
{
    "query": "What are the uses of paracetamol?",
    "mode": "hybrid",
    "top_k": 5,
    "collection": "medical"
}
```

Supported search modes:

- `keyword`
- `semantic`
- `hybrid`

## 10. Incremental Indexing

The project supports incremental indexing to avoid unnecessarily rebuilding the complete search index.

SHA-256 hashing is used to identify document changes.

| Document Status | System Behaviour |
|---|---|
| New document | Creates document and indexes its chunks |
| Modified document | Replaces its old indexed content |
| Unchanged document | Skips re-indexing |
| Deleted document | Removes its indexed records |

To update the index after adding, modifying or deleting Markdown files, run:

```bash
python -m app.indexing.index_manager
```

## 11. Testing

The project uses Pytest for testing.

Run all tests:

```bash
python -m pytest tests/ -v
```

The project also includes search evaluation using metrics such as:

- Precision@5
- Recall@5
- F1 Score

These metrics help evaluate the quality of retrieved search results.

## 12. Adding New Markdown Documents

To add a new document:

1. Open the `documents/` directory.
2. Select an appropriate collection folder.
3. Create a new `.md` file.
4. Add document content using Markdown headings and sections.
5. Save the file.
6. Run the indexing command.

Example:

```text
documents/
    medical/
        paracetamol.md
        ibuprofen.md
        cetirizine.md
```

After indexing, the new documents become available through the search interface.

## 13. Current Project Scope

The current implementation includes:

- Markdown document ingestion.
- Metadata extraction and chunking.
- SQLite database storage.
- FTS5-based keyword retrieval.
- Sentence Transformer embeddings.
- Cosine similarity-based semantic retrieval.
- RRF-based hybrid ranking.
- Incremental indexing.
- FastAPI endpoints.
- Browser-based search interface.
- Search evaluation tests.

The current implementation does not include:

- LLM-based query expansion.
- Cross-encoder or LLM-based reranking.
- LLM-generated answers.
- Retrieval-Augmented Generation (RAG) answer generation.

These can be considered future enhancements.

## 14. Future Enhancements

Potential improvements include:

1. Rule-based or model-based query expansion.
2. Cross-encoder reranking for improved result ordering.
3. Relevance thresholds for filtering weak search matches.
4. Improved search evaluation using a larger query dataset.
5. Support for additional document formats.
6. Search result highlighting.
7. More advanced filtering and sorting options.
8. Optional RAG integration for answer generation.

## 15. Learning Outcomes

Through this project, the following concepts are implemented and explored:

- Document ingestion and preprocessing.
- Text chunking and metadata extraction.
- SQLite database design.
- Full-text search using FTS5.
- BM25 information retrieval.
- Text embeddings using Sentence Transformers.
- Vector similarity and cosine similarity.
- Hybrid information retrieval.
- Reciprocal Rank Fusion.
- Incremental indexing.
- REST API development using FastAPI.
- Frontend and backend integration.
- Search evaluation using precision, recall and F1.

## 16. Conclusion

QMD is a local Markdown document search engine that combines keyword-based and semantic retrieval to identify relevant information from document collections.

By integrating SQLite FTS5, BM25, Sentence Transformer embeddings, cosine similarity and Reciprocal Rank Fusion, the project provides a hybrid retrieval approach that supports both exact keyword matching and meaning-based search.

The project demonstrates the practical implementation of information retrieval techniques, vector embeddings, database indexing and backend API development in Python.

---

**Developed using Python, FastAPI, SQLite, Sentence Transformers and JavaScript.**
