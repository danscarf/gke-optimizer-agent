"""
Slack notifier service for GKE Resource Optimizer.

This module contains functions for sending notifications about resource changes
to Slack channels.
"""

import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def notify_resource_change(
    slack_client,
    channel: str,
    namespace: str,
    workload_name: str,
    justification: str,
    jira_ticket: Any
) -> None:
    """
    Send a notification about a resource change to a Slack channel.
    
    Args:
        slack_client: The Slack client
        channel: The channel to send the notification to
        namespace: The namespace of the workload
        workload_name: The name of the workload
        justification: The justification for the changes
        jira_ticket: The Jira ticket object
    """
    notification_channel = os.environ.get("NOTIFICATION_CHANNEL", channel)
    
    try:
        # Create the notification message
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"GKE Resource Optimization: {namespace}/{workload_name}",
                    "emoji": True
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Jira Ticket:* <https://your-jira-url/browse/{jira_ticket.key}|{jira_ticket.key}>"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Justification:*\n{justification}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"This optimization was performed by the GKE Resource Optimizer."
                    }
                ]
            }
        ]
        
        # Send the notification
        slack_client.chat_postMessage(
            channel=notification_channel,
            blocks=blocks,
            text=f"GKE Resource Optimization: {namespace}/{workload_name}"
        )
        
        logger.info(f"Sent notification to channel {notification_channel}")
    except Exception as e:
        logger.error(f"Error sending Slack notification: {e}")
        
        # Try to send a simplified notification if the block format fails
        try:
            slack_client.chat_postMessage(
                channel=notification_channel,
                text=f"GKE Resource Optimization: {namespace}/{workload_name}\n"
                     f"Jira Ticket: {jira_ticket.key}\n"
                     f"Justification: {justification}"
            )
        except Exception as e2:
            logger.error(f"Error sending simplified Slack notification: {e2}") 