"""
Slack interaction handlers for GKE Resource Optimizer.

This module contains handlers for the interactive components like buttons, 
modals, and select menus in the Slack interface.
"""

import logging
import json
from slack_bolt import App
from services.k8s import modify_workload_resources, get_workload_details
from services.ai import generate_change_justification
from services.jira import create_jira_ticket
from services.slack_notifier import notify_resource_change
from views.slack_blocks import (
    build_confirmation_modal_blocks,
    build_resource_modification_modal_blocks
)

logger = logging.getLogger(__name__)

def register_slack_interactions(app: App) -> None:
    """Register all Slack interaction handlers"""
    # Button click handlers
    app.action("optimize_workload_btn")(handle_optimize_workload_button)
    app.action("confirm_optimization_btn")(handle_confirm_optimization)
    app.action("cancel_optimization_btn")(handle_cancel_optimization)
    
    # Select menu handlers
    app.action("select_namespace")(handle_namespace_selection)
    app.action("select_workload")(handle_workload_selection)
    
    # View submission handlers
    app.view("resource_modification_modal")(handle_resource_modification_submission)
    app.view("confirmation_modal")(handle_confirmation_submission)

def handle_optimize_workload_button(ack, body, client, logger):
    """Handle the 'Optimize Workload' button click"""
    # Acknowledge the button click immediately
    ack()
    
    try:
        user_id = body["user"]["id"]
        trigger_id = body["trigger_id"]
        
        # Extract workload information from the button action
        action = body["actions"][0]
        value = json.loads(action["value"])
        namespace = value.get("namespace")
        workload_name = value.get("workload")
        
        logger.info(f"Optimize workload button clicked by {user_id} for {namespace}/{workload_name}")
        
        # Get current workload details
        workload_details = get_workload_details(namespace, workload_name)
        
        # Open a modal for resource modification
        client.views_open(
            trigger_id=trigger_id,
            view={
                "type": "modal",
                "callback_id": "resource_modification_modal",
                "title": {"type": "plain_text", "text": "Optimize Resources"},
                "submit": {"type": "plain_text", "text": "Preview Changes"},
                "close": {"type": "plain_text", "text": "Cancel"},
                "private_metadata": json.dumps({
                    "namespace": namespace,
                    "workload": workload_name
                }),
                "blocks": build_resource_modification_modal_blocks(namespace, workload_name, workload_details)
            }
        )
    except Exception as e:
        logger.error(f"Error handling optimize workload button: {e}")
        client.chat_postEphemeral(
            channel=body["channel"]["id"],
            user=user_id,
            text=f"Sorry, there was an error opening the resource modification form: {str(e)}"
        )

def handle_namespace_selection(ack, body, client, logger):
    """Handle the namespace selection dropdown"""
    # Acknowledge the selection immediately
    ack()
    
    # Implementation would update available workloads based on namespace

def handle_workload_selection(ack, body, client, logger):
    """Handle the workload selection dropdown"""
    # Acknowledge the selection immediately
    ack()
    
    # Implementation would update workload details display

def handle_resource_modification_submission(ack, body, client, view, logger):
    """Handle the submission of the resource modification form"""
    # Acknowledge the submission immediately
    ack()
    
    try:
        user_id = body["user"]["id"]
        
        # Extract values from the form
        values = view["state"]["values"]
        metadata = json.loads(view["private_metadata"])
        namespace = metadata["namespace"]
        workload_name = metadata["workload"]
        
        # Extract CPU and memory resource values from form
        cpu_request = values["cpu_request_block"]["cpu_request"]["value"]
        cpu_limit = values["cpu_limit_block"]["cpu_limit"]["value"]
        memory_request = values["memory_request_block"]["memory_request"]["value"]
        memory_limit = values["memory_limit_block"]["memory_limit"]["value"]
        
        # Get current workload details for comparison
        current_resources = get_workload_details(namespace, workload_name)
        
        # Generate justification for the change
        justification = generate_change_justification(
            namespace, 
            workload_name, 
            current_resources, 
            {
                "cpu_request": cpu_request,
                "cpu_limit": cpu_limit,
                "memory_request": memory_request,
                "memory_limit": memory_limit
            }
        )
        
        # Show confirmation modal
        client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "confirmation_modal",
                "title": {"type": "plain_text", "text": "Confirm Resource Changes"},
                "submit": {"type": "plain_text", "text": "Apply Changes"},
                "close": {"type": "plain_text", "text": "Cancel"},
                "private_metadata": json.dumps({
                    "namespace": namespace,
                    "workload": workload_name,
                    "cpu_request": cpu_request,
                    "cpu_limit": cpu_limit,
                    "memory_request": memory_request,
                    "memory_limit": memory_limit,
                    "justification": justification
                }),
                "blocks": build_confirmation_modal_blocks(
                    namespace, 
                    workload_name, 
                    current_resources,
                    {
                        "cpu_request": cpu_request,
                        "cpu_limit": cpu_limit,
                        "memory_request": memory_request,
                        "memory_limit": memory_limit
                    },
                    justification
                )
            }
        )
    except Exception as e:
        logger.error(f"Error handling resource modification submission: {e}")
        # Send an ephemeral message to the user
        client.chat_postEphemeral(
            channel=body["user"]["id"],  # DM the user
            user=user_id,
            text=f"Sorry, there was an error processing your resource modification: {str(e)}"
        )

def handle_confirmation_submission(ack, body, client, view, logger):
    """Handle the submission of the confirmation modal"""
    # Acknowledge the submission immediately
    ack()
    
    try:
        user_id = body["user"]["id"]
        
        # Extract values from the form metadata
        metadata = json.loads(view["private_metadata"])
        namespace = metadata["namespace"]
        workload_name = metadata["workload"]
        cpu_request = metadata["cpu_request"]
        cpu_limit = metadata["cpu_limit"]
        memory_request = metadata["memory_request"]
        memory_limit = metadata["memory_limit"]
        justification = metadata["justification"]
        
        # Apply the resource changes
        modify_workload_resources(
            namespace, 
            workload_name, 
            cpu_request, 
            cpu_limit, 
            memory_request, 
            memory_limit
        )
        
        # Create Jira ticket
        jira_ticket = create_jira_ticket(
            namespace,
            workload_name,
            {
                "cpu_request": cpu_request,
                "cpu_limit": cpu_limit,
                "memory_request": memory_request,
                "memory_limit": memory_limit
            },
            justification,
            user_id
        )
        
        # Notify the channel
        notification_channel = body.get("user", {}).get("team_id")  # Default to the team
        notify_resource_change(
            client,
            notification_channel,
            namespace,
            workload_name,
            justification,
            jira_ticket
        )
        
        # Send confirmation to the user
        client.chat_postMessage(
            channel=user_id,
            text=f"✅ Successfully updated resources for {namespace}/{workload_name}.\n"
                 f"Jira ticket created: {jira_ticket.key}\n"
                 f"Notification sent to the team channel."
        )
    except Exception as e:
        logger.error(f"Error handling confirmation submission: {e}")
        # Send an ephemeral message to the user
        client.chat_postMessage(
            channel=user_id,
            text=f"❌ Sorry, there was an error applying the resource changes: {str(e)}"
        )

def handle_cancel_optimization(ack, body, logger):
    """Handle the 'Cancel' button click in optimization flow"""
    # Acknowledge the button click immediately
    ack()
    
    logger.info(f"Optimization cancelled by user {body['user']['id']}") 