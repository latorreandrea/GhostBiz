# Google Places API Configuration
GOOGLE_API_KEY = "Replace with your actual API key"  

# Optional: Other configuration settings
DEFAULT_PLACE = "København, Danmark"
DEFAULT_RADIUS = 200  # meters
API_DELAY = 1  # seconds between API calls

# Expanded OSM tags for more comprehensive business search
DEFAULT_TAGS = {
    "shop": True,
    "amenity": [
        "restaurant", 
        "cafe", 
        "bar", 
        "pub", 
        "fast_food", 
        "pharmacy", 
        "bank"
        ],
    "tourism": ["hotel", "hostel", "guest_house"],
    "craft": True,
    "office": True
}