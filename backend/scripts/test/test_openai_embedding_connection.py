
import os
import json
import ast
import time
import random
import threading
import logging
from dotenv import load_dotenv
from openai import OpenAI


def main():
    # 1. Load environment variables (API keys)
    load_dotenv()

    print(f"Testing Open AI API connection....\n")

    try:
        print(f"Establishing connection...\n")
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        text_batch = ["Text batch string used to test effectiveness of connection"]

        # 2. Fire the batch request to OpenAI
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text_batch
        )

        # print response 
        if response:
            # How we will access it in the real worker:
            vector = response.data[0].embedding
            print(f"✅ Connection successful! Received dense vector array.")
            print(f"Vector Dimensions: {len(vector)}")  # Should print 1536
            print(f"Sample values: {vector[:5]}...")     # Sneak peek of the first 5 floats

    except Exception as e:
        print(f"\n❌ ERROR! Failed to connect...")
        
        # Check if the error came from OpenAI's server response
        if hasattr(e, 'status_code'):
            print(f"🔹 HTTP Status Code: {e.status_code}")
        if hasattr(e, 'code'):
            print(f"🔹 Error Code: {e.code}")
        if hasattr(e, 'message'):
            print(f"🔹 Message: {e.message}")
        else:
            # Fallback for standard Python network/system errors
            print(f"🔹 Details: {str(e)}")




if __name__ == "__main__":
    main()

