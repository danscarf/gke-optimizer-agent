"""
AI service for GKE Resource Optimizer.

This module contains functions for:
1. Natural language understanding
2. Generating justifications for resource changes
3. Translating recommendations into natural language explanations
"""

import os
import logging
from typing import Dict, Any, List, Tuple
import google.generativeai as genai
from langchain.llms import GoogleGenerativeAI
from langchain.prompts import PromptTemplate

logger = logging.getLogger(__name__)

# Initialize Google Gemini API
API_KEY = os.environ.get("GOOGLE_GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

def get_llm():
    """Get LLM client for generation tasks"""
    return GoogleGenerativeAI(model="gemini-pro", google_api_key=API_KEY)

def generate_change_justification(
    namespace: str,
    workload_name: str,
    current_resources: Dict[str, Any],
    new_resources: Dict[str, Any]
) -> str:
    """
    Generate a justification for resource changes based on historical data.
    
    Args:
        namespace: The namespace of the workload
        workload_name: The name of the workload
        current_resources: Dictionary with current resource requests and limits
        new_resources: Dictionary with new resource requests and limits
        
    Returns:
        A natural language justification for the changes
    """
    llm = get_llm()
    
    # Create a prompt template for the justification
    template = """
    You are an AI assistant that helps DevOps engineers optimize Kubernetes resources.
    You need to generate a professional and detailed justification for changes to resource requests and limits.
    
    Workload: {workload_name} in namespace {namespace}
    
    Current Resources:
    - CPU Request: {current_cpu_request}
    - CPU Limit: {current_cpu_limit}
    - Memory Request: {current_memory_request}
    - Memory Limit: {current_memory_limit}
    
    New Resources:
    - CPU Request: {new_cpu_request}
    - CPU Limit: {new_cpu_limit}
    - Memory Request: {new_memory_request}
    - Memory Limit: {new_memory_limit}
    
    Changes:
    - CPU Request: {cpu_request_change}
    - CPU Limit: {cpu_limit_change}
    - Memory Request: {memory_request_change}
    - Memory Limit: {memory_limit_change}
    
    Based on this information, generate a clear, concise, and professional justification for these changes.
    Include specific technical details and benefits. Mention potential cost impacts and performance implications.
    The justification should be suitable for a Jira ticket or team communication.
    """
    
    # Calculate the changes
    cpu_request_change = calculate_change(
        current_resources["requests"]["cpu"],
        new_resources["cpu_request"]
    )
    cpu_limit_change = calculate_change(
        current_resources["limits"]["cpu"],
        new_resources["cpu_limit"]
    )
    memory_request_change = calculate_change(
        current_resources["requests"]["memory"],
        new_resources["memory_request"]
    )
    memory_limit_change = calculate_change(
        current_resources["limits"]["memory"],
        new_resources["memory_limit"]
    )
    
    # Create the prompt
    prompt = PromptTemplate(
        input_variables=[
            "namespace", "workload_name", 
            "current_cpu_request", "current_cpu_limit", 
            "current_memory_request", "current_memory_limit",
            "new_cpu_request", "new_cpu_limit", 
            "new_memory_request", "new_memory_limit",
            "cpu_request_change", "cpu_limit_change", 
            "memory_request_change", "memory_limit_change"
        ],
        template=template
    )
    
    # Fill the prompt template
    formatted_prompt = prompt.format(
        namespace=namespace,
        workload_name=workload_name,
        current_cpu_request=current_resources["requests"]["cpu"],
        current_cpu_limit=current_resources["limits"]["cpu"],
        current_memory_request=current_resources["requests"]["memory"],
        current_memory_limit=current_resources["limits"]["memory"],
        new_cpu_request=new_resources["cpu_request"],
        new_cpu_limit=new_resources["cpu_limit"],
        new_memory_request=new_resources["memory_request"],
        new_memory_limit=new_resources["memory_limit"],
        cpu_request_change=cpu_request_change,
        cpu_limit_change=cpu_limit_change,
        memory_request_change=memory_request_change,
        memory_limit_change=memory_limit_change
    )
    
    try:
        # Generate the justification
        justification = llm.invoke(formatted_prompt).strip()
        logger.info(f"Generated justification for {namespace}/{workload_name} resource changes")
        return justification
    except Exception as e:
        logger.error(f"Error generating justification: {e}")
        return f"Resource changes for {namespace}/{workload_name} to optimize cluster performance and cost efficiency."

def calculate_change(current_value: str, new_value: str) -> str:
    """
    Calculate the change between two resource values.
    
    Args:
        current_value: The current resource value
        new_value: The new resource value
        
    Returns:
        A string describing the change (e.g., "Decreased by 50%")
    """
    # This is a simplified implementation that assumes simple numeric values
    # In a real-world scenario, we would need to parse values like "500m" or "1Gi"
    try:
        # Remove units for comparison
        current_numeric = extract_numeric_value(current_value)
        new_numeric = extract_numeric_value(new_value)
        
        if current_numeric == 0:
            return f"Increased from 0 to {new_value}"
        
        percentage_change = ((new_numeric - current_numeric) / current_numeric) * 100
        
        if percentage_change > 0:
            return f"Increased by {abs(percentage_change):.1f}% (from {current_value} to {new_value})"
        elif percentage_change < 0:
            return f"Decreased by {abs(percentage_change):.1f}% (from {current_value} to {new_value})"
        else:
            return "No change"
    except Exception as e:
        logger.warning(f"Error calculating change: {e}")
        return f"Changed from {current_value} to {new_value}"

def extract_numeric_value(value_str: str) -> float:
    """
    Extract the numeric portion of a resource value string.
    
    Args:
        value_str: The resource value string (e.g., "500m", "1Gi")
        
    Returns:
        The numeric value
    """
    # This is a simplified implementation
    # In a real-world scenario, we would need to handle various units properly
    try:
        # Handle millicores (e.g., "500m")
        if value_str.endswith("m"):
            return float(value_str[:-1]) / 1000
        
        # Handle memory units
        if value_str.endswith("Mi"):
            return float(value_str[:-2])
        if value_str.endswith("Gi"):
            return float(value_str[:-2]) * 1024
        if value_str.endswith("Ki"):
            return float(value_str[:-2]) / 1024
        
        # Default case: try to convert directly
        return float(value_str)
    except (ValueError, TypeError):
        logger.warning(f"Could not extract numeric value from {value_str}")
        return 0 