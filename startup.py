# startup.py - Railway startup script

import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def startup():
    """Initialize database and start API"""
    try:
        # Check if this is first run
        from db_models_complete import engine, init_db, SessionLocal, Game
        
        logger.info("Checking database...")
        
        # Try to initialize tables
        try:
            init_db()
            logger.info("Database tables initialized")
        except Exception as e:
            logger.warning(f"Table initialization: {e}")
        
        # Check if we have data
        db = SessionLocal()
        try:
            game_count = db.query(Game).count()
            logger.info(f"Database contains {game_count} games")
            
            if game_count == 0:
                logger.warning("No games in database!")
                logger.info("Run 'python setup_railway.py' to sync data")
                logger.info("Or use POST /admin/sync endpoint")
        except Exception as e:
            logger.warning(f"Could not check game count: {e}")
        finally:
            db.close()
        
        logger.info("Starting API server...")
        
        # Start the API
        import uvicorn
        from api import app
        
        port = int(os.environ.get("PORT", 8000))
        uvicorn.run(app, host="0.0.0.0", port=port)
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    startup()