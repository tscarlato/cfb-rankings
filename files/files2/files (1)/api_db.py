# api_db.py
# Minimal version that restores original functionality with database backend

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os

app = FastAPI(
    title="College Football Rankings API",
    description="Custom ranking system for college football teams",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models (same as original)
class GameResultResponse(BaseModel):
    opponent: str
    opponent_record: str
    opponent_rank: float
    won: bool
    margin: int
    value: float

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
    classification: str

class FormulaParams(BaseModel):
    win_loss_multiplier: float = 1.0
    one_score_multiplier: float = 1.0
    two_score_multiplier: float = 1.3
    three_score_multiplier: float = 1.5
    strength_of_schedule_multiplier: float = 1.0

# Cache for storing ranking system
ranking_cache = {}

def get_or_create_rankings(
    year: int = 2024,
    season_type: str = "regular",
    classification: str = "fbs",
    week: Optional[int] = None,
    formula_params: Optional[FormulaParams] = None
):
    """Get rankings from cache or compute them from database."""
    
    # Create cache key
    formula_key = ""
    if formula_params:
        formula_key = f"_{formula_params.win_loss_multiplier}_{formula_params.one_score_multiplier}_{formula_params.two_score_multiplier}_{formula_params.three_score_multiplier}_{formula_params.strength_of_schedule_multiplier}"
    
    cache_key = f"{year}_{season_type}_{classification}_{week}{formula_key}"
    
    if cache_key in ranking_cache:
        return ranking_cache[cache_key]
    
    # Import database-backed ranking system
    from cfb_ranking_system_db import DatabaseLoader, RankingSystem, RankingFormula
    
    # Update formula if custom params provided
    if formula_params:
        RankingFormula.WIN_LOSS_MULTIPLIER = formula_params.win_loss_multiplier
        RankingFormula.ONE_SCORE_MULTIPLIER = formula_params.one_score_multiplier
        RankingFormula.TWO_SCORE_MULTIPLIER = formula_params.two_score_multiplier
        RankingFormula.THREE_SCORE_MULTIPLIER = formula_params.three_score_multiplier
        RankingFormula.STRENGTH_OF_SCHEDULE_MULTIPLIER = formula_params.strength_of_schedule_multiplier
    
    # Load from database instead of API
    try:
        db_loader = DatabaseLoader()
        system = RankingSystem()
        
        system.load_games_from_database(
            db_loader=db_loader,
            year=year,
            season_type=season_type,
            classification=classification,
            week=week
        )
        
        # Check if any games were loaded
        if len(system.teams) == 0:
            raise ValueError(f"No games found in database for {year} {season_type} {classification}")
        
        system.calculate_rankings(iterations=20)
        
        # Cache the result
        ranking_cache[cache_key] = system
        return system
        
    except Exception as e:
        print(f"Error loading from database: {e}")
        raise

def format_team_response(team, rank: int) -> TeamResponse:
    """Convert Team object to API response format."""
    games = []
    for game in team.game_results:
        opp_wins, opp_losses = game.opponent.get_record()
        games.append(GameResultResponse(
            opponent=game.opponent.name,
            opponent_record=f"{opp_wins}-{opp_losses}",
            opponent_rank=game.opponent.ranking,
            won=game.won,
            margin=game.margin,
            value=game.ranking_value
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
    """Serve the frontend HTML."""
    return FileResponse('cfb-rankings.html')

@app.get("/rankings", response_model=RankingsResponse)
async def get_rankings(
    year: int = Query(2024, description="Season year"),
    season_type: str = Query("regular", description="Season type: regular or postseason"),
    classification: str = Query("fbs", description="Division: fbs, fcs, ii, or iii"),
    week: Optional[int] = Query(None, description="Specific week number (1-15)"),
    top_n: Optional[int] = Query(None, description="Limit to top N teams"),
    # Formula parameters
    win_loss_multiplier: float = Query(1.0, description="Multiplier applied to base (+1 for win, -1 for loss)"),
    one_score_multiplier: float = Query(1.0, description="Multiplier for 1-score games (≤8 pts)"),
    two_score_multiplier: float = Query(1.3, description="Multiplier for 2-score games (9-16 pts)"),
    three_score_multiplier: float = Query(1.5, description="Multiplier for 3+ score games (>16 pts)"),
    strength_of_schedule_multiplier: float = Query(1.0, description="Multiplier for strength of schedule impact")
):
    """
    Get rankings - exactly like the original but loads from database.
    """
    try:
        formula_params = FormulaParams(
            win_loss_multiplier=win_loss_multiplier,
            one_score_multiplier=one_score_multiplier,
            two_score_multiplier=two_score_multiplier,
            three_score_multiplier=three_score_multiplier,
            strength_of_schedule_multiplier=strength_of_schedule_multiplier
        )
        
        system = get_or_create_rankings(year, season_type, classification, week, formula_params)
        
        ranked_teams = system.get_rankings(sort=True)
        if top_n:
            ranked_teams = ranked_teams[:top_n]
        
        teams_response = [
            format_team_response(team, idx + 1) 
            for idx, team in enumerate(ranked_teams)
        ]
        
        return RankingsResponse(
            teams=teams_response,
            total_teams=len(system.teams),
            year=year,
            season_type=season_type,
            classification=classification
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Error: {error_msg}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/team/{team_name}", response_model=TeamResponse)
async def get_team(
    team_name: str,
    year: int = Query(2024, description="Season year"),
    season_type: str = Query("regular", description="Season type"),
    classification: str = Query("fbs", description="Division")
):
    """
    Get detailed information for a specific team.
    """
    try:
        system = get_or_create_rankings(year, season_type, classification, None, None)
        
        if team_name not in system.teams:
            raise HTTPException(status_code=404, detail=f"Team '{team_name}' not found")
        
        team = system.teams[team_name]
        ranked_teams = system.get_rankings(sort=True)
        rank = next(i + 1 for i, t in enumerate(ranked_teams) if t.name == team_name)
        
        return format_team_response(team, rank)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear-cache")
async def clear_cache():
    """Clear the rankings cache to force recalculation."""
    ranking_cache.clear()
    return {"message": "Cache cleared successfully"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
