import os
import json

def validate_first_100_businesses():
    print("=" * 70)
    print("Scanning First 100 Records from True Business Dataset...")
    print("=" * 70)

    # 1. Path Setup - Pointing directly to your production file
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    prod_biz_path = os.path.join(base_dir, 'Data', 'yelp_academic_dataset_business.json')

    if not os.path.exists(prod_biz_path):
        print(f"❌ ERROR: Production file not found at: {prod_biz_path}")
        print("Please verify that the raw 'yelp_academic_dataset_business.json' is in your Data/ folder.")
        return

    restaurant_count = 0
    non_restaurant_count = 0

    try:
        with open(prod_biz_path, 'r', encoding='utf-8') as f:
            for idx, line in enumerate(f, 1):
                if restaurant_count == 100:
                    break

                if not line.strip():
                    continue
                
                biz = json.loads(line)
                cats = biz.get("categories") or ""
                location_state = biz.get('state') or ""

                #Simple bool flag to check if its a food/restaurant place
                is_restaurant = any(keyword in cats for keyword in ["Restaurants", "Food", "Bars", "Eateries", "Cafes"])
                is_new_york  = any(keyword in location_state for keyword in ["NY"])

                if is_restaurant and is_new_york:
                    restaurant_count += 1
                    print(f"🟢 [RECORD {idx}] RESTAURANT FOUND:")
                    print(f"   ID        : {biz.get('business_id')}")
                    print(f"   Name      : {biz.get('name')}")
                    print(f"   Location  : {biz.get('city')}, {biz.get('state')} {biz.get('postal_code')}")
                    print(f"   Categories: {cats}")
                    print("-" * 50)
                else:
                    non_restaurant_count += 1
                    # print(f"⚪ [RECORD {idx}] Skipping non-food business: {biz.get('name')} ({cats[:40]}...)")

        print("\n" + "=" * 70)
        print("SCANNED SUMMARY (FIRST 100 RECORDS):")
        print(f"   Total Food/Restaurant Locations: {restaurant_count}")
        print(f"   Total Other/Irrelevant Businesses: {non_restaurant_count}")
        print("=" * 70)

    except Exception as e:
        print(f"❌ Exploration failed: {str(e)}")




if __name__ == "__main__":
    validate_first_100_businesses()