# db_models_complete.py - Complete schema mirroring all CFBD API endpoints

from sqlalchemy import (
    create_engine, Column, Integer, String, Boolean, TIMESTAMP, 
    DECIMAL, ARRAY, JSON, Float, Text, ForeignKey, Index, BigInteger
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/cfb_rankings")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==================== CORE ENTITIES ====================

class Team(Base):
    """Mirror of /teams endpoint"""
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    school = Column(String(100), unique=True, nullable=False, index=True)
    mascot = Column(String(100))
    abbreviation = Column(String(10))
    alt_name1 = Column(String(100))
    alt_name2 = Column(String(100))
    alt_name3 = Column(String(100))
    classification = Column(String(10), index=True)  # fbs, fcs, ii, iii
    conference = Column(String(100), index=True)
    division = Column(String(50))
    color = Column(String(7))
    alt_color = Column(String(7))
    logos = Column(ARRAY(String))
    twitter = Column(String(100))
    
    # Location data
    location_name = Column(String(200))
    location_city = Column(String(100))
    location_state = Column(String(50))
    location_zip = Column(String(20))
    location_country_code = Column(String(10))
    location_timezone = Column(String(50))
    location_latitude = Column(Float)
    location_longitude = Column(Float)
    location_elevation = Column(Float)
    location_capacity = Column(Integer)
    location_year_constructed = Column(Integer)
    location_grass = Column(Boolean)
    location_dome = Column(Boolean)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

class Conference(Base):
    """Mirror of /conferences endpoint"""
    __tablename__ = "conferences"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    short_name = Column(String(50))
    abbreviation = Column(String(10))
    classification = Column(String(10))
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

class Venue(Base):
    """Mirror of /venues endpoint"""
    __tablename__ = "venues"
    
    id = Column(Integer, primary_key=True)  # API venue ID
    name = Column(String(200))
    city = Column(String(100))
    state = Column(String(50))
    zip = Column(String(20))
    country_code = Column(String(10))
    timezone = Column(String(50))
    latitude = Column(Float)
    longitude = Column(Float)
    elevation = Column(Float)
    capacity = Column(Integer)
    year_constructed = Column(Integer)
    grass = Column(Boolean)
    dome = Column(Boolean)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

# ==================== GAMES ====================

class Game(Base):
    """Mirror of /games endpoint"""
    __tablename__ = "games"
    
    id = Column(Integer, primary_key=True)  # API game ID
    season = Column(Integer, nullable=False, index=True)
    week = Column(Integer, index=True)
    season_type = Column(String(20), index=True)
    start_date = Column(String(50))
    start_time_tbd = Column(Boolean)
    completed = Column(Boolean, default=False, index=True)
    neutral_site = Column(Boolean)
    conference_game = Column(Boolean)
    attendance = Column(Integer)
    
    venue_id = Column(Integer)
    venue = Column(String(200))
    
    home_id = Column(Integer)
    home_team = Column(String(100), nullable=False, index=True)
    home_conference = Column(String(100))
    home_division = Column(String(50))
    home_points = Column(Integer)
    home_line_scores = Column(ARRAY(Integer))
    home_post_win_prob = Column(Float)
    home_pregame_elo = Column(Integer)
    home_postgame_elo = Column(Integer)
    
    away_id = Column(Integer)
    away_team = Column(String(100), nullable=False, index=True)
    away_conference = Column(String(100))
    away_division = Column(String(50))
    away_points = Column(Integer)
    away_line_scores = Column(ARRAY(Integer))
    away_post_win_prob = Column(Float)
    away_pregame_elo = Column(Integer)
    away_postgame_elo = Column(Integer)
    
    excitement_index = Column(Float)
    highlights = Column(String(500))
    notes = Column(Text)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

class GameLine(Base):
    """Mirror of /lines endpoint"""
    __tablename__ = "game_lines"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, nullable=False, index=True)
    season = Column(Integer)
    week = Column(Integer)
    season_type = Column(String(20))
    home_team = Column(String(100))
    away_team = Column(String(100))
    home_conference = Column(String(100))
    away_conference = Column(String(100))
    home_score = Column(Integer)
    away_score = Column(Integer)
    provider = Column(String(50))
    spread = Column(Float)
    formatted_spread = Column(String(20))
    spread_open = Column(Float)
    over_under = Column(Float)
    over_under_open = Column(Float)
    home_moneyline = Column(Integer)
    away_moneyline = Column(Integer)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class GameMedia(Base):
    """Mirror of /games/media endpoint"""
    __tablename__ = "game_media"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, nullable=False, index=True)
    season = Column(Integer, nullable=False, index=True)
    week = Column(Integer)
    season_type = Column(String(20))
    start_time = Column(String(50))
    is_start_time_tbd = Column(Boolean)
    home_team = Column(String(100))
    home_conference = Column(String(100))
    away_team = Column(String(100))
    away_conference = Column(String(100))
    media_type = Column(String(20))
    outlet = Column(String(100))
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class GameWeather(Base):
    """Mirror of /games/weather endpoint"""
    __tablename__ = "game_weather"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, nullable=False, index=True)
    season = Column(Integer)
    week = Column(Integer)
    season_type = Column(String(20))
    start_time = Column(String(50))
    home_team = Column(String(100))
    away_team = Column(String(100))
    venue = Column(String(200))
    venue_id = Column(Integer)
    temperature = Column(Float)
    dew_point = Column(Float)
    humidity = Column(Float)
    precipitation = Column(Float)
    snowfall = Column(Float)
    wind_direction = Column(Integer)
    wind_speed = Column(Float)
    pressure = Column(Float)
    weather_condition_code = Column(Integer)
    weather_condition = Column(String(100))
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

