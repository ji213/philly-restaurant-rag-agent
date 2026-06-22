========================================================================
NYC RESTAURANT RAG AGENT
========================================================================

An AI-driven restaurant recommendation agent that uses semantic search and
metadata filtering over Yelp datasets to surface hyper-localized dining insights.
Powered by OpenAI, Pinecone, FastAPI, and Vite + React.

------------------------------------------------------------------------
🛠️ BACKEND ARCHITECTURE & DATA PIPELINE
------------------------------------------------------------------------

To power the RAG agent, the project features a highly configurable, high-throughput
data ingestion pipeline (import_yelpreviewdata.py) built to process, embed, and
index massive academic business and review datasets.

Key Engineering Features:
* Environment-Driven Configuration: All critical performance thresholds, execution
  parameters, and API credentials are fully decoupled from the codebase and managed
  dynamically via a .env configuration file.
* Multi-Threaded Parallel Processing: Utilizes a Python ThreadPoolExecutor paired
  with a bounded semaphore throttling mechanism. The system scales dynamically based
  on .env parameters to safely manage concurrent background workers, maximizing network
  throughput without exhausting system RAM.
* Resilient Network Architecture: Implemented a custom exponential backoff retry
  policy with decoupled random jitter execution to handle
  downstream provider rate limits (HTTP 429) gracefully and guarantee data delivery.
* Payload Serialization & Optimization: Automatically chunks heavy text-and-vector
  payloads into structured packets based on configurable threshold limits to strictly
  comply with downstream gRPC 4MB network transfer constraints.
* Fault-Tolerant Logging: Isolated live execution logs from atomic failure tracking,
  writing schema mismatches or chunk delivery errors into localized .log streams to
  ensure uninterrupted pipeline continuity over million-row datasets.

------------------------------------------------------------------------
⚙️ PIPELINE CONFIGURATION (.env)
------------------------------------------------------------------------

The operational behavior and performance characteristics of the pipeline can be
tuned directly from your environment file:

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_HOST=your_pinecone_cluster_host_url_if_needed
PINECONE_INDEX_NAME=philly-restaurants
PINECONE_NAMESPACE=standard_namespace
PINECONE_CHUNK_SIZE=100       # Maximizes payload size safely below gRPC 4MB limits

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Pipeline Process Configuration
MAX_CONCURRENT_REQUESTS=3     # Limits active thread pool background workers
BATCH_SIZE=1000               # Number of rows compiled before handing off to a worker


------------------------------------------------------------------------
🚀 HOW TO RUN THE INGESTION PIPELINE
------------------------------------------------------------------------

1. Ensure your .env file is fully populated in the project root.
2. Place the Yelp academic datasets in the /Data directory.
3. Launch the orchestrator script or run bat file (run_backend_pipeline.bat):
   python scripts/import_yelpreviewdata.py



========================================================================