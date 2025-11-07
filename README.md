# Menu Pricing System

An intelligent REST API that dynamically recommends competitive menu item prices based on internal factors (competitor pricing) and external factors (weather conditions, nearby events).


##  Project Structure

```
pricing-system/
│
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app initialization
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── pricing.py           # Pricing endpoints
│   │       ├── weather.py           # Weather endpoints
│   │       └── events.py            # Events endpoints
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py                # Settings and configuration
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── database.py              # SQLAlchemy models
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── pricing.py               # Pydantic models
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pricing_engine.py        # Core pricing logic
│   │   ├── weather_service.py       # Weather API integration
│   │   └── event_service.py         # Events API integration
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py              # Database connection
│   │
│   └── utils/
│       ├── __init__.py
│       └── helpers.py               # Helper functions
│
├── requirements.txt
├── .env.example
├── .gitignore
├── run.py
└── README.md
```

##  Tech Stack

- **Framework**: FastAPI (modern, fast, async)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Python Version**: 3.8+
- **External APIs**: OpenWeatherMap, Ticketmaster
- **Validation**: Pydantic v2
- **Server**: Uvicorn (ASGI server)

##  Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd pricing-system
```

2. **Create virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up PostgreSQL database**
```bash
# Create database
createdb pricing_db

# Or using psql
psql -U postgres
CREATE DATABASE pricing_db;
```

5. **Configure environment variables**
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use any text editor
```

6. **Initialize database**
```bash
python -c "from app.db.database import init_db; init_db()"
```

##  Running the Application

**Method 1: Using run.py**
```bash
python run.py
```

**Method 2: Using uvicorn directly**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
**Method 3: Using start.bat**
1. Open Command Prompt in project folder
2. Run: start.bat
3. Wait for everything to start
4. Open browser: http://localhost:8000/docs

The API will be available at `http://localhost:8000`

##  API Documentation

Once running, access interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

##  API Endpoints

### 1. Pricing Suggestion
**POST** `/api/pricing/suggest`

Generate AI-powered pricing recommendation.

**Request:**
```json
{
  "menu_item_id": 123,
  "current_price": 250,
  "competitor_prices": [240, 260, 245],
  "weather": {
    "temperature": 32,
    "condition": "Sunny"
  },
  "events": [
    {
      "name": "Food Festival",
      "popularity": "High",
      "distance_km": 2.5
    }
  ]
}
```

**Response:**
```json
{
  "menu_item_id": 123,
  "recommended_price": 268.50,
  "factors": {
    "internal_weight": 0.6,
    "external_weight": 0.4
  },
  "reasoning": "Price adjustment recommended due to: competitors are pricing higher, favorable weather (Sunny, 32°C), nearby events (Food Festival) increasing demand."
}
```

### 2. Pricing History
**GET** `/api/pricing/history/{menu_item_id}?limit=10`

Get historical pricing data for analysis.

### 3. Weather Data
**GET** `/api/weather/{city}`

Fetch current weather for a city.

### 4. Events Data
**GET** `/api/events/{location}?radius_km=5.0`

Get nearby events within radius.

##  Pricing Algorithm

The AI engine uses a weighted approach:

### Internal Factors (60% weight)
- Competitor price comparison
- Market positioning analysis

### External Factors (40% weight)
- **Weather Impact**:
  - Perfect conditions (20-30°C, Sunny): +8-13%
  - Extreme weather (>35°C or <10°C): -3-5%
  - Rain/storms: -8%

- **Event Impact**:
  - High popularity: +10% base
  - Medium popularity: +5% base
  - Low popularity: +2% base
  - Distance decay: Exponential reduction with distance

### Formula
```
recommended_price = current_price × (1 + adjustment)

where:
adjustment = (internal_weight × competitor_factor) + 
             (external_weight × (weather_factor + event_factor - 1))
```

##  Database Schema

### Tables

1. **pricing_history**
   - Historical pricing decisions
   - Tracks trends and patterns

2. **weather_cache**
   - Cached weather data (30 min TTL)
   - Reduces API calls

3. **event_cache**
   - Cached event data (6 hour TTL)
   - Improves response time

4. **competitor_prices**
   - Competitor pricing tracking
   - Time-series analysis

##  Testing

### Using cURL
```bash
curl -X POST "http://localhost:8000/api/pricing/suggest" \
  -H "Content-Type: application/json" \
  -d '{
    "menu_item_id": 101,
    "current_price": 200,
    "competitor_prices": [195, 210, 205],
    "weather": {
      "temperature": 28,
      "condition": "Sunny"
    },
    "events": [
      {
        "name": "Music Concert",
        "popularity": "High",
        "distance_km": 1.5
      }
    ]
  }'
```

### Using Python
```python
import requests

response = requests.post(
    "http://localhost:8000/api/pricing/suggest",
    json={
        "menu_item_id": 101,
        "current_price": 200,
        "competitor_prices": [195, 210, 205],
        "weather": {"temperature": 28, "condition": "Sunny"},
        "events": [
            {
                "name": "Music Concert",
                "popularity": "High",
                "distance_km": 1.5
            }
        ]
    }
)

print(response.json())
```



##  Configuration Options

Edit `app/core/config.py` or `.env` file:

```python
# Pricing weights
INTERNAL_WEIGHT = 0.6  # Competitor influence
EXTERNAL_WEIGHT = 0.4  # Weather + Events influence

# Cache durations
WEATHER_CACHE_MINUTES = 30
EVENT_CACHE_HOURS = 6

# API Rate limiting
RATE_LIMIT_PER_MINUTE = 60
```

##  Troubleshooting

**Database connection error:**
```bash
# Check PostgreSQL is running
sudo service postgresql status

# Create database if missing
createdb pricing_db
```

**Module not found:**
```bash
# Ensure you're in virtual environment
pip install -r requirements.txt
```

**API key errors:**
```bash
# Set up .env file with valid API keys
cp .env.example .env
# Edit .env with your keys
```

## 📄 License

MIT License - Free to use for educational and commercial purposes

## 👨‍💻 Author

Created as part of Python Developer Assignment

---

**Note**: This is a demonstration project. For production use:
- Add proper authentication/authorization
- Implement comprehensive error handling
- Add unit and integration tests
- Use real API keys for weather and events
- Set up proper logging and monitoring
- Configure rate limiting
- Add data validation and sanitization