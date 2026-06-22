import os
import json
import logging
import time
import random
from dotenv import load_dotenv
from pinecone import Pinecone
from pinecone import Index  # Import the class definition
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor
from utils.data_transformers import transform_review_to_payload
import threading



def retry_operation(operation, max_retries=3, initial_delay=2):
    ## helper function to retry failures

    if initial_delay <= 0:
        initial_delay = 1

    max_retries = int(max_retries)

    delay = initial_delay
    for attempt in range(max_retries):
        try:
            return operation()
        except Exception as e:
            if attempt == max_retries - 1:
                logging.error(f"❌ Operation permanently failed after {max_retries} attempts. Error details: {str(e)}")
                raise e

            # what if initial delay is passed in as 0? default to 1
            jitter = random.uniform(1.0, 3.0)
            sleep_time = delay * jitter

            logging.warning(f"⚠️ Operation failed on attempt {attempt + 1}. Retrying in {sleep_time:.2f} seconds...")

            time.sleep(sleep_time)
            delay *= 2

            


def process_and_upload_batch_worker(openai_client: OpenAI, index: Index, batch_data, namespace, failure_log_path, semaphore):
    """
    Worker function executed inside background threads.

    -- Ingest batch_data
    -- embed batch_data with text embedding model
    -- pass results in expected format into the pinecone vector db
    """
    # Work on payload generation before we do this

    # randomized delay to ease pipeline
    time.sleep(random.uniform(0.1, 0.5))

    # Identify exactly which worker thread is executing this task
    thread_name = threading.current_thread().name
    
    try:
        logging.info(f"▶️ [{thread_name}] Starting processing simulation for batch of size {len(batch_data)}...")
        
        if not batch_data:
            return


        # embed batch of x payloads into open AI model
        # The absolute technical limit is 2,048 input strings per API call.
        # response payload will have matrix
        #       -- index will match index of review from the input batch
        # once we receive the results, generate pinecone_payload to be ingested by pinecone
        # use as little API calls as possible to minimize cost

        # list to assemble final payload for Pinecone
        output_payload = []
        chunk_size = int(os.getenv("PINECONE_CHUNK_SIZE"))

        # Extract just the review text strings
        review_to_embed = [row["metadata"]["review_text"] for row in batch_data]

        # One batch call 
        response = retry_operation(
            lambda: openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=review_to_embed
        ))

        # Map vector result from response back by positional index
        for i, row in enumerate(batch_data):
            # extract the matching vector matrix
            vector_matrix = response.data[i].embedding

            # Structure the item exactly how Pinecone's client expects it
            vector_item = {
                "id": row["id"],
                "values": vector_matrix,
                "metadata": row["metadata"]
            }

            # append to result
            output_payload.append(vector_item)
        
        # now we have output_payload constructed, process into pinecone
        logging.info(f"🚀 [{thread_name}] Transmitting vectors to Pinecone Index under namespace '{namespace}'...")

        for x in range(0, len(output_payload), chunk_size):
            chunk = output_payload[x: x + chunk_size]

            # push chunk
            try:
                retry_operation(
                    lambda: index.upsert(vectors=chunk, namespace=namespace)
                )
            except Exception as chunk_error:
                with open(failure_log_path, "a", encoding="utf-8") as f:
                    f.write(f"--- Chunk Failure on lines {x} to {x+len(chunk)} ---\n{str(chunk_error)}\n\n")


        logging.info(f"✅ [{thread_name}] Batch transmission completed successfully.")

    except Exception as worker_error:
        # Catch and trace any issues without crashing the main orchestrator thread
        logging.error(f"❌ [{thread_name}] Critical error during simulated worker execution: {str(worker_error)}")
        with open(failure_log_path, "a", encoding="utf-8") as f:
            f.write(f"--- Batch Failure Details ({thread_name}) ---\n")
            f.write(f"Error: {str(worker_error)}\n\n")
        
    finally:
        # Releasing the semaphore inside the 'finally' block ensures that even if an exception 
        # explodes above, this thread slot is unlocked, allowing the main loop to continue.
        semaphore.release()
        logging.info(f"🔓 [{thread_name}] Semaphore released. Active thread slots replenished.")




def process_review_pipeline(business_map: dict, openai_client: OpenAI, index: Index) ->None:
    # Business Map passed in
    # do i need to load_dotenv?
    load_dotenv()

    # establish path for review file
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    review_path = os.path.join(base_dir, 'Data', 'yelp_academic_dataset_review.json')

    # Configuration Parameters
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
                            payload = transform_review_to_payload(rev, business_map)
                            if payload:
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
                    except json.JSONDecodeError as decode_err:
                        # Log or print malformed row warning
                        # Open with safe utf-8 append parameters
                        with open(failure_log_path, "a", encoding="utf-8") as f:
                            f.write(f"--- Parsing Error at Line {line_count} ---\n")
                            f.write(f"Error details: {str(decode_err)}\n\n")

                        continue
                    except Exception as row_error:
                        with open(failure_log_path, "a", encoding="utf-8") as f:
                            f.write(f"--- Unexpected Error at Line {line_count} ---\n")
                            f.write(f"Error details: {str(row_error)}\n\n")

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

