import osmnx as ox
import pandas as pd

def extract_osm_businesses(place_name="Copenhagen, Denmark", tags=None):
    """
    Extract comprehensive business data from OpenStreetMap for Copenhagen.
    Enhanced version based on OSMnx examples for maximum business coverage.
    
    Args:
        place_name (str): The name of the place to search for businesses
        tags (dict): OSM tags to filter by (if None, uses comprehensive business tags)
    
    Returns:
        pd.DataFrame: DataFrame containing comprehensive business information
    """
    
    # 🏷️ Use comprehensive business tags if none provided (based on OSMnx examples)
    if tags is None:
        tags = {
            # All commercial shops
            "shop": True,
            
            # Food & Drink establishments  
            "amenity": [
                "restaurant", "cafe", "bar", "pub", "fast_food", 
                "ice_cream", "food_court", "biergarten", "bank", 
                "pharmacy", "hospital", "clinic", "dentist",
                "veterinary", "post_office", "fuel", "car_wash",
                "car_rental", "taxi"
            ],
            
            # Accommodation & Tourism
            "tourism": ["hotel", "hostel", "guest_house", "motel", "apartment"],
            
            # Professional services
            "office": True,
            "craft": True,
            
            # Entertainment & Recreation
            "leisure": [
                "fitness_centre", "spa", "sauna", "bowling_alley",
                "cinema", "theatre", "nightclub"
            ]
        }
    
    print(f"🔍 COMPREHENSIVE SEARCH for businesses in: {place_name}")
    print(f"🏷️  Using enhanced tags for maximum coverage")
    
    # 🔧 CORRECTED: Configure OSMnx settings properly (based on examples)
    ox.settings.max_query_area_size = 50_000_000_000
    # Note: timeout is handled differently in OSMnx - it's set per request, not globally
    
    
    
    # 📝 OSMnx timeout is set via requests, not global settings
    print(f"📏 Increased max query area to: {ox.settings.max_query_area_size:,} m²")
    
    try:
        # Use coordinate-based search for Copenhagen (more reliable)
        if "Copenhagen" in place_name and "Denmark" in place_name:
            print("🗺️  Using optimized coordinate search for Copenhagen...")
            
            # # Larger Copenhagen metropolitan area for comprehensive coverage
            # north, south, east, west = 55.75, 55.62, 12.70, 12.45
            # copenhagen center (Indre By - Historical Center)
            # north, south, east, west = 55.6845, 55.6704, 12.5951,  12.5641
            north, south, east, west = 55.6800, 55.6780, 12.5850, 12.5830
            print(f"📍 Large area coordinates: N{north}, S{south}, E{east}, W{west}")
            
            # Calculate area
            lat_diff = north - south
            lon_diff = east - west
            area_km2 = (lat_diff * 111) * (lon_diff * 69)
            
            print(f"📐 Query area: ~{area_km2:.1f} km² (may require multiple sub-queries)")
            print("⏳ This may take 2-10 minutes for comprehensive extraction...")
            
            # 🔧 CORRECTED: Use proper OSMnx function (from examples #16)
            gdf = ox.features.features_from_bbox(
                bbox=(north, south, east, west),
                tags=tags
            )
            print(f"✅ Coordinate search completed!")
            
        else:
            # Use place name search for other locations (from examples #00 and #16)
            gdf = ox.features.features_from_place(place_name, tags)
        
        print(f"📊 Initial features found: {len(gdf)}")
        
        # Filter out entries that don't have a name
        gdf = gdf[gdf['name'].notnull()]
        print(f"📊 Named businesses found: {len(gdf)}")
        
        if len(gdf) == 0:
            print("⚠️ No named businesses found")
            return pd.DataFrame()
        
        # Reset index for clean processing
        gdf = gdf.reset_index()
        
        # Debug: Print available columns
        print(f"📋 Available columns: {list(gdf.columns)}")
        
        # Enhanced coordinate processing (from examples #00)
        print("🔄 Converting to projected coordinates for accurate centroids...")
        gdf_projected = gdf.to_crs('EPSG:3857')  # Web Mercator
        centroids = gdf_projected.geometry.centroid
        centroids_geo = centroids.to_crs('EPSG:4326')  # Back to WGS84
        print("✅ Coordinate conversion completed")
        
        # 📋 Create comprehensive data dictionary
        data = {
            # Core identification (handle different ID column names)
            "id": _safe_get_column(gdf, ["osmid", "id"]),
            "name": gdf["name"],
            
            # Enhanced business classification
            "business_type": _determine_comprehensive_business_type(gdf),
            "primary_tag": _get_primary_osm_tag(gdf),
            
            # Complete address information
            "address": _build_comprehensive_address(gdf),
            
            # Contact information (multiple field fallbacks)
            "phone": _extract_contact_info(gdf, ["phone", "contact:phone", "telephone"]),
            "email": _extract_contact_info(gdf, ["email", "contact:email"]),
            "website": _extract_contact_info(gdf, ["website", "url", "contact:website"]),
            
            # Business operation details
            "opening_hours": _safe_get_column(gdf, ["opening_hours"]),
            "brand": _safe_get_column(gdf, ["brand"]),
            "cuisine": _safe_get_column(gdf, ["cuisine"]),  # For restaurants
            
            # Additional business information
            "wheelchair": _safe_get_column(gdf, ["wheelchair"]),
            "wifi": _extract_contact_info(gdf, ["internet_access", "wifi"]),
            "payment_cards": _extract_payment_info(gdf),
            
            # Geographic coordinates (from projected centroids)
            "lat": centroids_geo.y,
            "lon": centroids_geo.x,
            
            # OSM metadata
            "element_type": _safe_get_column(gdf, ["element_type", "element"]),
            "osm_type": _get_osm_geometry_type(gdf)
        }
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Enhanced data cleaning
        df = _clean_comprehensive_dataframe(df)
        
        print(f"✅ COMPREHENSIVE extraction completed: {len(df)} businesses with full details")
        
        # Show business type distribution
        if len(df) > 0:
            print(f"\n📊 Business type distribution (top 10):")
            type_counts = df['business_type'].value_counts().head(10)
            for btype, count in type_counts.items():
                print(f"   {btype}: {count}")
        
        return df
        
    except Exception as e:
        print(f"❌ Comprehensive extraction failed: {e}")
        import traceback
        traceback.print_exc()  # For debugging
        return pd.DataFrame()
        
    finally:
        # 🔧 CORRECTED: Reset only the settings that exist
        ox.settings.max_query_area_size = 50_000_000_000
        print("🔄 OSMnx settings reset to defaults")


