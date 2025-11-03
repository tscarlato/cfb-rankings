# cfb_ranking_system.py - Updated with minor improvements

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
        week_str = f" (Week {self.week})" if self.week else ""
        return f"{result} vs {self.opponent.name} ({self.margin:+d}pts, value={self.ranking_value:.2f}){week_str}"


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
    """Encapsulates the ranking calculation logic with configurable parameters."""
    
    # Class variables that can be modified to customize the formula
    WIN_LOSS_MULTIPLIER = 1.0
    ONE_SCORE_MULTIPLIER = 1.0      # Margin ≤ 8 points
    TWO_SCORE_MULTIPLIER = 1.3      # Margin 9-16 points
    THREE_SCORE_MULTIPLIER = 1.5    # Margin > 16 points
    STRENGTH_OF_SCHEDULE_MULTIPLIER = 1.0
    
    @classmethod
    def calculate(cls, game_result: GameResult, opponent_rank: float) -> float:
        """
        Calculate ranking value for a single game.
        
        Formula: (Win/Loss × Margin Multiplier) + ((Opponent Rank ÷ 100) × SoS Multiplier)
        
        Rules:
        - Non-FBS wins: 0 points (no credit for beating lower divisions)
        - Win/Loss: +1 or -1 (multiplied by WIN_LOSS_MULTIPLIER)
        - Margin Multipliers:
          * 1-score game (≤8 pts): ONE_SCORE_MULTIPLIER
          * 2-score game (9-16 pts): TWO_SCORE_MULTIPLIER  
          * 3+ score game (>16 pts): THREE_SCORE_MULTIPLIER
        - Opponent strength: (rank ÷ 100) × STRENGTH_OF_SCHEDULE_MULTIPLIER
        """
        # Non-FBS wins don't count
        if game_result.won and not game_result.opponent_fbs:
            return 0.0
        
        win_mult = cls.WIN_LOSS_MULTIPLIER if game_result.won else -cls.WIN_LOSS_MULTIPLIER
        margin_mult = cls._get_margin_multiplier(game_result.margin)
        opponent_bonus = (opponent_rank / 100.0) * cls.STRENGTH_OF_SCHEDULE_MULTIPLIER
        
        return win_mult * margin_mult + opponent_bonus
    
    @classmethod
    def _get_margin_multiplier(cls, margin: int) -> float:
        """Get margin multiplier based on point differential (score categories)."""
        abs_margin = abs(margin)
        if abs_margin <= 8:
            return cls.ONE_SCORE_MULTIPLIER
        elif abs_margin <= 16:
            return cls.TWO_SCORE_MULTIPLIER
        else:
            return cls.THREE_SCORE_MULTIPLIER
    
    @classmethod
    def reset_to_defaults(cls):
        """Reset all multipliers to default values."""
        cls.WIN_LOSS_MULTIPLIER = 1.0
        cls.ONE_SCORE_MULTIPLIER = 1.0
        cls.TWO_SCORE_MULTIPLIER = 1.3
        cls.THREE_SCORE_MULTIPLIER = 1.5
        cls.STRENGTH_OF_SCHEDULE_MULTIPLIER = 1.0
    
    @classmethod
    def get_current_params(cls) -> dict:
        """Get current formula parameters as dictionary."""
        return {
            'win_loss_multiplier': cls.WIN_LOSS_MULTIPLIER,
            'one_score_multiplier': cls.ONE_SCORE_MULTIPLIER,
            'two_score_multiplier': cls.TWO_SCORE_MULTIPLIER,
            'three_score_multiplier': cls.THREE_SCORE_MULTIPLIER,
            'strength_of_schedule_multiplier': cls.STRENGTH_OF_SCHEDULE_MULTIPLIER
        }


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
    
    def calculate_rankings(self, iterations: int = 20, convergence_threshold: float = 0.01):
        """Iteratively calculate rankings until convergence."""
        # Initialize all teams at 50.0
        for team in self.teams.values():
            team.ranking = 50.0
        
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
                break
        
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
    
    def get_team(self, name: str) -> Optional[Team]:
        """Get a specific team by name."""
        return self.teams.get(name)
    
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
        
        # Sort games by week if available
        sorted_games = sorted(team.game_results, key=lambda g: g.week if g.week else 0)
        
        for game in sorted_games:
            result = "W" if game.won else "L"
            opp_wins, opp_losses = game.opponent.get_record()
            week_str = f"Week {game.week:2d}" if game.week else "Week ??"
            print(f"  {week_str} {result} vs {game.opponent.name:<20} ({opp_wins}-{opp_losses}, rank {game.opponent.ranking:>6.2f}) "
                  f"Margin: {game.margin:>+4} Value: {game.ranking_value:>6.2f}")