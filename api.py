# api.py - Refactored to use database

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import uvicorn
import logging

from db_models_complete import get_db, Game, Team, CustomRanking, init_db
from cfb_ranking_system import RankingSystem, RankingFormula
from sync_service_complete import CFBDataSyncService, run_daily_sync

logging.basicConfig(level=logging.INFO)
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

# Pydantic models for API responses
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

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and start background scheduler"""
    init_db()
    logger.info("Database initialized")
    
    # Start background scheduler for daily syncs
    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_daily_sync, 'cron', hour=6)  # Run at 6 AM daily
    scheduler.start()
    logger.info("Background scheduler started")

def compute_rankings_from_db(
    db: Session,
    year: int,
    season_type: str = "regular",
    week: Optional[int] = None,
    formula_params: Optional[FormulaParams] = None
) -> RankingSystem:
    """
    Compute rankings from database games.
    
    Args:
        db: Database session
        year: Season year
        season_type: 'regular' or 'postseason'
        week: Optional week number (includes all games up to and including this week)
        formula_params: Optional custom formula parameters
    
    Returns:
        RankingSystem with computed rankings
    """
    # Update formula if custom params provided
    if formula_params:
        RankingFormula.WIN_LOSS_MULTIPLIER = formula_params.win_loss_multiplier
        RankingFormula.ONE_SCORE_MULTIPLIER = formula_params.one_score_multiplier
        RankingFormula.TWO_SCORE_MULTIPLIER = formula_params.two_score_multiplier
        RankingFormula.THREE_SCORE_MULTIPLIER = formula_params.three_score_multiplier
        RankingFormula.STRENGTH_OF_SCHEDULE_MULTIPLIER = formula_params.strength_of_schedule_multiplier
    else:
        # Reset to defaults
        RankingFormula.WIN_LOSS_MULTIPLIER = 1.0
        RankingFormula.ONE_SCORE_MULTIPLIER = 1.0
        RankingFormula.TWO_SCORE_MULTIPLIER = 1.3
        RankingFormula.THREE_SCORE_MULTIPLIER = 1.5
        RankingFormula.STRENGTH_OF_SCHEDULE_MULTIPLIER = 1.0
    
    # Query games from database
    query = db.query(Game).filter(
        Game.season == year,
        Game.season_type == season_type,
        Game.completed == True  # Only completed games
    )
    
    # Filter by week if specified (include all games up to this week)
    if week is not None:
        query = query.filter(Game.week <= week)
    
    games = query.all()
    
    if not games:
        raise ValueError(f"No games found for {year} {season_type}" + (f" week {week}" if week else ""))
    
    # Build ranking system from database games
    system = RankingSystem()
    
    for game in games:
        # Skip games without scores
        if game.home_points is None or game.away_points is None:
            continue
        
        # Determine FBS status
        # Query teams to get classification
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
            CustomRanking.team == team.name,
            CustomRanking.formula_params == formula_json
        ).first()
        
        if existing:
            # Update existing
            existing.rank = rank
            existing.ranking_value = float(team.ranking)
            existing.wins = wins
            existing.losses = losses
            existing.computed_at = datetime.utcnow()
        else:
            # Create new
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

@app.get("/")
async def root():
    """Serve the frontend HTML"""
    return FileResponse('cfb-rankings.html')

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
        # Compute rankings
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

@app.get("/games")
async def get_games(
    year: int = Query(2024, description="Season year"),
    season_type: str = Query("regular", description="Season type"),
    week: Optional[int] = Query(None, description="Week number"),
    team: Optional[str] = Query(None, description="Filter by team"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
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
                (Game.home_team == team) | (Game.away_team == team)
            )
        
        if completed is not None:
            query = query.filter(Game.completed == completed)
        
        games = query.order_by(Game.week, Game.start_date).all()
        
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
                    'venue': g.venue
                }
                for g in games
            ],
            'total': len(games)
        }
        
    except Exception as e:
        logger.error(f"Error getting games: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/sync")
async def trigger_sync(
    season: int = Query(2024, description="Season to sync"),
    sync_type: str = Query("weekly", description="Sync type: weekly, full, or games_only"),
    week: Optional[int] = Query(None, description="Week number for weekly sync"),
    db: Session = Depends(get_db)
):
    """
    Manually trigger a data sync from College Football Data API.
    """
    import os
    
    try:
        api_key = os.getenv("CFBD_API_KEY", "mBIqtiooiszQC3myFOJyvK4y8j5ZUzRr5JXRCjl0yjOvXIOFrdKLix4b+upMY2cw")
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
            raise HTTPException(status_code=400, detail="Invalid sync_type")
        
        return {"status": "success", "results": result}
        
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats/sync-log")
async def get_sync_log(
    limit: int = Query(50, description="Number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Get sync log history.
    """
    from db_models_complete import SyncLog
    
    try:
        logs = db.query(SyncLog).order_by(
            SyncLog.started_at.desc()
        ).limit(limit).all()
        
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
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting sync log: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint with database connectivity test"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        
        # Get some basic stats
        from db_models_complete import SyncLog
        last_sync = db.query(SyncLog).order_by(
            SyncLog.completed_at.desc()
        ).first()
        
        game_count = db.query(Game).count()
        
        return {
            "status": "healthy",
            "database": "connected",
            "total_games": game_count,
            "last_sync": last_sync.completed_at.isoformat() if last_sync and last_sync.completed_at else None
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)