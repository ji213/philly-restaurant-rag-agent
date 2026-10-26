## service to control connections to open AI
import logging 
import time
import random
from openai import OpenAI
from models.schemas import RestaurantCard
from typing import List, Optional
from config import settings

# Configure logger to output to stdout/stderr
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Instantiate module-level logger
logger = logging.getLogger(__name__)

# initialize connection client at module level
try:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
except Exception:
    logger.exception("Exception when trying to establish connection to Open AI client")
    raise


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
                logger.error(f"❌ Operation permanently failed after {max_retries} attempts. Error details: {str(e)}")
                raise e

            # what if initial delay is passed in as 0? default to 1
            sleep_time = delay + random.uniform(0.1, 1.0)

            logger.warning(f"⚠️ Operation failed on attempt {attempt + 1}. Retrying in {sleep_time:.2f} seconds...")

            time.sleep(sleep_time)
            delay *= 2




def inputquery_to_vector(userquery: str) -> List[float]:
    # function to convert users query into a vector
    # connection established at module level

    if not client or not userquery:
        logger.error("Error! Required input variables are missing")
        return []

    # data tranformation on the input user query?

    # need to utilize retry logic on this
    try:
        response = retry_operation(
            lambda: client.embeddings.create(
            model="text-embedding-3-small",
            input=userquery
        ))
    except Exception:
        logger.exception("Exception occurred when attempting to enbed the user query...")
        return []

    # might need to check syntax here? pull vector embedding
    embedding_vector: List[float] =  response.data[0].embedding

    # may need to validate data output here... return for now

    return embedding_vector



def synthesize_response (userquery: str, restaurantCards: List[RestaurantCard]) -> str:
    #function to synthesize response
    # inputs restaurant cards object and users input query
    # generates a tailored response using gpt-4o or or gpt-4o-mini
    ## client.chat.completions.create()

    # if we are missing any input parameters do not proceed
    if not client or not userquery or not restaurantCards:
        logger.error("ERROR! Missing input parameters for synthesization")
        return "Something went wrong. Please try again!"

    # build out context string with RestaurantCards
    context_string = "\n\n".join([
        f"Restaurant: {card.restaurant_name}\n"
        f"Address: {card.full_address} (Zip: {card.postal_code})\n"
        f"Rating: {card.review_stars} stars\n"
        f"Categories: {', '.join(card.categories)}\n"
        f"Sample Review: {card.review_text}"
        for card in restaurantCards
    ])

    # send request to gpt-4o with retry logic
    try:
        response = retry_operation(
            lambda: client.chat.completions.create(
                model="gpt-4o",
                messages= [
                    {
                        "role": "system",
                        "content": "You are an expert Philadepelphia food content creator. Synthesize recommendations based soley on provided context"
                    },
                    {
                        "role": "system",
                        "content": f"Retreived Context:\n{context_string}"
                    },
                    {
                        "role":"user",
                        "content": userquery
                    }
                ],
                temperature=0.7
                #, max_tokens = 1000
        ))
    except Exception:
        logger.exception(" An exception occurred when attempting to synthesize the user response")
        return "Something went wrong. Please try again!"
    
    # gather response and return results
    synthesized_response: str = response.choices[0].message.content

    return synthesized_response