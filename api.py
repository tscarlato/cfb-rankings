# api.py - Complete version with all features and Railway compatibility

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime
import uvicorn
import logging
import os

from db_models_complete import (
    get_db, Game, Team, CustomRanking, SyncLog, init_db, 
    engine, DATABASE_URL, SessionLocal
)
from cfb_ranking_system import RankingSystem, RankingFormula

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="College Football Rankings API",
    description="Custom ranking system for college football teams",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== PYDANTIC MODELS ====================

class GameResultResponse(BaseModel):
    opponent: str
    opponent_record: str
    opponent_rank: float
    won: bool
    margin: int
    value: float
    week: Optional[int] = None

class TeamResponse(BaseModel):
    name: str
    wins: int
    losses: int
    ranking: float
    games: List[GameResultResponse]

class RankingsResponse(BaseModel):
    teams: List[TeamResponse]
    total_teams: int
    year: int
    season_type: str
    week: Optional[int] = None
    computed_at: str

class FormulaParams(BaseModel):
    win_loss_multiplier: float = 1.0
    one_score_multiplier: float = 1.0
    two_score_multiplier: float = 1.3
    three_score_multiplier: float = 1.5
    strength_of_schedule_multiplier: float = 1.0

# ==================== STARTUP ====================

@app.on_event("startup")
async def startup_event():
    """Initialize database and start background scheduler"""
    try:
        logger.info("=" * 60)
        logger.info("CFB Rankings API Starting Up")
        logger.info("=" * 60)
        
        # Check database connection
        logger.info("Testing database connection...")
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("✓ Database connection successful!")
        
        # Initialize tables
        logger.info("Initializing database tables...")
        init_db()
        logger.info("✓ Database tables initialized!")
        
        # Check for existing data
        db = SessionLocal()
        try:
            game_count = db.query(Game).count()
            team_count = db.query(Team).count()
            logger.info(f"✓ Database contains {team_count} teams and {game_count} games")
        finally:
            db.close()
        
        # Start scheduler if enabled
        if os.getenv("ENABLE_SCHEDULER", "false").lower() == "true":
            from apscheduler.schedulers.background import BackgroundScheduler
            from sync_service_complete import run_daily_sync
            
            scheduler = BackgroundScheduler()
            scheduler.add_job(run_daily_sync, 'cron', hour=6)
            scheduler.start()
            logger.info("✓ Background scheduler started (runs daily at 6 AM)")
        else:
            logger.info("ℹ Background scheduler disabled (set ENABLE_SCHEDULER=true to enable)")
        
        logger.info("=" * 60)
        logger.info("CFB Rankings API Ready!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"✗ Startup error: {e}")
        logger.warning("App will continue but some features may not work")
        import traceback
        traceback.print_exc()

# ==================== HELPER FUNCTIONS ====================

def compute_rankings_from_db(
    db: Session,
    year: int,
    season_type: str = "regular",
    week: Optional[int] = None,
    formula_params: Optional[FormulaParams] = None
) -> RankingSystem:
    """
    Compute rankings from database games.
    """
    # Update formula if custom params provided
    if formula_params:
        RankingFormula.WIN_LOSS_MULTIPLIER = formula_params.win_loss_multiplier
        RankingFormula.ONE_SCORE_MULTIPLIER = formula_params.one_score_multiplier
        RankingFormula.TWO_SCORE_MULTIPLIER = formula_params.two_score_multiplier
        RankingFormula.THREE_SCORE_MULTIPLIER = formula_params.three_score_multiplier
        RankingFormula.STRENGTH_OF_SCHEDULE_MULTIPLIER = formula_params.strength_of_schedule_multiplier
    else:
        RankingFormula.reset_to_defaults()
    
    # Query games from database
    query = db.query(Game).filter(
        Game.season == year,
        Game.season_type == season_type,
        Game.completed == True
    )
    
    if week is not None:
        query = query.filter(Game.week <= week)
    
    games = query.all()
    
    if not games:
        raise ValueError(f"No games found for {year} {season_type}" + (f" week {week}" if week else ""))
    
    # Build ranking system
    system = RankingSystem()
    
    for game in games:
        if game.home_points is None or game.away_points is None:
            continue
        
        # Get team classifications
        home_team_obj = db.query(Team).filter(Team.school == game.home_team).first()
        away_team_obj = db.query(Team).filter(Team.school == game.away_team).first()
        
        home_fbs = home_team_obj.classification == 'fbs' if home_team_obj else True
        away_fbs = away_team_obj.classification == 'fbs' if away_team_obj else True
        
        system.add_game(
            home_name=game.home_team,
            home_score=game.home_points,
            away_name=game.away_team,
            away_score=game.away_points,
            home_fbs=home_fbs,
            away_fbs=away_fbs,
            week=game.week
        )
    
    # Calculate rankings
    system.calculate_rankings(iterations=20)
    
    logger.info(f"Computed rankings from {len(games)} games, {len(system.teams)} teams")
    
    return system

def save_rankings_to_db(
    db: Session,
    system: RankingSystem,
    year: int,
    season_type: str,
    week: Optional[int],
    formula_params: Optional[FormulaParams]
):
    """Save computed rankings to database"""
    ranked_teams = system.get_rankings(sort=True)
    
    # Store formula params as JSON
    formula_json = None
    if formula_params:
        formula_json = {
            'win_loss_multiplier': formula_params.win_loss_multiplier,
            'one_score_multiplier': formula_params.one_score_multiplier,
            'two_score_multiplier': formula_params.two_score_multiplier,
            'three_score_multiplier': formula_params.three_score_multiplier,
            'strength_of_schedule_multiplier': formula_params.strength_of_schedule_multiplier,
        }
    
    for rank, team in enumerate(ranked_teams, 1):
        wins, losses = team.get_record()
        
        # Check if ranking already exists
        existing = db.query(CustomRanking).filter(
            CustomRanking.season == year,
            CustomRanking.season_type == season_type,
            CustomRanking.week == week,
            CustomRanking.team == team.name
        ).first()
        
        if existing:
            existing.rank = rank
            existing.ranking_value = float(team.ranking)
            existing.wins = wins
            existing.losses = losses
            existing.formula_params = formula_json
            existing.computed_at = datetime.utcnow()
        else:
            db.add(CustomRanking(
                season=year,
                season_type=season_type,
                week=week,
                team=team.name,
                rank=rank,
                ranking_value=float(team.ranking),
                wins=wins,
                losses=losses,
                formula_params=formula_json,
                computed_at=datetime.utcnow()
            ))
    
    db.commit()
    logger.info(f"Saved {len(ranked_teams)} rankings to database")

def format_team_response(team, system: RankingSystem) -> TeamResponse:
    """Convert Team object to API response format"""
    games = []
    for game in team.game_results:
        opp_wins, opp_losses = game.opponent.get_record()
        games.append(GameResultResponse(
            opponent=game.opponent.name,
            opponent_record=f"{opp_wins}-{opp_losses}",
            opponent_rank=game.opponent.ranking,
            won=game.won,
            margin=game.margin,
            value=game.ranking_value,
            week=game.week
        ))
    
    wins, losses = team.get_record()
    return TeamResponse(
        name=team.name,
        wins=wins,
        losses=losses,
        ranking=team.ranking,
        games=games
    )

# ==================== ROOT & HEALTH ENDPOINTS ====================

@app.get("/")
async def root():
    """Basic API info"""
    return {
        "name": "College Football Rankings API",
        "version": "2.0.0",
        "status": "running",
        "database_configured": bool(DATABASE_URL),
        "endpoints": {
            "rankings": "/rankings",
            "team": "/team/{team_name}",
            "games": "/games",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check with database connectivity test"""
    response = {
        "status": "healthy",
        "database": "not_configured",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        response["database"] = "connected"
        
        # Get some stats
        db = SessionLocal()
        try:
            game_count = db.query(Game).count()
            team_count = db.query(Team).count()
            response["total_games"] = game_count
            response["total_teams"] = team_count
        except Exception as e:
            logger.warning(f"Could not get database stats: {e}")
        finally:
            db.close()
            
    except Exception as e:
        logger.warning(f"Health check database test failed: {e}")
        response["database"] = "unavailable"
        response["database_error"] = str(e)
    
    return response

@app.get("/db-status")
async def db_status():
    """Detailed database status"""
    try:
        # Hide sensitive info
        safe_url = "not_configured"
        if DATABASE_URL:
            safe_url = DATABASE_URL.split('@')[0] + "@***" if '@' in DATABASE_URL else "***"
        
        status = {
            "database_url_configured": bool(DATABASE_URL),
            "database_url": safe_url,
            "connection": "unknown",
            "using_sqlite": DATABASE_URL.startswith("sqlite") if DATABASE_URL else False
        }
        
        try:
            with engine.connect() as conn:
                result = conn.execute("SELECT version()")
                version_row = result.fetchone()
                version = version_row[0] if version_row else "unknown"
                status["connection"] = "success"
                status["version"] = version
        except Exception as e:
            status["connection"] = "failed"
            status["error"] = str(e)
        
        return status
    except Exception as e:
        return {
            "error": str(e),
            "connection": "failed"
        }

# ==================== RANKINGS ENDPOINTS ====================

@app.get("/rankings", response_model=RankingsResponse)
async def get_rankings(
    year: int = Query(2024, description="Season year"),
    season_type: str = Query("regular", description="Season type: regular or postseason"),
    week: Optional[int] = Query(None, description="Specific week number (includes all games up to this week)"),
    top_n: Optional[int] = Query(None, description="Limit to top N teams"),
    save: bool = Query(False, description="Save computed rankings to database"),
    # Formula parameters
    win_loss_multiplier: float = Query(1.0, description="Win/loss multiplier"),
    one_score_multiplier: float = Query(1.0, description="1-score game multiplier (≤8 pts)"),
    two_score_multiplier: float = Query(1.3, description="2-score game multiplier (9-16 pts)"),
    three_score_multiplier: float = Query(1.5, description="3+ score game multiplier (>16 pts)"),
    strength_of_schedule_multiplier: float = Query(1.0, description="Strength of schedule multiplier"),
    db: Session = Depends(get_db)
):
    """
    Get custom rankings computed from database games.
    """
    try:
        formula_params = FormulaParams(
            win_loss_multiplier=win_loss_multiplier,
            one_score_multiplier=one_score_multiplier,
            two_score_multiplier=two_score_multiplier,
            three_score_multiplier=three_score_multiplier,
            strength_of_schedule_multiplier=strength_of_schedule_multiplier
        )
        
        # Compute rankings from database
        system = compute_rankings_from_db(db, year, season_type, week, formula_params)
        
        # Optionally save to database
        if save:
            save_rankings_to_db(db, system, year, season_type, week, formula_params)
        
        # Get ranked teams
        ranked_teams = system.get_rankings(sort=True)
        if top_n:
            ranked_teams = ranked_teams[:top_n]
        
        teams_response = [
            format_team_response(team, system) 
            for team in ranked_teams
        ]
        
        return RankingsResponse(
            teams=teams_response,
            total_teams=len(system.teams),
            year=year,
            season_type=season_type,
            week=week,
            computed_at=datetime.utcnow().isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        logger.error(f"Error computing rankings: {error_msg}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/team/{team_name}", response_model=TeamResponse)
async def get_team(
    team_name: str,
    year: int = Query(2024, description="Season year"),
    season_type: str = Query("regular", description="Season type"),
    week: Optional[int] = Query(None, description="Specific week"),
    db: Session = Depends(get_db)
):
    """
    Get detailed information for a specific team.
    """
    try:
        system = compute_rankings_from_db(db, year, season_type, week)
        
        if team_name not in system.teams:
            raise HTTPException(status_code=404, detail=f"Team '{team_name}' not found")
        
        team = system.teams[team_name]
        return format_team_response(team, system)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting team: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/saved-rankings")
async def get_saved_rankings(
    year: int = Query(2024, description="Season year"),
    season_type: str = Query("regular", description="Season type"),
    week: Optional[int] = Query(None, description="Week number"),
    db: Session = Depends(get_db)
):
    """
    Get previously saved rankings from database.
    """
    try:
        query = db.query(CustomRanking).filter(
            CustomRanking.season == year,
            CustomRanking.season_type == season_type
        )
        
        if week is not None:
            query = query.filter(CustomRanking.week == week)
        
        rankings = query.order_by(CustomRanking.rank).all()
        
        if not rankings:
            raise HTTPException(
                status_code=404, 
                detail=f"No saved rankings found for {year} {season_type}" + 
                       (f" week {week}" if week else "")
            )
        
        return {
            'rankings': [
                {
                    'rank': r.rank,
                    'team': r.team,
                    'ranking_value': float(r.ranking_value),
                    'wins': r.wins,
                    'losses': r.losses,
                    'computed_at': r.computed_at.isoformat()
                }
                for r in rankings
            ],
            'formula_params': rankings[0].formula_params if rankings else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting saved rankings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== GAMES ENDPOINTS ====================

@app.get("/games")
async def get_games(
    year: int = Query(2024, description="Season year"),
    season_type: str = Query("regular", description="Season type"),
    week: Optional[int] = Query(None, description="Week number"),
    team: Optional[str] = Query(None, description="Filter by team"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    limit: int = Query(100, description="Max number of games to return"),
    db: Session = Depends(get_db)
):
    """
    Get games from database.
    """
    try:
        query = db.query(Game).filter(
            Game.season == year,
            Game.season_type == season_type
        )
        
        if week is not None:
            query = query.filter(Game.week == week)
        
        if team:
            query = query.filter(
                or_(Game.home_team == team, Game.away_team == team)
            )
        
        if completed is not None:
            query = query.filter(Game.completed == completed)
        
        games = query.order_by(Game.week, Game.start_date).limit(limit).all()
        
        return {
            'games': [
                {
                    'id': g.id,
                    'week': g.week,
                    'home_team': g.home_team,
                    'away_team': g.away_team,
                    'home_points': g.home_points,
                    'away_points': g.away_points,
                    'completed': g.completed,
                    'start_date': g.start_date,
                    'venue': g.venue,
                    'neutral_site': g.neutral_site
                }
                for g in games
            ],
            'total': len(games),
            'limited': len(games) == limit
        }
        
    except Exception as e:
        logger.error(f"Error getting games: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ADMIN ENDPOINTS ====================

@app.post("/admin/sync")
async def trigger_sync(
    season: int = Query(2024, description="Season to sync"),
    sync_type: str = Query("weekly", description="Sync type: weekly, full, or games_only"),
    week: Optional[int] = Query(None, description="Week number for weekly sync"),
    db: Session = Depends(get_db)
):
    """
    Manually trigger a data sync from College Football Data API.
    Requires CFBD_API_KEY environment variable.
    """
    try:
        api_key = os.getenv("CFBD_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500, 
                detail="CFBD_API_KEY not configured. Set environment variable to enable syncing."
            )
        
        from sync_service_complete import CFBDataSyncService
        sync_service = CFBDataSyncService(api_key)
        
        if sync_type == "weekly" and week:
            result = sync_service.sync_weekly_update(db, season, week)
        elif sync_type == "full":
            result = sync_service.sync_season_core_data(db, season)
        elif sync_type == "games_only":
            result = {
                'games_regular': sync_service.sync_games(db, season, 'regular'),
                'games_postseason': sync_service.sync_games(db, season, 'postseason')
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid sync_type. Must be: weekly, full, or games_only")
        
        return {"status": "success", "results": result}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/sync-log")
async def get_sync_log(
    limit: int = Query(50, description="Number of records to return"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """
    Get sync log history.
    """
    try:
        query = db.query(SyncLog).order_by(SyncLog.started_at.desc())
        
        if status:
            query = query.filter(SyncLog.status == status)
        
        logs = query.limit(limit).all()
        
        return {
            'logs': [
                {
                    'id': log.id,
                    'sync_type': log.sync_type,
                    'season': log.season,
                    'week': log.week,
                    'status': log.status,
                    'records_added': log.records_added,
                    'records_updated': log.records_updated,
                    'error_message': log.error_message,
                    'started_at': log.started_at.isoformat(),
                    'completed_at': log.completed_at.isoformat() if log.completed_at else None
                }
                for log in logs
            ],
            'total': len(logs)
        }
        
    except Exception as e:
        logger.error(f"Error getting sync log: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== STATS ENDPOINTS ====================

@app.get("/stats/summary")
async def get_stats_summary(db: Session = Depends(get_db)):
    """Get summary statistics about the database"""
    try:
        stats = {
            "teams": db.query(Team).count(),
            "games": db.query(Game).count(),
            "completed_games": db.query(Game).filter(Game.completed == True).count(),
            "custom_rankings": db.query(CustomRanking).count(),
        }
        
        # Get seasons with data
        seasons = db.query(Game.season).distinct().all()
        stats["seasons"] = sorted([s[0] for s in seasons])
        
        # Get most recent sync
        last_sync = db.query(SyncLog).order_by(SyncLog.completed_at.desc()).first()
        if last_sync and last_sync.completed_at:
            stats["last_sync"] = last_sync.completed_at.isoformat()
            stats["last_sync_status"] = last_sync.status
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting stats summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== RUN SERVER ====================

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)