"""
Pydantic models for Jira data structures
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CommentAuthor(BaseModel):
    """Author of a comment"""
    account_id: Optional[str] = Field(None, alias="accountId")
    active: bool = True
    display_name: str = Field(..., alias="displayName")
    email_address: Optional[str] = Field(None, alias="emailAddress")

    class Config:
        populate_by_name = True


class IssueComment(BaseModel):
    """Comment on a Jira issue"""
    id: str
    created_at: str = Field(..., alias="createdAt")
    updated_at: str = Field(..., alias="updatedAt")
    author: CommentAuthor
    body: dict = {}

    class Config:
        populate_by_name = True


class JiraIssue(BaseModel):
    """Jira Issue data structure"""
    id: str
    key: str
    summary: str
    issue_type: str = Field(..., alias="issueType")
    status: str
    assignee: Optional[str] = None
    url: str
    web_url: str = Field(..., alias="webUrl")
    project_id: str = Field(..., alias="projectId")
    project_key: str = Field(..., alias="projectKey")
    project_name: str = Field(..., alias="projectName")
    created_at: str = Field(..., alias="createdAt")
    updated_at: str = Field(..., alias="updatedAt")
    comments: List[IssueComment] = []

    class Config:
        populate_by_name = True


class JiraProject(BaseModel):
    """Jira Project data structure"""
    id: str
    key: str
    name: str
    url: str
    project_type_key: str = Field(..., alias="projectTypeKey")
    web_url: str = Field(..., alias="webUrl")

    class Config:
        populate_by_name = True


class JiraIssueType(BaseModel):
    """Jira Issue Type"""
    id: str
    name: str
    description: Optional[str] = None
    icon_url: Optional[str] = Field(None, alias="iconUrl")
    subtask: bool = False

    class Config:
        populate_by_name = True


class CreateIssueRequest(BaseModel):
    """Request body for creating a Jira issue"""
    project_key: str = Field(..., alias="projectKey", description="Project key (e.g., 'PROJ')")
    summary: str = Field(..., description="Issue summary/title")
    description: Optional[str] = Field(None, description="Issue description")
    issue_type: str = Field("Task", alias="issueType", description="Issue type name")
    assignee_id: Optional[str] = Field(None, alias="assigneeId", description="Assignee account ID")
    labels: List[str] = Field(default_factory=list, description="Labels to add")

    class Config:
        populate_by_name = True


class CreateIssueResponse(BaseModel):
    """Response from creating a Jira issue"""
    id: str
    key: str
    self_url: str = Field(..., alias="self")

    class Config:
        populate_by_name = True


class ConnectionStatus(BaseModel):
    """Nango connection status"""
    connected: bool
    connection_id: Optional[str] = Field(None, alias="connectionId")
    provider: str = "jira"
    cloud_id: Optional[str] = Field(None, alias="cloudId")
    account_id: Optional[str] = Field(None, alias="accountId")
    user_email: Optional[str] = Field(None, alias="userEmail")
    user_name: Optional[str] = Field(None, alias="userName")
    error: Optional[str] = None

    class Config:
        populate_by_name = True


class JiraUser(BaseModel):
    """Current Jira user info"""
    account_id: str = Field(..., alias="accountId")
    email_address: Optional[str] = Field(None, alias="emailAddress")
    display_name: str = Field(..., alias="displayName")
    active: bool = True

    class Config:
        populate_by_name = True


# MongoDB Document Models
class ConnectionDocument(BaseModel):
    """MongoDB document for storing connection info"""
    connection_id: str
    provider: str = "jira"
    cloud_id: Optional[str] = None
    account_id: Optional[str] = None
    user_email: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class IssueHistoryDocument(BaseModel):
    """MongoDB document for issue creation history"""
    connection_id: str
    issue_id: str
    issue_key: str
    project_key: str
    summary: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
