from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(
    title="College Football Rankings API",
    description="Custom ranking system for college football teams",
    version="1.0.0"
)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "*"  # Allow all for development
    ],
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
    base_value: float = 1.0
    win_loss_multiplier: float = 1.0  # Applied to base for W (+1) or L (-1)
    margin_threshold_1: int = 8       # Margin ≤ this gets 1x
    margin_multiplier_1: float = 1.0
    margin_threshold_2: int = 16      # Margin ≤ this gets multiplier 2
    margin_multiplier_2: float = 1.5
    margin_multiplier_3: float = 2.0  # Margin > threshold 2 gets this
    opponent_strength_divisor: float = 100.0  # opponent_rank / this value

# Cache for storing ranking system (could use Redis in production)
ranking_cache = {}

def get_or_create_rankings(
    year: int = 2024,
    season_type: str = "regular",
    classification: str = "fbs",
    week: Optional[int] = None,
    api_key: Optional[str] = None,
    formula_params: Optional[FormulaParams] = None
):
    """Get rankings from cache or compute them."""
    # Include formula params in cache key
    formula_key = ""
    if formula_params:
        formula_key = f"_{formula_params.base_value}_{formula_params.win_loss_multiplier}_{formula_params.margin_multiplier_1}_{formula_params.margin_multiplier_2}_{formula_params.margin_multiplier_3}_{formula_params.opponent_strength_divisor}"
    
    cache_key = f"{year}_{season_type}_{classification}_{week}{formula_key}"
    
    if cache_key in ranking_cache:
        return ranking_cache[cache_key]
    
    # Import here to avoid circular imports
    from cfb_ranking_system import CFBDataAPI, RankingSystem, RankingFormula
    
    # Update formula if custom params provided
    if formula_params:
        RankingFormula.BASE_VALUE = formula_params.base_value
        RankingFormula.WIN_LOSS_MULTIPLIER = formula_params.win_loss_multiplier
        RankingFormula.MARGIN_THRESHOLD_1 = formula_params.margin_threshold_1
        RankingFormula.MARGIN_MULTIPLIER_1 = formula_params.margin_multiplier_1
        RankingFormula.MARGIN_THRESHOLD_2 = formula_params.margin_threshold_2
        RankingFormula.MARGIN_MULTIPLIER_2 = formula_params.margin_multiplier_2
        RankingFormula.MARGIN_MULTIPLIER_3 = formula_params.margin_multiplier_3
        RankingFormula.OPPONENT_STRENGTH_DIVISOR = formula_params.opponent_strength_divisor
    
    # Use provided key or default
    if api_key is None:
        api_key = "mBIqtiooiszQC3myFOJyvK4y8j5ZUzRr5JXRCjl0yjOvXIOFrdKLix4b+upMY2cw"
    
    # Initialize and compute rankings
    api = CFBDataAPI(api_key=api_key)
    system = RankingSystem()
    
    system.load_games_from_api(
        api=api,
        year=year,
        season_type=season_type,
        classification=classification,
        week=week
    )
    
    # Check if any games were loaded
    if len(system.teams) == 0:
        raise ValueError(f"No teams loaded. This could mean: (1) No games found for {year} {season_type} {classification}, (2) API key issue, or (3) API is down")
    
    system.calculate_rankings(iterations=20)
    
    # Cache the result
    ranking_cache[cache_key] = system
    return system

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
    api_key: Optional[str] = Query(None, description="College Football Data API key"),
    # Formula parameters
    base_value: float = Query(1.0, description="Base value for each game"),
    win_loss_multiplier: float = Query(1.0, description="Multiplier applied to base (+1 for win, -1 for loss)"),
    margin_threshold_1: int = Query(8, description="First margin threshold"),
    margin_multiplier_1: float = Query(1.0, description="Multiplier for margins ≤ threshold 1"),
    margin_threshold_2: int = Query(16, description="Second margin threshold"),
    margin_multiplier_2: float = Query(1.5, description="Multiplier for margins between thresholds"),
    margin_multiplier_3: float = Query(2.0, description="Multiplier for margins > threshold 2"),
    opponent_strength_divisor: float = Query(100.0, description="Divisor for opponent strength bonus")
):
    """
    Get rankings for all teams with customizable formula parameters.
    """
    try:
        formula_params = FormulaParams(
            base_value=base_value,
            win_loss_multiplier=win_loss_multiplier,
            margin_threshold_1=margin_threshold_1,
            margin_multiplier_1=margin_multiplier_1,
            margin_threshold_2=margin_threshold_2,
            margin_multiplier_2=margin_multiplier_2,
            margin_multiplier_3=margin_multiplier_3,
            opponent_strength_divisor=opponent_strength_divisor
        )
        
        system = get_or_create_rankings(year, season_type, classification, week, api_key, formula_params)
        
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
    classification: str = Query("fbs", description="Division"),
    api_key: Optional[str] = Query(None, description="API key")
):
    """
    Get detailed information for a specific team.
    
    - **team_name**: Name of the team (case-sensitive)
    """
    try:
        system = get_or_create_rankings(year, season_type, classification, None, api_key)
        
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
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)