# ==================== PLAYS & DRIVES ====================

class Drive(Base):
    """Mirror of /drives endpoint"""
    __tablename__ = "drives"
    
    id = Column(BigInteger, primary_key=True, index=True)
    game_id = Column(Integer, nullable=False, index=True)
    season = Column(Integer, nullable=False)
    week = Column(Integer)
    
    offense = Column(String(100), nullable=False, index=True)
    offense_conference = Column(String(100))
    defense = Column(String(100), nullable=False)
    defense_conference = Column(String(100))
    
    drive_number = Column(Integer)
    scoring = Column(Boolean)
    start_period = Column(Integer)
    start_yardline = Column(Integer)
    start_yards_to_goal = Column(Integer)
    start_time_minutes = Column(Integer)
    start_time_seconds = Column(Integer)
    
    end_period = Column(Integer)
    end_yardline = Column(Integer)
    end_yards_to_goal = Column(Integer)
    end_time_minutes = Column(Integer)
    end_time_seconds = Column(Integer)
    
    plays = Column(Integer)
    yards = Column(Integer)
    drive_result = Column(String(50))
    is_home_offense = Column(Boolean)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class Play(Base):
    """Mirror of /plays endpoint"""
    __tablename__ = "plays"
    
    id = Column(BigInteger, primary_key=True, index=True)
    drive_id = Column(BigInteger, index=True)
    game_id = Column(Integer, nullable=False, index=True)
    season = Column(Integer, nullable=False)
    week = Column(Integer)
    
    offense = Column(String(100), index=True)
    offense_conference = Column(String(100))
    offense_score = Column(Integer)
    defense = Column(String(100))
    defense_conference = Column(String(100))
    defense_score = Column(Integer)
    home = Column(String(100))
    away = Column(String(100))
    
    period = Column(Integer)
    clock_minutes = Column(Integer)
    clock_seconds = Column(Integer)
    yard_line = Column(Integer)
    yards_to_goal = Column(Integer)
    down = Column(Integer)
    distance = Column(Integer)
    yards_gained = Column(Integer)
    
    play_number = Column(Integer)
    play_text = Column(Text)
    play_type = Column(String(100))
    
    ppa = Column(Float)  # Predicted Points Added
    scoring = Column(Boolean)
    
    # Additional play classifications
    rush_pass = Column(String(20))
    success = Column(Boolean)
    epa = Column(Float)  # Expected Points Added
    garbage_time = Column(Boolean)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class PlayStat(Base):
    """Mirror of /play/stats endpoint"""
    __tablename__ = "play_stats"
    
    id = Column(BigInteger, primary_key=True, index=True)
    play_id = Column(BigInteger, index=True)
    game_id = Column(Integer, index=True)
    season = Column(Integer)
    week = Column(Integer)
    team = Column(String(100))
    conference = Column(String(100))
    opponent = Column(String(100))
    
    player_id = Column(Integer, index=True)
    player_name = Column(String(200))
    
    stat_type = Column(String(50))  # RUSH, PASS, REC, etc.
    stat = Column(Integer)  # yards, attempts, etc.
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class PlayType(Base):
    """Mirror of /play/types endpoint"""
    __tablename__ = "play_types"
    
    id = Column(Integer, primary_key=True, index=True)
    play_type_id = Column(Integer, unique=True)
    text = Column(String(100))
    abbreviation = Column(String(20))
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

