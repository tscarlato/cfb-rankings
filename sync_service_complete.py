# sync_service_complete.py - Complete sync for ALL CFBD API endpoints

from typing import Optional, List, Dict, Any
import requests
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging
import time
import os

# This import is critical - make sure it works
from db_models_complete import (
    SessionLocal, Team, Conference, Venue, Game, GameLine, GameMedia,
    TeamSeasonStat, TeamGameStats, APRanking, CustomRanking,
    RecruitingTeam, Player, Drive, SyncLog,
    GameWeather, TeamRecord, TeamTalent, TeamPPA, TeamSP, TeamSRS,
    TeamFPI, TeamElo, Recruit, Coach, DraftPick, TransferPortal
)

logger = logging.getLogger(__name__)

class CFBDataSyncService:
    """Complete sync service for College Football Data API"""
    
    BASE_URL = "https://api.collegefootballdata.com"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {'Authorization': f'Bearer {api_key}'}
    
    def _api_request(self, endpoint: str, params: Dict = None) -> Any:
        """Make API request with error handling and rate limiting"""
        try:
            # Rate limiting - be nice to the API
            time.sleep(0.1)  # 100ms between requests
            
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
        log_entry.completed_at = datetime.utcnow()
        db.commit()
    
    # ==================== CORE DATA ====================
    
    def sync_conferences(self, db: Session) -> Dict:
        """Sync all conferences"""
        log_entry = self._log_sync(db, 'conferences')
        
        try:
            conferences_data = self._api_request('/conferences')
            added = updated = 0
            
            for conf_data in conferences_data:
                existing = db.query(Conference).filter(
                    Conference.name == conf_data['name']
                ).first()
                
                conf_dict = {
                    'name': conf_data['name'],
                    'short_name': conf_data.get('short_name'),
                    'abbreviation': conf_data.get('abbreviation'),
                    'classification': conf_data.get('classification'),
                }
                
                if existing:
                    for key, value in conf_dict.items():
                        setattr(existing, key, value)
                    updated += 1
                else:
                    db.add(Conference(**conf_dict))
                    added += 1
            
            db.commit()
            self._complete_sync_log(db, log_entry, 'success', added, updated)
            logger.info(f"Conferences synced: {added} added, {updated} updated")
            return {'added': added, 'updated': updated}
            
        except Exception as e:
            db.rollback()
            self._complete_sync_log(db, log_entry, 'failed', error=str(e))
            raise
    
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
    
    def sync_venues(self, db: Session) -> Dict:
        """Sync all venues"""
        log_entry = self._log_sync(db, 'venues')
        
        try:
            venues_data = self._api_request('/venues')
            added = updated = 0
            
            for venue_data in venues_data:
                venue_id = venue_data.get('id')
                if not venue_id:
                    continue
                
                existing = db.query(Venue).filter(Venue.id == venue_id).first()
                
                venue_dict = {
                    'id': venue_id,
                    'name': venue_data.get('name'),
                    'city': venue_data.get('city'),
                    'state': venue_data.get('state'),
                    'zip': venue_data.get('zip'),
                    'country_code': venue_data.get('country_code'),
                    'timezone': venue_data.get('timezone'),
                    'latitude': venue_data.get('latitude'),
                    'longitude': venue_data.get('longitude'),
                    'elevation': venue_data.get('elevation'),
                    'capacity': venue_data.get('capacity'),
                    'year_constructed': venue_data.get('year_constructed'),
                    'grass': venue_data.get('grass'),
                    'dome': venue_data.get('dome'),
                }
                
                if existing:
                    for key, value in venue_dict.items():
                        setattr(existing, key, value)
                    updated += 1
                else:
                    db.add(Venue(**venue_dict))
                    added += 1
            
            db.commit()
            self._complete_sync_log(db, log_entry, 'success', added, updated)
            logger.info(f"Venues synced: {added} added, {updated} updated")
            return {'added': added, 'updated': updated}
            
        except Exception as e:
            db.rollback()
            self._complete_sync_log(db, log_entry, 'failed', error=str(e))
            raise
    
    # ==================== GAMES ====================
    
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
            
            for game_data in games_data:
                game_id = game_data.get('id')
                if not game_id:
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
                    'home_team': game_data.get('home_team'),
                    'home_conference': game_data.get('home_conference'),
                    'home_division': game_data.get('home_division'),
                    'home_points': game_data.get('home_points'),
                    'home_line_scores': game_data.get('home_line_scores', []),
                    'home_post_win_prob': game_data.get('home_post_win_prob'),
                    'home_pregame_elo': game_data.get('home_pregame_elo'),
                    'home_postgame_elo': game_data.get('home_postgame_elo'),
                    'away_id': game_data.get('away_id'),
                    'away_team': game_data.get('away_team'),
                    'away_conference': game_data.get('away_conference'),
                    'away_division': game_data.get('away_division'),
                    'away_points': game_data.get('away_points'),
                    'away_line_scores': game_data.get('away_line_scores', []),
                    'away_post_win_prob': game_data.get('away_post_win_prob'),
                    'away_pregame_elo': game_data.get('away_pregame_elo'),
                    'away_postgame_elo': game_data.get('away_postgame_elo'),
                    'excitement_index': game_data.get('excitement_index'),
                    'highlights': game_data.get('highlights'),
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
            logger.info(f"Games synced for {season} {season_type}: {added} added, {updated} updated")
            return {'added': added, 'updated': updated}
            
        except Exception as e:
            db.rollback()
            self._complete_sync_log(db, log_entry, 'failed', error=str(e))
            raise
    
    def sync_game_lines(self, db: Session, season: int, week: Optional[int] = None) -> Dict:
        """Sync betting lines"""
        log_entry = self._log_sync(db, 'game_lines', season, week=week)
        
        try:
            params = {'year': season}
            if week:
                params['week'] = week
            
            lines_data = self._api_request('/lines', params)
            added = 0
            
            for line_data in lines_data:
                game_id = line_data.get('id')
                if not game_id:
                    continue
                
                for line in line_data.get('lines', []):
                    # Check if exists
                    existing = db.query(GameLine).filter(
                        and_(
                            GameLine.game_id == game_id,
                            GameLine.provider == line.get('provider')
                        )
                    ).first()
                    
                    if not existing:
                        db.add(GameLine(
                            game_id=game_id,
                            season=line_data.get('season'),
                            week=line_data.get('week'),
                            season_type=line_data.get('seasonType'),
                            home_team=line_data.get('homeTeam'),
                            away_team=line_data.get('awayTeam'),
                            home_conference=line_data.get('homeConference'),
                            away_conference=line_data.get('awayConference'),
                            home_score=line_data.get('homeScore'),
                            away_score=line_data.get('awayScore'),
                            provider=line.get('provider'),
                            spread=line.get('spread'),
                            formatted_spread=line.get('formattedSpread'),
                            spread_open=line.get('spreadOpen'),
                            over_under=line.get('overUnder'),
                            over_under_open=line.get('overUnderOpen'),
                            home_moneyline=line.get('homeMoneyline'),
                            away_moneyline=line.get('awayMoneyline'),
                        ))
                        added += 1
            
            db.commit()
            self._complete_sync_log(db, log_entry, 'success', added)
            logger.info(f"Game lines synced: {added} added")
            return {'added': added}
            
        except Exception as e:
            db.rollback()
            self._complete_sync_log(db, log_entry, 'failed', error=str(e))
            raise
    
    def sync_game_media(self, db: Session, season: int, week: Optional[int] = None) -> Dict:
        """Sync game media (TV, radio, etc.)"""
        log_entry = self._log_sync(db, 'game_media', season, week=week)
        
        try:
            params = {'year': season}
            if week:
                params['week'] = week
            
            media_data = self._api_request('/games/media', params)
            added = 0
            
            for media in media_data:
                game_id = media.get('id')
                if not game_id:
                    continue
                
                # Check if exists
                existing = db.query(GameMedia).filter(
                    and_(
                        GameMedia.game_id == game_id,
                        GameMedia.outlet == media.get('outlet')
                    )
                ).first()
                
                if not existing:
                    db.add(GameMedia(
                        game_id=game_id,
                        season=media.get('season'),
                        week=media.get('week'),
                        season_type=media.get('seasonType'),
                        start_time=media.get('startTime'),
                        is_start_time_tbd=media.get('isStartTimeTBD'),
                        home_team=media.get('homeTeam'),
                        home_conference=media.get('homeConference'),
                        away_team=media.get('awayTeam'),
                        away_conference=media.get('awayConference'),
                        media_type=media.get('mediaType'),
                        outlet=media.get('outlet'),
                    ))
                    added += 1
            
            db.commit()
            self._complete_sync_log(db, log_entry, 'success', added)
            logger.info(f"Game media synced: {added} added")
            return {'added': added}
            
        except Exception as e:
            db.rollback()
            self._complete_sync_log(db, log_entry, 'failed', error=str(e))
            raise
    
    def sync_game_weather(self, db: Session, season: int, week: Optional[int] = None) -> Dict:
        """Sync game weather"""
        log_entry = self._log_sync(db, 'game_weather', season, week=week)
        
        try:
            params = {'year': season}
            if week:
                params['week'] = week
            
            weather_data = self._api_request('/games/weather', params)
            added = updated = 0
            
            for weather in weather_data:
                game_id = weather.get('id')
                if not game_id:
                    continue
                
                existing = db.query(GameWeather).filter(
                    GameWeather.game_id == game_id
                ).first()
                
                weather_dict = {
                    'game_id': game_id,
                    'season': weather.get('season'),
                    'week': weather.get('week'),
                    'season_type': weather.get('seasonType'),
                    'start_time': weather.get('startTime'),
                    'home_team': weather.get('homeTeam'),
                    'away_team': weather.get('awayTeam'),
                    'venue': weather.get('venue'),
                    'venue_id': weather.get('venueId'),
                    'temperature': weather.get('temperature'),
                    'dew_point': weather.get('dewPoint'),
                    'humidity': weather.get('humidity'),
                    'precipitation': weather.get('precipitation'),
                    'snowfall': weather.get('snowfall'),
                    'wind_direction': weather.get('windDirection'),
                    'wind_speed': weather.get('windSpeed'),
                    'pressure': weather.get('pressure'),
                    'weather_condition_code': weather.get('weatherConditionCode'),
                    'weather_condition': weather.get('weatherCondition'),
                }
                
                if existing:
                    for key, value in weather_dict.items():
                        setattr(existing, key, value)
                    updated += 1
                else:
                    db.add(GameWeather(**weather_dict))
                    added += 1
            
            db.commit()
            self._complete_sync_log(db, log_entry, 'success', added, updated)
            logger.info(f"Game weather synced: {added} added, {updated} updated")
            return {'added': added, 'updated': updated}
            
        except Exception as e:
            db.rollback()
            self._complete_sync_log(db, log_entry, 'failed', error=str(e))
            raise
    
    # ==================== RANKINGS ====================
    
    def sync_rankings(self, db: Session, season: int, week: Optional[int] = None) -> Dict:
        """Sync AP/Coaches rankings"""
        log_entry = self._log_sync(db, 'rankings', season, week=week)
        
        try:
            params = {'year': season}
            if week:
                params['week'] = week
            
            rankings_data = self._api_request('/rankings', params)
            added = 0
            
            for week_data in rankings_data:
                season_val = week_data.get('season')
                week_val = week_data.get('week')
                season_type = week_data.get('seasonType')
                
                for poll in week_data.get('polls', []):
                    poll_name = poll.get('poll')
                    
                    for rank_data in poll.get('ranks', []):
                        existing = db.query(APRanking).filter(
                            and_(
                                APRanking.season == season_val,
                                APRanking.week == week_val,
                                APRanking.poll == poll_name,
                                APRanking.school == rank_data.get('school')
                            )
                        ).first()
                        
                        if not existing:
                            db.add(APRanking(
                                season=season_val,
                                season_type=season_type,
                                week=week_val,
                                poll=poll_name,
                                rank=rank_data.get('rank'),
                                school=rank_data.get('school'),
                                conference=rank_data.get('conference'),
                                first_place_votes=rank_data.get('firstPlaceVotes'),
                                points=rank_data.get('points'),
                            ))
                            added += 1
            
            db.commit()
            self._complete_sync_log(db, log_entry, 'success', added)
            logger.info(f"Rankings synced: {added} added")
            return {'added': added}
            
        except Exception as e:
            db.rollback()
            self._complete_sync_log(db, log_entry, 'failed', error=str(e))
            raise
    
    # ==================== ADVANCED METRICS ====================
    
    def sync_team_sp_ratings(self, db: Session, season: int) -> Dict:
        """Sync SP+ ratings"""
        log_entry = self._log_sync(db, 'sp_ratings', season)
        
        try:
            params = {'year': season}
            sp_data = self._api_request('/ratings/sp', params)
            added = updated = 0
            
            for rating in sp_data:
                existing = db.query(TeamSP).filter(
                    and_(
                        TeamSP.year == rating.get('year'),
                        TeamSP.team == rating.get('team')
                    )
                ).first()
                
                rating_dict = {
                    'year': rating.get('year'),
                    'team': rating.get('team'),
                    'conference': rating.get('conference'),
                    'rating': rating.get('rating'),
                    'ranking': rating.get('ranking'),
                    'second_order_wins': rating.get('secondOrderWins'),
                    'sos': rating.get('sos'),
                }
                
                # Add offense/defense/special teams metrics
                if 'offense' in rating:
                    off = rating['offense']
                    rating_dict.update({
                        'offense_ranking': off.get('ranking'),
                        'offense_rating': off.get('rating'),
                        'offense_success': off.get('success'),
                        'offense_explosiveness': off.get('explosiveness'),
                        'offense_rushing': off.get('rushing'),
                        'offense_passing': off.get('passing'),
                        'offense_standard_downs': off.get('standardDowns'),
                        'offense_passing_downs': off.get('passingDowns'),
                        'offense_run_rate': off.get('runRate'),
                        'offense_pace': off.get('pace'),
                    })
                
                if 'defense' in rating:
                    def_data = rating['defense']
                    rating_dict.update({
                        'defense_ranking': def_data.get('ranking'),
                        'defense_rating': def_data.get('rating'),
                        'defense_success': def_data.get('success'),
                        'defense_explosiveness': def_data.get('explosiveness'),
                        'defense_rushing': def_data.get('rushing'),
                        'defense_passing': def_data.get('passing'),
                        'defense_standard_downs': def_data.get('standardDowns'),
                        'defense_passing_downs': def_data.get('passingDowns'),
                    })
                    
                    if 'havoc' in def_data:
                        havoc = def_data['havoc']
                        rating_dict.update({
                            'defense_havoc_total': havoc.get('total'),
                            'defense_havoc_front_seven': havoc.get('frontSeven'),
                            'defense_havoc_db': havoc.get('db'),
                        })
                
                if 'specialTeams' in rating:
                    rating_dict['special_teams_rating'] = rating['specialTeams'].get('rating')
                
                if existing:
                    for key, value in rating_dict.items():
                        setattr(existing, key, value)
                    updated += 1
                else:
                    db.add(TeamSP(**rating_dict))
                    added += 1
            
            db.commit()
            self._complete_sync_log(db, log_entry, 'success', added, updated)
            logger.info(f"SP+ ratings synced: {added} added, {updated} updated")
            return {'added': added, 'updated': updated}
            
        except Exception as e:
            db.rollback()
            self._complete_sync_log(db, log_entry, 'failed', error=str(e))
            raise
    
    def sync_team_fpi_ratings(self, db: Session, season: int) -> Dict:
        """Sync FPI ratings"""
        log_entry = self._log_sync(db, 'fpi_ratings', season)
        
        try:
            params = {'year': season}
            fpi_data = self._api_request('/ratings/fpi', params)
            added = updated = 0
            
            for rating in fpi_data:
                existing = db.query(TeamFPI).filter(
                    and_(
                        TeamFPI.year == rating.get('year'),
                        TeamFPI.team == rating.get('team')
                    )
                ).first()
                
                rating_dict = {
                    'year': rating.get('year'),
                    'team': rating.get('team'),
                    'conference': rating.get('conference'),
                    'fpi': rating.get('fpi'),
                    'resume_ranks': rating.get('resumeRanks'),
                    'strength_of_record': rating.get('strengthOfRecord'),
                    'average_win_probability': rating.get('averageWinProbability'),
                    'strength_of_schedule': rating.get('strengthOfSchedule'),
                    'remaining_strength_of_schedule': rating.get('remainingStrengthOfSchedule'),
                    'game_control': rating.get('gameControl'),
                }
                
                if existing:
                    for key, value in rating_dict.items():
                        setattr(existing, key, value)
                    updated += 1
                else:
                    db.add(TeamFPI(**rating_dict))
                    added += 1
            
            db.commit()
            self._complete_sync_log(db, log_entry, 'success', added, updated)
            logger.info(f"FPI ratings synced: {added} added, {updated} updated")
            return {'added': added, 'updated': updated}
            
        except Exception as e:
            db.rollback()
            self._complete_sync_log(db, log_entry, 'failed', error=str(e))
            raise
    
    def sync_team_srs_ratings(self, db: Session, season: int) -> Dict:
        """Sync SRS ratings"""
        log_entry = self._log_sync(db, 'srs_ratings', season)
        
        try:
            params = {'year': season}
            srs_data = self._api_request('/ratings/srs', params)
            added = updated = 0
            
            for rating in srs_data:
                existing = db.query(TeamSRS).filter(
                    and_(
                        TeamSRS.year == rating.get('year'),
                        TeamSRS.team == rating.get('team')
                    )
                ).first()
                
                rating_dict = {
                    'year': rating.get('year'),
                    'team': rating.get('team'),
                    'conference': rating.get('conference'),
                    'division': rating.get('division'),
                    'rating': rating.get('rating'),
                    'ranking': rating.get('ranking'),
                }
                
                if existing:
                    for key, value in rating_dict.items():
                        setattr(existing, key, value)
                    updated += 1
                else:
                    db.add(TeamSRS(**rating_dict))
                    added += 1
            
            db.commit()
            self._complete_sync_log(db, log_entry, 'success', added, updated)
            logger.info(f"SRS ratings synced: {added} added, {updated} updated")
            return {'added': added, 'updated': updated}
            
        except Exception as e:
            db.rollback()
            self._complete_sync_log(db, log_entry, 'failed', error=str(e))
            raise
    
    def sync_team_elo_ratings(self, db: Session, season: int) -> Dict:
        """Sync Elo ratings"""
        log_entry = self._log_sync(db, 'elo_ratings', season)
        
        try:
            params = {'year': season}
            elo_data = self._api_request('/ratings/elo', params)
            added = updated = 0
            
            for rating in elo_data:
                existing = db.query(TeamElo).filter(
                    and_(
                        TeamElo.year == rating.get('year'),
                        TeamElo.team == rating.get('team')
                    )
                ).first()
                
                rating_dict = {
                    'year': rating.get('year'),
                    'team': rating.get('team'),
                    'conference': rating.get('conference'),
                    'elo': rating.get('elo'),
                }
                
                if existing:
                    for key, value in rating_dict.items():
                        setattr(existing, key, value)
                    updated += 1
                else:
                    db.add(TeamElo(**rating_dict))
                    added += 1
            
            db.commit()
            self._complete_sync_log(db, log_entry, 'success', added, updated)
            logger.info(f"Elo ratings synced: {added} added, {updated} updated")
            return {'added': added, 'updated': updated}
            
        except Exception as e:
            db.rollback()
            self._complete_sync_log(db, log_entry, 'failed', error=str(e))
            raise
    
    def sync_team_ppa(self, db: Session, season: int) -> Dict:
        """Sync team PPA (Predicted Points Added)"""
        log_entry = self._log_sync(db, 'team_ppa', season)
        
        try:
            params = {'year': season}
            ppa_data = self._api_request('/ppa/teams', params)
            added = updated = 0
            
            for ppa in ppa_data:
                existing = db.query(TeamPPA).filter(
                    and_(
                        TeamPPA.season == ppa.get('season'),
                        TeamPPA.team == ppa.get('team')
                    )
                ).first()
                
                ppa_dict = {
                    'season': ppa.get('season'),
                    'conference': ppa.get('conference'),
                    'team': ppa.get('team'),
                }
                
                # Offense metrics
                if 'offense' in ppa:
                    off = ppa['offense']
                    ppa_dict.update({
                        'offense_overall': off.get('overall'),
                        'offense_passing': off.get('passing'),
                        'offense_rushing': off.get('rushing'),
                        'offense_first_down': off.get('firstDown'),
                        'offense_second_down': off.get('secondDown'),
                        'offense_third_down': off.get('thirdDown'),
                    })
                
                # Defense metrics
                if 'defense' in ppa:
                    def_data = ppa['defense']
                    ppa_dict.update({
                        'defense_overall': def_data.get('overall'),
                        'defense_passing': def_data.get('passing'),
                        'defense_rushing': def_data.get('rushing'),
                        'defense_first_down': def_data.get('firstDown'),
                        'defense_second_down': def_data.get('secondDown'),
                        'defense_third_down': def_data.get('thirdDown'),
                    })
                
                if existing:
                    for key, value in ppa_dict.items():
                        setattr(existing, key, value)
                    updated += 1
                else:
                    db.add(TeamPPA(**ppa_dict))
                    added += 1
            
            db.commit()
            self._complete_sync_log(db, log_entry, 'success', added, updated)
            logger.info(f"Team PPA synced: {added} added, {updated} updated")
            return {'added': added, 'updated': updated}
            
        except Exception as e:
            db.rollback()
            self._complete_sync_log(db, log_entry, 'failed', error=str(e))
            raise
    
    def sync_team_talent(self, db: Session, season: int) -> Dict:
        """Sync team talent composite"""
        log_entry = self._log_sync(db, 'team_talent', season)
        
        try:
            params = {'year': season}
            talent_data = self._api_request('/talent', params)
            added = updated = 0
            
            for talent in talent_data:
                existing = db.query(TeamTalent).filter(
                    and_(
                        TeamTalent.year == talent.get('year'),
                        TeamTalent.team == talent.get('school')
                    )
                ).first()
                
                talent_dict = {
                    'year': talent.get('year'),
                    'team': talent.get('school'),
                    'talent': talent.get('talent'),
                }
                
                if existing:
                    for key, value in talent_dict.items():
                        setattr(existing, key, value)
                    updated += 1
                else:
                    db.add(TeamTalent(**talent_dict))
                    added += 1
            
            db.commit()
            self._complete_sync_log(db, log_entry, 'success', added, updated)
            logger.info(f"Team talent synced: {added} added, {updated} updated")
            return {'added': added, 'updated': updated}
            
        except Exception as e:
            db.rollback()
            self._complete_sync_log(db, log_entry, 'failed', error=str(e))
            raise
    
    def sync_team_records(self, db: Session, season: int) -> Dict:
        """Sync team records"""
        log_entry = self._log_sync(db, 'team_records', season)
        
        try:
            params = {'year': season}
            records_data = self._api_request('/records', params)
            added = updated = 0
            
            for record in records_data:
                existing = db.query(TeamRecord).filter(
                    and_(
                        TeamRecord.year == record.get('year'),
                        TeamRecord.team == record.get('team')
                    )
                ).first()
                
                record_dict = {
                    'year': record.get('year'),
                    'team': record.get('team'),
                    'conference': record.get('conference'),
                    'division': record.get('division'),
                    'expected_wins': record.get('expectedWins'),
                }
                
                # Total record
                if 'total' in record:
                    total = record['total']
                    record_dict.update({
                        'total_games': total.get('games'),
                        'total_wins': total.get('wins'),
                        'total_losses': total.get('losses'),
                        'total_ties': total.get('ties'),
                    })
                
                # Conference record
                if 'conferenceGames' in record:
                    conf = record['conferenceGames']
                    record_dict.update({
                        'conference_games': conf.get('games'),
                        'conference_wins': conf.get('wins'),
                        'conference_losses': conf.get('losses'),
                        'conference_ties': conf.get('ties'),
                    })
                
                # Home record
                if 'homeGames' in record:
                    home = record['homeGames']
                    record_dict.update({
                        'home_games': home.get('games'),
                        'home_wins': home.get('wins'),
                        'home_losses': home.get('losses'),
                        'home_ties': home.get('ties'),
                    })
                
                # Away record
                if 'awayGames' in record:
                    away = record['awayGames']
                    record_dict.update({
                        'away_games': away.get('games'),
                        'away_wins': away.get('wins'),
                        'away_losses': away.get('losses'),
                        'away_ties': away.get('ties'),
                    })
                
                if existing:
                    for key, value in record_dict.items():
                        setattr(existing, key, value)
                    updated += 1
                else:
                    db.add(TeamRecord(**record_dict))
                    added += 1
            
            db.commit()
            self._complete_sync_log(db, log_entry, 'success', added, updated)
            logger.info(f"Team records synced: {added} added, {updated} updated")
            return {'added': added, 'updated': updated}
            
        except Exception as e:
            db.rollback()
            self._complete_sync_log(db, log_entry, 'failed', error=str(e))
            raise
    
    # ==================== RECRUITING ====================
    
    def sync_recruiting_teams(self, db: Session, year: int) -> Dict:
        """Sync team recruiting rankings"""
        log_entry = self._log_sync(db, 'recruiting_teams', year)
        
        try:
            params = {'year': year}
            recruiting_data = self._api_request('/recruiting/teams', params)
            added = updated = 0
            
            for recruit_team in recruiting_data:
                existing = db.query(RecruitingTeam).filter(
                    and_(
                        RecruitingTeam.year == recruit_team.get('year'),
                        RecruitingTeam.team == recruit_team.get('team')
                    )
                ).first()
                
                recruit_dict = {
                    'year': recruit_team.get('year'),
                    'rank': recruit_team.get('rank'),
                    'team': recruit_team.get('team'),
                    'points': recruit_team.get('points'),
                }
                
                if existing:
                    for key, value in recruit_dict.items():
                        setattr(existing, key, value)
                    updated += 1
                else:
                    db.add(RecruitingTeam(**recruit_dict))
                    added += 1
            
            db.commit()
            self._complete_sync_log(db, log_entry, 'success', added, updated)
            logger.info(f"Recruiting teams synced: {added} added, {updated} updated")
            return {'added': added, 'updated': updated}
            
        except Exception as e:
            db.rollback()
            self._complete_sync_log(db, log_entry, 'failed', error=str(e))
            raise
    
    def sync_recruits(self, db: Session, year: int, classification: str = 'HighSchool') -> Dict:
        """Sync individual recruits"""
        log_entry = self._log_sync(db, f'recruits_{classification}', year)
        
        try:
            params = {'year': year, 'classification': classification}
            recruits_data = self._api_request('/recruiting/players', params)
            added = updated = 0
            
            for recruit_data in recruits_data:
                recruit_id = recruit_data.get('id')
                if not recruit_id:
                    continue
                
                existing = db.query(Recruit).filter(Recruit.id == recruit_id).first()
                
                recruit_dict = {
                    'id': recruit_id,
                    'recruit_type': recruit_data.get('recruitType'),
                    'year': recruit_data.get('year'),
                    'ranking': recruit_data.get('ranking'),
                    'name': recruit_data.get('name'),
                    'school': recruit_data.get('school'),
                    'committed_to': recruit_data.get('committedTo'),
                    'position': recruit_data.get('position'),
                    'height': recruit_data.get('height'),
                    'weight': recruit_data.get('weight'),
                    'stars': recruit_data.get('stars'),
                    'rating': recruit_data.get('rating'),
                    'city': recruit_data.get('city'),
                    'state_province': recruit_data.get('stateProvince'),
                    'country': recruit_data.get('country'),
                }
                
                if existing:
                    for key, value in recruit_dict.items():
                        setattr(existing, key, value)
                    updated += 1
                else:
                    db.add(Recruit(**recruit_dict))
                    added += 1
            
            db.commit()
            self._complete_sync_log(db, log_entry, 'success', added, updated)
            logger.info(f"Recruits synced: {added} added, {updated} updated")
            return {'added': added, 'updated': updated}
            
        except Exception as e:
            db.rollback()
            self._complete_sync_log(db, log_entry, 'failed', error=str(e))
            raise
    
    # ==================== PLAYERS ====================
    
    def sync_roster(self, db: Session, team: str, year: int) -> Dict:
        """Sync team roster"""
        log_entry = self._log_sync(db, f'roster_{team}', year)
        
        try:
            params = {'team': team, 'year': year}
            roster_data = self._api_request('/roster', params)
            added = updated = 0
            
            for player_data in roster_data:
                player_id = player_data.get('id')
                if not player_id:
                    continue
                
                existing = db.query(Player).filter(Player.id == player_id).first()
                
                player_dict = {
                    'id': player_id,
                    'team': player_data.get('team'),
                    'name': player_data.get('name'),
                    'first_name': player_data.get('first_name'),
                    'last_name': player_data.get('last_name'),
                    'weight': player_data.get('weight'),
                    'height': player_data.get('height'),
                    'jersey': player_data.get('jersey'),
                    'year': player_data.get('year'),
                    'position': player_data.get('position'),
                    'home_city': player_data.get('home_city'),
                    'home_state': player_data.get('home_state'),
                    'home_country': player_data.get('home_country'),
                    'home_latitude': player_data.get('home_latitude'),
                    'home_longitude': player_data.get('home_longitude'),
                    'home_county_fips': player_data.get('home_county_fips'),
                    'recruit_ids': player_data.get('recruit_ids', []),
                }
                
                if existing:
                    for key, value in player_dict.items():
                        setattr(existing, key, value)
                    updated += 1
                else:
                    db.add(Player(**player_dict))
                    added += 1
            
            db.commit()
            self._complete_sync_log(db, log_entry, 'success', added, updated)
            logger.info(f"Roster synced for {team}: {added} added, {updated} updated")
            return {'added': added, 'updated': updated}
            
        except Exception as e:
            db.rollback()
            self._complete_sync_log(db, log_entry, 'failed', error=str(e))
            raise
    
    def sync_transfer_portal(self, db: Session, year: int) -> Dict:
        """Sync transfer portal entries"""
        log_entry = self._log_sync(db, 'transfer_portal', year)
        
        try:
            params = {'year': year}
            transfers_data = self._api_request('/player/portal', params)
            added = 0
            
            for transfer in transfers_data:
                # Transfers don't have unique IDs, so check by name/origin/destination
                existing = db.query(TransferPortal).filter(
                    and_(
                        TransferPortal.season == transfer.get('season'),
                        TransferPortal.first_name == transfer.get('firstName'),
                        TransferPortal.last_name == transfer.get('lastName'),
                        TransferPortal.origin == transfer.get('origin')
                    )
                ).first()
                
                if not existing:
                    db.add(TransferPortal(
                        season=transfer.get('season'),
                        first_name=transfer.get('firstName'),
                        last_name=transfer.get('lastName'),
                        position=transfer.get('position'),
                        origin=transfer.get('origin'),
                        destination=transfer.get('destination'),
                        transfer_date=transfer.get('transferDate'),
                        rating=transfer.get('rating'),
                        stars=transfer.get('stars'),
                        eligibility=transfer.get('eligibility'),
                    ))
                    added += 1
            
            db.commit()
            self._complete_sync_log(db, log_entry, 'success', added)
            logger.info(f"Transfer portal synced: {added} added")
            return {'added': added}
            
        except Exception as e:
            db.rollback()
            self._complete_sync_log(db, log_entry, 'failed', error=str(e))
            raise
    
    # ==================== COACHES ====================
    
    def sync_coaches(self, db: Session, team: Optional[str] = None, year: Optional[int] = None) -> Dict:
        """Sync coaches"""
        log_entry = self._log_sync(db, 'coaches', year)
        
        try:
            params = {}
            if team:
                params['team'] = team
            if year:
                params['year'] = year
            
            coaches_data = self._api_request('/coaches', params)
            added = updated = 0
            
            for coach_data in coaches_data:
                # Coaches might not have unique IDs, use name + school + year
                existing = db.query(Coach).filter(
                    and_(
                        Coach.first_name == coach_data.get('first_name'),
                        Coach.last_name == coach_data.get('last_name'),
                        Coach.school == coach_data.get('school'),
                        Coach.year == coach_data.get('year')
                    )
                ).first()
                
                coach_dict = {
                    'first_name': coach_data.get('first_name'),
                    'last_name': coach_data.get('last_name'),
                    'hire_date': coach_data.get('hire_date'),
                    'school': coach_data.get('school'),
                    'year': coach_data.get('year'),
                    'seasons': coach_data.get('seasons', []),
                }
                
                if existing:
                    for key, value in coach_dict.items():
                        setattr(existing, key, value)
                    updated += 1
                else:
                    db.add(Coach(**coach_dict))
                    added += 1
            
            db.commit()
            self._complete_sync_log(db, log_entry, 'success', added, updated)
            logger.info(f"Coaches synced: {added} added, {updated} updated")
            return {'added': added, 'updated': updated}
            
        except Exception as e:
            db.rollback()
            self._complete_sync_log(db, log_entry, 'failed', error=str(e))
            raise
    
    # ==================== DRAFT ====================
    
    def sync_draft_picks(self, db: Session, year: Optional[int] = None) -> Dict:
        """Sync NFL draft picks"""
        log_entry = self._log_sync(db, 'draft_picks', year)
        
        try:
            params = {}
            if year:
                params['year'] = year
            
            draft_data = self._api_request('/draft/picks', params)
            added = updated = 0
            
            for pick in draft_data:
                # Use college_athlete_id if available, otherwise name + year
                existing = None
                if pick.get('collegeAthleteId'):
                    existing = db.query(DraftPick).filter(
                        DraftPick.college_athlete_id == pick.get('collegeAthleteId')
                    ).first()
                
                if not existing:
                    existing = db.query(DraftPick).filter(
                        and_(
                            DraftPick.name == pick.get('name'),
                            DraftPick.year == pick.get('year')
                        )
                    ).first()
                
                pick_dict = {
                    'college_athlete_id': pick.get('collegeAthleteId'),
                    'nfl_athlete_id': pick.get('nflAthleteId'),
                    'college_id': pick.get('collegeId'),
                    'college_team': pick.get('collegeTeam'),
                    'college_conference': pick.get('collegeConference'),
                    'nfl_team': pick.get('nflTeam'),
                    'year': pick.get('year'),
                    'overall': pick.get('overall'),
                    'round': pick.get('round'),
                    'pick': pick.get('pick'),
                    'name': pick.get('name'),
                    'position': pick.get('position'),
                    'height': pick.get('height'),
                    'weight': pick.get('weight'),
                    'pre_draft_ranking': pick.get('preDraftRanking'),
                    'pre_draft_position_ranking': pick.get('preDraftPositionRanking'),
                    'pre_draft_grade': pick.get('preDraftGrade'),
                }
                
                # Hometown info
                if 'hometownInfo' in pick:
                    hometown = pick['hometownInfo']
                    pick_dict.update({
                        'hometownInfo_city': hometown.get('city'),
                        'hometownInfo_state': hometown.get('state'),
                        'hometownInfo_country': hometown.get('country'),
                    })
                
                if existing:
                    for key, value in pick_dict.items():
                        setattr(existing, key, value)
                    updated += 1
                else:
                    db.add(DraftPick(**pick_dict))
                    added += 1
            
            db.commit()
            self._complete_sync_log(db, log_entry, 'success', added, updated)
            logger.info(f"Draft picks synced: {added} added, {updated} updated")
            return {'added': added, 'updated': updated}
            
        except Exception as e:
            db.rollback()
            self._complete_sync_log(db, log_entry, 'failed', error=str(e))
            raise
    
    # ==================== DRIVES & PLAYS ====================
    
    def sync_drives(self, db: Session, season: int, week: Optional[int] = None) -> Dict:
        """Sync drive data"""
        log_entry = self._log_sync(db, 'drives', season, week=week)
        
        try:
            params = {'year': season}
            if week:
                params['week'] = week
            
            drives_data = self._api_request('/drives', params)
            added = 0
            
            for drive in drives_data:
                drive_id = drive.get('id')
                if not drive_id:
                    continue
                
                existing = db.query(Drive).filter(Drive.id == drive_id).first()
                
                if not existing:
                    db.add(Drive(
                        id=drive_id,
                        game_id=drive.get('game_id'),
                        season=drive.get('season'),
                        week=drive.get('week'),
                        offense=drive.get('offense'),
                        offense_conference=drive.get('offense_conference'),
                        defense=drive.get('defense'),
                        defense_conference=drive.get('defense_conference'),
                        drive_number=drive.get('drive_number'),
                        scoring=drive.get('scoring'),
                        start_period=drive.get('start_period'),
                        start_yardline=drive.get('start_yardline'),
                        start_yards_to_goal=drive.get('start_yards_to_goal'),
                        start_time_minutes=drive.get('start_time', {}).get('minutes') if drive.get('start_time') else None,
                        start_time_seconds=drive.get('start_time', {}).get('seconds') if drive.get('start_time') else None,
                        end_period=drive.get('end_period'),
                        end_yardline=drive.get('end_yardline'),
                        end_yards_to_goal=drive.get('end_yards_to_goal'),
                        end_time_minutes=drive.get('end_time', {}).get('minutes') if drive.get('end_time') else None,
                        end_time_seconds=drive.get('end_time', {}).get('seconds') if drive.get('end_time') else None,
                        plays=drive.get('plays'),
                        yards=drive.get('yards'),
                        drive_result=drive.get('drive_result'),
                        is_home_offense=drive.get('is_home_offense'),
                    ))
                    added += 1
            
            db.commit()
            self._complete_sync_log(db, log_entry, 'success', added)
            logger.info(f"Drives synced: {added} added")
            return {'added': added}
            
        except Exception as e:
            db.rollback()
            self._complete_sync_log(db, log_entry, 'failed', error=str(e))
            raise
    
    def sync_plays(self, db: Session, season: int, week: int) -> Dict:
        """Sync play-by-play data (warning: this is A LOT of data!)"""
        log_entry = self._log_sync(db, 'plays', season, week=week)
        
        try:
            params = {'year': season, 'week': week}
            plays_data = self._api_request('/plays', params)
            added = 0
            
            for play in plays_data:
                play_id = play.get('id')
                if not play_id:
                    continue
                
                existing = db.query(Play).filter(Play.id == play_id).first()
                
                if not existing:
                    # Parse clock
                    clock_minutes = None
                    clock_seconds = None
                    if play.get('clock'):
                        clock_dict = play['clock']
                        clock_minutes = clock_dict.get('minutes')
                        clock_seconds = clock_dict.get('seconds')
                    
                    db.add(Play(
                        id=play_id,
                        drive_id=play.get('drive_id'),
                        game_id=play.get('game_id'),
                        season=play.get('season'),
                        week=play.get('week'),
                        offense=play.get('offense'),
                        offense_conference=play.get('offense_conference'),
                        offense_score=play.get('offense_score'),
                        defense=play.get('defense'),
                        defense_conference=play.get('defense_conference'),
                        defense_score=play.get('defense_score'),
                        home=play.get('home'),
                        away=play.get('away'),
                        period=play.get('period'),
                        clock_minutes=clock_minutes,
                        clock_seconds=clock_seconds,
                        yard_line=play.get('yard_line'),
                        yards_to_goal=play.get('yards_to_goal'),
                        down=play.get('down'),
                        distance=play.get('distance'),
                        yards_gained=play.get('yards_gained'),
                        play_number=play.get('play_number'),
                        play_text=play.get('play_text'),
                        play_type=play.get('play_type'),
                        ppa=play.get('ppa'),
                        scoring=play.get('scoring'),
                        rush_pass=play.get('rushPass'),
                        success=play.get('success'),
                        epa=play.get('epa'),
                        garbage_time=play.get('garbageTime'),
                    ))
                    added += 1
            
            db.commit()
            self._complete_sync_log(db, log_entry, 'success', added)
            logger.info(f"Plays synced for week {week}: {added} added")
            return {'added': added}
            
        except Exception as e:
            db.rollback()
            self._complete_sync_log(db, log_entry, 'failed', error=str(e))
            raise
    
    # ==================== COMPREHENSIVE SYNC ====================
    
    def sync_season_core_data(self, db: Session, season: int) -> Dict:
        """Sync all core data for a season"""
        results = {}
        
        logger.info(f"Starting comprehensive sync for {season} season")
        
        # Core reference data (only needs to be done once or occasionally)
        try:
            results['conferences'] = self.sync_conferences(db)
            results['teams'] = self.sync_teams(db, 'fbs')
            results['venues'] = self.sync_venues(db)
        except Exception as e:
            logger.error(f"Error syncing reference data: {e}")
        
        # Games and related data
        try:
            results['games_regular'] = self.sync_games(db, season, 'regular')
            results['games_postseason'] = self.sync_games(db, season, 'postseason')
            results['game_lines'] = self.sync_game_lines(db, season)
            results['game_media'] = self.sync_game_media(db, season)
            results['game_weather'] = self.sync_game_weather(db, season)
        except Exception as e:
            logger.error(f"Error syncing game data: {e}")
        
        # Rankings
        try:
            results['rankings'] = self.sync_rankings(db, season)
        except Exception as e:
            logger.error(f"Error syncing rankings: {e}")
        
        # Advanced metrics
        try:
            results['sp_ratings'] = self.sync_team_sp_ratings(db, season)
            results['fpi_ratings'] = self.sync_team_fpi_ratings(db, season)
            results['srs_ratings'] = self.sync_team_srs_ratings(db, season)
            results['elo_ratings'] = self.sync_team_elo_ratings(db, season)
            results['team_ppa'] = self.sync_team_ppa(db, season)
            results['team_talent'] = self.sync_team_talent(db, season)
            results['team_records'] = self.sync_team_records(db, season)
        except Exception as e:
            logger.error(f"Error syncing advanced metrics: {e}")
        
        # Recruiting
        try:
            results['recruiting_teams'] = self.sync_recruiting_teams(db, season)
            results['recruits'] = self.sync_recruits(db, season)
        except Exception as e:
            logger.error(f"Error syncing recruiting data: {e}")
        
        # Draft (for completed seasons)
        try:
            results['draft_picks'] = self.sync_draft_picks(db, season)
        except Exception as e:
            logger.error(f"Error syncing draft data: {e}")
        
        # Coaches
        try:
            results['coaches'] = self.sync_coaches(db, year=season)
        except Exception as e:
            logger.error(f"Error syncing coaches: {e}")
        
        # Transfer portal
        try:
            results['transfer_portal'] = self.sync_transfer_portal(db, season)
        except Exception as e:
            logger.error(f"Error syncing transfer portal: {e}")
        
        logger.info(f"Comprehensive sync completed for {season}")
        return results
    
    def sync_weekly_update(self, db: Session, season: int, week: int) -> Dict:
        """Quick weekly update during the season"""
        results = {}
        
        logger.info(f"Starting weekly sync for {season} week {week}")
        
        # Games for this week
        results['games'] = self.sync_games(db, season, 'regular', week)
        results['game_lines'] = self.sync_game_lines(db, season, week)
        results['game_media'] = self.sync_game_media(db, season, week)
        results['game_weather'] = self.sync_game_weather(db, season, week)
        
        # Rankings (if available)
        try:
            results['rankings'] = self.sync_rankings(db, season, week)
        except:
            pass
        
        # Drives for this week (optional - lots of data)
        # results['drives'] = self.sync_drives(db, season, week)
        
        logger.info(f"Weekly sync completed for week {week}")
        return results


