import os
import pandas as pd
import time
from osm_extractor import extract_osm_businesses
from google_checker import check_google_business

# Import all configuration parameters
from config import GOOGLE_API_KEY, DEFAULT_PLACE, DEFAULT_RADIUS, API_DELAY, DEFAULT_TAGS


def main(checker=False, output_file="ghostbiz_results.csv", place_name=None, tags=None):
    """
    Main function to extract OSM business data with optional Google Places verification.
    
    Args:
        checker (bool): If True, cross-references with Google Places API. 
                       If False, exports only OSM data directly to CSV.
        output_file (str): Path to the output CSV file
        place_name (str): Place to extract businesses from. If None, uses DEFAULT_PLACE from config
        tags (dict): OSM tags to filter by. If None, uses DEFAULT_TAGS from config
    """
    # Use config defaults if not provided
    if place_name is None:
        place_name = DEFAULT_PLACE
    if tags is None:
        tags = DEFAULT_TAGS
        
    print(f"Starting GhostBiz extraction...")
    print(f"Location: {place_name}")
    print(f"Tags: {tags}")
    print(f"Checker mode: {'enabled' if checker else 'disabled'}")

     # Step 1: Extract businesses from OpenStreetMap
    print("Extracting businesses from OpenStreetMap...")
    df_osm = extract_osm_businesses(place_name=place_name, tags=DEFAULT_TAGS)
    print(f"Found {len(df_osm)} businesses from OSM")

    if not checker:
        # Direct export mode - save OSM data directly to CSV
        print(f"Checker disabled - Saving OSM data directly to CSV...")
        df_osm.to_csv(output_file, index=False)
        print(f"OSM data saved to {output_file}")
        print(f"Total businesses exported: {len(df_osm)}")
        
        # Debug: Show coordinate range to verify location
        if len(df_osm) > 0:
            lat_range = (df_osm['lat'].min(), df_osm['lat'].max())
            lon_range = (df_osm['lon'].min(), df_osm['lon'].max())
            print(f"Coordinate ranges:")
            print(f"Latitude: {lat_range[0]:.4f} to {lat_range[1]:.4f}")
            print(f"Longitude: {lon_range[0]:.4f} to {lon_range[1]:.4f}")
        
        return df_osm

    # Checker mode enabled - cross-reference with Google Places
    print(f"Checker enabled - Cross-referencing with Google Places API...")
    print(f"Using API delay: {API_DELAY} second(s) between calls")
    print(f"Using search radius: {DEFAULT_RADIUS} meters")
    # Check for GOOGLE_API_KEY
    try:
        # Already imported at top, but let's validate it's not the placeholder
        if GOOGLE_API_KEY == "Replace with your actual API key":
            print("Error: Please replace the placeholder with your actual Google API key in config.py")
            return None
        print("Google API key loaded from config")
    except (ImportError, NameError):
        print("Error: config.py not found or GOOGLE_API_KEY not defined")
        print("Please create config.py with your Google API key")
        return None
    
    # Step 2: Load existing results (if any) for checkpoint functionality
    if os.path.exists(output_file):
        df_done = pd.read_csv(output_file)
        done_names = set(df_done["osm_name"])
        print(f"Resuming from checkpoint. {len(done_names)} businesses already processed.")
    else:
        df_done = pd.DataFrame()
        done_names = set()

    # Step 3: Process each business with Google Places verification
    total_businesses = len(df_osm)
    processed_count = len(done_names)
    
    for i, row in df_osm.iterrows():
        # Skip already processed businesses
        if row["name"] in done_names:
            continue
        
        processed_count += 1
        print(f"[{processed_count}/{total_businesses}] Checking: {row['name']}...")
        
        # Check if business already has a website from OSM
        if pd.notna(row.get("website")) and row["website"] not in ["", None]:
            print(f"Has OSM website: {row['website']} - Skipping Google check")
            entry = {
                "osm_name": row["name"],
                "lat": row["lat"],
                "lon": row["lon"],
                "google_name": None,
                "website": row["website"],  # Use OSM website
                "status": "HAS_OSM_WEBSITE",
                "not_found": False
            }
        else:
            print(f"No OSM website found - Checking Google Places...")
            try:
                google_data = check_google_business(
                    row["name"], 
                    row["lat"], 
                    row["lon"], 
                    GOOGLE_API_KEY,
                    radius=DEFAULT_RADIUS  # Use configured radius
                    )
                
                entry = {
                    "osm_name": row["name"],
                    "lat": row["lat"],
                    "lon": row["lon"],
                    "google_name": google_data["google_name"],
                    "website": google_data["website"],
                    "status": google_data["status"],
                    "not_found": not google_data["found"]
                }
                
                # Display result
                if google_data["found"]:
                    website_status = f"Website: {google_data['website']}" if google_data['website'] else "No website"
                    print(f"Found on Google: {google_data['google_name']} | {website_status}")
                else:
                    print(f"Not found on Google Places")
                    
            except Exception as e:
                print(f"Error checking Google Places: {e}")
                entry = {
                    "osm_name": row["name"],
                    "lat": row["lat"],
                    "lon": row["lon"],
                    "google_name": None,
                    "website": None,
                    "status": "API_ERROR",
                    "not_found": True
                }
            
            # Rate limiting - only for Google API calls
            time.sleep(1)

        # Add to results DataFrame
        df_done = pd.concat([df_done, pd.DataFrame([entry])], ignore_index=True)

        # Save immediately (checkpoint system)
        df_done.to_csv(output_file, index=False)

    print(f"Processing completed!")
    print(f"Total businesses processed: {processed_count}")
    print(f"Results saved to: {output_file}")
    
    return df_done


if __name__ == "__main__":
    # Examples of how to run the script:
    
    # Option 1: Extract only OSM data using all config defaults
    print("=== OSM ONLY MODE (Uses DEFAULT_PLACE and DEFAULT_TAGS) ===")
    osm_data = main(checker=False, output_file="osm_businesses.csv")
    
    # Option 2: Extract from a different city with default tags
    # print("=== DIFFERENT CITY ===")
    # osm_data = main(checker=False, place_name="Milan, Italy", output_file="milan_businesses.csv")
    
    # Option 3: Custom location and tags
    # print("=== CUSTOM SEARCH ===")
    # custom_tags = {"amenity": ["restaurant", "cafe"]}
    # osm_data = main(checker=False, place_name="Milan, Italy", tags=custom_tags, output_file="milan_restaurants.csv")
    
    # Option 4: Full mode with Google Places verification
    # print("=== FULL VERIFICATION MODE ===")
    # verified_data = main(checker=True, output_file="ghostbiz_results.csv")