# ==================== TEAM STATS ====================

class TeamSeasonStat(Base):
    """Mirror of /stats/season endpoint"""
    __tablename__ = "team_season_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    season = Column(Integer, nullable=False, index=True)
    team = Column(String(100), nullable=False, index=True)
    conference = Column(String(100))
    stat_name = Column(String(100), nullable=False)
    stat_value = Column(Float)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_team_season_stats_lookup', 'season', 'team', 'stat_name'),
    )

class TeamGameStats(Base):
    """Mirror of /games/teams endpoint"""
    __tablename__ = "team_game_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, nullable=False, index=True)
    season = Column(Integer, nullable=False)
    week = Column(Integer)
    team = Column(String(100), nullable=False, index=True)
    opponent = Column(String(100))
    home_away = Column(String(10))
    points = Column(Integer)
    conference = Column(String(100))
    
    # Store all stats as JSON (too many individual stats)
    stats = Column(JSON)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class TeamRecord(Base):
    """Mirror of /records endpoint"""
    __tablename__ = "team_records"
    
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False, index=True)
    team = Column(String(100), nullable=False, index=True)
    conference = Column(String(100))
    division = Column(String(50))
    
    total_games = Column(Integer)
    total_wins = Column(Integer)
    total_losses = Column(Integer)
    total_ties = Column(Integer)
    
    conference_games = Column(Integer)
    conference_wins = Column(Integer)
    conference_losses = Column(Integer)
    conference_ties = Column(Integer)
    
    home_games = Column(Integer)
    home_wins = Column(Integer)
    home_losses = Column(Integer)
    home_ties = Column(Integer)
    
    away_games = Column(Integer)
    away_wins = Column(Integer)
    away_losses = Column(Integer)
    away_ties = Column(Integer)
    
    expected_wins = Column(Float)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class TeamTalent(Base):
    """Mirror of /talent endpoint"""
    __tablename__ = "team_talent"
    
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False, index=True)
    team = Column(String(100), nullable=False, index=True)
    talent = Column(Float)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class TeamMatchup(Base):
    """Mirror of /teams/matchup endpoint"""
    __tablename__ = "team_matchups"
    
    id = Column(Integer, primary_key=True, index=True)
    team1 = Column(String(100), nullable=False, index=True)
    team2 = Column(String(100), nullable=False, index=True)
    start_year = Column(Integer)
    end_year = Column(Integer)
    
    team1_wins = Column(Integer)
    team2_wins = Column(Integer)
    ties = Column(Integer)
    
    # Store game history as JSON
    games = Column(JSON)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

# ==================== ADVANCED METRICS ====================

