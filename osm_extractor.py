import osmnx as ox
import pandas as pd

def extract_osm_businesses(place_name="Copenhagen, Denmark", tags={"shop": True}):
    """
    Extract business data from OpenStreetMap for Copenhagen.
    
    Args:
        place_name (str): The name of the place to search for businesses
        tags (dict): OSM tags to filter by (default: {"shop": True})
    
    Returns:
        pd.DataFrame: DataFrame containing business information
    """
    # Fetch OSM features (businesses) from the specified place using the given tags
    gdf = ox.features_from_place(place_name, tags)    
    # Filter out entries that don't have a name (unnamed businesses)
    gdf = gdf[gdf['name'].notnull()]    
    # Reset the index to have a clean sequential index
    gdf = gdf.reset_index()
    # Debug: Print available columns to understand the data structure
    print(f"Available columns: {list(gdf.columns)}")

    # Create a dictionary to structure the business data
    # Each key represents a field we want to extract from the OSM data
    data = {
        # Extract the OSM ID for unique identification
        "id": gdf["id"],
        
        # Extract the business name
        "name": gdf["name"],
        
        # Determine business type by combining shop and amenity tags
        "business_type": _determine_business_type(gdf),
        
        # Build complete address from available address components
        "address": _build_full_address(gdf),
        
        # Extract email (None if not available)
        "email": gdf.get("email", None) if "email" in gdf.columns else None,
        
        # Extract phone number (None if not available)
        "phone": gdf.get("phone", None) if "phone" in gdf.columns else None,
        
        # Extract website URL - try both "website" and "url" fields
        "website": _extract_website(gdf),
        
        # Extract opening hours (None if not available)
        "opening_hours": gdf.get("opening_hours", None) if "opening_hours" in gdf.columns else None,
        
        # Additional useful information for reference
        "element_type": gdf.get("element", None),
        "brand": gdf.get("brand", None) if "brand" in gdf.columns else None,
        
        # Geographic coordinates from geometry centroid
        "lat": gdf.geometry.centroid.y,
        "lon": gdf.geometry.centroid.x
    }

    # Convert dictionary to pandas DataFrame
    df = pd.DataFrame(data)
    
    # Clean and standardize the data
    df = _clean_dataframe(df)
    
    return df

def _determine_business_type(gdf):
    """
    Determine the business type based on OSM shop, amenity, and other relevant tags.
    
    Args:
        gdf: GeoDataFrame containing OSM data
        
    Returns:
        list: List of business types for each row
    """
    business_types = []
    
    for idx, row in gdf.iterrows():
        # Check different tag sources in order of priority
        type_sources = ['shop', 'amenity', 'tourism', 'craft', 'office', 'leisure']
        
        business_type = "Unknown"
        for source in type_sources:
            if source in gdf.columns and pd.notna(row.get(source)):
                business_type = str(row[source]).title()  # Capitalize for consistency
                break
                
        business_types.append(business_type)
    
    return business_types

def _build_full_address(gdf):
    """
    Build complete address string from OSM address components.
    
    Args:
        gdf: GeoDataFrame containing OSM data
        
    Returns:
        list: List of complete addresses for each row
    """
    addresses = []
    
    # Standard OSM address field names
    address_fields = ['addr:housenumber', 'addr:street', 'addr:postcode', 'addr:city']
    
    for idx, row in gdf.iterrows():
        address_parts = []
        
        # Collect available address components
        for field in address_fields:
            if field in gdf.columns and pd.notna(row.get(field)):
                address_parts.append(str(row[field]))
        
        # If no standard components, try full address field
        if not address_parts and 'addr:full' in gdf.columns and pd.notna(row.get('addr:full')):
            address_parts.append(str(row['addr:full']))
            
        # Join components into complete address or None if empty
        full_address = ', '.join(address_parts) if address_parts else None
        addresses.append(full_address)
    
    return addresses

def _extract_website(gdf):
    """
    Extract website URL trying multiple possible OSM fields.
    
    Args:
        gdf: GeoDataFrame containing OSM data
        
    Returns:
        list: List of website URLs for each row
    """
    websites = []
    
    for idx, row in gdf.iterrows():
        website = None
        
        # Try different website fields in order of priority
        website_fields = ['website', 'url', 'contact:website']
        
        for field in website_fields:
            if field in gdf.columns and pd.notna(row.get(field)):
                website = row[field]
                break
                
        websites.append(website)
    
    return websites

def _clean_dataframe(df):
    """
    Clean and standardize the DataFrame data.
    
    Args:
        df: Raw DataFrame with business data
        
    Returns:
        pd.DataFrame: Cleaned DataFrame
    """
    # Replace empty strings and NaN with None
    df = df.replace('', None)
    df = df.where(pd.notna(df), None)
    
    # Clean phone numbers (remove extra spaces)
    if 'phone' in df.columns:
        df['phone'] = df['phone'].apply(lambda x: x.strip() if isinstance(x, str) else x)
    
    # Clean and normalize website URLs
    if 'website' in df.columns:
        df['website'] = df['website'].apply(_clean_url)
    
    return df

def _clean_url(url):
    """
    Clean and normalize website URLs.
    
    Args:
        url: Raw URL string
        
    Returns:
        str: Cleaned URL or None
    """
    if not isinstance(url, str):
        return url
        
    url = url.strip()
    
    # Add http:// if no protocol is present
    if url and not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    return url if url else None