from pinecone import Pinecone 
from config import settings
from models.schemas import RestaurantCard
from typing import List, Optional
import logging

# Configure logger to output to stdout/stderr
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Instantiate module-level logger
logger = logging.getLogger(__name__)


# at Module level so this is initialized only Once when the module is loaded / server boots
try:
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    index = pc.Index(settings.PINECONE_INDEX_NAME)
    logger.info("Successfully connected to Pinecone index")
except Exception:
    logger.exception("Failed to connect to Pinecone client")
    raise

# Surrounding zip map
SURROUNDING_ZIP_MAP = {
    # Center City & Surrounds
    "19102": ["19102", "19103", "19107", "19146"],
    "19103": ["19103", "19102", "19107", "19106", "19146", "19130"],
    "19104": ["19104", "19146", "19130", "19143", "19131"],
    "19106": ["19106", "19107", "19123", "19147", "19103"],
    "19107": ["19107", "19102", "19103", "19106", "19123", "19147"],
    "19123": ["19123", "19106", "19107", "19130", "19122", "19125"],
    "19130": ["19130", "19103", "19123", "19104", "19121"],
    "19146": ["19146", "19103", "19104", "19147", "19145"],
    "19147": ["19147", "19106", "19107", "19146", "19148"],
    "19148": ["19148", "19147", "19145", "19146"],
    "19145": ["19145", "19148", "19146"],

    # Fishtown / River Wards
    "19125": ["19125", "19123", "19122", "19134"],
    "19122": ["19122", "19123", "19125", "19121"],

    # Manayunk & Northwest
    "19127": ["19127", "19128"],
    "19128": ["19128", "19127", "19119", "19144"],
    "19118": ["19118", "19119"],
    "19119": ["19118", "19119", "19128", "19144"],
}

def query_vector_store(vector: List[float], top_k: int = 5, postal_code: Optional[str] = None) -> List[RestaurantCard]:
    """
    Queries Pinecone vector store using query embedding vector and optional postal code filter.
    Returns a list of formatted RestaurantCard objects.
    """
    ## validate input vector is supplied, if not log error and return
    if not vector:
        logger.error("ERROR! No input embedding vector supplied... aborting")
        return []

    filter_dict = None

    if postal_code:
        target_zips = SURROUNDING_ZIP_MAP.get(postal_code, [postal_code])
        filter_dict = {"postal_code": {"$in": target_zips}}
        logger.info("Applying multi-zip filter for %s: %s", postal_code, target_zips)

    # Query pinecone with exception handling 
    try:
        logger.info("Executing Pinecone vector search (top_k = %d) ...", top_k)
        response = index.query(
            namespace=settings.PINECONE_NAMESPACE,
            vector=vector,
            top_k=top_k,
            include_metadata=True,
            filter=filter_dict
        )

        matches = response.get("matches", [])

        ## handle fallbacks in case of 0 matches, using broader search if that happens 
        ## (no zip code filtering)
        if not matches and filter_dict:
            logger.warning("Zero matches found with zip filter %s. Retrying city-wide search...", target_zips)
            response = index.query(
                namespace=settings.PINECONE_NAMESPACE,
                vector=vector,
                top_k=top_k,
                include_metadata=True,
                filter=None
            )

            matches = response.get("matches", [])

        logger.info("Retrieved %d matching records from Pinecone", len(matches))

        # format matches into RestaurantCard PyDantic models
        restaurant_cards = []
        for match in matches:
            meta = match.get("metadata", {})
            restaurant_cards.append(
                RestaurantCard(
                    restaurant_name=meta.get("restaurant_name", "Unknown"),
                    full_address=meta.get("full_address", ""),
                    postal_code=meta.get("postal_code", ""),
                    review_stars=float(meta.get("review_stars", 0.0)),
                    categories=meta.get("categories", []),
                    features=meta.get("features", []),
                    review_text=meta.get("review_text", ""),
                    score=float(match.get("score", 0.0))
                )
            )
        
        return restaurant_cards

    except Exception:
        logger.exception("An error occurred while querying the Pinecone index.")
        return []