class TeamPPA(Base):
    """Mirror of /ppa/teams endpoint - Predicted Points Added"""
    __tablename__ = "team_ppa"
    
    id = Column(Integer, primary_key=True, index=True)
    season = Column(Integer, nullable=False, index=True)
    conference = Column(String(100))
    team = Column(String(100), nullable=False, index=True)
    
    # Overall PPA
    offense_overall = Column(Float)
    offense_passing = Column(Float)
    offense_rushing = Column(Float)
    offense_first_down = Column(Float)
    offense_second_down = Column(Float)
    offense_third_down = Column(Float)
    
    defense_overall = Column(Float)
    defense_passing = Column(Float)
    defense_rushing = Column(Float)
    defense_first_down = Column(Float)
    defense_second_down = Column(Float)
    defense_third_down = Column(Float)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class TeamSP(Base):
    """Mirror of /ratings/sp endpoint - Success Rate and other SP+ metrics"""
    __tablename__ = "team_sp_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False, index=True)
    team = Column(String(100), nullable=False, index=True)
    conference = Column(String(100))
    
    rating = Column(Float)
    ranking = Column(Integer)
    second_order_wins = Column(Float)
    sos = Column(Float)  # Strength of schedule
    
    offense_ranking = Column(Integer)
    offense_rating = Column(Float)
    offense_success = Column(Float)
    offense_explosiveness = Column(Float)
    offense_rushing = Column(Float)
    offense_passing = Column(Float)
    offense_standard_downs = Column(Float)
    offense_passing_downs = Column(Float)
    offense_run_rate = Column(Float)
    offense_pace = Column(Float)
    
    defense_ranking = Column(Integer)
    defense_rating = Column(Float)
    defense_success = Column(Float)
    defense_explosiveness = Column(Float)
    defense_rushing = Column(Float)
    defense_passing = Column(Float)
    defense_standard_downs = Column(Float)
    defense_passing_downs = Column(Float)
    defense_havoc_total = Column(Float)
    defense_havoc_front_seven = Column(Float)
    defense_havoc_db = Column(Float)
    
    special_teams_rating = Column(Float)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class TeamSRS(Base):
    """Mirror of /ratings/srs endpoint - Simple Rating System"""
    __tablename__ = "team_srs_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False, index=True)
    team = Column(String(100), nullable=False, index=True)
    conference = Column(String(100))
    division = Column(String(50))
    rating = Column(Float)
    ranking = Column(Integer)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class TeamFPI(Base):
    """Mirror of /ratings/fpi endpoint - Football Power Index"""
    __tablename__ = "team_fpi_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False, index=True)
    team = Column(String(100), nullable=False, index=True)
    conference = Column(String(100))
    fpi = Column(Float)
    resume_ranks = Column(Float)
    strength_of_record = Column(Float)
    average_win_probability = Column(Float)
    strength_of_schedule = Column(Float)
    remaining_strength_of_schedule = Column(Float)
    game_control = Column(Float)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class TeamElo(Base):
    """Mirror of /ratings/elo endpoint"""
    __tablename__ = "team_elo_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False, index=True)
    team = Column(String(100), nullable=False, index=True)
    conference = Column(String(100))
    elo = Column(Float)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class GamePPA(Base):
    """Mirror of /ppa/games endpoint"""
    __tablename__ = "game_ppa"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, nullable=False, index=True)
    season = Column(Integer)
    week = Column(Integer)
    conference = Column(String(100))
    team = Column(String(100), index=True)
    opponent = Column(String(100))
    
    offense_overall = Column(Float)
    offense_passing = Column(Float)
    offense_rushing = Column(Float)
    
    defense_overall = Column(Float)
    defense_passing = Column(Float)
    defense_rushing = Column(Float)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class PlayerPPA(Base):
    """Mirror of /ppa/players/season endpoint"""
    __tablename__ = "player_ppa"
    
    id = Column(Integer, primary_key=True, index=True)
    season = Column(Integer, nullable=False, index=True)
    player_id = Column(Integer, index=True)
    player = Column(String(200))
    team = Column(String(100), index=True)
    conference = Column(String(100))
    position = Column(String(20))
    
    total_ppa = Column(Float)
    average_ppa = Column(Float)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class WinProbability(Base):
    """Mirror of /metrics/wp endpoint"""
    __tablename__ = "win_probabilities"
    
    id = Column(BigInteger, primary_key=True, index=True)
    game_id = Column(Integer, nullable=False, index=True)
    play_id = Column(BigInteger)
    play_text = Column(Text)
    home_id = Column(Integer)
    home = Column(String(100))
    away_id = Column(Integer)
    away = Column(String(100))
    
    spread = Column(Float)
    home_ball = Column(Boolean)
    home_score = Column(Integer)
    away_score = Column(Integer)
    
    time_remaining = Column(Integer)  # seconds
    yard_line = Column(Integer)
    down = Column(Integer)
    distance = Column(Integer)
    
    home_win_prob = Column(Float)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

# ==================== RANKINGS ====================

class APRanking(Base):
    """Mirror of /rankings endpoint"""
    __tablename__ = "ap_rankings"
    
    id = Column(Integer, primary_key=True, index=True)
    season = Column(Integer, nullable=False, index=True)
    season_type = Column(String(20))
    week = Column(Integer, index=True)
    poll = Column(String(50), index=True)
    rank = Column(Integer)
    school = Column(String(100), nullable=False, index=True)
    conference = Column(String(100))
    first_place_votes = Column(Integer)
    points = Column(Integer)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

