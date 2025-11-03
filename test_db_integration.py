# test_db_integration.py - Test the database integration

import os
from sqlalchemy.orm import Session
from db_models_complete import SessionLocal, init_db, Game, Team
from cfb_ranking_system import RankingSystem, RankingFormula
from sync_service_complete import CFBDataSyncService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_compute_rankings_from_db():
    """Test computing rankings from database"""
    db = SessionLocal()
    
    try:
        # Get some games from database
        games = db.query(Game).filter(
            Game.season == 2024,
            Game.season_type == 'regular',
            Game.completed == True
        ).limit(50).all()
        
        if not games:
            logger.warning("No games found in database. Run sync first!")
            return
        
        logger.info(f"Found {len(games)} games in database")
        
        # Build ranking system
        system = RankingSystem()
        
        for game in games:
            if game.home_points is None or game.away_points is None:
                continue
            
            # Get team classifications
            home_team = db.query(Team).filter(Team.school == game.home_team).first()
            away_team = db.query(Team).filter(Team.school == game.away_team).first()
            
            home_fbs = home_team.classification == 'fbs' if home_team else True
            away_fbs = away_team.classification == 'fbs' if away_team else True
            
            system.add_game(
                home_name=game.home_team,
                home_score=game.home_points,
                away_name=game.away_team,
                away_score=game.away_points,
                home_fbs=home_fbs,
                away_fbs=away_fbs,
                week=game.week
            )
        
        # Calculate rankings
        logger.info("Calculating rankings...")
        system.calculate_rankings(iterations=20)
        
        # Print top 10
        logger.info("\nTop 10 Teams:")
        system.print_rankings(top_n=10)
        
        logger.info("\nTest successful!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def test_sync_and_rank():
    """Test syncing data and computing rankings"""
    db = SessionLocal()
    
    try:
        # Initialize database
        init_db()
        
        # Sync teams
        api_key = os.getenv("CFBD_API_KEY", "mBIqtiooiszQC3myFOJyvK4y8j5ZUzRr5JXRCjl0yjOvXIOFrdKLix4b+upMY2cw")
        sync_service = CFBDataSyncService(api_key)
        
        logger.info("Syncing teams...")
        sync_service.sync_teams(db, 'fbs')
        
        logger.info("Syncing games for 2024...")
        sync_service.sync_games(db, 2024, 'regular')
        
        logger.info("Computing rankings...")
        test_compute_rankings_from_db()
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "sync":
        test_sync_and_rank()
    else:
        test_compute_rankings_from_db()