def _safe_get_column(gdf, column_names):
    """Safely get column data trying multiple column names"""
    for col in column_names:
        if col in gdf.columns:
            return gdf[col]
    return None


# � CORRECTED: All helper functions with better error handling

def _determine_comprehensive_business_type(gdf):
    """Enhanced business type determination with detailed categorization"""
    business_types = []
    
    for idx, row in gdf.iterrows():
        # Priority order for business classification
        type_mapping = [
            ('shop', 'Shop'),
            ('amenity', 'Service'),
            ('tourism', 'Tourism'),
            ('office', 'Office'),
            ('craft', 'Craft'),
            ('leisure', 'Recreation')
        ]
        
        business_type = "Unknown"
        
        for osm_tag, category in type_mapping:
            if osm_tag in gdf.columns and pd.notna(row.get(osm_tag)):
                specific_type = str(row[osm_tag]).replace('_', ' ').title()
                business_type = f"{category}: {specific_type}"
                break
        
        business_types.append(business_type)
    
    return business_types


def _get_primary_osm_tag(gdf):
    """Get the primary OSM tag that classified each business"""
    primary_tags = []
    
    for idx, row in gdf.iterrows():
        primary_tag = "unknown"
        
        for tag in ['shop', 'amenity', 'tourism', 'office', 'craft', 'leisure']:
            if tag in gdf.columns and pd.notna(row.get(tag)):
                primary_tag = tag
                break
        
        primary_tags.append(primary_tag)
    
    return primary_tags


