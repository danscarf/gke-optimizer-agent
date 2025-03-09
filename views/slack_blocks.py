"""
Slack Block Kit templates for GKE Resource Optimizer.

This module contains functions for building interactive Slack message blocks.
"""

import json
from typing import Dict, Any, List, Optional

def build_optimization_request_blocks(intent: Optional[str], entities: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Build Slack blocks for an optimization request.
    
    Args:
        intent: The extracted intent from NLU
        entities: The extracted entities from NLU
        
    Returns:
        A list of Slack blocks
    """
    workload_name = entities.get("workload_name", "")
    namespace = entities.get("namespace", "default")
    resource_type = entities.get("resource_type", "both")
    direction = entities.get("direction", "")
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "GKE Resource Optimization",
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Let's optimize your GKE workload resources. Please provide the following details:"
            }
        },
        {
            "type": "divider"
        }
    ]
    
    # Input for namespace
    blocks.append({
        "type": "input",
        "block_id": "namespace_block",
        "element": {
            "type": "plain_text_input",
            "action_id": "namespace_input",
            "initial_value": namespace if namespace else "default",
            "placeholder": {
                "type": "plain_text",
                "text": "Enter the namespace"
            }
        },
        "label": {
            "type": "plain_text",
            "text": "Namespace",
            "emoji": True
        }
    })
    
    # Input for workload name
    blocks.append({
        "type": "input",
        "block_id": "workload_block",
        "element": {
            "type": "plain_text_input",
            "action_id": "workload_input",
            "initial_value": workload_name if workload_name else "",
            "placeholder": {
                "type": "plain_text",
                "text": "Enter the workload name"
            }
        },
        "label": {
            "type": "plain_text",
            "text": "Workload Name",
            "emoji": True
        }
    })
    
    # Radio buttons for resource type
    blocks.append({
        "type": "section",
        "block_id": "resource_type_block",
        "text": {
            "type": "mrkdwn",
            "text": "*Resource Type*"
        },
        "accessory": {
            "type": "radio_buttons",
            "action_id": "resource_type_selection",
            "initial_option": {
                "value": resource_type,
                "text": {
                    "type": "plain_text",
                    "text": resource_type.capitalize()
                }
            } if resource_type in ["cpu", "memory", "both"] else None,
            "options": [
                {
                    "value": "cpu",
                    "text": {
                        "type": "plain_text",
                        "text": "CPU Only"
                    }
                },
                {
                    "value": "memory",
                    "text": {
                        "type": "plain_text",
                        "text": "Memory Only"
                    }
                },
                {
                    "value": "both",
                    "text": {
                        "type": "plain_text",
                        "text": "Both CPU and Memory"
                    }
                }
            ]
        }
    })
    
    # Buttons for getting workload or fetching suggestions
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Get Workload",
                    "emoji": True
                },
                "value": json.dumps({
                    "action": "get_workload",
                    "namespace": namespace,
                    "workload": workload_name
                }),
                "action_id": "get_workload_btn"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Suggest Workloads",
                    "emoji": True
                },
                "value": json.dumps({
                    "action": "suggest_workloads"
                }),
                "action_id": "suggest_workloads_btn"
            }
        ]
    })
    
    return blocks

def build_resource_usage_blocks(namespace: str, workload_name: str, usage_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Build Slack blocks for displaying resource usage.
    
    Args:
        namespace: The namespace of the workload
        workload_name: The name of the workload
        usage_data: The resource usage data
        
    Returns:
        A list of Slack blocks
    """
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"Resource Usage: {namespace}/{workload_name}",
                "emoji": True
            }
        },
        {
            "type": "divider"
        }
    ]
    
    # CPU usage
    cpu_data = usage_data.get("cpu", {})
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*CPU Usage*\n"
                   f"Current: {cpu_data.get('current', 'N/A')}\n"
                   f"Request: {cpu_data.get('request', 'N/A')}\n"
                   f"Limit: {cpu_data.get('limit', 'N/A')}\n"
                   f"Usage: {cpu_data.get('usage_percentage', 0)}%"
        }
    })
    
    # Memory usage
    memory_data = usage_data.get("memory", {})
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*Memory Usage*\n"
                   f"Current: {memory_data.get('current', 'N/A')}\n"
                   f"Request: {memory_data.get('request', 'N/A')}\n"
                   f"Limit: {memory_data.get('limit', 'N/A')}\n"
                   f"Usage: {memory_data.get('usage_percentage', 0)}%"
        }
    })
    
    # Add a button to optimize resources
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Optimize Resources",
                    "emoji": True
                },
                "value": json.dumps({
                    "namespace": namespace,
                    "workload": workload_name
                }),
                "action_id": "optimize_workload_btn"
            }
        ]
    })
    
    return blocks

