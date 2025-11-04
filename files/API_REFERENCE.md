# College Football Rankings API - Quick Reference

## Base URL
```
Production: https://cfb.projectthomas.com
Local Dev: http://localhost:8000
```

## 🔄 Data Sync Endpoints (POST)

### Sync All Data (Recommended)
```bash
# Sync everything for a specific week
curl -X POST "https://cfb.projectthomas.com/admin/sync-all?season=2024&week=10&include=all"

# Sync only specific datasets
curl -X POST "https://cfb.projectthomas.com/admin/sync-all?season=2024&week=10&include=rankings,sp_ratings,lines"

# Response:
{
  "success": true,
  "season": 2024,
  "week": 10,
  "datasets_synced": ["ap_rankings", "sp_ratings", "fpi_ratings", "team_records", "betting_lines", "recruiting_rankings"],
  "total_added": 453,
  "total_updated": 87,
  "details": {
    "ap_rankings": {"success": true, "records_added": 25, "records_updated": 0},
    "sp_ratings": {"success": true, "records_added": 133, "records_updated": 0},
    ...
  }
}
```

### Sync Individual Datasets

#### AP Poll Rankings
```bash
# Specific week
curl -X POST "https://cfb.projectthomas.com/admin/sync/rankings?season=2024&week=10"

# All weeks (no week parameter)
curl -X POST "https://cfb.projectthomas.com/admin/sync/rankings?season=2024"

# Response:
{
  "success": true,
  "records_added": 25,
  "records_updated": 0
}
```

#### SP+ Ratings
```bash
# Specific week
curl -X POST "https://cfb.projectthomas.com/admin/sync/sp-ratings?season=2024&week=10"

# All weeks
curl -X POST "https://cfb.projectthomas.com/admin/sync/sp-ratings?season=2024"

# Response:
{
  "success": true,
  "records_added": 133,
  "records_updated": 0
}
```

#### FPI Ratings
```bash
# Specific week
curl -X POST "https://cfb.projectthomas.com/admin/sync/fpi-ratings?season=2024&week=10"

# All weeks
curl -X POST "https://cfb.projectthomas.com/admin/sync/fpi-ratings?season=2024"
```

#### Team Records
```bash
# Season records (no week needed)
curl -X POST "https://cfb.projectthomas.com/admin/sync/team-records?season=2024"

# Response:
{
  "success": true,
  "records_added": 133,
  "records_updated": 0
}
```

#### Betting Lines
```bash
# Specific week
curl -X POST "https://cfb.projectthomas.com/admin/sync/betting-lines?season=2024&week=10"

# All weeks
curl -X POST "https://cfb.projectthomas.com/admin/sync/betting-lines?season=2024"

# Response:
{
  "success": true,
  "records_added": 234,
  "records_updated": 12
}
```

#### Recruiting Rankings
```bash
# Recruiting class rankings (season-level only)
curl -X POST "https://cfb.projectthomas.com/admin/sync/recruiting?season=2024"

# Response:
{
  "success": true,
  "records_added": 65,
  "records_updated": 0
}
```

## 📊 Data Retrieval Endpoints (GET)

### Custom Rankings (Your Formula)
```bash
# Current week rankings
curl "https://cfb.projectthomas.com/rankings?season=2024&week=10"

# Response:
{
  "rankings": [
    {
      "rank": 1,
      "team": "Georgia",
      "ranking_value": 15.234,
      "wins": 9,
      "losses": 0,
      "formula_params": {"margin_1": 1.0, "margin_2": 1.3, "margin_3": 1.5, "sos": 0.8}
    },
    ...
  ]
}
```

### AP Poll Rankings
```bash
# Specific week
curl "https://cfb.projectthomas.com/admin/rankings/ap?season=2024&week=10"

# Latest rankings (no week)
curl "https://cfb.projectthomas.com/admin/rankings/ap?season=2024"

# Response:
{
  "rankings": [
    {
      "season": 2024,
      "week": 10,
      "season_type": "regular",
      "team": "Georgia",
      "rank": 1,
      "first_place_votes": 45,
      "points": 1523
    },
    ...
  ],
  "count": 25
}
```