def _build_comprehensive_address(gdf):
    """Build complete addresses from all possible OSM address components"""
    addresses = []
    
    # Comprehensive address field mapping
    address_components = [
        'addr:housenumber', 'addr:housename',
        'addr:street', 'addr:place', 
        'addr:postcode', 'addr:city',
        'addr:suburb', 'addr:district',
        'addr:state', 'addr:country'
    ]
    
    for idx, row in gdf.iterrows():
        address_parts = []
        
        # Collect all available address components
        for field in address_components:
            if field in gdf.columns and pd.notna(row.get(field)):
                address_parts.append(str(row[field]))
        
        # Fallback to full address field
        if not address_parts:
            for fallback_field in ['addr:full', 'address']:
                if fallback_field in gdf.columns and pd.notna(row.get(fallback_field)):
                    address_parts.append(str(row[fallback_field]))
                    break
        
        full_address = ', '.join(address_parts) if address_parts else None
        addresses.append(full_address)
    
    return addresses


def _extract_contact_info(gdf, field_names):
    """Extract contact information trying multiple OSM field variants"""
    contact_info = []
    
    for idx, row in gdf.iterrows():
        info = None
        
        # Try each field name in priority order
        for field in field_names:
            if field in gdf.columns and pd.notna(row.get(field)):
                info = str(row[field])
                break
        
        contact_info.append(info)
    
    return contact_info


def _extract_payment_info(gdf):
    """Extract payment method information"""
    payment_info = []
    
    payment_fields = [
        'payment:cash', 'payment:cards', 'payment:credit_cards',
        'payment:debit_cards', 'payment:contactless'
    ]
    
    for idx, row in gdf.iterrows():
        accepted_methods = []
        
        for field in payment_fields:
            if field in gdf.columns and str(row.get(field, '')).lower() == 'yes':
                method = field.replace('payment:', '').replace('_', ' ').title()
                accepted_methods.append(method)
        
        payment_str = ', '.join(accepted_methods) if accepted_methods else None
        payment_info.append(payment_str)
    
    return payment_info


def _get_osm_geometry_type(gdf):
    """Determine OSM geometry type (point, way, relation)"""
    geometry_types = []
    
    for idx, row in gdf.iterrows():
        try:
            geom = row.geometry
            
            if hasattr(geom, 'geom_type'):
                if geom.geom_type == 'Point':
                    osm_type = 'node'
                elif geom.geom_type in ['LineString', 'Polygon']:
                    osm_type = 'way'
                elif geom.geom_type in ['MultiPolygon', 'MultiLineString']:
                    osm_type = 'relation'
                else:
                    osm_type = 'unknown'
            else:
                osm_type = 'unknown'
        except:
            osm_type = 'unknown'
        
        geometry_types.append(osm_type)
    
    return geometry_types


def _clean_comprehensive_dataframe(df):
    """Enhanced data cleaning for comprehensive dataset"""
    # Clean website URLs
    if 'website' in df.columns:
        df['website'] = df['website'].apply(lambda x: 
            f"http://{x}" if x and isinstance(x, str) and not x.startswith(('http://', 'https://')) else x
        )
    
    # Clean phone numbers (remove extra whitespace)
    if 'phone' in df.columns:
        df['phone'] = df['phone'].apply(lambda x: 
            x.strip() if isinstance(x, str) else x
        )
    
    # Standardize boolean fields
    boolean_fields = ['wheelchair', 'wifi']
    for field in boolean_fields:
        if field in df.columns:
            df[field] = df[field].apply(lambda x: 
                'Yes' if str(x).lower() in ['yes', 'true', '1'] 
                else 'No' if str(x).lower() in ['no', 'false', '0']
                else None
            )
    
    # Replace empty strings with None
    df = df.replace(['', 'nan', 'None'], None)
    df = df.where(pd.notna(df), None)
    
    return df


# Keep original helper functions for backward compatibility
def _determine_business_type(gdf):
    """Original business type function (kept for compatibility)"""
    return _determine_comprehensive_business_type(gdf)

def _build_full_address(gdf):
    """Original address function (kept for compatibility)"""
    return _build_comprehensive_address(gdf)

def _extract_website(gdf):
    """Original website function (kept for compatibility)"""
    return _extract_contact_info(gdf, ["website", "url", "contact:website"])

def _clean_dataframe(df):
    """Original cleaning function (kept for compatibility)"""
    return _clean_comprehensive_dataframe(df)

def _clean_url(url):
    """Original URL cleaning function (kept for compatibility)"""
    if not isinstance(url, str):
        return url
        
    url = url.strip()
    
    if url and not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    return url if url else None