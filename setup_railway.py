# setup_railway.py - Initialize database on Railway

import os
import sys
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_railway():
    """Setup database on Railway"""
    try:
        logger.info("=" * 60)
        logger.info("RAILWAY SETUP")
        logger.info("=" * 60)
        
        # Import after logging is set up
        from db_models_complete import init_db, test_connection, SessionLocal
        from sync_service_complete import CFBDataSyncService
        
        # Test connection
        logger.info("Testing database connection...")
        if not test_connection():
            logger.error("Database connection failed!")
            return False
        logger.info("✓ Database connection successful")
        
        # Initialize tables
        logger.info("Creating database tables...")
        init_db()
        logger.info("✓ Database tables created")
        
        # Check for API key
        api_key = os.getenv("CFBD_API_KEY")
        if not api_key:
            logger.warning("CFBD_API_KEY not set - skipping data sync")
            logger.info("Set CFBD_API_KEY environment variable to enable data syncing")
            return True
        
        # Sync current season data
        current_year = datetime.now().year
        logger.info(f"Syncing data for {current_year} season...")
        
        db = SessionLocal()
        try:
            sync_service = CFBDataSyncService(api_key)
            
            # Sync teams first
            logger.info("Syncing teams...")
            sync_service.sync_teams(db, 'fbs')
            
            # Sync games
            logger.info("Syncing games...")
            sync_service.sync_games(db, current_year, 'regular')
            
            logger.info("✓ Data sync complete")
            
        except Exception as e:
            logger.error(f"Data sync failed: {e}")
            logger.warning("Database is set up but no data was synced")
            logger.info("You can manually trigger sync via /admin/sync endpoint")
        finally:
            db.close()
        
        logger.info("\n" + "=" * 60)
        logger.info("SETUP COMPLETE!")
        logger.info("=" * 60)
        return True
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = setup_railway()
    sys.exit(0 if success else 1)