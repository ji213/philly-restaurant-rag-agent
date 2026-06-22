"""

    import_yelpreviewdata.py
    Process to Import yelp data from kaggle dataset file. 
    Plan to migrate this process to a live API feed once we get an end-to-end MVP

"""

import os
import sys
import json
import ast
import time
import random
import threading
import logging
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from pinecone import Pinecone
from openai import OpenAI
from utils.data_transformers import process_philly_restaurant_data
from utils.pipeline_workers import process_review_pipeline


""" 
Process Outline 
"""

"""
If your pipeline encounters a network failure at row 340,000, 
you don't want to restart from the beginning of the file. You can easily track this by writing a tiny local checkpoint.json file. 
Each time a thread successfully completes a batch, it logs the last successfully parsed line number or file byte offset. When you re-run the main file, it reads the checkpoint file and uses an iterator skip to pick up right where it left off.
"""
## *** need logic to track errors into custom log file, we will create a directory
## *** all of step 3 will be part of the batch process, which will run async
## *** max 5 concurrent processes
## 3a - Extract raw strings from the batch metadata
## 3b - once batch is ingested, pass into embedding model text-embedding-3-small
## 3c - take embedded matrix and attach payload to it, in format required by Pinecone
## 3d - call Pinecone API and post into philly-restaurants namespace (offical name tbd)

## 4 - track completed rows, and exit process once file is completely done
## need to add logic after the main processing loop finishes that checks
## if current_batch has items, submit them to the executor one last time before exiting


# Create a folder for logs if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Reconfigure stdout/stderr to support emojis natively in the Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Configure the logging engine
logging.basicConfig(
    level=logging.INFO,  # Captures INFO, WARNING, and ERROR logs
    format="%(asctime)s [%(threadName)s] %(levelname)s: %(message)s",
    handlers=[
        # StreamHandler will now inherit the updated sys.stdout encoding
        # keep this commented out to keep the terminal calm
        # logging.StreamHandler(sys.stdout),                      
        
        # Explicitly pass encoding="utf-8" to the FileHandler
        logging.FileHandler("logs/pipeline_run.log", encoding="utf-8")
    ]
)

def main():

    # 1. Load environment variables (API keys)
    load_dotenv()

    # build out path to business file
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    biz_path = os.path.join(base_dir, 'Data', 'yelp_academic_dataset_business.json')

    # gather philly business data
    # should I put a try exception as E block outside of this?
    logging.info("⏳ Step 1: Processing Philadelphia restaurant maps...")
    print("⏳ Step 1: Processing Philadelphia restaurant maps...")
    philly_restaurant_map = process_philly_restaurant_data(biz_path)
    logging.info(f"✅ Step 1 Complete: {len(philly_restaurant_map)} restaurants loaded.")
    print(f"✅ Step 1 Complete: {len(philly_restaurant_map)} restaurants loaded.")

    logging.info("⏳ Step 2: Initializing API clients...")
    print("⏳ Step 2: Initializing API clients...")
    try:
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        # Connect to your specific vector index
        index = pc.Index(os.getenv("PINECONE_INDEX_NAME", "philly-restaurants"))

        logging.info("✅ Step 2 Complete: API connections securely established.")
        print("✅ Step 2 Complete: API connections securely established.")

    except Exception as e:
        logging.critical(f"❌ CRITICAL INITIALIZATION FAILURE: Could not connect to downstream APIs. Error: {str(e)}")
        # Exit execution immediately since the pipeline cannot function without valid API clients
        return

    
    # 3. Hand everything off to the parallel processing engine
    logging.info("🚀 Step 3: Launching parallel review processing pipeline...")
    print("🚀 Step 3: Launching parallel review processing pipeline...")
    process_review_pipeline(philly_restaurant_map, openai_client, index)







if __name__ == "__main__":
    main()


