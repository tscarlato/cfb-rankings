# sync_service_enhanced.py - Enhanced version that extends your existing sync service

from typing import Optional, List, Dict, Any
import requests
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
import time
import os

from db_models_complete import (
    SessionLocal, Team, Game, SyncLog
)

logger = logging.getLogger(__name__)

class CFBDataSyncService:
    """Enhanced sync service for College Football Data API with additional datasets"""
    
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
    
    # ==================== EXISTING METHODS (from your current file) ====================
    
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
                
                # Use camelCase field names from API
                home_team = game_data.get('home_team') or game_data.get('homeTeam')
                away_team = game_data.get('away_team') or game_data.get('awayTeam')
                
                if not home_team or not away_team:
                    logger.debug(f"Skipping game {game_id} - missing team names")
                    skipped += 1
                    continue
                
                existing = db.query(Game).filter(Game.id == game_id).first()
                
                # Map all fields - use camelCase from API
                game_dict = {
                    'id': game_id,
                    'season': game_data.get('season'),
                    'week': game_data.get('week'),
                    'season_type': game_data.get('season_type') or game_data.get('seasonType'),
                    'start_date': game_data.get('start_date') or game_data.get('startDate'),
                    'start_time_tbd': game_data.get('start_time_tbd') or game_data.get('startTimeTBD'),
                    'completed': game_data.get('completed', False),
                    'neutral_site': game_data.get('neutral_site') or game_data.get('neutralSite'),
                    'conference_game': game_data.get('conference_game') or game_data.get('conferenceGame'),
                    'attendance': game_data.get('attendance'),
                    'venue_id': game_data.get('venue_id') or game_data.get('venueId'),
                    'venue': game_data.get('venue'),
                    'home_id': game_data.get('home_id') or game_data.get('homeId'),
                    'home_team': home_team,
                    'home_conference': game_data.get('home_conference') or game_data.get('homeConference'),
                    'home_division': game_data.get('home_division') or game_data.get('homeDivision'),
                    'home_points': game_data.get('home_points') or game_data.get('homePoints'),
                    'home_line_scores': game_data.get('home_line_scores') or game_data.get('homeLineScores', []),
                    'home_post_win_prob': game_data.get('home_post_win_prob') or game_data.get('homePostWinProbability'),
                    'home_pregame_elo': game_data.get('home_pregame_elo') or game_data.get('homePregameElo'),
                    'home_postgame_elo': game_data.get('home_postgame_elo') or game_data.get('homePostgameElo'),
                    'away_id': game_data.get('away_id') or game_data.get('awayId'),
                    'away_team': away_team,
                    'away_conference': game_data.get('away_conference') or game_data.get('awayConference'),
                    'away_division': game_data.get('away_division') or game_data.get('awayDivision'),
                    'away_points': game_data.get('away_points') or game_data.get('awayPoints'),
                    'away_line_scores': game_data.get('away_line_scores') or game_data.get('awayLineScores', []),
                    'away_post_win_prob': game_data.get('away_post_win_prob') or game_data.get('awayPostWinProbability'),
                    'away_pregame_elo': game_data.get('away_pregame_elo') or game_data.get('awayPregameElo'),
                    'away_postgame_elo': game_data.get('away_postgame_elo') or game_data.get('awayPostgameElo'),
                    'excitement_index': game_data.get('excitement_index') or game_data.get('excitementIndex'),
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
    
    # ==================== NEW ENHANCED METHODS ====================
    
    def sync_ap_rankings(self, db: Session, season: int, week: Optional[int] = None) -> Dict:
        """Sync AP Poll rankings"""
        log_entry = self._log_sync(db, 'ap_rankings', season, 'regular', week)
        
        try:
            params = {'year': season, 'seasonType': 'regular'}
            if week:
                params['week'] = week
            
            data = self._api_request('/rankings', params)
            added = updated = 0
            
            for poll_week in data:
                week_num = poll_week.get('week')
                season_type = poll_week.get('seasonType', 'regular')
                
                # Process AP Poll rankings
                ap_polls = poll_week.get('polls', [])
                for poll in ap_polls:
                    if poll.get('poll') != 'AP Top 25':
                        continue
                    
                    ranks = poll.get('ranks', [])
                    for rank_data in ranks:
                        team = rank_data.get('school')
                        rank = rank_data.get('rank')
                        first_place_votes = rank_data.get('firstPlaceVotes', 0)
                        points = rank_data.get('points', 0)
                        
                        if not team or not rank:
                            continue
                        
                        # Check if record exists
                        existing = db.execute(
                            text("""
                                SELECT id FROM ap_rankings 
                                WHERE season = :season AND week = :week 
                                AND season_type = :season_type AND team = :team
                            """),
                            {"season": season, "week": week_num, 
                             "season_type": season_type, "team": team}
                        ).fetchone()
                        
                        if existing:
                            db.execute(
                                text("""
                                    UPDATE ap_rankings 
                                    SET rank = :rank, first_place_votes = :fpv, points = :points
                                    WHERE id = :id
                                """),
                                {"id": existing[0], "rank": rank, "fpv": first_place_votes, 
                                 "points": points}
                            )
                            updated += 1
                        else:
                            db.execute(
                                text("""
                                    INSERT INTO ap_rankings 
                                    (season, week, season_type, team, rank, first_place_votes, points)
                                    VALUES (:season, :week, :season_type, :team, :rank, :fpv, :points)
                                """),
                                {"season": season, "week": week_num, "season_type": season_type,
                                 "team": team, "rank": rank, "fpv": first_place_votes, 
                                 "points": points}
                            )
                            added += 1
            
            db.commit()
            self._complete_sync_log(db, log_entry, 'success', added, updated)
            logger.info(f"AP rankings synced: {added} added, {updated} updated")
            return {'success': True, 'added': added, 'updated': updated}
            
        except Exception as e:
            db.rollback()
            self._complete_sync_log(db, log_entry, 'failed', error=str(e))
            logger.error(f"Error syncing AP rankings: {e}")
            return {'success': False, 'error': str(e)}
    
    def sync_sp_ratings(self, db: Session, season: int, week: Optional[int] = None) -> Dict:
        """Sync SP+ ratings"""
        log_entry = self._log_sync(db, 'sp_ratings', season, 'regular', week)
        
        try:
            params = {'year': season}
            if week:
                params['week'] = week
            
            data = self._api_request('/ratings/sp', params)
            added = updated = 0
            
            for rating in data:
                team = rating.get('team')
                week_num = rating.get('week')
                sp_rating = rating.get('rating')
                ranking = rating.get('ranking')
                
                # Additional SP+ metrics
                offense_rating = rating.get('offense', {}).get('rating') if rating.get('offense') else None
                defense_rating = rating.get('defense', {}).get('rating') if rating.get('defense') else None
                special_teams = rating.get('specialTeams', {}).get('rating') if rating.get('specialTeams') else None
                
                if not team or week_num is None:
                    continue
                
                # Check if record exists
                existing = db.execute(
                    text("""
                        SELECT id FROM team_sp_ratings 
                        WHERE season = :season AND week = :week AND team = :team
                    """),
                    {"season": season, "week": week_num, "team": team}
                ).fetchone()
                
                if existing:
                    db.execute(
                        text("""
                            UPDATE team_sp_ratings 
                            SET rating = :rating, ranking = :ranking,
                                offense_rating = :off, defense_rating = :def, 
                                special_teams_rating = :st
                            WHERE id = :id
                        """),
                        {"id": existing[0], "rating": sp_rating, "ranking": ranking,
                         "off": offense_rating, "def": defense_rating, "st": special_teams}
                    )
                    updated += 1
                else:
                    db.execute(
                        text("""
                            INSERT INTO team_sp_ratings 
                            (season, week, team, rating, ranking, offense_rating, 
                             defense_rating, special_teams_rating)
                            VALUES (:season, :week, :team, :rating, :ranking, :off, :def, :st)
                        """),
                        {"season": season, "week": week_num, "team": team, 
                         "rating": sp_rating, "ranking": ranking,
                         "off": offense_rating, "def": defense_rating, "st": special_teams}
                    )
                    added += 1
            
            db.commit()
            self._complete_sync_log(db, log_entry, 'success', added, updated)
            logger.info(f"SP+ ratings synced: {added} added, {updated} updated")
            return {'success': True, 'added': added, 'updated': updated}
            
        except Exception as e:
            db.rollback()
            self._complete_sync_log(db, log_entry, 'failed', error=str(e))
            logger.error(f"Error syncing SP+ ratings: {e}")
            return {'success': False, 'error': str(e)}
    
    def sync_fpi_ratings(self, db: Session, season: int, week: Optional[int] = None) -> Dict:
        """Sync FPI ratings"""
        log_entry = self._log_sync(db, 'fpi_ratings', season, 'regular', week)
        
        try:
            params = {'year': season}
            if week:
                params['week'] = week
            
            data = self._api_request('/ratings/fpi', params)
            added = updated = 0
            
            for rating in data:
                team = rating.get('team')
                week_num = rating.get('week')
                fpi = rating.get('fpi')
                
                if not team or week_num is None:
                    continue
                
                # Check if record exists
                existing = db.execute(
                    text("""
                        SELECT id FROM team_fpi_ratings 
                        WHERE season = :season AND week = :week AND team = :team
                    """),
                    {"season": season, "week": week_num, "team": team}
                ).fetchone()
                
                if existing:
                    db.execute(
                        text("UPDATE team_fpi_ratings SET fpi = :fpi WHERE id = :id"),
                        {"id": existing[0], "fpi": fpi}
                    )
                    updated += 1
                else:
                    db.execute(
                        text("""
                            INSERT INTO team_fpi_ratings (season, week, team, fpi)
                            VALUES (:season, :week, :team, :fpi)
                        """),
                        {"season": season, "week": week_num, "team": team, "fpi": fpi}
                    )
                    added += 1
            
            db.commit()
            self._complete_sync_log(db, log_entry, 'success', added, updated)
            logger.info(f"FPI ratings synced: {added} added, {updated} updated")
            return {'success': True, 'added': added, 'updated': updated}
            
        except Exception as e:
            db.rollback()
            self._complete_sync_log(db, log_entry, 'failed', error=str(e))
            logger.error(f"Error syncing FPI ratings: {e}")
            return {'success': False, 'error': str(e)}
    
    def sync_team_records(self, db: Session, season: int) -> Dict:
        """Sync team season records"""
        log_entry = self._log_sync(db, 'team_records', season)
        
        try:
            params = {'year': season}
            data = self._api_request('/records', params)
            added = updated = 0
            
            for record in data:
                team = record.get('team')
                year = record.get('year', season)
                
                # Overall record
                total = record.get('total', {})
                wins = total.get('wins', 0)
                losses = total.get('losses', 0)
                ties = total.get('ties', 0)
                
                # Conference record
                conf_games = record.get('conferenceGames', {})
                conf_wins = conf_games.get('wins', 0)
                conf_losses = conf_games.get('losses', 0)
                conf_ties = conf_games.get('ties', 0)
                
                # Home/Away records
                home_games = record.get('homeGames', {})
                home_wins = home_games.get('wins', 0)
                home_losses = home_games.get('losses', 0)
                
                away_games = record.get('awayGames', {})
                away_wins = away_games.get('wins', 0)
                away_losses = away_games.get('losses', 0)
                
                if not team:
                    continue
                
                # Check if record exists
                existing = db.execute(
                    text("SELECT id FROM team_records WHERE season = :season AND team = :team"),
                    {"season": year, "team": team}
                ).fetchone()
                
                if existing:
                    db.execute(
                        text("""
                            UPDATE team_records 
                            SET total_wins = :wins, total_losses = :losses, total_ties = :ties,
                                conf_wins = :cw, conf_losses = :cl, conf_ties = :ct,
                                home_wins = :hw, home_losses = :hl,
                                away_wins = :aw, away_losses = :al
                            WHERE id = :id
                        """),
                        {"id": existing[0], "wins": wins, "losses": losses, "ties": ties,
                         "cw": conf_wins, "cl": conf_losses, "ct": conf_ties,
                         "hw": home_wins, "hl": home_losses, 
                         "aw": away_wins, "al": away_losses}
                    )
                    updated += 1
                else:
                    db.execute(
                        text("""
                            INSERT INTO team_records 
                            (season, team, total_wins, total_losses, total_ties,
                             conf_wins, conf_losses, conf_ties,
                             home_wins, home_losses, away_wins, away_losses)
                            VALUES (:season, :team, :wins, :losses, :ties,
                                    :cw, :cl, :ct, :hw, :hl, :aw, :al)
                        """),
                        {"season": year, "team": team, "wins": wins, "losses": losses, 
                         "ties": ties, "cw": conf_wins, "cl": conf_losses, "ct": conf_ties,
                         "hw": home_wins, "hl": home_losses, 
                         "aw": away_wins, "al": away_losses}
                    )
                    added += 1
            
            db.commit()
            self._complete_sync_log(db, log_entry, 'success', added, updated)
            logger.info(f"Team records synced: {added} added, {updated} updated")
            return {'success': True, 'added': added, 'updated': updated}
            
        except Exception as e:
            db.rollback()
            self._complete_sync_log(db, log_entry, 'failed', error=str(e))
            logger.error(f"Error syncing team records: {e}")
            return {'success': False, 'error': str(e)}
    
    def sync_betting_lines(self, db: Session, season: int, week: Optional[int] = None) -> Dict:
        """Sync betting lines for games"""
        log_entry = self._log_sync(db, 'betting_lines', season, 'regular', week)
        
        try:
            params = {'year': season, 'seasonType': 'regular'}
            if week:
                params['week'] = week
            
            data = self._api_request('/lines', params)
            added = updated = 0
            
            for game in data:
                game_id = game.get('id')
                home_team = game.get('homeTeam') or game.get('home_team')
                away_team = game.get('awayTeam') or game.get('away_team')
                
                if not game_id or not home_team or not away_team:
                    continue
                
                # Process each betting line provider
                lines = game.get('lines', [])
                for line in lines:
                    provider = line.get('provider')
                    spread = line.get('spread')
                    over_under = line.get('overUnder')
                    home_moneyline = line.get('homeMoneyline')
                    away_moneyline = line.get('awayMoneyline')
                    
                    if not provider:
                        continue
                    
                    # Check if record exists
                    existing = db.execute(
                        text("""
                            SELECT id FROM game_lines 
                            WHERE game_id = :game_id AND provider = :provider
                        """),
                        {"game_id": game_id, "provider": provider}
                    ).fetchone()
                    
                    if existing:
                        db.execute(
                            text("""
                                UPDATE game_lines 
                                SET spread = :spread, over_under = :ou,
                                    home_moneyline = :hm, away_moneyline = :am
                                WHERE id = :id
                            """),
                            {"id": existing[0], "spread": spread, "ou": over_under,
                             "hm": home_moneyline, "am": away_moneyline}
                        )
                        updated += 1
                    else:
                        db.execute(
                            text("""
                                INSERT INTO game_lines 
                                (game_id, provider, spread, over_under, 
                                 home_moneyline, away_moneyline)
                                VALUES (:game_id, :provider, :spread, :ou, :hm, :am)
                            """),
                            {"game_id": game_id, "provider": provider, 
                             "spread": spread, "ou": over_under,
                             "hm": home_moneyline, "am": away_moneyline}
                        )
                        added += 1
            
            db.commit()
            self._complete_sync_log(db, log_entry, 'success', added, updated)
            logger.info(f"Betting lines synced: {added} added, {updated} updated")
            return {'success': True, 'added': added, 'updated': updated}
            
        except Exception as e:
            db.rollback()
            self._complete_sync_log(db, log_entry, 'failed', error=str(e))
            logger.error(f"Error syncing betting lines: {e}")
            return {'success': False, 'error': str(e)}
    
    def sync_recruiting_rankings(self, db: Session, season: int) -> Dict:
        """Sync team recruiting rankings"""
        log_entry = self._log_sync(db, 'recruiting', season)
        
        try:
            params = {'year': season}
            data = self._api_request('/recruiting/teams', params)
            added = updated = 0
            
            for team_data in data:
                team = team_data.get('team')
                year = team_data.get('year', season)
                rank = team_data.get('rank')
                points = team_data.get('points')
                
                if not team:
                    continue
                
                # Check if record exists
                existing = db.execute(
                    text("""
                        SELECT id FROM recruiting_teams 
                        WHERE year = :year AND team = :team
                    """),
                    {"year": year, "team": team}
                ).fetchone()
                
                if existing:
                    db.execute(
                        text("""
                            UPDATE recruiting_teams 
                            SET rank = :rank, points = :points
                            WHERE id = :id
                        """),
                        {"id": existing[0], "rank": rank, "points": points}
                    )
                    updated += 1
                else:
                    db.execute(
                        text("""
                            INSERT INTO recruiting_teams (year, team, rank, points)
                            VALUES (:year, :team, :rank, :points)
                        """),
                        {"year": year, "team": team, "rank": rank, "points": points}
                    )
                    added += 1
            
            db.commit()
            self._complete_sync_log(db, log_entry, 'success', added, updated)
            logger.info(f"Recruiting rankings synced: {added} added, {updated} updated")
            return {'success': True, 'added': added, 'updated': updated}
            
        except Exception as e:
            db.rollback()
            self._complete_sync_log(db, log_entry, 'failed', error=str(e))
            logger.error(f"Error syncing recruiting rankings: {e}")
            return {'success': False, 'error': str(e)}
    
    def sync_all(self, db: Session, season: int, week: Optional[int] = None, 
                 include: List[str] = None) -> Dict:
        """Sync multiple datasets at once"""
        if include is None or 'all' in include:
            include = ['rankings', 'sp_ratings', 'fpi_ratings', 'records', 'lines', 'recruiting']
        
        results = {}
        
        # AP Rankings (weekly)
        if 'rankings' in include:
            results['ap_rankings'] = self.sync_ap_rankings(db, season, week)
        
        # SP+ Ratings (weekly)
        if 'sp_ratings' in include:
            results['sp_ratings'] = self.sync_sp_ratings(db, season, week)
        
        # FPI Ratings (weekly)
        if 'fpi_ratings' in include:
            results['fpi_ratings'] = self.sync_fpi_ratings(db, season, week)
        
        # Team Records (season-level)
        if 'records' in include:
            results['team_records'] = self.sync_team_records(db, season)
        
        # Betting Lines (weekly)
        if 'lines' in include:
            results['betting_lines'] = self.sync_betting_lines(db, season, week)
        
        # Recruiting Rankings (season-level)
        if 'recruiting' in include:
            results['recruiting_rankings'] = self.sync_recruiting_rankings(db, season)
        
        # Calculate totals
        total_added = sum(r.get('added', 0) for r in results.values() if r.get('success'))
        total_updated = sum(r.get('updated', 0) for r in results.values() if r.get('success'))
        
        return {
            "success": True,
            "results": results,
            "total_added": total_added,
            "total_updated": total_updated
        }
    
    # ==================== EXISTING METHODS (from your current file) ====================
    
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
