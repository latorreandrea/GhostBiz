# GhostBiz

GhostBiz is a Python script that maps local businesses without a website by combining OpenStreetMap data and Google Maps lookups. It helps identify active businesses that are missing from the digital world.

## 🎯 Objective

- Extract commercial activities from OpenStreetMap (for example, in Copenhagen)
- Check if they have a website or still exist using the Google Places API
- Save the results in a CSV file

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [How It Works](#how-it-works)
- [Usage](#usage)
- [Output Format](#output-format)
- [Features](#features)
- [Rate Limiting](#rate-limiting)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🔧 Prerequisites

- Python 3.7+
- Google Places API key
- Internet connection

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/latorreandrea/GhostBiz.git
cd GhostBiz
```

2. Install required dependencies:
```bash
pip install osmnx pandas requests
```

## ⚙️ Configuration

1. Open `config.py`
2. Replace the placeholder with your Google Places API key:
```python
GOOGLE_API_KEY = "your_actual_google_api_key_here"
```

To get a Google Places API key:
1. Visit the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Places API
4. Create credentials (API key)
5. Optionally restrict the API key to Places API for security

## 🔄 How It Works

GhostBiz follows a structured three-phase process to identify local businesses without a web presence. The system is designed to be resilient, resumable, and respectful of API limits.

### System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   OpenStreetMap │    │   Google Places  │    │   CSV Results   │
│      Data       │───▶│       API        │───▶│     Output      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
        ▲                         ▲                        ▲
        │                         │                        │
   ┌─────────┐              ┌─────────────┐         ┌─────────────┐
   │ OSM     │              │ Google      │         │ Main        │
   │ Extract │              │ Checker     │         │ Processing  │
   └─────────┘              └─────────────┘         └─────────────┘
```

### Detailed Execution Flow

#### **Phase 1: OSM Data Extraction** 📍
**File:** `osm_extractor.py`

```python
def extract_osm_businesses(place_name="Copenhagen, Denmark", tags={"shop": True})
```

**Process:**
1. **Geographic Query**: Uses OSMnx to query OpenStreetMap with parameters:
   - `place_name`: Target location (default: Copenhagen, Denmark)
   - `tags`: Business type filters (default: shop=True)

2. **Applied Filters**:
   - Only entities with populated `name` field
   - Removal of duplicates and empty entries
   - Index reset for consistency

3. **Extracted Data**:
   ```python
   {
       "osm_id": "Unique OSM ID",
       "name": "Business name",
       "brand": "Brand/chain (if available)",
       "amenity": "Amenity type (restaurant, cafe, etc.)",
       "shop": "Shop type",
       "street": "Street address",
       "housenumber": "House number",
       "postcode": "Postal code",
       "city": "City",
       "opening_hours": "Opening hours",
       "phone": "Phone number",
       "website_osm": "Website from OSM",
       "email": "Email address",
       "lat": "Latitude (geometry centroid)",
       "lon": "Longitude (geometry centroid)"
   }
   ```

#### **Phase 2: Smart Google Places Verification** 🔍
**File:** `google_checker.py`

```python
def check_google_business(name, lat, lon, api_key)
```

**Optimized Process:**
1. **Pre-check**: Only called for businesses **without** OSM website
2. **Text Search API Call**:
   ```python
   url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
   params = {
       "query": name,           # Business name from OSM
       "location": f"{lat},{lon}",  # OSM coordinates
       "radius": 200,           # 200m search radius
       "key": api_key          # Google API key
   }
   ```

3. **Matching Logic**:
   - Search within 200 meters of OSM coordinates
   - Takes first result (most relevant)
   - Handles "business not found" cases

4. **Returned Data**:
   ```python
   {
       "found": bool,           # Business found on Google
       "google_name": str,      # Official Google name
       "website": str,          # Website (if present)
       "status": str           # Business status (OPERATIONAL, CLOSED, etc.)
   }
   ```

#### **Phase 3: Orchestration and Persistence** 💾
**File:** `main.py`

**Main Process:**

1. **Initialization**:
   ```python
   # Extract OSM data
   df_osm = extract_osm_businesses()
   
   # Check for existing checkpoints
   if os.path.exists(OUTPUT_FILE):
       df_done = pd.read_csv(OUTPUT_FILE)
       done_names = set(df_done["osm_name"])
   ```

2. **Smart Processing Loop**:
   ```python
   for i, row in df_osm.iterrows():
       if row["name"] in done_names:
           continue  # Skip already processed businesses
       
       # Check for existing OSM website
       if pd.notna(row.get("website_osm")) and row["website_osm"]:
           # Skip Google API call - use OSM website
           entry = {"website": row["website_osm"], "status": "HAS_OSM_WEBSITE"}
       else:
           # Only for businesses without website: check Google Places
           google_data = check_google_business(...)
           time.sleep(1)  # Rate limiting only for API calls
       
       # Immediate save (checkpoint)
       df_done.to_csv(OUTPUT_FILE, index=False)
   ```

3. **Checkpoint System**:
   - **Resume Capability**: Automatically resumes from interruptions
   - **Duplicate Prevention**: Avoids reprocessing
   - **Progressive Saving**: Saves after each business verification
   - **Data Integrity**: No data loss in case of crash

### Technical Features

#### **Smart API Management and Cost Optimization**
- **Intelligent API Usage**: Calls Google Places only for businesses without OSM website
- **Conditional Rate Limiting**: 1-second delay only when making API calls
- **Radius Optimization**: 200m search for precision/recall balance
- **Error Handling**: Continues processing even with individual failures
- **Cost Reduction**: Dramatically reduces the number of API calls (potentially 50-80% savings)

#### **Data Persistence Strategy**
- **Output Format**: CSV for universal compatibility
- **Incremental Updates**: Progressive append without overwrites
- **Checkpoint System**: File-based state management

#### **Memory Management**
- **Streaming Processing**: One business at a time
- **No Full Load**: Avoids loading complete dataset in memory
- **Garbage Collection**: Automatic cleanup of temporary objects

### Complete Flow Diagram

```
┌─────────────────┐
│   START SCRIPT  │
└─────────┬───────┘
          │
          ▼
┌─────────────────────┐
│ Extract OSM Data    │ ◄── osm_extractor.py
│ (location, tags)    │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Check Checkpoint    │ ◄── Verify ghostbiz_results.csv
│ (resume detection)  │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ LOOP: For each      │
│ OSM business        │ ◄─┐
└─────────┬───────────┘   │
          │               │
          ▼               │
┌─────────────────────┐   │
│ Already processed?  │   │
│ (skip if in CSV)    │   │
└─────────┬───────────┘   │
          │ NO            │
          ▼               │
┌─────────────────────┐   │
│ Has OSM website?    │   │
│ (website_osm field) │   │
└─────────┬───────────┘   │
          │ NO            │ YES
          ▼               │  │
┌─────────────────────┐   │  │
│ Google Places API   │ ◄── google_checker.py
│ (text search)       │   │  │
└─────────┬───────────┘   │  │
          │               │  │
          ▼               │  │
┌─────────────────────┐   │  │
│ Rate Limit          │   │  │
│ (sleep 1s)          │   │  │
└─────────┬───────────┘   │  │
          │               │  │
          ▼               │  │
┌─────────────────────┐   │  │
│ Merge Data &        │ ◄─┘  │
│ Mark as PROCESSED   │      │
└─────────┬───────────┘      │
          │                  │
          ▼                  │
┌─────────────────────┐      │
│ Save to CSV         │      │
│ (checkpoint)        │ ─────┘
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Processing done?    │
└─────────┬───────────┘
          │ YES
          ▼
┌─────────────────────┐
│ COMPLETED           │
│ ✅ ghostbiz_results │
│    .csv generated   │
└─────────────────────┘
```

## 🚀 Usage

Run the script with:
```bash
python main.py
```

The script will:
1. Extract businesses from Copenhagen, Denmark (default location)
2. Check each business against Google Places API
3. Save results progressively to `ghostbiz_results.csv`
4. Display progress in the terminal

### Customizing the Location

To change the target location, modify the `extract_osm_businesses()` call in `main.py`:
```python
df_osm = extract_osm_businesses(place_name="Milan, Italy")
```

### Customizing Business Types

To search for different business types, modify the tags parameter:
```python
df_osm = extract_osm_businesses(tags={"amenity": ["restaurant", "cafe", "bar"]})
```

## 📊 Output Format

The script generates a CSV file (`ghostbiz_results.csv`) with the following columns:

| Column | Description |
|--------|-------------|
| `osm_name` | Business name from OpenStreetMap |
| `lat` | Latitude coordinate |
| `lon` | Longitude coordinate |
| `google_name` | Business name from Google Places |
| `website` | Website URL (if available) |
| `status` | Business status from Google Places |
| `not_found` | Boolean indicating if business was not found on Google |

## ✨ Features

### Resume Capability
- **Checkpoint System**: If the script is interrupted, it automatically resumes from where it left off
- **Duplicate Prevention**: Skips already processed businesses
- **Progress Tracking**: Shows how many businesses have been processed

### Rate Limiting
- **API Respect**: 1-second delay between Google API calls to respect rate limits
- **Cost Optimization**: Prevents unnecessary API charges

### Data Integrity
- **Progressive Saving**: Results are saved after each business check
- **Error Handling**: Continues processing even if individual lookups fail

## ⚠️ Rate Limiting

The script implements a 1-second delay between Google Places API calls to:
- Respect Google's rate limiting policies
- Avoid API quota exhaustion
- Prevent potential IP blocking

For large datasets, consider:
- Running the script during off-peak hours
- Monitoring your Google Cloud Console for API usage
- Adjusting the delay in `main.py` if needed

## 🐛 Troubleshooting

### Common Issues

**API Key Errors**
- Ensure your Google Places API key is correctly set in `config.py`
- Verify the Places API is enabled in Google Cloud Console
- Check API key restrictions and quotas

**No Results Found**
- Verify the location name is recognized by OpenStreetMap
- Check if the area has businesses with the specified tags
- Try broader search tags or different locations

**Memory Issues**
- For very large areas, consider processing in smaller geographic chunks
- Monitor system memory usage during execution

**Network Errors**
- Ensure stable internet connection
- The script will continue processing after temporary network issues

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- [OSMnx](https://osmnx.readthedocs.io/) for OpenStreetMap data extraction
- [Google Places API](https://developers.google.com/maps/documentation/places/web-service) for business verification
- OpenStreetMap contributors for maintaining the global map database