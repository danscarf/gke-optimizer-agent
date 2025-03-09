"""
Jira service for GKE Resource Optimizer.

This module contains functions for creating Jira tickets to document resource changes.
"""

import os
import logging
from typing import Dict, Any
from jira import JIRA

logger = logging.getLogger(__name__)

def get_jira_client() -> JIRA:
    """Initialize and return a Jira client."""
    jira_url = os.environ.get("JIRA_URL")
    jira_username = os.environ.get("JIRA_USERNAME")
    jira_api_token = os.environ.get("JIRA_API_TOKEN")
    
    if not all([jira_url, jira_username, jira_api_token]):
        logger.error("Missing required environment variables for Jira integration")
        raise ValueError("Missing required environment variables for Jira integration")
    
    return JIRA(
        server=jira_url,
        basic_auth=(jira_username, jira_api_token)
    )

def create_jira_ticket(
    namespace: str,
    workload_name: str,
    new_resources: Dict[str, Any],
    justification: str,
    slack_user_id: str
) -> Any:
    """
    Create a Jira ticket for a resource change.
    
    Args:
        namespace: The namespace of the workload
        workload_name: The name of the workload
        new_resources: Dictionary with new resource requests and limits
        justification: The justification for the changes
        slack_user_id: The Slack user ID who initiated the change
        
    Returns:
        The created Jira issue
    """
    try:
        jira = get_jira_client()
        project_key = os.environ.get("JIRA_PROJECT")
        
        if not project_key:
            logger.error("Missing JIRA_PROJECT environment variable")
            raise ValueError("Missing JIRA_PROJECT environment variable")
        
        # Create the ticket summary
        summary = f"GKE Resource Optimization: {namespace}/{workload_name}"
        
        # Create the ticket description
        description = f"""
        *GKE Resource Optimization*
        
        *Workload*: {namespace}/{workload_name}
        
        *New Resources*:
        - CPU Request: {new_resources['cpu_request']}
        - CPU Limit: {new_resources['cpu_limit']}
        - Memory Request: {new_resources['memory_request']}
        - Memory Limit: {new_resources['memory_limit']}
        
        *Justification*:
        {justification}
        
        *Initiated by*: {slack_user_id}
        """
        
        # Create the issue
        issue_dict = {
            'project': {'key': project_key},
            'summary': summary,
            'description': description,
            'issuetype': {'name': 'Task'},
            'labels': ['gke-optimization', 'automated']
        }
        
        new_issue = jira.create_issue(fields=issue_dict)
        logger.info(f"Created Jira ticket: {new_issue.key}")
        
        return new_issue
    except Exception as e:
        logger.error(f"Error creating Jira ticket: {e}")
        
        # Create a mock issue for development or when Jira integration fails
        class MockIssue:
            def __init__(self, key):
                self.key = key
        
        return MockIssue(f"MOCK-{hash(namespace + workload_name) % 1000}") 