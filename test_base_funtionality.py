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
import geopandas as gpd

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

def prototype_osmnx_connection(): ## SECOND STEP COMPLETED
    """
    Step 2: Test basic OSMnx connectivity and simple feature extraction
    using the real Copenhagen place
    """
    try:
        # Test 2a: Very simple query - get building footprints for Copenhagen
        print("\n2a. Testing simple building footprints query for Copenhagen...")
        # place = "Copenhagen, Denmark" first error now we try Copenhagen Municipality, Denmark
        place = "Copenhagen Municipality, Denmark"
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

def prototype_amenity_osmnx_connection(): ## SECOND STEP COMPLETED
    """
    Step 3: Test tags OSMnx functionality using the real Copenhagen place
    """
    try:
        # Test 3a: Very simple query - get amenities for Copenhagen
        print("\n3a. Testing simple amenities query for Copenhagen...")
        place = "Copenhagen Municipality, Denmark"
        tags = {"amenity": True}

        start_time = time.time()
        gdf = ox.features.features_from_place(place, tags)
        duration = time.time() - start_time

        print(f"    ✅ SUCCESS: Found {len(gdf)} amenities in {duration:.1f}s")
        print(f"    📋 Columns: {list(gdf.columns)[:8]}...")  # First 8 columns

        # Save for inspection
        if len(gdf) > 0:
            gdf.to_file("test_data/step3a_amenities.gpkg", driver="GPKG")
            print(f"    💾 Saved to test_data/step3a_amenities.gpkg")

        return True

    except Exception as e:
        print(f"    ❌ FAILED: {e}")
        return False

        place = "Copenhagen Municipality, Denmark"
        tags = {"building": True}

        start_time = time.time()
        gdf = ox.features.features_from_place(place, tags)
        duration = time.time() - start_time

        print(f"    ✅ SUCCESS: Found {len(gdf)} buildings in {duration:.1f}s")
        print(f"    📋 Columns: {list(gdf.columns)[:8]}...")  # First 8 columns

        # Save for inspection
        if len(gdf) > 0:
            gdf.to_file("test_data/step3a_buildings.gpkg", driver="GPKG")
            print(f"    💾 Saved to test_data/step3a_buildings.gpkg")

        return True

    except Exception as e:
        print(f"    ❌ FAILED: {e}")
        return False