### SP+ Ratings
```bash
# Specific week
curl "https://cfb.projectthomas.com/admin/ratings/sp?season=2024&week=10"

# Latest ratings (no week)
curl "https://cfb.projectthomas.com/admin/ratings/sp?season=2024"

# Response:
{
  "ratings": [
    {
      "season": 2024,
      "week": 10,
      "team": "Georgia",
      "rating": 28.5,
      "ranking": 1,
      "offense_rating": 15.2,
      "defense_rating": 13.3,
      "special_teams_rating": -0.1
    },
    ...
  ],
  "count": 133
}
```

### FPI Ratings
```bash
# Specific week
curl "https://cfb.projectthomas.com/admin/ratings/fpi?season=2024&week=10"

# Response similar to SP+ ratings
```

### Team Details (Comprehensive)
```bash
# Get all available data for a team
curl "https://cfb.projectthomas.com/admin/team/Georgia/details?season=2024"

# Response:
{
  "team": "Georgia",
  "season": 2024,
  "conference": "SEC",
  "record": {
    "overall": "9-0",
    "conference": "6-0",
    "home": "5-0",
    "away": "4-0"
  },
  "rankings": {
    "ap_poll": {
      "rank": 1,
      "points": 1523,
      "week": 10
    },
    "sp_plus": {
      "rating": 28.5,
      "ranking": 1,
      "week": 10
    },
    "fpi": {
      "rating": 25.3,
      "week": 10
    },
    "recruiting": {
      "rank": 3,
      "points": 295.45
    }
  }
}
```

### Existing Endpoints (From Your Current System)

#### Team Info
```bash
curl "https://cfb.projectthomas.com/team/Georgia"
```

#### Games
```bash
# All games for a team
curl "https://cfb.projectthomas.com/games?team=Georgia&season=2024"

# Specific week
curl "https://cfb.projectthomas.com/games?season=2024&week=10"
```

#### System Status
```bash
# Health check
curl "https://cfb.projectthomas.com/health"

# Database status
curl "https://cfb.projectthomas.com/db-status"

# Response:
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-11-03T12:34:56Z"
}
```

## 🧪 Testing Workflow

### 1. Initial Setup (First Time)
```bash
# Sync all historical data for 2024 season
curl -X POST "https://cfb.projectthomas.com/admin/sync-all?season=2024&include=all"

# This will take ~30 seconds, syncing:
# - AP rankings for all weeks
# - SP+ ratings for all weeks  
# - FPI ratings for all weeks
# - Team records
# - Betting lines
# - Recruiting rankings
```

### 2. Weekly Update (During Season)
```bash
# Update just the current week (faster)
CURRENT_WEEK=10

curl -X POST "https://cfb.projectthomas.com/admin/sync-all?season=2024&week=$CURRENT_WEEK&include=rankings,sp_ratings,fpi_ratings,lines"

# Also update team records (cumulative)
curl -X POST "https://cfb.projectthomas.com/admin/sync/team-records?season=2024"
```

### 3. Verify Data
```bash
# Check what got synced
curl "https://cfb.projectthomas.com/admin/rankings/ap?season=2024&week=10" | jq '.count'

# Should return 25 (top 25 teams)

# Check SP+ data
curl "https://cfb.projectthomas.com/admin/ratings/sp?season=2024&week=10" | jq '.count'

# Should return 133 (all FBS teams)
```

### 4. Frontend Testing
```bash
# Visit in browser
open "https://cfb.projectthomas.com"

# Or test with curl
curl "https://cfb.projectthomas.com" | grep "College Football Rankings"
```

## 📈 Expected Response Times

| Endpoint | Typical Response Time | Notes |
|----------|----------------------|--------|
| GET /rankings | < 100ms | From database |
| GET /admin/rankings/ap | < 100ms | From database |
| GET /admin/ratings/sp | < 200ms | More data |
| GET /admin/team/{name}/details | < 150ms | Multiple queries |
| POST /admin/sync/rankings | 2-5 seconds | API call + DB insert |
| POST /admin/sync/sp-ratings | 3-7 seconds | Larger dataset |
| POST /admin/sync-all | 15-30 seconds | Multiple API calls |

