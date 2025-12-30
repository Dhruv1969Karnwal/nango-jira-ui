"""
Jira API service for project and issue operations
"""
import httpx
from typing import List, Optional, Dict, Any
from services.nango_service import nango_service


class JiraService:
    """Service for Jira-specific operations via Nango proxy"""
    
    async def get_myself(self, connection_id: str, cloud_id: str) -> Optional[dict]:
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
            return {
                "account_id": data.get("accountId"),
                "email_address": data.get("emailAddress"),
                "display_name": data.get("displayName"),
                "active": data.get("active", True)
            }
        except Exception:
            return None
    
    async def get_projects(self, connection_id: str, cloud_id: str) -> List[dict]:
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
                projects.append({
                    "id": p["id"],
                    "key": p["key"],
                    "name": p["name"],
                    "url": p.get("self", ""),
                    "project_type_key": p.get("projectTypeKey", "software"),
                    "web_url": f"https://atlassian.net/browse/{p['key']}"
                })
            return projects
        except Exception:
            return []
    
    async def get_issues(
        self, 
        connection_id: str, 
        cloud_id: str,
        project_key: Optional[str] = None,
        max_results: int = 50,
        jql: Optional[str] = None
    ) -> List[dict]:
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
                
                issues.append({
                    "id": issue["id"],
                    "key": issue["key"],
                    "summary": fields.get("summary", ""),
                    "issue_type": issue_type.get("name", "Task"),
                    "status": status.get("name", "Unknown"),
                    "assignee": assignee.get("displayName") if assignee else None,
                    "url": issue.get("self", ""),
                    "web_url": f"https://atlassian.net/browse/{issue['key']}",
                    "project_id": project.get("id", ""),
                    "project_key": project.get("key", ""),
                    "project_name": project.get("name", ""),
                    "created_at": fields.get("created", ""),
                    "updated_at": fields.get("updated", ""),
                    "comments": comments
                })
            
            return issues
        except httpx.HTTPStatusError:
            raise
        except Exception:
            return []
    
    async def get_issue_types(
        self, 
        connection_id: str, 
        cloud_id: str,
        project_id: str
    ) -> List[dict]:
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
                issue_types.append({
                    "id": it["id"],
                    "name": it["name"],
                    "description": it.get("description"),
                    "icon_url": it.get("iconUrl"),
                    "subtask": it.get("subtask", False)
                })
            return issue_types
        except Exception:
            return []
    
    async def create_issue(
        self,
        connection_id: str,
        cloud_id: str,
        request: dict
    ) -> Optional[dict]:
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
                    "project": {"key": request["projectKey"]},
                    "summary": request["summary"],
                    "issuetype": {"name": request["issueType"]}
                }
            }

            # Add optional fields
            if request.get("description"):
                issue_data["fields"]["description"] = {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": request["description"]}
                            ]
                        }
                    ]
                }

            if request.get("assignee_id"):
                issue_data["fields"]["assignee"] = {"accountId": request["assignee_id"]}

            if request.get("labels"):
                issue_data["fields"]["labels"] = request["labels"]
            
            data = await nango_service.proxy_post(connection_id, endpoint, issue_data)

            return {
                "id": data["id"],
                "key": data["key"],
                "self_url": data["self"]
            }
        except Exception:
            raise


# Singleton instance
jira_service = JiraService()