# ==================== BACKGROUND JOB ====================

def run_daily_sync():
    """Daily sync job to run during the season"""
    from datetime import datetime
    
    db = SessionLocal()
    api_key = os.getenv("CFBD_API_KEY", "mBIqtiooiszQC3myFOJyvK4y8j5ZUzRr5JXRCjl0yjOvXIOFrdKLix4b+upMY2cw")
    sync_service = CFBDataSyncService(api_key)
    
    try:
        current_date = datetime.now()
        current_season = current_date.year
        
        # Determine current week (rough estimate - Aug-Dec)
        if 8 <= current_date.month <= 12:
            # Calculate week based on start of season (late August)
            weeks_since_start = (current_date - datetime(current_season, 8, 25)).days // 7
            current_week = min(max(weeks_since_start, 1), 15)
            
            logger.info(f"Running weekly sync for {current_season} week {current_week}")
            sync_service.sync_weekly_update(db, current_season, current_week)
        elif current_date.month == 1:
            # Postseason
            logger.info(f"Running postseason sync for {current_season}")
            sync_service.sync_games(db, current_season, 'postseason')
        else:
            # Off-season - just update reference data
            logger.info("Off-season: updating reference data only")
            sync_service.sync_teams(db, 'fbs')
            sync_service.sync_venues(db)
        
    except Exception as e:
        logger.error(f"Daily sync failed: {e}")
    finally:
        db.close()

def run_initial_historical_sync(start_year: int = 2014, end_year: int = 2024):
    """One-time sync to populate historical data"""
    db = SessionLocal()
    api_key = os.getenv("CFBD_API_KEY", "mBIqtiooiszQC3myFOJyvK4y8j5ZUzRr5JXRCjl0yjOvXIOFrdKLix4b+upMY2cw")
    sync_service = CFBDataSyncService(api_key)
    
    try:
        for year in range(start_year, end_year + 1):
            logger.info(f"Syncing historical data for {year}")
            sync_service.sync_season_core_data(db, year)
            logger.info(f"Completed sync for {year}")
    except Exception as e:
        logger.error(f"Historical sync failed: {e}")
    finally:
        db.close()