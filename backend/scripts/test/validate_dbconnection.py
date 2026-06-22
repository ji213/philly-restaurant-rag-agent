import os
from dotenv import load_dotenv
from pinecone import Pinecone

def test_pinecone_connection():
    print("=" * 60)
    print("Initializing Pinecone Connection Validation...")
    print("=" * 60)

    # 1. Load environment variables from backend/.env
    # We specify the exact path to make sure it reads cleanly from the scripts folder
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
        print("✅ Found and loaded .env file configuration.")
    else:
        print("❌ ERROR: Could not find .env file at expected path:", dotenv_path)
        return

    # 2. Extract configuration parameters
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME")
    host_url = os.getenv("PINECONE_HOST")

    # Guardrails: Ensure no empty params
    if not all([api_key, index_name, host_url]):
        print("❌ ERROR: One or more environment variables are missing!")
        print(f"   PINECONE_API_KEY: {'Loaded' if api_key else 'MISSING'}")
        print(f"   PINECONE_INDEX_NAME: {'Loaded' if index_name else 'MISSING'}")
        print(f"   PINECONE_HOST: {'Loaded' if host_url else 'MISSING'}")
        return

    try:
        # 3. Initialize the Pinecone client
        print(f"Connecting to Pinecone organization using dev-key...")
        pc = Pinecone(api_key=api_key)

        # 4. Target your specific serverless index
        print(f"Targeting index: '{index_name}'...")
        index = pc.Index(name=index_name, host=host_url)

        # Fetch the physical configuration of the index rather than just its data stats
        index_description = pc.describe_index(name=index_name)

        # 5. Ping the index by fetching statistics
        stats = index.describe_index_stats()
        
        print("\n" + "🎉 SUCCESS: Connected to Pinecone Database cleanly!")
        print("-" * 40)
        print(f"   Index Name : {index_name}")
        print(f"   Total Vectors: {stats.get('total_vector_count', 0)}")
        print(f"   Dimension    : {stats.get('dimension')}")
        print(f"   Distance Metric: {index_description.metric}")
        print("-" * 40)
        
    except Exception as e:
        print("\n❌ ERROR: Connection failed!")
        print(f"Details: {str(e)}")
        print("\nDouble-check that your PINECONE_HOST URL includes 'https://' and your API key is active.")

if __name__ == "__main__":
    test_pinecone_connection()