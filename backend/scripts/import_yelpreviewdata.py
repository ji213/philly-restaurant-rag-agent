"""
    Process to Import yelp data from kaggle dataset file. 
    Plan to migrate this process to a live API feed once we get an end-to-end MVP

"""

import os
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


## Configure final version of functions used to clean/normalize import data
## import that file into this file once done
## generate test script to test effectiveness of process and load top 100 ( we can adapt our current process)


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

def main():
    # build out path to business file
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    biz_path = os.path.join(base_dir, 'Data', 'yelp_academic_dataset_business.json')

    # gather philly business data
    # should I put a try exception as E block outside of this?
    
    philly_restaurant_map = process_philly_restaurant_data(biz_path)

    # loop through review file 1 by one
    # normalize payloads
    # append payload to current batch
    # start processing when batch gets to 1000; send processing to thread once it is open







if __name__ == "__main__":
    main()


