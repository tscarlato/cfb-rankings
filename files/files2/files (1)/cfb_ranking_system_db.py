# cfb_ranking_system_db.py
# Modified version that loads from database instead of API

from typing import Optional, List
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import os

# ==================== ORIGINAL DATA MODELS (unchanged) ====================

class GameResult:
    """Represents a game from one team's perspective."""
    
    def __init__(self, opponent, won: bool, margin: int, opponent_fbs: bool = True, week: Optional[int] = None):
        self.opponent = opponent
        self.won = won
        self.margin = margin
        self.opponent_fbs = opponent_fbs
        self.ranking_value = 0.0
        self.week = week
    
    def __repr__(self):
        result = "W" if self.won else "L"
        return f"{result} vs {self.opponent.name} ({self.margin:+d}pts, value={self.ranking_value:.2f})"


class Team:
    """Represents a college football team."""
    
    def __init__(self, name: str):
        self.name = name
        self.game_results: List[GameResult] = []
        self.ranking = 0.0
    
    def add_game(self, game_result: GameResult):
        """Add a game result to this team's record."""
        self.game_results.append(game_result)
    
    def get_record(self) -> tuple:
        """Returns (wins, losses)."""
        wins = sum(1 for g in self.game_results if g.won)
        losses = len(self.game_results) - wins
        return (wins, losses)
    
    def calculate_ranking(self):
        """Calculate team ranking as sum of game values."""
        self.ranking = sum(g.ranking_value for g in self.game_results)
    
    def __repr__(self):
        wins, losses = self.get_record()
        return f"{self.name} ({wins}-{losses}, rank={self.ranking:.2f})"


# ==================== RANKING FORMULA (unchanged) ====================

class RankingFormula:
    """Encapsulates the ranking calculation logic with configurable parameters."""
    
    WIN_LOSS_MULTIPLIER = 1.0
    ONE_SCORE_MULTIPLIER = 1.0
    TWO_SCORE_MULTIPLIER = 1.3
    THREE_SCORE_MULTIPLIER = 1.5
    STRENGTH_OF_SCHEDULE_MULTIPLIER = 1.0
    
    @classmethod
    def calculate(cls, game_result: GameResult, opponent_rank: float) -> float:
        """Calculate ranking value for a single game."""
        # Non-FBS wins don't count
        if game_result.won and not game_result.opponent_fbs:
            return 0.0
        
        win_mult = cls.WIN_LOSS_MULTIPLIER if game_result.won else -cls.WIN_LOSS_MULTIPLIER
        margin_mult = cls._get_margin_multiplier(game_result.margin)
        opponent_bonus = (opponent_rank / 100.0) * cls.STRENGTH_OF_SCHEDULE_MULTIPLIER
        
        return win_mult * margin_mult + opponent_bonus
    
    @classmethod
    def _get_margin_multiplier(cls, margin: int) -> float:
        """Get margin multiplier based on point differential."""
        abs_margin = abs(margin)
        if abs_margin <= 8:
            return cls.ONE_SCORE_MULTIPLIER
        elif abs_margin <= 16:
            return cls.TWO_SCORE_MULTIPLIER
        else:
            return cls.THREE_SCORE_MULTIPLIER


# ==================== DATABASE LOADER (NEW - replaces API) ====================

class DatabaseLoader:
    """Load games from database instead of API"""
    
    def __init__(self, db_url: Optional[str] = None):
        if db_url is None:
            db_url = os.getenv("DATABASE_URL")
            if not db_url:
                raise ValueError("DATABASE_URL not set")
        
        self.engine = create_engine(db_url)
    
    def get_games(self, year: int, season_type: str = "regular", 
                  classification: str = "fbs", week: Optional[int] = None) -> List[dict]:
        """Fetch games from database."""
        
        query = """
            SELECT 
                g.id,
                g.season,
                g.week,
                g.season_type,
                g.home_team,
                g.away_team,
                g.home_points,
                g.away_points,
                g.completed,
                ht.classification as home_classification,
                at.classification as away_classification
            FROM games g
            LEFT JOIN teams ht ON g.home_team = ht.school
            LEFT JOIN teams at ON g.away_team = at.school
            WHERE g.season = :year
                AND g.season_type = :season_type
                AND g.completed = true
                AND g.home_points IS NOT NULL
                AND g.away_points IS NOT NULL
        """
        
        params = {
            "year": year,
            "season_type": season_type
        }
        
        # Include games up to the specified week
        if week is not None:
            query += " AND g.week <= :week"
            params["week"] = week
        
        query += " ORDER BY g.week, g.start_date"
        
        with self.engine.connect() as conn:
            result = conn.execute(text(query), params)
            
            games = []
            for row in result:
                games.append({
                    'id': row[0],
                    'season': row[1],
                    'week': row[2],
                    'seasonType': row[3],
                    'homeTeam': row[4],
                    'awayTeam': row[5],
                    'homePoints': row[6],
                    'awayPoints': row[7],
                    'completed': row[8],
                    'homeClassification': row[9] or 'fbs',
                    'awayClassification': row[10] or 'fbs'
                })
            
            return games