# ==================== RECRUITING ====================

class RecruitingTeam(Base):
    """Mirror of /recruiting/teams endpoint"""
    __tablename__ = "recruiting_teams"
    
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False, index=True)
    rank = Column(Integer)
    team = Column(String(100), nullable=False, index=True)
    points = Column(Float)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class Recruit(Base):
    """Mirror of /recruiting/players endpoint"""
    __tablename__ = "recruits"
    
    id = Column(Integer, primary_key=True)  # API recruit ID
    recruit_type = Column(String(20))  # HighSchool, JUCO, PrepSchool
    year = Column(Integer, nullable=False, index=True)
    ranking = Column(Integer)
    name = Column(String(200))
    school = Column(String(100))
    committed_to = Column(String(100), index=True)
    position = Column(String(20), index=True)
    height = Column(Float)
    weight = Column(Integer)
    stars = Column(Integer, index=True)
    rating = Column(Float)
    
    city = Column(String(100))
    state_province = Column(String(50))
    country = Column(String(100))
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

# ==================== PLAYERS ====================

class Player(Base):
    """Mirror of /player/search and /roster endpoints"""
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True)  # API player ID
    team = Column(String(100), index=True)
    name = Column(String(200))
    first_name = Column(String(100))
    last_name = Column(String(100))
    weight = Column(Integer)
    height = Column(Integer)
    jersey = Column(Integer)
    year = Column(Integer, index=True)  # class year
    position = Column(String(20), index=True)
    
    home_city = Column(String(100))
    home_state = Column(String(50))
    home_country = Column(String(100))
    home_latitude = Column(Float)
    home_longitude = Column(Float)
    home_county_fips = Column(String(20))
    
    recruit_ids = Column(ARRAY(Integer))
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

class PlayerSeasonStats(Base):
    """Mirror of /stats/player/season endpoint"""
    __tablename__ = "player_season_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    season = Column(Integer, nullable=False, index=True)
    player_id = Column(Integer, index=True)
    player = Column(String(200))
    team = Column(String(100), index=True)
    conference = Column(String(100))
    category = Column(String(50))  # passing, rushing, receiving, etc.
    stat_type = Column(String(50))  # YDS, TD, etc.
    stat = Column(Float)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class PlayerGameStats(Base):
    """Mirror of /games/players endpoint"""
    __tablename__ = "player_game_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, nullable=False, index=True)
    season = Column(Integer, nullable=False)
    week = Column(Integer)
    player_id = Column(Integer, index=True)
    player = Column(String(200))
    team = Column(String(100), index=True)
    opponent = Column(String(100))
    category = Column(String(50))
    stat_type = Column(String(50))
    stat = Column(Float)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class PlayerUsage(Base):
    """Mirror of /player/usage endpoint"""
    __tablename__ = "player_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    season = Column(Integer, nullable=False, index=True)
    player_id = Column(Integer, index=True)
    player = Column(String(200))
    team = Column(String(100), index=True)
    conference = Column(String(100))
    position = Column(String(20))
    
    usage_overall = Column(Float)
    usage_pass = Column(Float)
    usage_rush = Column(Float)
    usage_first_down = Column(Float)
    usage_second_down = Column(Float)
    usage_third_down = Column(Float)
    usage_standard_downs = Column(Float)
    usage_passing_downs = Column(Float)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class ReturningProduction(Base):
    """Mirror of /player/returning endpoint"""
    __tablename__ = "returning_production"
    
    id = Column(Integer, primary_key=True, index=True)
    season = Column(Integer, nullable=False, index=True)
    team = Column(String(100), nullable=False, index=True)
    conference = Column(String(100))
    
    total_ppa = Column(Float)
    total_passing_ppa = Column(Float)
    total_receiving_ppa = Column(Float)
    total_rushing_ppa = Column(Float)
    
    percent_ppa = Column(Float)
    percent_passing_ppa = Column(Float)
    percent_receiving_ppa = Column(Float)
    percent_rushing_ppa = Column(Float)
    
    usage = Column(Float)
    passing_usage = Column(Float)
    receiving_usage = Column(Float)
    rushing_usage = Column(Float)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class TransferPortal(Base):
    """Mirror of /player/portal endpoint"""
    __tablename__ = "transfer_portal"
    
    id = Column(Integer, primary_key=True, index=True)
    season = Column(Integer, nullable=False, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    position = Column(String(20))
    origin = Column(String(100), index=True)
    destination = Column(String(100), index=True)
    transfer_date = Column(String(50))
    rating = Column(Float)
    stars = Column(Integer)
    eligibility = Column(String(50))
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

# ==================== BETTING & PREDICTIONS ====================

class PregameWinProbability(Base):
    """Mirror of /metrics/wp/pregame endpoint"""
    __tablename__ = "pregame_win_probabilities"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, nullable=False, unique=True, index=True)
    season = Column(Integer)
    season_type = Column(String(20))
    week = Column(Integer)
    start_date = Column(String(50))
    
    home_team = Column(String(100))
    away_team = Column(String(100))
    spread = Column(Float)
    home_win_prob = Column(Float)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