def build_workload_suggestion_blocks(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Build Slack blocks for displaying workload optimization suggestions.
    
    Args:
        candidates: The list of workload candidates for optimization
        
    Returns:
        A list of Slack blocks
    """
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Suggested Workloads for Optimization",
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Here are some workloads that could benefit from resource optimization:"
            }
        },
        {
            "type": "divider"
        }
    ]
    
    # Add each candidate as a section with a button
    for candidate in candidates:
        namespace = candidate.get("namespace", "default")
        workload_name = candidate.get("workload_name", "")
        current_resources = candidate.get("current_resources", {})
        recommended_resources = candidate.get("recommended_resources", {})
        justification = candidate.get("justification", "")
        priority = candidate.get("priority", "MEDIUM")
        potential_savings = candidate.get("potential_savings", "")
        
        # Format the resources comparison
        resources_text = ""
        if current_resources and recommended_resources:
            resources_text = "*Current vs. Recommended Resources*\n"
            resources_text += f"CPU Request: {current_resources.get('cpu_request', 'N/A')} → {recommended_resources.get('cpu_request', 'N/A')}\n"
            resources_text += f"CPU Limit: {current_resources.get('cpu_limit', 'N/A')} → {recommended_resources.get('cpu_limit', 'N/A')}\n"
            resources_text += f"Memory Request: {current_resources.get('memory_request', 'N/A')} → {recommended_resources.get('memory_request', 'N/A')}\n"
            resources_text += f"Memory Limit: {current_resources.get('memory_limit', 'N/A')} → {recommended_resources.get('memory_limit', 'N/A')}"
        
        # Add the candidate section
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{namespace}/{workload_name}*\n"
                       f"{resources_text}\n\n"
                       f"*Justification*: {justification}\n"
                       f"*Priority*: {priority}\n"
                       f"*Potential Savings*: {potential_savings}"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Optimize",
                    "emoji": True
                },
                "value": json.dumps({
                    "namespace": namespace,
                    "workload": workload_name
                }),
                "action_id": "optimize_workload_btn"
            }
        })
        
        blocks.append({
            "type": "divider"
        })
    
    return blocks

def build_resource_modification_modal_blocks(
    namespace: str,
    workload_name: str,
    workload_details: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Build blocks for the resource modification modal.
    
    Args:
        namespace: The namespace of the workload
        workload_name: The name of the workload
        workload_details: The details of the workload
        
    Returns:
        A list of Slack blocks
    """
    # Extract current resources
    resources = workload_details.get("resources", {})
    requests = resources.get("requests", {})
    limits = resources.get("limits", {})
    
    cpu_request = requests.get("cpu", "0")
    cpu_limit = limits.get("cpu", "0")
    memory_request = requests.get("memory", "0")
    memory_limit = limits.get("memory", "0")
    
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Modify resource requests and limits for *{namespace}/{workload_name}*"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Current Resources*\n"
                       f"CPU Request: {cpu_request}\n"
                       f"CPU Limit: {cpu_limit}\n"
                       f"Memory Request: {memory_request}\n"
                       f"Memory Limit: {memory_limit}"
            }
        },
        {
            "type": "input",
            "block_id": "cpu_request_block",
            "element": {
                "type": "plain_text_input",
                "action_id": "cpu_request",
                "initial_value": cpu_request,
                "placeholder": {
                    "type": "plain_text",
                    "text": "e.g., 100m, 0.5"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "CPU Request",
                "emoji": True
            }
        },
        {
            "type": "input",
            "block_id": "cpu_limit_block",
            "element": {
                "type": "plain_text_input",
                "action_id": "cpu_limit",
                "initial_value": cpu_limit,
                "placeholder": {
                    "type": "plain_text",
                    "text": "e.g., 200m, 1"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "CPU Limit",
                "emoji": True
            }
        },
        {
            "type": "input",
            "block_id": "memory_request_block",
            "element": {
                "type": "plain_text_input",
                "action_id": "memory_request",
                "initial_value": memory_request,
                "placeholder": {
                    "type": "plain_text",
                    "text": "e.g., 256Mi, 1Gi"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "Memory Request",
                "emoji": True
            }
        },
        {
            "type": "input",
            "block_id": "memory_limit_block",
            "element": {
                "type": "plain_text_input",
                "action_id": "memory_limit",
                "initial_value": memory_limit,
                "placeholder": {
                    "type": "plain_text",
                    "text": "e.g., 512Mi, 2Gi"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "Memory Limit",
                "emoji": True
            }
        }
    ]
    
    return blocks

def build_confirmation_modal_blocks(
    namespace: str,
    workload_name: str,
    current_resources: Dict[str, Any],
    new_resources: Dict[str, Any],
    justification: str
) -> List[Dict[str, Any]]:
    """
    Build blocks for the confirmation modal.
    
    Args:
        namespace: The namespace of the workload
        workload_name: The name of the workload
        current_resources: Dictionary with current resource requests and limits
        new_resources: Dictionary with new resource requests and limits
        justification: The justification for the changes
        
    Returns:
        A list of Slack blocks
    """
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"You are about to modify resources for *{namespace}/{workload_name}*. Please review the changes."
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Current Resources*\n"
                       f"CPU Request: {current_resources['requests']['cpu']}\n"
                       f"CPU Limit: {current_resources['limits']['cpu']}\n"
                       f"Memory Request: {current_resources['requests']['memory']}\n"
                       f"Memory Limit: {current_resources['limits']['memory']}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*New Resources*\n"
                       f"CPU Request: {new_resources['cpu_request']}\n"
                       f"CPU Limit: {new_resources['cpu_limit']}\n"
                       f"Memory Request: {new_resources['memory_request']}\n"
                       f"Memory Limit: {new_resources['memory_limit']}"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Justification*\n" + justification
            }
        }
    ]
    
    return blocks 