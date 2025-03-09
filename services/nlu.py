"""
Natural Language Understanding service for GKE Resource Optimizer.

This module contains functions for processing natural language input from users
and extracting intents and entities.
"""

import os
import logging
from typing import Dict, Any, List, Tuple
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Initialize Google Gemini API
API_KEY = os.environ.get("GOOGLE_GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

def process_natural_language(text: str) -> Tuple[str, Dict[str, Any]]:
    """
    Process natural language input to extract intent and entities.
    
    Args:
        text: The natural language input from the user
        
    Returns:
        A tuple containing the intent and a dictionary of entities
    """
    logger.info(f"Processing natural language input: {text}")
    
    try:
        # Use the Gemini model to extract intent and entities
        if API_KEY:
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"""
            Extract the intent and entities from the following Kubernetes resource optimization request:
            
            "{text}"
            
            Possible intents:
            - optimize_cpu: The user wants to optimize CPU resources
            - optimize_memory: The user wants to optimize memory resources
            - optimize_both: The user wants to optimize both CPU and memory resources
            - get_usage: The user wants to see resource usage
            - suggest_workloads: The user wants suggestions for optimization candidates
            - unknown: The intent is not clear
            
            Possible entities:
            - workload_name: The name of the Kubernetes workload
            - namespace: The Kubernetes namespace
            - direction: Whether to increase or decrease resources (increase, decrease)
            - resource_type: The type of resource to optimize (cpu, memory, both)
            - percentage: Any percentage mentioned
            
            Format your response as a JSON object with 'intent' and 'entities' fields.
            For example:
            {{
                "intent": "optimize_cpu",
                "entities": {{
                    "workload_name": "frontend-service",
                    "namespace": "default",
                    "direction": "decrease",
                    "resource_type": "cpu",
                    "percentage": "50"
                }}
            }}
            
            If an entity is not present, omit it from the entities object.
            """
            
            response = model.generate_content(prompt)
            result = response.text
            
            # Parse the JSON result - in a production system we would add proper
            # error handling and fallback for the JSON parsing
            import json
            import re
            
            # Find the JSON object in the response using regex
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed = json.loads(json_str)
                intent = parsed.get("intent", "unknown")
                entities = parsed.get("entities", {})
                
                logger.info(f"Extracted intent: {intent}, entities: {entities}")
                return intent, entities
        
        # Fallback to simple rule-based parsing
        intent = "unknown"
        entities = {}
        
        # Extract workload name if present (assuming format "workload-name" or "namespace/workload-name")
        import re
        workload_match = re.search(r'(?:for|on)\s+(?:the\s+)?([a-zA-Z0-9-]+(?:/[a-zA-Z0-9-]+)?)', text)
        if workload_match:
            workload_ref = workload_match.group(1)
            if "/" in workload_ref:
                namespace, workload_name = workload_ref.split("/", 1)
                entities["namespace"] = namespace
                entities["workload_name"] = workload_name
            else:
                entities["workload_name"] = workload_ref
        
        # Determine the intent based on keywords
        if "cpu" in text.lower() and ("reduce" in text.lower() or "decrease" in text.lower()):
            intent = "optimize_cpu"
            entities["direction"] = "decrease"
            entities["resource_type"] = "cpu"
        elif "memory" in text.lower() and ("reduce" in text.lower() or "decrease" in text.lower()):
            intent = "optimize_memory"
            entities["direction"] = "decrease"
            entities["resource_type"] = "memory"
        elif "resource" in text.lower() and ("usage" in text.lower() or "show" in text.lower()):
            intent = "get_usage"
        elif "suggest" in text.lower() or "recommend" in text.lower():
            intent = "suggest_workloads"
        
        # Extract percentage if present
        percentage_match = re.search(r'(\d+)%', text)
        if percentage_match:
            entities["percentage"] = percentage_match.group(1)
        
        logger.info(f"Simple rule-based extraction - intent: {intent}, entities: {entities}")
        return intent, entities
    
    except Exception as e:
        logger.error(f"Error processing natural language input: {e}")
        return "unknown", {} 