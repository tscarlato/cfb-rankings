# setup_database.py - Initialize and populate database

import os
import sys
from db_models_complete import init_db, drop_all
from sync_service_complete import CFBDataSyncService, SessionLocal, run_initial_historical_sync
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_fresh_database():
    """Setup database from scratch"""
    logger.info("Creating database tables...")
    init_db()
    logger.info("Database tables created successfully")

def populate_current_season():
    """Populate database with current season data"""
    from datetime import datetime
    
    current_year = datetime.now().year
    db = SessionLocal()
    api_key = os.getenv("CFBD_API_KEY", "mBIqtiooiszQC3myFOJyvK4y8j5ZUzRr5JXRCjl0yjOvXIOFrdKLix4b+upMY2cw")
    sync_service = CFBDataSyncService(api_key)
    
    try:
        logger.info(f"Populating current season ({current_year}) data...")
        sync_service.sync_season_core_data(db, current_year)
        logger.info("Current season data populated successfully")
    except Exception as e:
        logger.error(f"Error populating current season: {e}")
    finally:
        db.close()

def main():
    """Main setup function"""
    if len(sys.argv) < 2:
        print("Usage: python setup_database.py [init|populate|historical]")
        print("  init       - Create database tables")
        print("  populate   - Populate with current season data")
        print("  historical - Populate with historical data (2014-2024)")
        print("  reset      - Drop all tables and reinitialize (DANGER!)")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "init":
        setup_fresh_database()
    elif command == "populate":
        populate_current_season()
    elif command == "historical":
        years = input("Enter year range (e.g., 2014 2024) or press enter for 2014-2024: ")
        if years.strip():
            start_year, end_year = map(int, years.split())
        else:
            start_year, end_year = 2014, 2024
        run_initial_historical_sync(start_year, end_year)
    elif command == "reset":
        confirm = input("This will DELETE ALL DATA. Type 'yes' to confirm: ")
        if confirm.lower() == 'yes':
            logger.warning("Dropping all tables...")
            drop_all()
            logger.info("Reinitializing database...")
            init_db()
            logger.info("Database reset complete")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()