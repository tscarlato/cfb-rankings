import requests
from typing import Optional, List


# ==================== DATA MODELS ====================

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


# ==================== RANKING FORMULA ====================

class RankingFormula:
    """Encapsulates the ranking calculation logic."""
    
    @staticmethod
    def calculate(game_result: GameResult, opponent_rank: float) -> float:
        """
        Calculate ranking value for a single game.
        
        Rules:
        - Non-FBS wins: 0 points (no credit for beating lower divisions)
        - Win/Loss: +1 or -1
        - Margin: 1x (≤8), 1.5x (9-16), 2x (>16)
        - Opponent strength: +rank/100 (added bonus)
        """
        # Non-FBS wins don't count
        if game_result.won and not game_result.opponent_fbs:
            return 0.0
        
        base = 1.0
        win_mult = 1 if game_result.won else -1
        margin_mult = RankingFormula._get_margin_multiplier(game_result.margin)
        opponent_bonus = opponent_rank / 100.0
        
        return base * win_mult * margin_mult + opponent_bonus
    
    @staticmethod
    def _get_margin_multiplier(margin: int) -> float:
        """Get margin multiplier based on point differential."""
        abs_margin = abs(margin)
        if abs_margin <= 8:
            return 1.0
        elif abs_margin <= 16:
            return 1.5
        else:
            return 2.0


# ==================== API CLIENT ====================

class CFBDataAPI:
    """College Football Data API client."""
    
    BASE_URL = "https://api.collegefootballdata.com"
    
    def __init__(self, api_key: Optional[str] = None):
        self.headers = {}
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'
    
    def get_games(self, year: int, season_type: str = "regular", 
                  classification: str = "fbs", debug: bool = False) -> List[dict]:
        """Fetch games from the API."""
        params = {
            'year': year,
            'seasonType': season_type,
            'classification': classification
        }
        
        if debug:
            print(f"API Request: {self.BASE_URL}/games with {params}")
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/games",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return []


# ==================== RANKING SYSTEM ====================

class RankingSystem:
    """Main ranking system that orchestrates teams and calculations."""
    
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
        
        # Track FBS teams
        if home_fbs:
            self.fbs_teams.add(home_name)
        if away_fbs:
            self.fbs_teams.add(away_name)
        
        margin = home_score - away_score
        
        # Add from home team perspective
        home_team.add_game(GameResult(
            opponent=away_team,
            won=margin > 0,
            margin=margin,
            opponent_fbs=away_fbs,
            week=week
        ))
        
        # Add from away team perspective
        away_team.add_game(GameResult(
            opponent=home_team,
            won=margin < 0,
            margin=-margin,
            opponent_fbs=home_fbs,
            week=week
        ))
    
    def load_games_from_api(self, api: CFBDataAPI, year: int, 
                           season_type: str = "regular", 
                           classification: str = "fbs",
                           conference: Optional[str] = None,
                           week: Optional[int] = None,
                           debug: bool = False):
        """Load games from College Football Data API."""
        print(f"Fetching {classification.upper()} games for {year}, week {week if week else 'all'}...")
        games = api.get_games(year, season_type, classification, debug)
        
        games_added = 0
        for game in games:
            # Skip incomplete games
            if game.get('homePoints') is None or game.get('awayPoints') is None:
                continue
            
            home_team = game.get('homeTeam')
            away_team = game.get('awayTeam')
            
            if not home_team or not away_team:
                continue
            
            # Filter by week if specified (include all games UP TO that week)
            game_week = game.get('week')
            if week and game_week and game_week > week:
                continue
            
            # Optional conference filter
            if conference:
                if conference not in [game.get('homeConference'), game.get('awayConference')]:
                    continue
            
            # Determine FBS status
            home_fbs = game.get('homeClassification', 'fbs').lower() == 'fbs'
            away_fbs = game.get('awayClassification', 'fbs').lower() == 'fbs'
            
            # Get week number
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
        # Initialize
        for team in self.teams.values():
            team.ranking = 50.0
        
        print(f"Calculating rankings ({iterations} iterations max)...")
        
        for iteration in range(iterations):
            old_rankings = {name: team.ranking for name, team in self.teams.items()}
            
            # Update game values based on current opponent rankings
            self._update_game_values()
            
            # Update team rankings
            for team in self.teams.values():
                team.calculate_ranking()
            
            # Check convergence
            max_change = max(
                abs(team.ranking - old_rankings[name])
                for name, team in self.teams.items()
            )
            
            if max_change < convergence_threshold:
                print(f"Converged after {iteration + 1} iterations")
                break
        else:
            print(f"Completed {iterations} iterations")
        
        # Final update to match final rankings
        self._update_game_values()
    
    def _update_game_values(self):
        """Recalculate all game values based on current rankings."""
        for team in self.teams.values():
            for game in team.game_results:
                # Update opponent FBS status
                game.opponent_fbs = game.opponent.name in self.fbs_teams
                # Calculate value using formula
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


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    # Setup
    API_KEY = "mBIqtiooiszQC3myFOJyvK4y8j5ZUzRr5JXRCjl0yjOvXIOFrdKLix4b+upMY2cw"
    api = CFBDataAPI(api_key=API_KEY)
    system = RankingSystem()
    
    # Load games
    system.load_games_from_api(
        api=api,
        year=2024,
        season_type="regular",
        classification="fbs"
    )
    
    # Calculate rankings
    system.calculate_rankings(iterations=20)
    
    # Display results
    system.print_rankings(top_n=25)
    
    # Show top 3 teams
    print("\nDetailed breakdown for top 3 teams:")
    for team in system.get_rankings()[:3]:
        system.print_team_details(team.name)