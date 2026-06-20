""" 
    data_transformers.py
    This file is for loading

"""

import os
import json
import ast


def clean_yelp_value(val_str):
    """Strips Yelp's legacy unicode 'u' prefixes and outer quotes."""
    s = val_str.strip()
    if (s.startswith("u'") and s.endswith("'")) or (s.startswith('u"') and s.endswith('"')):
        s = s[2:-1]
    if (s.startswith("'") and s.endswith("'")) or (s.startswith('"') and s.endswith('"')):
        s = s[1:-1]
    return s.strip()

def process_philly_restaurant_data(file_path: str) -> dict:
    """
    Parses the raw business JSON file and returns a structured dictionary
    of filtered Philadelphia food establishments.

    We dont batch through this one, we need one full object will all of the businesses

    """

    # init variables
    philly_restaurant_map = {}
    restaurant_keywords = {"Restaurants", "Food", "Bars", "Eateries", "Cafes", "Bakeries"}

    ### processing logic
    # file path will be passed in as the full file path

    # validate if path exists
    if not os.path.exists(file_path):
        print("❌ ERROR: Invalid Path or Source files missing.")
        return
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue

                try:
                    biz = json.loads(line)

                    #only process philly lines
                    if biz.get("city", "").strip().lower() != "philadelphia":
                        continue

                    cats_raw = biz.get("categories") or ""
                    cats_list = [c.strip() for c in cats_raw.split(",")] if cats_raw else []

                    ## check to see if any cats match the restaurant categories list
                    if not any(kw in cats_list for kw in restaurant_keywords):
                        continue

                    # -----------------Dynamic Attribute Inspection Engine -----------------------------
                    feature_flags = []
                    raw_attrs = biz.get("attributes") or {}

                    if raw_attrs and isinstance(raw_attrs, dict):
                        for key, val in raw_attrs.items():
                            # remove redundant words like Restaurants and Businesss from key
                            # Ex: "BusinessParking" -> "Parking"
                            clean_key = key.replace("Restaurants", "").replace("Business", "")
                            val_str = str(val).strip()

                            # Case 1: Detect and parse nested stringified dictionaries
                            if val_str.startswith("{") and val_str.endswith("}"):
                                try:
                                    # Safely convert raw text '{'romantic': False...}' into a true Python dict
                                    # EX: nested_dict = {"garage": False, "street": False, "validated": False, "lot": True, "valet": False}
                                    nested_dict = ast.literal_eval(val_str)

                                    for sub_key, sub_val in nested_dict.items():
                                        sub_val_clean = clean_yelp_value(str(sub_val))
                                        if sub_val_clean == "True":
                                            # EX: append Parking_lot
                                            feature_flags.append(f"{clean_key}_{sub_key}")
                                        elif sub_val_clean not in ["False", "None", "{}"]:
                                            # For text values that aren't True, False, None, or {}, 
                                            # append the descriptive string
                                            feature_flags.append(f"{clean_key}_{sub_key}_{sub_val_clean}")
                                except Exception as e:
                                    #Fallback if literal_eval fails on malformed lines... do we need this?
                                    feature_flags.append(f"{clean_key}_{val_str}")

                                    #log error message

                            # Case 2: Simple Bool Flags
                            elif val_str == "True":
                                feature_flags.append(clean_key)

                            # Case 3: Simple value pairs (e.g. Alcohol_full_bar)
                            elif val_str not in ["False", "None", "{}"]:
                                clean_v = clean_yelp_value(val_str)
                                if clean_v:
                                    feature_flags.append(f"{clean_key}_{clean_v}")

                    # grab business id
                    bid = biz.get("business_id")
                    philly_restaurant_map[bid] = {
                        "name": biz.get("name"),
                        "address": biz.get("address"),
                        "postalcode": biz.get("postal_code", "").strip(),
                        "latitude": float(biz.get("latitude")) if biz.get("latitude") is not None else None,
                        "longitude": float(biz.get("longitude")) if biz.get("longitude") is not None else None,
                        "stars_business": float(biz.get("stars", 0)),
                        "categories": cats_list,
                        "features": feature_flags
                    }
                except json.JSONDecodeError:
                    continue # Corrupted JSON line, safely skip to next line
                except Exception as row_error:
                    # Log files to error log 
                    continue

    
    except Exception as file_error:
        print(f"❌ CRITICAL FILE SYSTEM ERROR: {str(file_error)}")
        return {}


    return philly_restaurant_map

def transform_review_to_payload(review_row: dict, business_map: dict) -> dict:
    """ 
        Logic to append business metadata to review and estabish the payload

        in prepare philly sample logic

        Takes in review json and business dict and returns normalized payload
    """

    normalized_payload = None

    # if review row is empty, just return
    if not review_row:
        return

    # grab business id 
    bid = review_row.get("business_id")

    # validate bid is in business map
    if bid in business_map:
        metadata = business_map[bid]

        # Establish address components
        display_address = f"{metadata['address']}, Philadelphia, PA {metadata['postalcode']}"

        # Clean review text safely with a string fallback
        clean_text = review_row.get("text", "").replace("\n", " ").strip()

        normalized_payload = {
            "id": review_row.get("review_id"),
            "metadata": {
                "business_id": bid,
                "restaurant_name": metadata["name"],
                "full_address": display_address,
                "postal_code": metadata["postalcode"],
                "latitude": metadata['latitude'],
                "longitude": metadata['longitude'],
                "review_stars": float(review_row.get("stars", 0)),
                "stars_business": metadata["stars_business"],
                "categories": metadata["categories"],
                "features": metadata["features"],
                "review_text": clean_text
            }
        }

    
    return normalized_payload


