"""
Slack command handlers for GKE Resource Optimizer.

This module contains handlers for the slack slash commands:
- /optimize-resources
- /resource-usage
- /suggest-workloads
"""

import logging
from slack_bolt import App
from services.nlu import process_natural_language
from services.k8s import get_resource_usage
from services.recommender import suggest_optimization_candidates
from views.slack_blocks import (
    build_optimization_request_blocks, 
    build_resource_usage_blocks,
    build_workload_suggestion_blocks
)

logger = logging.getLogger(__name__)

def register_slack_commands(app: App) -> None:
    """Register all Slack command handlers"""
    app.command("/optimize-resources")(handle_optimize_resources)
    app.command("/resource-usage")(handle_resource_usage)
    app.command("/suggest-workloads")(handle_suggest_workloads)

def handle_optimize_resources(ack, command, client, logger):
    """
    Handle the /optimize-resources command
    
    This command initiates the resource optimization workflow.
    It accepts natural language input like:
    "/optimize-resources Reduce memory for my-app"
    """
    # Acknowledge the command request immediately
    ack()
    
    try:
        user_id = command["user_id"]
        channel_id = command["channel_id"]
        text = command["text"]
        
        logger.info(f"Optimize resources request from {user_id}: {text}")
        
        # Process the natural language input
        if text:
            # Extract intent and entities using NLU service
            intent, entities = process_natural_language(text)
            logger.info(f"Processed NL input - Intent: {intent}, Entities: {entities}")
        else:
            intent, entities = None, {}
        
        # Build the interactive message blocks
        blocks = build_optimization_request_blocks(intent, entities)
        
        # Send the response message
        client.chat_postMessage(
            channel=channel_id,
            blocks=blocks,
            text="Resource Optimization Request"
        )
    except Exception as e:
        logger.error(f"Error handling optimize resources command: {e}")
        client.chat_postMessage(
            channel=channel_id,
            text=f"Sorry, there was an error processing your request: {str(e)}"
        )

def handle_resource_usage(ack, command, client, logger):
    """
    Handle the /resource-usage command
    
    This command displays resource usage trends for a specified workload.
    """
    # Acknowledge the command request immediately
    ack()
    
    try:
        user_id = command["user_id"]
        channel_id = command["channel_id"]
        text = command["text"]
        
        logger.info(f"Resource usage request from {user_id}: {text}")
        
        if not text:
            client.chat_postMessage(
                channel=channel_id,
                text="Please specify a workload name. Usage: `/resource-usage [namespace/]deployment-name`"
            )
            return
        
        # Parse the workload name and namespace
        parts = text.split("/", 1)
        if len(parts) == 1:
            namespace = "default"
            workload_name = parts[0]
        else:
            namespace = parts[0]
            workload_name = parts[1]
        
        # Get resource usage data
        usage_data = get_resource_usage(namespace, workload_name)
        
        # Build the resource usage message blocks
        blocks = build_resource_usage_blocks(namespace, workload_name, usage_data)
        
        # Send the response message
        client.chat_postMessage(
            channel=channel_id,
            blocks=blocks,
            text=f"Resource usage for {namespace}/{workload_name}"
        )
    except Exception as e:
        logger.error(f"Error handling resource usage command: {e}")
        client.chat_postMessage(
            channel=channel_id,
            text=f"Sorry, there was an error retrieving resource usage: {str(e)}"
        )

def handle_suggest_workloads(ack, command, client, logger):
    """
    Handle the /suggest-workloads command
    
    This command suggests workloads that are good candidates for optimization.
    """
    # Acknowledge the command request immediately
    ack()
    
    try:
        user_id = command["user_id"]
        channel_id = command["channel_id"]
        
        logger.info(f"Workload suggestion request from {user_id}")
        
        # Get optimization candidates
        candidates = suggest_optimization_candidates()
        
        # Build the workload suggestion message blocks
        blocks = build_workload_suggestion_blocks(candidates)
        
        # Send the response message
        client.chat_postMessage(
            channel=channel_id,
            blocks=blocks,
            text="Suggested workloads for optimization"
        )
    except Exception as e:
        logger.error(f"Error handling suggest workloads command: {e}")
        client.chat_postMessage(
            channel=channel_id,
            text=f"Sorry, there was an error suggesting workloads: {str(e)}"
        ) 