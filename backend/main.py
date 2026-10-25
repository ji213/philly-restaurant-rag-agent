import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from models.schemas import RecommendationRequest, RecommendationResponse
from services.openai_service import inputquery_to_vector, synthesize_response
from services.pinecone_service import query_vector_store


# Configure logger to output to stdout/stderr
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application instance
app = FastAPI(
    title="Philadelphia Restaurant Recommendation API",
    description="Vector search and LLM-synthesized recommendation engine",
    version="1.0.0"
)

# Configure CORS Middleware to allow React/Vite frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def read_root():
    """Health check root endpoint"""
    return {"status": "online", "message": "Philadelphia Restaurant API is running"}


@app.post("/api/recommend", response_model=RecommendationResponse)
def recommend_restaurants(payload: RecommendationRequest) -> RecommendationResponse:
    """
        Orchestration from request to recommendation reesponse
    """

    logger.info("Received recommendation request for query: '%s' (Zip: %s)", payload.query, payload.postal_code)

    try:
        # Convert user text to vector
        vector = inputquery_to_vector(payload.query)
        if not vector:
            logger.error("Failed to generate embedding vector for query")
            raise HTTPException(
                status_code=500,
                detail="Failed to process search query embedding"
            )
        
        # Query Pinecone db using vector + optional zip
        restaurant_cards = query_vector_store(
            vector=vector,
            top_k=5,
            postal_code=payload.postal_code
        )

        if not restaurant_cards:
            logger.warning("No matching restaurants retreived ...")
            return RecommendationResponse(
                query=payload.query,
                recommendation="I couldn't find any matching restaurants with your criteria. Can you try again?",
                restaurants=[]
            )
        
        #Synthesize recommendation
        synthesized_text = synthesize_response(
            userquery=payload.query,
            Restaurant_cards=restaurant_cards
        )

        #Package and return final response payload
        return RecommendationResponse(
            query=payload.query,
            recommendation=synthesized_text,
            restaurants=restaurant_cards
        )
    except HTTPException as http_ex:
        #Re-reaise explicit HTTP exceptions so FastAPI handles status codes correctly
        raise http_ex
    except Exception:
        logger.exception("Unexpected error occurred during recommendation orchestration.")
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred while generating recommendations..."
        )

