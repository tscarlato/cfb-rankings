# Simple Integration Guide - Database-Backed Rankings

## What This Does

Restores your original 4-file functionality, but:
- ✅ Loads from database instead of hitting CFBD API every request
- ✅ No rate limiting issues
- ✅ Same exact endpoints and behavior
- ✅ Nightly sync keeps data fresh

## Files You Need

1. **cfb_ranking_system_db.py** - Modified ranking system (loads from DB)
2. **api_db.py** - Your API (loads from DB instead of API)
3. **sync_nightly.py** - Nightly sync script
4. **cfb-rankings.html** - Your existing HTML (NO CHANGES)

## Step 1: Replace Files

```bash
# Backup originals
cp cfb_ranking_system.py cfb_ranking_system.py.backup
cp api.py api.py.backup

# Replace with database versions
cp cfb_ranking_system_db.py cfb_ranking_system.py
cp api_db.py api.py

# Add sync script
cp sync_nightly.py sync_nightly.py
```

## Step 2: Update requirements.txt

Add one line:
```
sqlalchemy==2.0.23
```

Your full requirements.txt should be:
```
fastapi==0.115.0
uvicorn==0.32.0
requests==2.32.3
pydantic==2.10.0
python-multipart==0.0.12
sqlalchemy==2.0.23
```

## Step 3: Run Initial Sync

Before deploying, populate your database:

```bash
# Set environment variables
export DATABASE_URL="your_railway_postgres_url"
export CFBD_API_KEY="mBIqtiooiszQC3myFOJyvK4y8j5ZUzRr5JXRCjl0yjOvXIOFrdKLix4b+upMY2cw"

# Run sync
python sync_nightly.py
```

This will:
- Sync all FBS teams (~130)
- Sync all 2024 regular season games (~800)
- Takes ~2 minutes

## Step 4: Deploy

```bash
git add .
git commit -m "Switch to database backend"
git push origin main
```

Railway auto-deploys.

## Step 5: Set Up Nightly Sync

In Railway, add a cron job:

```yaml
# railway.toml (create this file)
[[services]]
name = "nightly-sync"
command = "python sync_nightly.py"
cron = "0 6 * * *"  # Run at 6 AM daily
```

Or use Railway's scheduled jobs feature in the dashboard.

## What Changed

### Your Original Flow:
```
Browser → /rankings → API calls CFBD → Calculate rankings → Return
```

### New Flow:
```
Browser → /rankings → Load from DB → Calculate rankings → Return
```

### No API Changes:
- ✅ Same `/rankings` endpoint
- ✅ Same `/team/{name}` endpoint  
- ✅ Same parameters
- ✅ Same responses
- ✅ Frontend unchanged

## Testing

```bash
# Test locally
python api_db.py

# In browser:
http://localhost:8000

# Should show rankings for 2024
```

## Verification

After deployment:

1. Visit https://cfb.projectthomas.com
2. Should load rankings instantly (no waiting for API)
3. Change week - should update instantly
4. Adjust formula parameters - should recalculate instantly

## Troubleshooting

### "No games found in database"
→ Run sync_nightly.py to populate data

### "DatabaseLoader error"
→ Check DATABASE_URL is set in Railway

### "Table doesn't exist"
→ You need the database schema from db_models_complete.py
→ Tables: teams, games (that's all you need)

## What You DON'T Need

- ❌ AP rankings sync
- ❌ SP+ ratings sync
- ❌ FPI ratings sync
- ❌ Betting lines
- ❌ Recruiting data
- ❌ Any of the complex stuff

## What You DO Need

- ✅ Teams table
- ✅ Games table
- ✅ Nightly sync
- ✅ That's it!

## Database Schema

Minimum required tables:

```sql
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    school VARCHAR(255) UNIQUE NOT NULL,
    mascot VARCHAR(255),
    abbreviation VARCHAR(10),
    classification VARCHAR(10),
    conference VARCHAR(255),
    division VARCHAR(255),
    color VARCHAR(10),
    alt_color VARCHAR(10)
);

CREATE TABLE games (
    id INTEGER PRIMARY KEY,
    season INTEGER NOT NULL,
    week INTEGER,
    season_type VARCHAR(20),
    start_date TIMESTAMP,
    completed BOOLEAN,
    home_team VARCHAR(255),
    away_team VARCHAR(255),
    home_points INTEGER,
    away_points INTEGER,
    venue VARCHAR(255),
    neutral_site BOOLEAN,
    conference_game BOOLEAN
);

CREATE INDEX idx_games_season_week ON games(season, week);
CREATE INDEX idx_games_teams ON games(home_team, away_team);
```

## Success Criteria

✅ Site loads instantly
✅ Rankings calculate from database
✅ No CFBD API calls on page load
✅ Formula parameters work
✅ Week selection works
✅ Nightly sync updates data

## Time to Implement

- Step 1-2: 5 minutes
- Step 3: 2 minutes (sync time)
- Step 4: 2 minutes (deploy)
- Step 5: 3 minutes (cron setup)

**Total: ~15 minutes**

## Summary

This is the minimal solution that:
1. Restores your original functionality
2. Eliminates rate limiting
3. Keeps data fresh with nightly sync
4. Changes nothing about how users interact with your site

No complicated features. No extra endpoints. Just your rankings, backed by a database.
