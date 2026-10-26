========================================================================
PHILLY RESTAURANT RAG AGENT
========================================================================

An end-to-end, AI-driven full-stack restaurant recommendation engine that 
combines semantic search, vector database retrieval, and dynamic LLM 
synthesis to surface hyper-localized dining insights across Philadelphia.

Powered by React, Vite, Tailwind CSS, FastAPI, Pinecone, and OpenAI[cite: 5].

------------------------------------------------------------------------
🏗️ SYSTEM ARCHITECTURE & FULL-STACK OVERVIEW
------------------------------------------------------------------------

The application is structured as a modern decoupled client-server architecture:
* **Frontend:** Built with React, Vite, and Tailwind CSS, featuring asynchronous 
  REST API integration, markdown rendering for structured LLM output, and 
  responsive card-based UI design[cite: 5].
* **Backend:** Built with FastAPI and Pydantic validation, orchestrating low-latency 
  semantic similarity queries and payload serialization.
* **Retrieval-Augmented Generation (RAG) Pipeline:** Leverages OpenAI embeddings 
  and Pinecone Vector DB to ground LLM responses in real restaurant review data, 
  mitigating hallucinations and ensuring precise local recommendations[cite: 5].

------------------------------------------------------------------------
🛠️ BACKEND & DATA INGESTION ENGINEERING FEATURES
------------------------------------------------------------------------

To power the RAG agent, the project features a highly configurable, high-throughput 
data ingestion pipeline (import_yelpreviewdata.py) built to process and index massive datasets:

* **Environment-Driven Configuration:** All performance thresholds, execution parameters, 
  and API credentials are fully decoupled and managed via a `.env` configuration file.
* **Multi-Threaded Parallel Processing:** Utilizes a Python `ThreadPoolExecutor` paired 
  with a bounded semaphore throttling mechanism to scale background workers dynamically 
  without exhausting system resources.
* **Resilient Network Architecture:** Implements custom exponential backoff retry 
  policies with random jitter to handle downstream rate limits (HTTP 429) gracefully.
* **Payload Serialization & Optimization:** Automatically chunks heavy text-and-vector 
  payloads to comply with downstream gRPC 4MB network transfer constraints.
* **Fault-Tolerant Logging:** Isolates live execution logs from atomic failure tracking, 
  writing schema mismatches or chunk delivery errors into localized `.log` streams.

------------------------------------------------------------------------
🔮 PLANNED ENHANCEMENTS & ROADMAP
------------------------------------------------------------------------

The project is actively evolving from a single-query prototype into a full conversational AI platform. Planned upgrades include:

* **Conversational Multi-Turn Session State:** Implementing in-memory chat session tracking in React to allow multi-turn dialogue, context-aware follow-up questions, and sliding-window memory management.
* **Backend Contextual Synthesis:** Enhancing the FastAPI recommendation endpoint to accept conversation history payloads, enabling the LLM to resolve pronouns and contextual shifts dynamically.
* **Location & Zip Code Inference:** Adding automated browser geolocation fallback alongside NLP-based neighborhood/zip code extraction from raw user prompts.
* **Conversational UI Redesign:** Shifting to a modern, chat-centric layout with sticky input controls, streaming text animations, and quick-reply suggestion chips.
* **Response Latency Optimizations:** Implementing server-side response streaming and vector embedding caching to significantly reduce end-to-end request latency.


------------------------------------------------------------------------
⚙️ CONFIGURATION (.env)
------------------------------------------------------------------------

The operational behavior and API connections are tuned via your environment file:

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_HOST=your_pinecone_cluster_host_url_if_needed
PINECONE_INDEX_NAME=philly-restaurants
PINECONE_NAMESPACE=standard_namespace
PINECONE_CHUNK_SIZE=100

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Pipeline Process Configuration
MAX_CONCURRENT_REQUESTS=3
BATCH_SIZE=1000

------------------------------------------------------------------------
🚀 AUTOMATED SETUP & LOCAL EXECUTION
------------------------------------------------------------------------

Ensure your root `.env` file is populated before setup.

### 1. First-Time Setup (One-Click Automation)

Run the setup batch files from the root directory to automatically build environments and install dependencies:

* **Backend Setup:**
  Double-click or execute in terminal:
  ```powershell
  .\setup_backend.bat ```

* **Frontend Setup:**
  Double-click or execute in terminal:
  ```powershell
  .\setup_frontend.bat ```

### 2. Running the Application (One-Click Automation)

Run these two files using split terminals from your root directory with powershell

* **Terminal 1: Backend:**
```powershell
.\start_backend.bat ```
(Launches the Uvicorn FastAPI server on http://localhost:8000)

* **Terminal 2: Frontend:**
```powershell
.\start_frontend.bat ```
(Launches the Vite React dev server on http://localhost:5173)