# ==================== COACHES ====================

class Coach(Base):
    """Mirror of /coaches endpoint"""
    __tablename__ = "coaches"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    hire_date = Column(String(50))
    
    # Current position
    school = Column(String(100), index=True)
    year = Column(Integer, index=True)
    
    # Seasons info as JSON (since it's an array)
    seasons = Column(JSON)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

# ==================== DRAFT ====================

class DraftPick(Base):
    """Mirror of /draft/picks endpoint"""
    __tablename__ = "draft_picks"
    
    id = Column(Integer, primary_key=True, index=True)
    college_athlete_id = Column(Integer)
    nfl_athlete_id = Column(Integer)
    college_id = Column(Integer)
    college_team = Column(String(100), index=True)
    college_conference = Column(String(100))
    
    nfl_team = Column(String(100))
    
    year = Column(Integer, nullable=False, index=True)
    overall = Column(Integer)
    round = Column(Integer)
    pick = Column(Integer)
    
    name = Column(String(200))
    position = Column(String(20), index=True)
    height = Column(Integer)
    weight = Column(Integer)
    
    pre_draft_ranking = Column(Integer)
    pre_draft_position_ranking = Column(Integer)
    pre_draft_grade = Column(Float)
    
    hometownInfo_city = Column(String(100))
    hometownInfo_state = Column(String(50))
    hometownInfo_country = Column(String(100))
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class DraftTeam(Base):
    """Mirror of /draft/teams endpoint"""
    __tablename__ = "draft_teams"
    
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False, index=True)
    team = Column(String(100), nullable=False, index=True)
    conference = Column(String(100))
    
    total_picks = Column(Integer)
    total_round_1 = Column(Integer)
    total_round_2 = Column(Integer)
    total_round_3 = Column(Integer)
    total_round_4 = Column(Integer)
    total_round_5 = Column(Integer)
    total_round_6 = Column(Integer)
    total_round_7 = Column(Integer)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

# ==================== CUSTOM RANKINGS ====================

class CustomRanking(Base):
    """Your computed rankings"""
    __tablename__ = "custom_rankings"
    
    id = Column(Integer, primary_key=True, index=True)
    season = Column(Integer, nullable=False, index=True)
    season_type = Column(String(20))
    week = Column(Integer, index=True)
    
    team = Column(String(100), nullable=False, index=True)
    rank = Column(Integer)
    ranking_value = Column(DECIMAL(10, 2))
    wins = Column(Integer)
    losses = Column(Integer)
    
    formula_params = Column(JSON)
    computed_at = Column(TIMESTAMP, default=datetime.utcnow)

# ==================== SYNC TRACKING ====================

class SyncLog(Base):
    """Track all sync operations"""
    __tablename__ = "sync_log"
    
    id = Column(Integer, primary_key=True, index=True)
    sync_type = Column(String(50), nullable=False, index=True)
    season = Column(Integer)
    season_type = Column(String(20))
    week = Column(Integer)
    status = Column(String(20), index=True)  # started, success, failed, partial
    records_added = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(TIMESTAMP, default=datetime.utcnow, index=True)
    completed_at = Column(TIMESTAMP)

# ==================== UTILITY FUNCTIONS ====================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize all tables"""
    Base.metadata.create_all(bind=engine)

def drop_all():
    """Drop all tables (use with caution!)"""
    Base.metadata.drop_all(bind=engine)