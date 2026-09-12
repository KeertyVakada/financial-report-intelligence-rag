# Financial Report RAG

A financial document question-answering system built using Retrieval-Augmented Generation (RAG), hybrid retrieval, financial-aware evidence ranking, and LLM-based answer generation.

The project uses **Microsoft's 2025 Annual Report** as the source document and provides an interactive Streamlit application where users can ask questions about the report and receive answers along with supporting evidence and page references.

---

## Live Demo

**Streamlit App:** Coming soon

---

## Project Objective

The goal of this project is to make financial reports easier to search and understand.

Annual reports contain a large amount of information across financial statements, tables, business segments, cash-flow statements, and explanatory sections. Finding one specific figure or piece of information manually can be time-consuming.

This project builds a RAG pipeline that retrieves relevant information from the financial report and uses the retrieved evidence to generate an answer.

The system was designed to go beyond basic vector search by combining semantic retrieval, keyword retrieval, financial-aware ranking, evidence classification, and reranking.

---

## Dataset

The project uses Microsoft's **2025 Annual Report** as the source document.

The report contains information about:

* Revenue
* Operating income
* Net income
* Balance sheet
* Cash flows
* Business segments
* Microsoft Cloud
* Gaming
* Server products and cloud services
* Research and development
* Multi-year financial information

The original report is not included in the GitHub repository.

The processed retrieval artifacts required by the application are included under:

```text
data/processed/
```

---

## Document Processing

The annual report goes through several preprocessing stages before it can be searched.

### PDF Text Extraction

Text is extracted page by page using **PyMuPDF**.

The original PDF page number and report page number are preserved as metadata.

### Text Preprocessing

The extracted text is cleaned and normalized before creating document chunks.

### Page-Aware Chunking

The document is divided into overlapping chunks while preserving page-level information.

This allows the application to identify where retrieved information came from in the original report.

### Embeddings

Document chunks are converted into vector embeddings using:

```text
BAAI/bge-small-en-v1.5
```

The generated embeddings are stored in:

```text
data/processed/embeddings.npy
```

The processed document chunks are stored in:

```text
data/processed/chunks.json
```

---

## Retrieval

The project uses more than one retrieval method to improve the quality of retrieved evidence.

### Dense Retrieval

Semantic retrieval is performed using the BGE embedding model.

This allows the system to find passages that are conceptually related to the user's question even when the wording is different.

### BM25 Retrieval

BM25 is used for keyword-based retrieval.

This is useful for financial reports because exact terms can be important when searching for items such as:

* Total assets
* Operating income
* Gaming revenue
* Microsoft Cloud
* Cash from operations
* Research and development

### Hybrid Retrieval

Dense retrieval and BM25 results are combined using **Reciprocal Rank Fusion (RRF)**.

This gives the system both semantic and keyword-based retrieval capabilities.

---

## Financial-Aware Evidence Ranking

Financial questions often require specific types of evidence.

For example:

* Asset questions should favor balance-sheet information.
* Cash-flow questions should favor cash-flow statements.
* Segment questions should favor segment information.
* Revenue questions should favor relevant financial statements and revenue tables.

To handle this, the project extracts financial metadata from retrieved chunks and applies additional relevance scoring.

The system looks for financial signals including:

* Revenue
* Total assets
* Liabilities
* Cash flow
* Operating income
* EPS
* Business segments
* Microsoft Cloud
* Gaming
* Server products and cloud services
* Financial years

This additional scoring helps prioritize evidence that is more appropriate for the question being asked.

---

## Evidence Classification

Retrieved chunks are classified according to the type of financial evidence they contain.

The project uses categories such as:

* Financial Statement
* Financial Table
* Revenue Table
* Segment Table
* Cash-Flow Table
* Narrative
* General

The evidence type is then used as another signal during the ranking process.

---

## Cross-Encoder Reranking

After the initial retrieval and financial-aware ranking, the retrieved candidates are reranked using a cross-encoder.

The project uses:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

The cross-encoder evaluates the user's question together with each retrieved passage and produces a refined ranking.

This helps select the most relevant evidence before generating the final answer.

---

## Answer Generation

The highest-ranked evidence is assembled into a structured context containing:

* Source document
* Report page
* PDF page
* Evidence type
* Retrieved text

This context is passed to the Groq LLM for answer generation.

The project uses:

```text
openai/gpt-oss-20b
```

The application then displays the generated answer together with the supporting evidence.

---

## Application

A Streamlit application was built to make the RAG system interactive.

Users can enter questions such as:

```text
What was Microsoft's revenue in fiscal year 2025?

Which business segment had the highest revenue in 2025?

What was Gaming revenue in 2025?

How much cash did Microsoft generate from operations?

What was Microsoft's operating income in 2025?

What was Microsoft's net income in 2025?
```

For each question, the application:

1. Retrieves relevant evidence from the report.
2. Applies financial-aware ranking.
3. Reranks the retrieved candidates.
4. Builds the context for the LLM.
5. Generates the final answer.
6. Displays the supporting evidence and page references.

---

## Evaluation

A benchmark of financial-report questions was created to evaluate the retrieval pipeline.

The benchmark includes questions covering:

* Direct financial facts
* Financial figures
* Comparisons
* Business segments
* Financial tables
* Cash flow
* Multi-year information
* Questions outside the source document

Several retrieval approaches were compared using **Hit@K** and **MRR**.

### Retrieval Performance

| Approach                             |      Hit@1 |      Hit@3 |      Hit@5 |        MRR |
| ------------------------------------ | ---------: | ---------: | ---------: | ---------: |
| Dense Retrieval                      |     41.67% |     66.67% |     83.33% |     0.5891 |
| Hybrid RRF                           |     41.67% |     75.00% |     83.33% |     0.6090 |
| Cross-Encoder Reranking              |     33.33% |     91.67% |    100.00% |     0.6042 |
| **Financial-Aware Evidence Ranking** | **66.67%** | **91.67%** | **91.67%** | **0.7778** |

### Evaluation Metrics

**Hit@K**

Measures whether the relevant evidence appears within the top K retrieved results.

**MRR (Mean Reciprocal Rank)**

Measures how highly the first relevant result appears in the ranking.

The evaluation was used to compare the retrieval approaches and measure the effect of adding financial-specific evidence signals.

---

## Tech Stack

* Python
* Streamlit
* PyMuPDF
* NumPy
* Sentence Transformers
* BAAI/bge-small-en-v1.5
* BM25
* Reciprocal Rank Fusion
* Cross-Encoder
* cross-encoder/ms-marco-MiniLM-L-6-v2
* Groq API
* GPT-OSS-20B
* python-dotenv

---

## Project Structure

```text
financial-report-rag/
│
├── data/
│   └── processed/
│       ├── chunks.json
│       └── embeddings.npy
│
├── src/
│   │
│   ├── app.py
│   │
│   ├── ingestion.py
│   ├── preprocessing.py
│   ├── chunking.py
│   ├── embeddings.py
│   │
│   ├── retrieval.py
│   ├── bm25_retrieval.py
│   ├── hybrid_retrieval.py
│   ├── reranker.py
│   │
│   ├── query_router.py
│   ├── query_routing_strategy.py
│   │
│   ├── financial_metadata.py
│   ├── financial_scoring.py
│   ├── evidence_type.py
│   ├── evidence_scoring.py
│   ├── financial_evidence_retrieval.py
│   │
│   ├── context_builder.py
│   ├── generation.py
│   │
│   ├── evaluation_questions.json
│   │
│   ├── evaluate_retrieval.py
│   ├── evaluate_bm25.py
│   ├── evaluate_hybrid.py
│   ├── evaluate_reranker.py
│   ├── evaluate_financial_retrieval.py
│   └── evaluate_financial_evidence.py
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Key Files

| File                              | Description                                    |
| --------------------------------- | ---------------------------------------------- |
| `app.py`                          | Streamlit application                          |
| `ingestion.py`                    | Extracts text from the PDF                     |
| `preprocessing.py`                | Cleans extracted text                          |
| `chunking.py`                     | Creates page-aware document chunks             |
| `embeddings.py`                   | Generates document embeddings                  |
| `retrieval.py`                    | Dense semantic retrieval                       |
| `bm25_retrieval.py`               | BM25 keyword retrieval                         |
| `hybrid_retrieval.py`             | Combines dense and BM25 retrieval using RRF    |
| `reranker.py`                     | Cross-encoder reranking                        |
| `query_router.py`                 | Classifies financial queries                   |
| `query_routing_strategy.py`       | Defines query-specific retrieval strategies    |
| `financial_metadata.py`           | Extracts financial characteristics from chunks |
| `financial_scoring.py`            | Applies financial-aware scoring                |
| `evidence_type.py`                | Classifies retrieved evidence                  |
| `evidence_scoring.py`             | Applies evidence-aware scoring                 |
| `financial_evidence_retrieval.py` | Combines the financial retrieval components    |
| `context_builder.py`              | Builds the context passed to the LLM           |
| `generation.py`                   | Generates answers using Groq                   |
| `evaluation_questions.json`       | Contains the retrieval evaluation benchmark    |
| `evaluate_*.py`                   | Evaluation scripts for the retrieval pipeline  |


## Repository Note

The original Microsoft annual report PDF is not included in the GitHub repository.

The application uses the processed retrieval artifacts stored under:

```text
data/processed/
```

These files contain the document chunks and precomputed embeddings required by the deployed application.

API credentials are also excluded from the repository and are loaded through environment variables.


