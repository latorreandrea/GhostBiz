import requests
import time

def check_google_business(name, lat, lon, api_key, radius=200):
    """
    Check if a business exists on Google Places and retrieve its website.
    
    Args:
        name (str): Business name to search for
        lat (float): Latitude coordinate
        lon (float): Longitude coordinate  
        api_key (str): Google Places API key
        radius (int): Search radius in meters (default: 200)
    
    Returns:
        dict: Dictionary containing business information from Google Places
    """
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": name,
        "location": f"{lat},{lon}",
        "radius": radius,  # Now configurable
        "key": api_key
    }
    
    resp = requests.get(url, params=params)
    data = resp.json()

    # Handle API errors
    if "error_message" in data:
        raise Exception(f"Google Places API Error: {data['error_message']}")

    if not data.get("results"):
        return {
            "found": False,
            "google_name": None,
            "website": None,
            "status": None
        }

    top_result = data["results"][0]
    return {
        "found": True,
        "google_name": top_result.get("name"),
        "website": top_result.get("website"),
        "status": top_result.get("business_status")
    }