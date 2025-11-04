# api_enhanced_endpoints.py
# Add these endpoints to your existing api.py file

"""
Enhanced API endpoints for your College Football Rankings system.
These integrate seamlessly with your existing code structure.

INTEGRATION INSTRUCTIONS:
1. Add these imports at the top of api.py (if not already present):
   from sqlalchemy import text
   
2. Copy the endpoints below into your api.py file after your existing endpoints
   
3. Replace 'sync_service_complete' with your actual sync service import if different
"""

# ==================== ENHANCED SYNC ENDPOINTS ====================

@app.post("/admin/sync-all")
async def sync_all_data(
    season: int = Query(..., description="Season year (e.g., 2024)"),
    week: Optional[int] = Query(None, description="Specific week number (optional)"),
    include: Optional[str] = Query(
        None, 
        description="Comma-separated list: rankings,sp_ratings,fpi_ratings,records,lines,recruiting or 'all'"
    ),
    db: Session = Depends(get_db)
):
    """
    Comprehensive sync endpoint - sync multiple datasets at once
    
    Examples:
    - /admin/sync-all?season=2024&include=all
    - /admin/sync-all?season=2024&week=10&include=rankings,sp_ratings,lines
    - /admin/sync-all?season=2024&include=records,recruiting
    """
    try:
        api_key = os.getenv("CFBD_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="CFBD_API_KEY not configured")
        
        # Parse include parameter
        include_list = None
        if include:
            include_list = [item.strip() for item in include.split(",")]
        
        # Initialize sync service
        from sync_service_complete import CFBDataSyncService
        sync_service = CFBDataSyncService(api_key)
        
        # Run comprehensive sync
        result = sync_service.sync_all(db, season, week, include_list)
        
        return {
            "success": True,
            "season": season,
            "week": week,
            "datasets_synced": list(result["results"].keys()),
            "total_added": result["total_added"],
            "total_updated": result["total_updated"],
            "details": result["results"]
        }
        
    except Exception as e:
        logger.error(f"Sync all failed: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@app.post("/admin/sync/rankings")
async def sync_rankings(
    season: int = Query(..., description="Season year"),
    week: Optional[int] = Query(None, description="Specific week (optional)"),
    db: Session = Depends(get_db)
):
    """Sync AP Poll rankings"""
    try:
        api_key = os.getenv("CFBD_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="CFBD_API_KEY not configured")
        
        from sync_service_complete import CFBDataSyncService
        sync_service = CFBDataSyncService(api_key)
        result = sync_service.sync_ap_rankings(db, season, week)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Rankings sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"Rankings sync failed: {str(e)}")


@app.post("/admin/sync/sp-ratings")
async def sync_sp_ratings(
    season: int = Query(..., description="Season year"),
    week: Optional[int] = Query(None, description="Specific week (optional)"),
    db: Session = Depends(get_db)
):
    """Sync SP+ ratings"""
    try:
        api_key = os.getenv("CFBD_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="CFBD_API_KEY not configured")
        
        from sync_service_complete import CFBDataSyncService
        sync_service = CFBDataSyncService(api_key)
        result = sync_service.sync_sp_ratings(db, season, week)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SP+ sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"SP+ sync failed: {str(e)}")


@app.post("/admin/sync/fpi-ratings")
async def sync_fpi_ratings(
    season: int = Query(..., description="Season year"),
    week: Optional[int] = Query(None, description="Specific week (optional)"),
    db: Session = Depends(get_db)
):
    """Sync FPI ratings"""
    try:
        api_key = os.getenv("CFBD_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="CFBD_API_KEY not configured")
        
        from sync_service_complete import CFBDataSyncService
        sync_service = CFBDataSyncService(api_key)
        result = sync_service.sync_fpi_ratings(db, season, week)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"FPI sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"FPI sync failed: {str(e)}")


@app.post("/admin/sync/team-records")
async def sync_team_records(
    season: int = Query(..., description="Season year"),
    db: Session = Depends(get_db)
):
    """Sync team season records"""
    try:
        api_key = os.getenv("CFBD_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="CFBD_API_KEY not configured")
        
        from sync_service_complete import CFBDataSyncService
        sync_service = CFBDataSyncService(api_key)
        result = sync_service.sync_team_records(db, season)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Team records sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"Team records sync failed: {str(e)}")


@app.post("/admin/sync/betting-lines")
async def sync_betting_lines(
    season: int = Query(..., description="Season year"),
    week: Optional[int] = Query(None, description="Specific week (optional)"),
    db: Session = Depends(get_db)
):
    """Sync betting lines for games"""
    try:
        api_key = os.getenv("CFBD_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="CFBD_API_KEY not configured")
        
        from sync_service_complete import CFBDataSyncService
        sync_service = CFBDataSyncService(api_key)
        result = sync_service.sync_betting_lines(db, season, week)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Betting lines sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"Betting lines sync failed: {str(e)}")


@app.post("/admin/sync/recruiting")
async def sync_recruiting(
    season: int = Query(..., description="Season year"),
    db: Session = Depends(get_db)
):
    """Sync recruiting rankings"""
    try:
        api_key = os.getenv("CFBD_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="CFBD_API_KEY not configured")
        
        from sync_service_complete import CFBDataSyncService
        sync_service = CFBDataSyncService(api_key)
        result = sync_service.sync_recruiting_rankings(db, season)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Recruiting sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"Recruiting sync failed: {str(e)}")


# ==================== DATA RETRIEVAL ENDPOINTS ====================

@app.get("/rankings/ap")
async def get_ap_rankings(
    season: int = Query(..., description="Season year"),
    week: Optional[int] = Query(None, description="Specific week"),
    db: Session = Depends(get_db)
):
    """Get AP Poll rankings from database"""
    try:
        query = """
            SELECT season, week, season_type, team, rank, 
                   first_place_votes, points
            FROM ap_rankings
            WHERE season = :season
        """
        params = {"season": season}
        
        if week is not None:
            query += " AND week = :week"
            params["week"] = week
        
        query += " ORDER BY week DESC, rank ASC"
        
        result = db.execute(text(query), params)
        rankings = []
        
        for row in result:
            rankings.append({
                "season": row[0],
                "week": row[1],
                "season_type": row[2],
                "team": row[3],
                "rank": row[4],
                "first_place_votes": row[5],
                "points": row[6]
            })
        
        return {"rankings": rankings, "count": len(rankings)}
        
    except Exception as e:
        logger.error(f"Failed to retrieve AP rankings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve rankings: {str(e)}")


@app.get("/ratings/sp")
async def get_sp_ratings(
    season: int = Query(..., description="Season year"),
    week: Optional[int] = Query(None, description="Specific week"),
    db: Session = Depends(get_db)
):
    """Get SP+ ratings from database"""
    try:
        query = """
            SELECT season, week, team, rating, ranking,
                   offense_rating, defense_rating, special_teams_rating
            FROM team_sp_ratings
            WHERE season = :season
        """
        params = {"season": season}
        
        if week is not None:
            query += " AND week = :week"
            params["week"] = week
        
        query += " ORDER BY week DESC, ranking ASC"
        
        result = db.execute(text(query), params)
        ratings = []
        
        for row in result:
            ratings.append({
                "season": row[0],
                "week": row[1],
                "team": row[2],
                "rating": row[3],
                "ranking": row[4],
                "offense_rating": row[5],
                "defense_rating": row[6],
                "special_teams_rating": row[7]
            })
        
        return {"ratings": ratings, "count": len(ratings)}
        
    except Exception as e:
        logger.error(f"Failed to retrieve SP+ ratings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve SP+ ratings: {str(e)}")


@app.get("/ratings/fpi")
async def get_fpi_ratings(
    season: int = Query(..., description="Season year"),
    week: Optional[int] = Query(None, description="Specific week"),
    db: Session = Depends(get_db)
):
    """Get FPI ratings from database"""
    try:
        query = """
            SELECT season, week, team, fpi
            FROM team_fpi_ratings
            WHERE season = :season
        """
        params = {"season": season}
        
        if week is not None:
            query += " AND week = :week"
            params["week"] = week
        
        query += " ORDER BY week DESC, fpi DESC"
        
        result = db.execute(text(query), params)
        ratings = []
        
        for row in result:
            ratings.append({
                "season": row[0],
                "week": row[1],
                "team": row[2],
                "fpi": row[3]
            })
        
        return {"ratings": ratings, "count": len(ratings)}
        
    except Exception as e:
        logger.error(f"Failed to retrieve FPI ratings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve FPI ratings: {str(e)}")


@app.get("/team/{team_name}/details")
async def get_team_details(
    team_name: str,
    season: int = Query(..., description="Season year"),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive team details including:
    - Basic team info
    - Season record
    - Latest rankings (AP, SP+, FPI)
    - Recruiting ranking
    """
    try:
        # Basic team info
        team_info = db.query(Team).filter(Team.school == team_name).first()
        
        if not team_info:
            raise HTTPException(status_code=404, detail="Team not found")
        
        # Season record
        record_query = """
            SELECT total_wins, total_losses, total_ties,
                   conf_wins, conf_losses, home_wins, home_losses,
                   away_wins, away_losses
            FROM team_records
            WHERE team = :team AND season = :season
        """
        record = db.execute(text(record_query), {"team": team_name, "season": season}).fetchone()
        
        # Latest AP ranking
        ap_query = """
            SELECT rank, points, week
            FROM ap_rankings
            WHERE team = :team AND season = :season
            ORDER BY week DESC LIMIT 1
        """
        ap_rank = db.execute(text(ap_query), {"team": team_name, "season": season}).fetchone()
        
        # Latest SP+ rating
        sp_query = """
            SELECT rating, ranking, week, offense_rating, defense_rating, special_teams_rating
            FROM team_sp_ratings
            WHERE team = :team AND season = :season
            ORDER BY week DESC LIMIT 1
        """
        sp_rating = db.execute(text(sp_query), {"team": team_name, "season": season}).fetchone()
        
        # Latest FPI rating
        fpi_query = """
            SELECT fpi, week
            FROM team_fpi_ratings
            WHERE team = :team AND season = :season
            ORDER BY week DESC LIMIT 1
        """
        fpi_rating = db.execute(text(fpi_query), {"team": team_name, "season": season}).fetchone()
        
        # Recruiting ranking
        recruiting_query = """
            SELECT rank, points
            FROM recruiting_teams
            WHERE team = :team AND year = :season
        """
        recruiting = db.execute(text(recruiting_query), {"team": team_name, "season": season}).fetchone()
        
        return {
            "team": team_name,
            "season": season,
            "conference": team_info.conference,
            "mascot": team_info.mascot,
            "colors": {
                "primary": team_info.color,
                "secondary": team_info.alt_color
            },
            "record": {
                "overall": f"{record[0]}-{record[1]}" if record else "N/A",
                "conference": f"{record[3]}-{record[4]}" if record and len(record) > 4 else "N/A",
                "home": f"{record[5]}-{record[6]}" if record and len(record) > 6 else "N/A",
                "away": f"{record[7]}-{record[8]}" if record and len(record) > 8 else "N/A"
            } if record else None,
            "rankings": {
                "ap_poll": {
                    "rank": ap_rank[0] if ap_rank else None,
                    "points": ap_rank[1] if ap_rank else None,
                    "week": ap_rank[2] if ap_rank else None
                } if ap_rank else None,
                "sp_plus": {
                    "rating": sp_rating[0] if sp_rating else None,
                    "ranking": sp_rating[1] if sp_rating else None,
                    "week": sp_rating[2] if sp_rating else None,
                    "offense": sp_rating[3] if sp_rating and len(sp_rating) > 3 else None,
                    "defense": sp_rating[4] if sp_rating and len(sp_rating) > 4 else None,
                    "special_teams": sp_rating[5] if sp_rating and len(sp_rating) > 5 else None
                } if sp_rating else None,
                "fpi": {
                    "rating": fpi_rating[0] if fpi_rating else None,
                    "week": fpi_rating[1] if fpi_rating else None
                } if fpi_rating else None,
                "recruiting": {
                    "rank": recruiting[0] if recruiting else None,
                    "points": recruiting[1] if recruiting else None
                } if recruiting else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve team details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve team details: {str(e)}")


@app.get("/records/{season}")
async def get_team_records(
    season: int,
    conference: Optional[str] = Query(None, description="Filter by conference"),
    db: Session = Depends(get_db)
):
    """Get team records for a season"""
    try:
        query = """
            SELECT r.team, r.total_wins, r.total_losses, r.total_ties,
                   r.conf_wins, r.conf_losses, r.home_wins, r.home_losses,
                   r.away_wins, r.away_losses, t.conference
            FROM team_records r
            LEFT JOIN teams t ON r.team = t.school
            WHERE r.season = :season
        """
        params = {"season": season}
        
        if conference:
            query += " AND t.conference = :conference"
            params["conference"] = conference
        
        query += " ORDER BY r.total_wins DESC, r.total_losses ASC"
        
        result = db.execute(text(query), params)
        records = []
        
        for row in result:
            records.append({
                "team": row[0],
                "overall": f"{row[1]}-{row[2]}" + (f"-{row[3]}" if row[3] else ""),
                "conference_record": f"{row[4]}-{row[5]}",
                "home": f"{row[6]}-{row[7]}",
                "away": f"{row[8]}-{row[9]}",
                "conference": row[10]
            })
        
        return {"season": season, "records": records, "count": len(records)}
        
    except Exception as e:
        logger.error(f"Failed to retrieve team records: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve team records: {str(e)}")