# ==================== RANKING SYSTEM (modified to use database) ====================

class RankingSystem:
    """Main ranking system - now loads from database"""
    
    def __init__(self):
        self.teams: dict = {}
        self.fbs_teams: set = set()
    
    def add_team(self, name: str) -> Team:
        """Get or create a team."""
        if name not in self.teams:
            self.teams[name] = Team(name)
        return self.teams[name]
    
    def add_game(self, home_name: str, home_score: int, away_name: str, away_score: int,
                 home_fbs: bool = True, away_fbs: bool = True, week: Optional[int] = None):
        """Add a completed game to the system."""
        home_team = self.add_team(home_name)
        away_team = self.add_team(away_name)
        
        if home_fbs:
            self.fbs_teams.add(home_name)
        if away_fbs:
            self.fbs_teams.add(away_name)
        
        margin = home_score - away_score
        
        home_team.add_game(GameResult(
            opponent=away_team,
            won=margin > 0,
            margin=margin,
            opponent_fbs=away_fbs,
            week=week
        ))
        
        away_team.add_game(GameResult(
            opponent=home_team,
            won=margin < 0,
            margin=-margin,
            opponent_fbs=home_fbs,
            week=week
        ))
    
    def load_games_from_database(self, db_loader: DatabaseLoader, year: int, 
                                 season_type: str = "regular", 
                                 classification: str = "fbs",
                                 week: Optional[int] = None):
        """Load games from database (replaces load_games_from_api)"""
        print(f"Loading {classification.upper()} games from database for {year}, week {week if week else 'all'}...")
        
        games = db_loader.get_games(year, season_type, classification, week)
        
        games_added = 0
        for game in games:
            home_team = game.get('homeTeam')
            away_team = game.get('awayTeam')
            
            if not home_team or not away_team:
                continue
            
            home_fbs = game.get('homeClassification', 'fbs').lower() == 'fbs'
            away_fbs = game.get('awayClassification', 'fbs').lower() == 'fbs'
            
            week_num = game.get('week')
            
            self.add_game(
                home_team, game.get('homePoints'),
                away_team, game.get('awayPoints'),
                home_fbs, away_fbs, week_num
            )
            games_added += 1
        
        print(f"Loaded {games_added} games")
        print(f"Total teams: {len(self.teams)}, FBS teams: {len(self.fbs_teams)}")
    
    def calculate_rankings(self, iterations: int = 20, convergence_threshold: float = 0.01):
        """Iteratively calculate rankings until convergence."""
        for team in self.teams.values():
            team.ranking = 50.0
        
        for iteration in range(iterations):
            old_rankings = {name: team.ranking for name, team in self.teams.items()}
            
            self._update_game_values()
            
            for team in self.teams.values():
                team.calculate_ranking()
            
            max_change = max(
                abs(team.ranking - old_rankings[name])
                for name, team in self.teams.items()
            )
            
            if max_change < convergence_threshold:
                break
        
        self._update_game_values()
    
    def _update_game_values(self):
        """Recalculate all game values based on current rankings."""
        for team in self.teams.values():
            for game in team.game_results:
                game.opponent_fbs = game.opponent.name in self.fbs_teams
                game.ranking_value = RankingFormula.calculate(game, game.opponent.ranking)
    
    def get_rankings(self, sort: bool = True) -> List[Team]:
        """Get ranked list of FBS teams only."""
        teams = [t for name, t in self.teams.items() if name in self.fbs_teams]
        if sort:
            teams.sort(key=lambda t: t.ranking, reverse=True)
        return teams
    
    def print_rankings(self, top_n: Optional[int] = None):
        """Print rankings in formatted table."""
        rankings = self.get_rankings()
        if top_n:
            rankings = rankings[:top_n]
        
        print("\n" + "="*70)
        print(f"{'Rank':<6} {'Team':<25} {'Record':<10} {'Rating':<10}")
        print("="*70)
        
        for rank, team in enumerate(rankings, 1):
            wins, losses = team.get_record()
            print(f"{rank:<6} {team.name:<25} {wins}-{losses:<8} {team.ranking:>8.2f}")
        
        print("="*70)
    
    def print_team_details(self, team_name: str):
        """Print detailed game results for a specific team."""
        if team_name not in self.teams:
            print(f"Team '{team_name}' not found.")
            return
        
        team = self.teams[team_name]
        wins, losses = team.get_record()
        
        print(f"\n{team.name} ({wins}-{losses}) - Ranking: {team.ranking:.2f}")
        print("-" * 70)
        
        for game in team.game_results:
            result = "W" if game.won else "L"
            opp_wins, opp_losses = game.opponent.get_record()
            print(f"  {result} vs {game.opponent.name:<20} ({opp_wins}-{opp_losses}, rank {game.opponent.ranking:>6.2f}) "
                  f"Margin: {game.margin:>+4} Value: {game.ranking_value:>6.2f}")
