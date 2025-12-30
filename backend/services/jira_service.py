"""
Jira API service for project and issue operations
"""
from typing import List, Optional, Dict, Any
from services.nango_service import nango_service
from models import (
    JiraProject, 
    JiraIssue, 
    JiraIssueType, 
    JiraUser,
    CreateIssueRequest,
    CreateIssueResponse
)


class JiraService:
    """Service for Jira-specific operations via Nango proxy"""
    
    async def get_myself(self, connection_id: str, cloud_id: str) -> Optional[JiraUser]:
        """
        Get current user information
        
        Args:
            connection_id: Nango connection ID
            cloud_id: Jira Cloud ID
            
        Returns:
            Current user info
        """
        try:
            endpoint = f"/ex/jira/{cloud_id}/rest/api/3/myself"
            data = await nango_service.proxy_get(connection_id, endpoint)
            return JiraUser(
                accountId=data.get("accountId"),
                emailAddress=data.get("emailAddress"),
                displayName=data.get("displayName"),
                active=data.get("active", True)
            )
        except Exception as e:
            print(f"Error getting current user: {e}")
            return None
    
    async def get_projects(self, connection_id: str, cloud_id: str) -> List[JiraProject]:
        """
        Fetch all accessible Jira projects
        
        Args:
            connection_id: Nango connection ID
            cloud_id: Jira Cloud ID
            
        Returns:
            List of Jira projects
        """
        try:
            endpoint = f"/ex/jira/{cloud_id}/rest/api/3/project/search"
            data = await nango_service.proxy_get(
                connection_id, 
                endpoint,
                params={"maxResults": 50, "expand": "description"}
            )
            
            projects = []
            for p in data.get("values", []):
                projects.append(JiraProject(
                    id=p["id"],
                    key=p["key"],
                    name=p["name"],
                    url=p.get("self", ""),
                    projectTypeKey=p.get("projectTypeKey", "software"),
                    webUrl=f"https://atlassian.net/browse/{p['key']}"
                ))
            return projects
        except Exception as e:
            print(f"Error fetching projects: {e}")
            return []
    
    async def get_issues(
        self, 
        connection_id: str, 
        cloud_id: str,
        project_key: Optional[str] = None,
        max_results: int = 50,
        jql: Optional[str] = None
    ) -> List[JiraIssue]:
        """
        Fetch Jira issues
        
        Args:
            connection_id: Nango connection ID
            cloud_id: Jira Cloud ID
            project_key: Optional project key to filter
            max_results: Maximum number of results
            jql: Optional JQL query
            
        Returns:
            List of Jira issues
        """
        try:
            endpoint = f"/ex/jira/{cloud_id}/rest/api/3/search/jql"
            
            # Build JQL query
            query_parts = []
            if project_key:
                query_parts.append(f"project = '{project_key}'")
            if jql:
                query_parts.append(jql)
            
            # The /search/jql endpoint requires at least one restriction to be 'bounded'
            if not query_parts:
                query_parts.append("created is not null")
            
            jql_query = " AND ".join(query_parts) + " ORDER BY created DESC"
            
            data = await nango_service.proxy_get(
                connection_id,
                endpoint,
                params={
                    "jql": jql_query,
                    "maxResults": max_results,
                    "fields": "summary,status,assignee,issuetype,project,created,updated"
                }
            )
            
            issues = []
            for issue in data.get("issues", []):
                fields = issue.get("fields", {})
                project = fields.get("project", {})
                assignee = fields.get("assignee")
                issue_type = fields.get("issuetype", {})
                status = fields.get("status", {})
                
                # Simplified comments handling (optional)
                comments = []
                if "comment" in fields:
                    comment_data = fields.get("comment", {})
                    for c in comment_data.get("comments", []):
                        author = c.get("author", {})
                        comments.append({
                            "id": c.get("id"),
                            "createdAt": c.get("created"),
                            "updatedAt": c.get("updated"),
                            "author": {
                                "accountId": author.get("accountId"),
                                "active": author.get("active", True),
                                "displayName": author.get("displayName", "Unknown"),
                                "emailAddress": author.get("emailAddress")
                            },
                            "body": c.get("body", {})
                        })
                
                issues.append(JiraIssue(
                    id=issue["id"],
                    key=issue["key"],
                    summary=fields.get("summary", ""),
                    issueType=issue_type.get("name", "Task"),
                    status=status.get("name", "Unknown"),
                    assignee=assignee.get("displayName") if assignee else None,
                    url=issue.get("self", ""),
                    webUrl=f"https://atlassian.net/browse/{issue['key']}",
                    projectId=project.get("id", ""),
                    projectKey=project.get("key", ""),
                    projectName=project.get("name", ""),
                    createdAt=fields.get("created", ""),
                    updatedAt=fields.get("updated", ""),
                    comments=comments
                ))
            
            return issues
        except httpx.HTTPStatusError as e:
            print(f"JIRA PROXY ERROR (HTTP {e.response.status_code}): {e.response.text}")
            raise
        except Exception as e:
            print(f"Error fetching issues: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def get_issue_types(
        self, 
        connection_id: str, 
        cloud_id: str,
        project_id: str
    ) -> List[JiraIssueType]:
        """
        Fetch issue types for a project
        
        Args:
            connection_id: Nango connection ID
            cloud_id: Jira Cloud ID
            project_id: Project ID
            
        Returns:
            List of issue types
        """
        try:
            endpoint = f"/ex/jira/{cloud_id}/rest/api/3/issuetype/project"
            data = await nango_service.proxy_get(
                connection_id,
                endpoint,
                params={"projectId": project_id}
            )
            
            issue_types = []
            for it in data:
                issue_types.append(JiraIssueType(
                    id=it["id"],
                    name=it["name"],
                    description=it.get("description"),
                    iconUrl=it.get("iconUrl"),
                    subtask=it.get("subtask", False)
                ))
            return issue_types
        except Exception as e:
            print(f"Error fetching issue types: {e}")
            return []
    
    async def create_issue(
        self,
        connection_id: str,
        cloud_id: str,
        request: CreateIssueRequest
    ) -> Optional[CreateIssueResponse]:
        """
        Create a new Jira issue
        
        Args:
            connection_id: Nango connection ID
            cloud_id: Jira Cloud ID
            request: Issue creation request
            
        Returns:
            Created issue response
        """
        try:
            endpoint = f"/ex/jira/{cloud_id}/rest/api/3/issue"
            
            # Build issue data
            issue_data: Dict[str, Any] = {
                "fields": {
                    "project": {"key": request.project_key},
                    "summary": request.summary,
                    "issuetype": {"name": request.issue_type}
                }
            }
            
            # Add optional fields
            if request.description:
                issue_data["fields"]["description"] = {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": request.description}
                            ]
                        }
                    ]
                }
            
            if request.assignee_id:
                issue_data["fields"]["assignee"] = {"accountId": request.assignee_id}
            
            if request.labels:
                issue_data["fields"]["labels"] = request.labels
            
            data = await nango_service.proxy_post(connection_id, endpoint, issue_data)
            
            return CreateIssueResponse(
                id=data["id"],
                key=data["key"],
                self=data["self"]
            )
        except Exception as e:
            print(f"Error creating issue: {e}")
            raise


# Singleton instance
jira_service = JiraService()
