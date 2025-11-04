# CFB Rankings API - Railway Deployment

## Quick Deploy to Railway

### 1. Prerequisites
- Railway account (https://railway.app)
- GitHub repository with this code

### 2. Setup Steps

1. **Create New Project in Railway**
   - Click "New Project"
   - Choose "Deploy from GitHub repo"
   - Select your repository

2. **Add PostgreSQL Database**
   - Click "New" → "Database" → "Add PostgreSQL"
   - Railway will automatically create `DATABASE_URL` variable

3. **Set Environment Variables**
   Go to your service → Variables tab:
```
   CFBD_API_KEY=mBIqtiooiszQC3myFOJyvK4y8j5ZUzRr5JXRCjl0yjOvXIOFrdKLix4b+upMY2cw
   ENABLE_SCHEDULER=false
```

4. **Deploy**
   - Push to GitHub
   - Railway will automatically build and deploy
   - Wait for deployment to complete

5. **Initialize Database**
   Once deployed, open the Railway shell and run:
```bash
   python setup_railway.py
```

6. **Test the API**
   Visit your Railway URL:
   - `https://your-app.railway.app/` - API info
   - `https://your-app.railway.app/health` - Health check
   - `https://your-app.railway.app/docs` - Interactive API docs

### 3. Manual Data Sync (Optional)

If automatic sync didn't work, you can manually trigger it:
```bash
curl -X POST "https://your-app.railway.app/admin/sync?season=2024&sync_type=full"
```

Or via the interactive docs at `/docs`

## API Endpoints

### Core Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `GET /db-status` - Database status

### Rankings
- `GET /rankings?year=2024&week=10` - Get rankings
- `GET /team/{team_name}` - Get team details
- `GET /saved-rankings` - Get saved rankings

### Data
- `GET /games?year=2024&week=10` - Get games
- `GET /stats/summary` - Database statistics

### Admin (requires CFBD_API_KEY)
- `POST /admin/sync` - Trigger data sync
- `GET /admin/sync-log` - View sync history

## Troubleshooting

### Database Connection Issues
1. Check that PostgreSQL service is added
2. Verify `DATABASE_URL` is set in environment variables
3. Check `/db-status` endpoint for connection info

### No Data
1. Make sure `CFBD_API_KEY` is set
2. Run `python setup_railway.py` in Railway shell
3. Or trigger sync via `/admin/sync` endpoint

### API Errors
1. Check logs in Railway dashboard
2. Visit `/health` to see system status
3. Check `/db-status` for database connectivity

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file:
```
DATABASE_URL=postgresql://user:password@localhost:5432/cfb_rankings
CFBD_API_KEY=your_api_key
ENABLE_SCHEDULER=false
PORT=8000
```

3. Initialize database:
```bash
python setup_database.py init
python setup_database.py populate
```

4. Run server:
```bash
python api.py
```

Visit http://localhost:8000

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes* | PostgreSQL connection string (auto-set by Railway) |
| `CFBD_API_KEY` | No** | College Football Data API key for syncing |
| `ENABLE_SCHEDULER` | No | Enable daily auto-sync (default: false) |
| `PORT` | No | Server port (default: 8000) |

\* Required for production, auto-set by Railway when you add PostgreSQL
\** Required only for data syncing

## Custom Formula Parameters

You can customize the ranking formula via query parameters:
```bash
/rankings?year=2024&win_loss_multiplier=1.5&three_score_multiplier=2.0
```

Available parameters:
- `win_loss_multiplier` (default: 1.0)
- `one_score_multiplier` (default: 1.0)
- `two_score_multiplier` (default: 1.3)
- `three_score_multiplier` (default: 1.5)
- `strength_of_schedule_multiplier` (default: 1.0)