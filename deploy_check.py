# deploy_check.py - Run this before deploying to verify everything works

import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_environment():
    """Check environment variables"""
    logger.info("=" * 60)
    logger.info("ENVIRONMENT CHECK")
    logger.info("=" * 60)
    
    checks = {
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "CFBD_API_KEY": os.getenv("CFBD_API_KEY"),
        "PORT": os.getenv("PORT", "8000"),
        "ENABLE_SCHEDULER": os.getenv("ENABLE_SCHEDULER", "false")
    }
    
    all_good = True
    for key, value in checks.items():
        status = "✓" if value else "✗"
        display_value = "***" if key in ["DATABASE_URL", "CFBD_API_KEY"] and value else value
        logger.info(f"{status} {key}: {display_value if value else 'NOT SET'}")
        if key in ["DATABASE_URL"] and not value:
            all_good = False
    
    return all_good

def check_database():
    """Test database connection"""
    logger.info("\n" + "=" * 60)
    logger.info("DATABASE CONNECTION CHECK")
    logger.info("=" * 60)
    
    try:
        from db_models_complete import engine, test_connection, DATABASE_URL
        
        if not DATABASE_URL:
            logger.error("✗ DATABASE_URL not set")
            return False
        
        logger.info(f"Testing connection to: {DATABASE_URL.split('@')[0] if '@' in DATABASE_URL else '***'}@***")
        
        if test_connection():
            logger.info("✓ Database connection successful")
            return True
        else:
            logger.error("✗ Database connection failed")
            return False
            
    except Exception as e:
        logger.error(f"✗ Database check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_imports():
    """Check that all imports work"""
    logger.info("\n" + "=" * 60)
    logger.info("IMPORTS CHECK")
    logger.info("=" * 60)
    
    modules = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "psycopg2",
        "requests",
        "pydantic",
        "apscheduler"
    ]
    
    all_good = True
    for module in modules:
        try:
            __import__(module)
            logger.info(f"✓ {module}")
        except ImportError as e:
            logger.error(f"✗ {module}: {e}")
            all_good = False
    
    return all_good

def check_files():
    """Check that required files exist"""
    logger.info("\n" + "=" * 60)
    logger.info("FILES CHECK")
    logger.info("=" * 60)
    
    files = [
        "api.py",
        "db_models_complete.py",
        "cfb_ranking_system.py",
        "sync_service_complete.py",
        "requirements.txt"
    ]
    
    all_good = True
    for file in files:
        if os.path.exists(file):
            logger.info(f"✓ {file}")
        else:
            logger.error(f"✗ {file} - NOT FOUND")
            all_good = False
    
    return all_good

def main():
    """Run all checks"""
    logger.info("\n" + "=" * 60)
    logger.info("PRE-DEPLOYMENT CHECK")
    logger.info("=" * 60)
    
    checks = {
        "Files": check_files(),
        "Imports": check_imports(),
        "Environment": check_environment(),
        "Database": check_database()
    }
    
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    
    for name, result in checks.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {name}")
    
    all_passed = all(checks.values())
    
    if all_passed:
        logger.info("\n✓ ALL CHECKS PASSED - Ready to deploy!")
        return 0
    else:
        logger.error("\n✗ SOME CHECKS FAILED - Fix issues before deploying")
        return 1

if __name__ == "__main__":
    sys.exit(main())