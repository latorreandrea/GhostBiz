"""
Base Functionality Test

File created to test the library's efficiency step by step, 
in order to understand how to use it in the most effective way.

This test follows the official OSMnx examples from:
https://github.com/gboeing/osmnx-examples/blob/main/notebooks/16-download-osm-geospatial-features.ipynb

The goal is to progressively test each OSMnx feature to identify 
the optimal approach for extracting business data from Copenhagen.
"""

import osmnx as ox
import pandas as pd
import time
from pathlib import Path

# Create data directory if it doesn't exist
Path("test_data").mkdir(parents=True, exist_ok=True)

def osmnx_connection(): ## FIRST STEP COMPLETED
    """
    Step 1: Test basic OSMnx connectivity and simple feature extraction
    Based on example: https://github.com/gboeing/osmnx-examples notebook #16
    """
    try:
        # Test 1a: Very simple query - get building footprints (like in example)
        print("\n1a. Testing simple building footprints query...")
        place = "Piedmont, California, USA"  # From official example
        tags = {"building": True}
        
        start_time = time.time()
        gdf = ox.features.features_from_place(place, tags)
        duration = time.time() - start_time
        
        print(f"    ✅ SUCCESS: Found {len(gdf)} buildings in {duration:.1f}s")
        print(f"    📋 Columns: {list(gdf.columns)[:8]}...")  # First 8 columns
        
        # Save for inspection
        if len(gdf) > 0:
            gdf.to_file("test_data/step1a_buildings.gpkg", driver="GPKG")
            print(f"    💾 Saved to test_data/step1a_buildings.gpkg")
        
        return True
        
    except Exception as e:
        print(f"    ❌ FAILED: {e}")
        return False

def prototype_osmnx_connection(): ## 
    """
    Step 2: Test basic OSMnx connectivity and simple feature extraction
    using the real Copenhagen place
    """
    try:
        # Test 2a: Very simple query - get building footprints for Copenhagen
        print("\n2a. Testing simple building footprints query for Copenhagen...")
        place = "Copenhagen, Denmark"
        tags = {"building": True}

        start_time = time.time()
        gdf = ox.features.features_from_place(place, tags)
        duration = time.time() - start_time

        print(f"    ✅ SUCCESS: Found {len(gdf)} buildings in {duration:.1f}s")
        print(f"    📋 Columns: {list(gdf.columns)[:8]}...")  # First 8 columns

        # Save for inspection
        if len(gdf) > 0:
            gdf.to_file("test_data/step2a_buildings.gpkg", driver="GPKG")
            print(f"    💾 Saved to test_data/step2a_buildings.gpkg")

        return True

    except Exception as e:
        print(f"    ❌ FAILED: {e}")
        return False

def main():
    """
    Main function to run the tests step by step
    """
    print("Starting OSMnx Base Functionality Test...\n")
    
    # # Step 1: Basic connectivity
    # step1_success = osmnx_connection()    
    # if not step1_success:
    #     print("\n❌ CRITICAL: Basic OSMnx functionality failed")
    #     print("Check internet connection and OSMnx installation")
    #     return
    # ## FIRST STEP COMPLETED
    # Step 2: Prototype connection with Copenhagen
    step2_success = prototype_osmnx_connection()
    if not step2_success:
        print("\n❌ CRITICAL: Prototype OSMnx functionality failed")
        print("Check internet connection and OSMnx installation")
        return
    # first bug the library find a city called Copenhagen, but not the one in Denmark
if __name__ == "__main__":
    main()