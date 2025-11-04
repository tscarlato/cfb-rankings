# sync_nightly.py
# Minimal sync script - just syncs teams and games (that's all you need)

import requests
import time
from sqlalchemy import create_engine, text
from datetime import datetime, timezone
import os

class MinimalSync:
    """Minimal sync - only teams and games"""
    
    def __init__(self, db_url: str, api_key: str):
        self.db_url = db_url
        self.api_key = api_key
        self.engine = create_engine(db_url)
        self.headers = {'Authorization': f'Bearer {api_key}'}
        self.base_url = "https://api.collegefootballdata.com"
    
    def _api_request(self, endpoint: str, params: dict = None):
        """Make API request with rate limiting"""
        time.sleep(0.1)  # Rate limiting
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                params=params or {},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API Error for {endpoint}: {e}")
            return None
    
    def sync_teams(self):
        """Sync FBS teams"""
        print("Syncing teams...")
        
        teams_data = self._api_request('/teams/fbs')
        if not teams_data:
            print("Failed to get teams data")
            return
        
        added = updated = 0
        
        with self.engine.connect() as conn:
            for team in teams_data:
                school = team.get('school')
                if not school:
                    continue
                
                # Check if exists
                existing = conn.execute(
                    text("SELECT id FROM teams WHERE school = :school"),
                    {"school": school}
                ).fetchone()
                
                if existing:
                    # Update
                    conn.execute(
                        text("""
                            UPDATE teams SET
                                mascot = :mascot,
                                abbreviation = :abbreviation,
                                classification = :classification,
                                conference = :conference,
                                division = :division,
                                color = :color,
                                alt_color = :alt_color
                            WHERE school = :school
                        """),
                        {
                            "school": school,
                            "mascot": team.get('mascot'),
                            "abbreviation": team.get('abbreviation'),
                            "classification": team.get('classification', 'fbs'),
                            "conference": team.get('conference'),
                            "division": team.get('division'),
                            "color": team.get('color'),
                            "alt_color": team.get('alt_color')
                        }
                    )
                    updated += 1
                else:
                    # Insert
                    conn.execute(
                        text("""
                            INSERT INTO teams 
                            (school, mascot, abbreviation, classification, conference, 
                             division, color, alt_color)
                            VALUES 
                            (:school, :mascot, :abbreviation, :classification, :conference,
                             :division, :color, :alt_color)
                        """),
                        {
                            "school": school,
                            "mascot": team.get('mascot'),
                            "abbreviation": team.get('abbreviation'),
                            "classification": team.get('classification', 'fbs'),
                            "conference": team.get('conference'),
                            "division": team.get('division'),
                            "color": team.get('color'),
                            "alt_color": team.get('alt_color')
                        }
                    )
                    added += 1
            
            conn.commit()
        
        print(f"Teams: {added} added, {updated} updated")
    
    def sync_games(self, season: int, season_type: str = "regular"):
        """Sync games for a season"""
        print(f"Syncing {season} {season_type} games...")
        
        games_data = self._api_request('/games', {
            'year': season,
            'seasonType': season_type
        })
        
        if not games_data:
            print(f"Failed to get games data for {season}")
            return
        
        added = updated = 0
        skipped = 0
        
        with self.engine.connect() as conn:
            for game in games_data:
                game_id = game.get('id')
                home_team = game.get('homeTeam') or game.get('home_team')
                away_team = game.get('awayTeam') or game.get('away_team')
                home_points = game.get('homePoints') or game.get('home_points')
                away_points = game.get('awayPoints') or game.get('away_points')
                
                # Skip if missing critical data
                if not game_id or not home_team or not away_team:
                    skipped += 1
                    continue
                
                # Check if exists
                existing = conn.execute(
                    text("SELECT id FROM games WHERE id = :id"),
                    {"id": game_id}
                ).fetchone()
                
                game_values = {
                    "id": game_id,
                    "season": game.get('season', season),
                    "week": game.get('week'),
                    "season_type": game.get('seasonType') or game.get('season_type', season_type),
                    "start_date": game.get('startDate') or game.get('start_date'),
                    "completed": game.get('completed', False),
                    "home_team": home_team,
                    "away_team": away_team,
                    "home_points": home_points,
                    "away_points": away_points,
                    "venue": game.get('venue'),
                    "neutral_site": game.get('neutralSite') or game.get('neutral_site', False),
                    "conference_game": game.get('conferenceGame') or game.get('conference_game', False)
                }
                
                if existing:
                    # Update
                    conn.execute(
                        text("""
                            UPDATE games SET
                                season = :season,
                                week = :week,
                                season_type = :season_type,
                                start_date = :start_date,
                                completed = :completed,
                                home_team = :home_team,
                                away_team = :away_team,
                                home_points = :home_points,
                                away_points = :away_points,
                                venue = :venue,
                                neutral_site = :neutral_site,
                                conference_game = :conference_game
                            WHERE id = :id
                        """),
                        game_values
                    )
                    updated += 1
                else:
                    # Insert
                    conn.execute(
                        text("""
                            INSERT INTO games 
                            (id, season, week, season_type, start_date, completed,
                             home_team, away_team, home_points, away_points,
                             venue, neutral_site, conference_game)
                            VALUES 
                            (:id, :season, :week, :season_type, :start_date, :completed,
                             :home_team, :away_team, :home_points, :away_points,
                             :venue, :neutral_site, :conference_game)
                        """),
                        game_values
                    )
                    added += 1
            
            conn.commit()
        
        print(f"Games: {added} added, {updated} updated, {skipped} skipped")
    
    def sync_current_season(self):
        """Sync current season data"""
        current_year = datetime.now().year
        
        # Sync teams first
        self.sync_teams()
        
        # Sync regular season
        self.sync_games(current_year, "regular")
        
        # If it's bowl season (December/January), sync postseason too
        current_month = datetime.now().month
        if current_month == 12 or current_month == 1:
            self.sync_games(current_year, "postseason")
        
        print("Sync complete!")


if __name__ == "__main__":
    # Get from environment
    db_url = os.getenv("DATABASE_URL")
    api_key = os.getenv("CFBD_API_KEY")
    
    if not db_url or not api_key:
        print("Error: DATABASE_URL and CFBD_API_KEY must be set")
        exit(1)
    
    syncer = MinimalSync(db_url, api_key)
    syncer.sync_current_season()