def create_table(file_path):
    """
    Read a file and return its content
    """
    # try:
    #     gdf = gpd.read_file(file_path)
    #     print(f"✅ Loaded file: {file_path}")
    #     print(gdf.head())
    #     print(f"📋 All columns ({len(gdf.columns)}): {list(gdf.columns)}")
    #     return gdf
    # except Exception as e:
    #     print(f"❌ Failed to load file: {e}")
    #     return None
    ## this works! level up the function to create a table
    try:
        # Load the full dataset
        gdf = gpd.read_file(file_path)
        print(f"Loaded {len(gdf)} features")
        
        # Essential business fields mapping
        business_data = []
        
        for idx, row in gdf.iterrows():
            
            # 1. BUSINESS NAME
            business_name = row.get('name', None)
            if pd.isna(business_name) or business_name == '':
                continue  # Skip unnamed businesses
            
            # 2. ADDRESS (combine multiple address fields)
            address_components = []
            address_fields = [
                'addr:housenumber', 'addr:street', 
                'addr:postcode', 'postal_code',
                'addr:city', 'addr:suburb'
            ]
            
            for field in address_fields:
                value = row.get(field, None)
                if pd.notna(value) and str(value).strip() != '':
                    address_components.append(str(value).strip())
            
            address = ', '.join(address_components) if address_components else None
            
            # 3. WEBSITE (check multiple website fields)
            website = None
            website_fields = ['website', 'url', 'contact:website', 'operator:website', 'brand:website']
            
            for field in website_fields:
                value = row.get(field, None)
                if pd.notna(value) and str(value).strip() != '':
                    website = str(value).strip()
                    break
            
            # 4. EMAIL (check multiple email fields)
            email = None
            email_fields = ['email', 'contact:email']
            
            for field in email_fields:
                value = row.get(field, None)
                if pd.notna(value) and str(value).strip() != '':
                    email = str(value).strip()
                    break
            
            # 5. PHONE (check multiple phone fields)
            phone = None
            phone_fields = ['phone', 'contact:phone', 'fax', 'contact:fax']
            
            for field in phone_fields:
                value = row.get(field, None)
                if pd.notna(value) and str(value).strip() != '':
                    phone = str(value).strip()
                    break
            
            # 6. OPENING HOURS
            opening_hours = None
            hours_fields = ['opening_hours', 'opening_hours:signed', 'service_times']
            
            for field in hours_fields:
                value = row.get(field, None)
                if pd.notna(value) and str(value).strip() != '':
                    opening_hours = str(value).strip()
                    break
            
            # 7. BUSINESS TYPE (determine from available fields)
            business_type = None
            type_priority = [
                ('shop', 'Shop'),
                ('amenity', 'Service'),  
                ('tourism', 'Tourism'),
                ('office', 'Office'),
                ('craft', 'Craft'),
                ('leisure', 'Leisure'),
                ('healthcare', 'Healthcare')
            ]
            
            for field, category in type_priority:
                value = row.get(field, None)
                if pd.notna(value) and str(value).strip() != '':
                    specific_type = str(value).replace('_', ' ').title()
                    business_type = f"{category}: {specific_type}"
                    break
            
            if not business_type:
                business_type = "Unknown"
            
            # 8. COORDINATES (from geometry)
            try:
                centroid = row.geometry.centroid
                latitude = centroid.y
                longitude = centroid.x
            except:
                latitude = None
                longitude = None
            
            # 9. OSM ID (for reference)
            osm_id = row.get('id', row.get('osmid', None))
            
            # Add to business data
            business_data.append({
                'business_name': business_name,
                'business_type': business_type,
                'address': address,
                'phone': phone,
                'email': email,
                'website': website,
                'opening_hours': opening_hours,
                'latitude': latitude,
                'longitude': longitude,
                'osm_id': osm_id
            })
        
        # Convert to DataFrame
        df = pd.DataFrame(business_data)
        
        print(f"Total businesses found: {len(df)}")
        
        if len(df) > 0:
            # Show first 10 rows only
            print("\nFirst 10 businesses:")
            print("=" * 80)
            
            for idx, row in df.head(10).iterrows():
                print(f"{idx+1}. {row['business_name']}")
                print(f"   Type: {row['business_type']}")
                print(f"   Address: {row['address'] or 'No address'}")
                print(f"   Phone: {row['phone'] or 'None'}")
                print(f"   Email: {row['email'] or 'None'}")
                print(f"   Website: {row['website'] or 'None'}")
                print(f"   Hours: {row['opening_hours'] or 'None'}")
                print(f"   Location: {row['latitude']:.4f}, {row['longitude']:.4f}")
                print("-" * 80)
            
            # Save to CSV
            output_file = "test_data/copenhagen_businesses_filtered.csv"
            df.to_csv(output_file, index=False)
            print(f"\nData saved to: {output_file}")
            
            return df
        
        else:
            print("No valid business data found")
            return None
            
    except Exception as e:
        print(f"Failed to filter business data: {e}")
        return None


    

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
    # step2_success = prototype_osmnx_connection()
    # if not step2_success:
    #     print("\n❌ CRITICAL: Prototype OSMnx functionality failed")
    #     print("Check internet connection and OSMnx installation")
    #     return
    # # first bug the library find a city called Copenhagen, but not the one in Denmark
    # Now that we found the right place, we can continue with the next steps
    # ## SECOND STEP COMPLETED
    # Step 3: Create a more complex query where we extract only the activities
    # step3_success = prototype_amenity_osmnx_connection()
    # if not step3_success:
    #     print("\n❌ CRITICAL: Prototype OSMnx functionality failed")
    #     print("Check internet connection and OSMnx installation")
    #     return
    # ## THIRD STEP COMPLETED
    # Step 4: Create a table from the file
    create_table("test_data/step3a_amenities.gpkg")

if __name__ == "__main__":
    main()