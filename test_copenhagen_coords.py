import osmnx as ox
import pandas as pd

def test_copenhagen_coordinates():
    """Test Copenhagen extraction using coordinates"""
    
    print("🧪 Testing Copenhagen with bounding box coordinates...")
    
    # Copenhagen areas approximate bounding box
    
    # copenhagen center (Indre By - Historical Center)
    north, south, east, west = 55.6845, 55.6704, 12.5951,  12.5641
    # norrebro (Nørrebro - Hip/Alternative District)
    north, south, east, west = 55.6950, 55.6800, 12.5600, 12.5300        
    # vesterbro (Vesterbro - Trendy District)
    north, south, east, west = 55.6700, 55.6550, 12.5500, 12.5200
    # osterbro (Østerbro - Upscale Residential)
    north, south, east, west = 55.6950, 55.6800, 12.5800, 12.5500
    # frederiksberg (Independent Municipality within Copenhagen)
    north, south, east, west = 55.6850, 55.6650, 12.5350, 12.5150
    # amager_west (Amager Vest - Islands District)
    north, south, east, west = 55.6600, 55.6400, 12.5800, 12.5600
    # amager_east (Amager Øst - Including Airport Area)
    north, south, east, west = 55.6300, 55.6100, 12.6200, 12.5900
    # christian_area (Christianshavn - Historic Harbor District)
    north, south, east, west = 55.6750, 55.6650, 12.5950, 12.5850
    # refshaleoen (New Development Area)
    north, south, east, west = 55.6900, 55.6800, 12.6100, 12.5950
    # bispebjerg (Northern Residential District)  
    north, south, east, west = 55.7050, 55.6900, 12.5500, 12.5300
    # valby (Western District)
    north, south, east, west = 55.6650, 55.6500, 12.5100, 12.4900
    # vanlose (Northwestern Suburb)
    north, south, east, west = 55.6950, 55.6800, 12.4850, 12.4650
    
    tags = {
        "shop": True,
        "amenity": ["restaurant", "cafe", "bar"]
    }
    
    try:
        # CORRECTED: Use bbox parameter or separate named parameters
        gdf = ox.features_from_bbox(
            bbox=(north, south, east, west),  # Pass as tuple
            tags=tags
        )
        print(f"✅ Found {len(gdf)} features")
        
        # Filter named businesses
        gdf_named = gdf[gdf['name'].notnull()]
        print(f"✅ Found {len(gdf_named)} named businesses")
        
        if len(gdf_named) > 0:
            # Check a few examples
            for i, (idx, row) in enumerate(gdf_named.head(10).iterrows()):
                lat = row.geometry.centroid.y
                lon = row.geometry.centroid.x
                business_type = row.get('shop', row.get('amenity', 'Unknown'))
                print(f"  {i+1}. {row['name']} ({business_type}) - Lat: {lat:.4f}, Lon: {lon:.4f}")
                
            # Check if coordinates are actually in Copenhagen (Denmark)
            avg_lat = gdf_named.geometry.centroid.y.mean()
            avg_lon = gdf_named.geometry.centroid.x.mean()
            
            print(f"\n📍 Average coordinates: Lat {avg_lat:.4f}, Lon {avg_lon:.4f}")
            
            if 55.0 < avg_lat < 56.0 and 12.0 < avg_lon < 13.0:
                print("🇩🇰 SUCCESS: These coordinates are in Copenhagen, Denmark!")
            else:
                print("❌ WARNING: These coordinates don't seem to be in Denmark")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_copenhagen_coordinates()
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("You can now update osm_extractor.py to use bbox coordinates")
    else:
        print("\n💡 Try alternative bbox syntax if this fails")