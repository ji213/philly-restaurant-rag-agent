import os
import json
import logging
from dotenv import load_dotenv
from pinecone import Pinecone
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor
from utils.data_transformers import transform_review_to_payload
import threading

# Create a folder for logs if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure the logging engine
logging.basicConfig(
    level=logging.INFO,  # Captures INFO, WARNING, and ERROR logs
    format="%(asctime)s [%(threadName)s] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(),                      # Streams clean logs directly to your terminal console
        logging.FileHandler("logs/pipeline_run.log")  # Simultaneously appends everything to a file
    ]
)

def process_and_upload_batch_worker(openai_client, index, batch_data, namespace, failure_log_path, semaphore):
    """
    Worker function executed inside background threads.
    """
    # Work on payload generation before we do this




def process_review_pipeline(business_map: dict, openai_client: OpenAI, index) ->None:
    # Business Map passed in

    # establish path for review file
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    review_path = os.path.join(base_dir, 'Data', 'yelp_academic_dataset_review.json')

    # Configuration Parameters
    # Maybe we can store these in env file
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", 5)) 
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", 1000))

    # Pinecone will create this automatically
    NAMESPACE = os.getenv("PINECONE_NAMESPACE", "standard_namespace")

    #Need to create a log folder for this
    failure_log_dir = "logs"
    os.makedirs(failure_log_dir, exist_ok=True)
    failure_log_path = os.path.join(failure_log_dir, "ingestion_failures.log")

    # Init Throttling Semaphore
    # This guarantees no more than 5 batches sit in RAM/Flight simultaneously
    semaphore = threading.BoundedSemaphore(MAX_CONCURRENT_REQUESTS)

    current_batch = []

    print(f"\nInitializing ThreadPoolExecutor with max_workers={MAX_CONCURRENT_REQUESTS}...")

    #Use context manager to handle pool shutdown correctly
    #Need to name threads here to add info to log file 
    #probably need to do the double try exception block here, one outside the executor
    # and one inside the loop
    try:
        with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_REQUESTS, thread_name_prefix="ReviewWorker") as executor:
            with open(review_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        rev = json.loads(line)
                        bid = rev.get("business_id")

                        if bid in business_map:
                            # ... [Keep payload formatting structure from previous script] ...
                            payload = transform_review_to_payload(rev, business_map, bid)
                            current_batch.append(payload)

                            if len(current_batch) == BATCH_SIZE:
                                # Block the main thread here if our 5 background slots are full
                                semaphore.acquire()

                                # Pass task to worker thread
                                executor.submit(
                                    process_and_upload_batch_worker,
                                    openai_client, index, current_batch, NAMESPACE, failure_log_path, semaphore
                                )

                                #Refresh variable for next batch
                                current_batch = []
                    except json.JSONDecodeError:
                        # Log or print malformed row warning
                        continue
                    except Exception as row_error:
                        # Catch other parsing edge cases safely
                        continue

                #Final sweep for trailing records
                if current_batch:
                    semaphore.acquire()
                    executor.submit(
                        process_and_upload_batch_worker,
                        openai_client, index, current_batch, NAMESPACE, failure_log_path, semaphore
                    )
    except FileNotFoundError:
        logging.info(f"❌ Thread: {threading.current_thread().name} - ERROR: Review file not found at {review_path}")
    except Exception as file_error:
        logging.info(f"❌ Thread: {threading.current_thread().name} - CRITICAL FILE SYSTEM ERROR: {str(file_error)}")
    
    print("\n🏁 Pipeline complete! All threads shut down cleanly.")

