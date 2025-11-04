# sync_service_complete.py - Complete working version

from typing import Optional, List, Dict, Any
import requests
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging
import time
import os

from db_models_complete import (
    SessionLocal, Team, Game, SyncLog
)

logger = logging.getLogger(__name__)

class CFBDataSyncService:
    """Sync service for College Football Data API"""
    
    BASE_URL = "https://api.collegefootballdata.com"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {'Authorization': f'Bearer {api_key}'}
    
    def _api_request(self, endpoint: str, params: Dict = None) -> Any:
        """Make API request with error handling and rate limiting"""
        try:
            time.sleep(0.1)  # Rate limiting
            
            response = requests.get(
                f"{self.BASE_URL}{endpoint}",
                headers=self.headers,
                params=params or {},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {endpoint}: {e}")
            raise
    
    def _log_sync(self, db: Session, sync_type: str, season: int = None, 
                  season_type: str = None, week: int = None) -> SyncLog:
        """Create sync log entry"""
        log_entry = SyncLog(
            sync_type=sync_type,
            season=season,
            season_type=season_type,
            week=week,
            status='started'
        )
        db.add(log_entry)
        db.commit()
        return log_entry
    
    def _complete_sync_log(self, db: Session, log_entry: SyncLog, 
                          status: str, added: int = 0, updated: int = 0, 
                          error: str = None):
        """Complete sync log entry"""
        log_entry.status = status
        log_entry.records_added = added
        log_entry.records_updated = updated
        log_entry.error_message = error
        log_entry.completed_at = datetime.now(timezone.utc)
        db.commit()
    
    def sync_teams(self, db: Session, classification: str = 'fbs') -> Dict:
        """Sync teams"""
        log_entry = self._log_sync(db, f'teams_{classification}')
        
        try:
            teams_data = self._api_request(f'/teams/{classification}')
            added = updated = 0
            
            for team_data in teams_data:
                existing = db.query(Team).filter(
                    Team.school == team_data['school']
                ).first()
                
                team_dict = {
                    'school': team_data['school'],
                    'mascot': team_data.get('mascot'),
                    'abbreviation': team_data.get('abbreviation'),
                    'alt_name1': team_data.get('alt_name1'),
                    'alt_name2': team_data.get('alt_name2'),
                    'alt_name3': team_data.get('alt_name3'),
                    'classification': team_data.get('classification'),
                    'conference': team_data.get('conference'),
                    'division': team_data.get('division'),
                    'color': team_data.get('color'),
                    'alt_color': team_data.get('alt_color'),
                    'logos': team_data.get('logos', []),
                    'twitter': team_data.get('twitter'),
                }
                
                # Location data
                if 'location' in team_data and team_data['location']:
                    loc = team_data['location']
                    team_dict.update({
                        'location_name': loc.get('name'),
                        'location_city': loc.get('city'),
                        'location_state': loc.get('state'),
                        'location_zip': loc.get('zip'),
                        'location_country_code': loc.get('country_code'),
                        'location_timezone': loc.get('timezone'),
                        'location_latitude': loc.get('latitude'),
                        'location_longitude': loc.get('longitude'),
                        'location_elevation': loc.get('elevation'),
                        'location_capacity': loc.get('capacity'),
                        'location_year_constructed': loc.get('year_constructed'),
                        'location_grass': loc.get('grass'),
                        'location_dome': loc.get('dome'),
                    })
                
                if existing:
                    for key, value in team_dict.items():
                        setattr(existing, key, value)
                    updated += 1
                else:
                    db.add(Team(**team_dict))
                    added += 1
            
            db.commit()
            self._complete_sync_log(db, log_entry, 'success', added, updated)
            logger.info(f"Teams synced: {added} added, {updated} updated")
            return {'added': added, 'updated': updated}
            
        except Exception as e:
            db.rollback()
            self._complete_sync_log(db, log_entry, 'failed', error=str(e))
            raise
    
    def sync_games(self, db: Session, season: int, season_type: str = 'regular',
                   week: Optional[int] = None) -> Dict:
        """Sync games"""
        log_entry = self._log_sync(db, 'games', season, season_type, week)
        
        try:
            params = {'year': season, 'seasonType': season_type}
            if week:
                params['week'] = week
            
            games_data = self._api_request('/games', params)
            added = updated = 0
            skipped = 0
            
            for game_data in games_data:
                game_id = game_data.get('id')
                if not game_id:
                    skipped += 1
                    continue
                
                # Skip games without team names
                home_team = game_data.get('home_team')
                away_team = game_data.get('away_team')
                
                if not home_team or not away_team:
                    logger.debug(f"Skipping game {game_id} - missing team names")
                    skipped += 1
                    continue
                
                existing = db.query(Game).filter(Game.id == game_id).first()
                
                game_dict = {
                    'id': game_id,
                    'season': game_data['season'],
                    'week': game_data.get('week'),
                    'season_type': game_data.get('season_type'),
                    'start_date': game_data.get('start_date'),
                    'start_time_tbd': game_data.get('start_time_tbd'),
                    'completed': game_data.get('completed', False),
                    'neutral_site': game_data.get('neutral_site'),
                    'conference_game': game_data.get('conference_game'),
                    'attendance': game_data.get('attendance'),
                    'venue_id': game_data.get('venue_id'),
                    'venue': game_data.get('venue'),
                    'home_id': game_data.get('home_id'),
                    'home_team': home_team,
                    'home_conference': game_data.get('home_conference'),
                    'home_division': game_data.get('home_division'),
                    'home_points': game_data.get('home_points'),
                    'home_line_scores': game_data.get('home_line_scores', []),
                    'home_post_win_prob': game_data.get('home_post_win_prob'),
                    'home_pregame_elo': game_data.get('home_pregame_elo'),
                    'home_postgame_elo': game_data.get('home_postgame_elo'),
                    'away_id': game_data.get('away_id'),
                    'away_team': away_team,
                    'away_conference': game_data.get('away_conference'),
                    'away_division': game_data.get('away_division'),
                    'away_points': game_data.get('away_points'),
                    'away_line_scores': game_data.get('away_line_scores', []),
                    'away_post_win_prob': game_data.get('away_post_win_prob'),
                    'away_pregame_elo': game_data.get('away_pregame_elo'),
                    'away_postgame_elo': game_data.get('away_postgame_elo'),
                    'excitement_index': game_data.get('excitement_index'),
                    'highlights': game_data.get('highlights', ''),
                    'notes': game_data.get('notes'),
                }
                
                if existing:
                    for key, value in game_dict.items():
                        setattr(existing, key, value)
                    updated += 1
                else:
                    db.add(Game(**game_dict))
                    added += 1
            
            db.commit()
            self._complete_sync_log(db, log_entry, 'success', added, updated)
            logger.info(f"Games synced for {season} {season_type}: {added} added, {updated} updated, {skipped} skipped")
            return {'added': added, 'updated': updated, 'skipped': skipped}
            
        except Exception as e:
            db.rollback()
            self._complete_sync_log(db, log_entry, 'failed', error=str(e))
            raise
    
    def sync_weekly_update(self, db: Session, season: int, week: int) -> Dict:
        """Quick weekly update during the season"""
        results = {}
        
        logger.info(f"Starting weekly sync for {season} week {week}")
        
        # Games for this week
        results['games'] = self.sync_games(db, season, 'regular', week)
        
        logger.info(f"Weekly sync completed for week {week}")
        return results
    
    def sync_season_core_data(self, db: Session, season: int) -> Dict:
        """Sync all core data for a season"""
        results = {}
        
        logger.info(f"Starting comprehensive sync for {season} season")
        
        # Core reference data
        try:
            results['teams'] = self.sync_teams(db, 'fbs')
        except Exception as e:
            logger.error(f"Error syncing teams: {e}")
        
        # Games
        try:
            results['games_regular'] = self.sync_games(db, season, 'regular')
            results['games_postseason'] = self.sync_games(db, season, 'postseason')
        except Exception as e:
            logger.error(f"Error syncing game data: {e}")
        
        logger.info(f"Comprehensive sync completed for {season}")
        return results


def run_daily_sync():
    """Daily sync job to run during the season"""
    from datetime import datetime
    
    db = SessionLocal()
    api_key = os.getenv("CFBD_API_KEY")
    
    if not api_key:
        logger.error("CFBD_API_KEY not set, skipping sync")
        return
    
    sync_service = CFBDataSyncService(api_key)
    
    try:
        current_date = datetime.now()
        current_season = current_date.year
        
        # Determine current week (rough estimate - Aug-Dec)
        if 8 <= current_date.month <= 12:
            weeks_since_start = (current_date - datetime(current_season, 8, 25)).days // 7
            current_week = min(max(weeks_since_start, 1), 15)
            
            logger.info(f"Running weekly sync for {current_season} week {current_week}")
            sync_service.sync_weekly_update(db, current_season, current_week)
        elif current_date.month == 1:
            # Postseason
            logger.info(f"Running postseason sync for {current_season}")
            sync_service.sync_games(db, current_season, 'postseason')
        else:
            # Off-season - just update teams
            logger.info("Off-season: updating teams only")
            sync_service.sync_teams(db, 'fbs')
        
    except Exception as e:
        logger.error(f"Daily sync failed: {e}")
    finally:
        db.close()