## 🔍 Debugging with jq

### Pretty print JSON
```bash
curl "https://cfb.projectthomas.com/rankings?season=2024&week=10" | jq '.'
```

### Extract specific fields
```bash
# Get just team names and ranks
curl "https://cfb.projectthomas.com/admin/rankings/ap?season=2024&week=10" | \
  jq '.rankings[] | {team: .team, rank: .rank}'
```

### Count records
```bash
# How many teams in AP poll?
curl "https://cfb.projectthomas.com/admin/rankings/ap?season=2024&week=10" | \
  jq '.rankings | length'
```

### Filter results
```bash
# Only SEC teams
curl "https://cfb.projectthomas.com/admin/rankings/ap?season=2024&week=10" | \
  jq '.rankings[] | select(.team | contains("Alabama", "Georgia", "LSU"))'
```

## 🐛 Common Errors & Solutions

### Error: 404 Not Found
```json
{
  "detail": "Not Found"
}
```
**Solution**: Check endpoint URL, ensure you're using correct HTTP method (GET vs POST)

### Error: 500 Internal Server Error
```json
{
  "detail": "Sync failed: No data returned from API"
}
```
**Solutions**:
1. Check if week number is valid (games have occurred)
2. Verify CFBD API key is valid
3. Check Railway logs: `railway logs`

### Error: Empty rankings array
```json
{
  "rankings": [],
  "count": 0
}
```
**Solutions**:
1. Run sync endpoint first to populate data
2. Check if data exists for that season/week in database
3. Verify week number is valid

### Error: Rate limit exceeded
```json
{
  "detail": "API request failed: 429 Too Many Requests"
}
```
**Solutions**:
1. Wait 60 seconds and try again
2. Increase `rate_limit_delay` in sync service
3. Don't sync all weeks at once, do them one at a time

## 🔐 Security Notes

### Add Authentication (Recommended for Production)
```python
# In api.py, add API key authentication
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    if api_key != os.getenv("ADMIN_API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

# Apply to admin endpoints
@app.post("/admin/sync-all", dependencies=[Depends(verify_api_key)])
async def sync_all_data(...):
    ...
```

### Then use with curl:
```bash
curl -X POST "https://cfb.projectthomas.com/admin/sync-all?season=2024&include=all" \
  -H "X-API-Key: your-secret-key"
```

## 📱 Mobile/Script Usage

### Python Script
```python
import requests

BASE_URL = "https://cfb.projectthomas.com"

# Sync data
response = requests.post(
    f"{BASE_URL}/admin/sync-all",
    params={"season": 2024, "week": 10, "include": "all"}
)
print(response.json())

# Get rankings
rankings = requests.get(
    f"{BASE_URL}/admin/rankings/ap",
    params={"season": 2024, "week": 10}
).json()

for team in rankings["rankings"][:10]:
    print(f"{team['rank']}. {team['team']} - {team['points']} pts")
```

### JavaScript (Browser)
```javascript
// Sync data
const syncData = async () => {
  const response = await fetch(
    '/admin/sync-all?season=2024&week=10&include=all',
    { method: 'POST' }
  );
  const result = await response.json();
  console.log(`Synced ${result.total_added} new records`);
};

// Get rankings
const getRankings = async () => {
  const response = await fetch('/admin/rankings/ap?season=2024&week=10');
  const data = await response.json();
  return data.rankings;
};
```

## 🎯 Quick Command Cheatsheet

```bash
# Sync everything for current week
curl -X POST "https://cfb.projectthomas.com/admin/sync-all?season=2024&week=10&include=all"

# Get AP rankings
curl "https://cfb.projectthomas.com/admin/rankings/ap?season=2024&week=10" | jq '.'

# Get SP+ ratings
curl "https://cfb.projectthomas.com/admin/ratings/sp?season=2024&week=10" | jq '.'

# Get team details
curl "https://cfb.projectthomas.com/admin/team/Georgia/details?season=2024" | jq '.'

# Check system health
curl "https://cfb.projectthomas.com/health"

# View API docs
open "https://cfb.projectthomas.com/docs"
```

---

**Tip**: Save these commands in a file like `sync-commands.sh` for easy reuse during the season!
