"""
API routes for Jira operations
"""
from fastapi import APIRouter, HTTPException, Query, Request
from typing import Optional, List, Dict, Any
from datetime import datetime
from services.nango_service import nango_service
from services.jira_service import jira_service

router = APIRouter(prefix="/api", tags=["jira"])


@router.post("/connection")
async def save_connection(request: Request, data: Dict[str, Any]):
    """
    Save or update a Nango connection in MongoDB
    """
    connection_id = data.get("connectionId")
    if not connection_id:
        raise HTTPException(status_code=400, detail="Missing connectionId")
    
    try:
        # Verify with Nango
        connection = await nango_service.get_connection(connection_id)
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found in Nango")

        config = connection.get("connection_config", {})
        cloud_id = config.get("cloudId")
        account_id = config.get("accountId")
        
        # Get user info from Jira
        user_email = None
        user_name = None
        if cloud_id:
            user = await jira_service.get_myself(connection_id, cloud_id)
            if user:
                user_email = user["email_address"]
                user_name = user["display_name"]

        # Save to MongoDB
        db = request.app.state.mongodb
        connection_doc = {
            "connection_id": connection_id,
            "provider": "jira",
            "cloud_id": cloud_id,
            "account_id": account_id,
            "user_email": user_email,
            "user_name": user_name,
            "updated_at": datetime.utcnow()
        }

        await db.connections.update_one(
            {"connection_id": connection_id},
            {"$set": connection_doc, "$setOnInsert": {"created_at": datetime.utcnow()}},
            upsert=True
        )
        
        return {
            "connected": True,
            "connection_id": connection_id,
            "cloud_id": cloud_id,
            "account_id": account_id,
            "user_email": user_email,
            "user_name": user_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/connection/{connection_id}")
async def get_connection_status(request: Request, connection_id: str):
    """
    Check the status of a Jira connection
    """
    try:
        # First check MongoDB
        db = request.app.state.mongodb
        stored_conn = await db.connections.find_one({"connection_id": connection_id})
        
        # Even if stored, verify with Nango to ensure it's still alive
        connection = await nango_service.get_connection(connection_id)
        
        if not connection:
            return {
                "connected": False,
                "connection_id": connection_id,
                "error": "Connection not found in Nango"
            }
        
        config = connection.get("connection_config", {})
        cloud_id = config.get("cloudId")
        
        # If not in MongoDB but valid in Nango, we should probably return it as valid
        # but the frontend will be prompted to "register" it if it wants persistence
        
        user_email = stored_conn.get("user_email") if stored_conn else None
        user_name = stored_conn.get("user_name") if stored_conn else None
        
        if not user_email and cloud_id:
            try:
                user = await jira_service.get_myself(connection_id, cloud_id)
                if user:
                    user_email = user["email_address"]
                    user_name = user["display_name"]
            except Exception:
                pass
        
        return {
            "connected": True,
            "connection_id": connection_id,
            "cloud_id": cloud_id,
            "account_id": config.get("accountId"),
            "user_email": user_email,
            "user_name": user_name
        }
    except Exception as e:
        return {
            "connected": False,
            "connection_id": connection_id,
            "error": str(e)
        }


@router.get("/projects/{connection_id}")
async def get_projects(connection_id: str):
    """
    Fetch all Jira projects for a connection
    
    Args:
        connection_id: The Nango connection identifier
        
    Returns:
        List of Jira projects
    """
    cloud_id = await nango_service.get_cloud_id(connection_id)
    if not cloud_id:
        raise HTTPException(status_code=400, detail="Could not get Jira Cloud ID")
    
    projects = await jira_service.get_projects(connection_id, cloud_id)
    return projects


@router.get("/issues/{connection_id}")
async def get_issues(
    connection_id: str,
    project_key: Optional[str] = Query(None, description="Filter by project key"),
    max_results: int = Query(50, ge=1, le=100, description="Maximum results"),
    jql: Optional[str] = Query(None, description="JQL query string")
):
    """
    Fetch Jira issues
    """
    cloud_id = await nango_service.get_cloud_id(connection_id)
    if not cloud_id:
        raise HTTPException(status_code=400, detail="Could not get Jira Cloud ID")
    
    try:
        issues = await jira_service.get_issues(
            connection_id, 
            cloud_id, 
            project_key=project_key,
            max_results=max_results,
            jql=jql
        )
        return issues
    except Exception as e:
        # Rethrow as 500 so frontend knows something went wrong
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/issue-types/{connection_id}/{project_id}")
async def get_issue_types(connection_id: str, project_id: str):
    """
    Fetch issue types for a project
    
    Args:
        connection_id: The Nango connection identifier
        project_id: The Jira project ID
        
    Returns:
        List of issue types
    """
    cloud_id = await nango_service.get_cloud_id(connection_id)
    if not cloud_id:
        raise HTTPException(status_code=400, detail="Could not get Jira Cloud ID")
    
    issue_types = await jira_service.get_issue_types(connection_id, cloud_id, project_id)
    return issue_types







@router.post("/issues/{connection_id}")
async def create_issue(connection_id: str, request: dict):
    """
    Create a new Jira issue
    
    Args:
        connection_id: The Nango connection identifier
        request: Issue creation details
        
    Returns:
        Created issue details
    """
    cloud_id = await nango_service.get_cloud_id(connection_id)
    if not cloud_id:
        raise HTTPException(status_code=400, detail="Could not get Jira Cloud ID")
    
    try:
        result = await jira_service.create_issue(connection_id, cloud_id, request)
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create issue")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
