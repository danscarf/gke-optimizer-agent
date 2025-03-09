"""
Kubernetes service for GKE Resource Optimizer.

This module contains functions for interacting with Kubernetes clusters to:
1. Get workload information
2. Retrieve resource usage metrics
3. Modify workload resource requests and limits
"""

import os
import logging
from typing import Dict, Any, List, Optional, Tuple
from kubernetes import client, config
from google.cloud import container_v1

logger = logging.getLogger(__name__)

def get_k8s_client() -> client.AppsV1Api:
    """
    Initialize and return a Kubernetes client.
    
    If running inside a cluster, uses in-cluster config.
    Otherwise, uses kubeconfig file or specified context.
    """
    try:
        # Try to load in-cluster config first
        config.load_incluster_config()
        logger.info("Using in-cluster Kubernetes configuration")
    except config.ConfigException:
        # Fall back to kubeconfig
        k8s_context = os.environ.get("K8S_CONTEXT")
        if k8s_context:
            config.load_kube_config(context=k8s_context)
            logger.info(f"Using Kubernetes configuration with context: {k8s_context}")
        else:
            config.load_kube_config()
            logger.info("Using default Kubernetes configuration from kubeconfig")
    
    return client.AppsV1Api()

def get_workloads(namespace: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get all deployments in the specified namespace or across all namespaces.
    
    Args:
        namespace: The namespace to filter by. If None, get deployments from all namespaces.
        
    Returns:
        A list of deployment details dictionaries.
    """
    k8s_client = get_k8s_client()
    
    try:
        if namespace:
            deployments = k8s_client.list_namespaced_deployment(namespace)
        else:
            deployments = k8s_client.list_deployment_for_all_namespaces()
        
        workload_list = []
        for deployment in deployments.items:
            name = deployment.metadata.name
            ns = deployment.metadata.namespace
            containers = deployment.spec.template.spec.containers
            
            # Extract resource requests and limits for the first container
            resources = containers[0].resources if containers else None
            
            # Format the resources
            formatted_resources = {
                "requests": {},
                "limits": {}
            }
            
            if resources:
                if resources.requests:
                    formatted_resources["requests"] = resources.requests
                if resources.limits:
                    formatted_resources["limits"] = resources.limits
            
            workload_list.append({
                "name": name,
                "namespace": ns,
                "replicas": deployment.spec.replicas,
                "resources": formatted_resources
            })
        
        return workload_list
    except client.exceptions.ApiException as e:
        logger.error(f"Error getting Kubernetes deployments: {e}")
        raise

def get_workload_details(namespace: str, workload_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific workload.
    
    Args:
        namespace: The namespace of the workload
        workload_name: The name of the workload (deployment)
        
    Returns:
        A dictionary with workload details
    """
    k8s_client = get_k8s_client()
    
    try:
        deployment = k8s_client.read_namespaced_deployment(
            name=workload_name,
            namespace=namespace
        )
        
        containers = deployment.spec.template.spec.containers
        container = containers[0] if containers else None
        
        resources = {
            "requests": {
                "cpu": "0",
                "memory": "0"
            },
            "limits": {
                "cpu": "0",
                "memory": "0"
            }
        }
        
        if container and container.resources:
            if container.resources.requests:
                cpu_request = container.resources.requests.get("cpu", "0")
                memory_request = container.resources.requests.get("memory", "0")
                resources["requests"]["cpu"] = str(cpu_request)
                resources["requests"]["memory"] = str(memory_request)
            
            if container.resources.limits:
                cpu_limit = container.resources.limits.get("cpu", "0")
                memory_limit = container.resources.limits.get("memory", "0")
                resources["limits"]["cpu"] = str(cpu_limit)
                resources["limits"]["memory"] = str(memory_limit)
        
        return {
            "name": workload_name,
            "namespace": namespace,
            "replicas": deployment.spec.replicas,
            "resources": resources,
            "labels": deployment.metadata.labels or {},
            "annotations": deployment.metadata.annotations or {},
            "container_name": container.name if container else ""
        }
    except client.exceptions.ApiException as e:
        logger.error(f"Error getting Kubernetes deployment {namespace}/{workload_name}: {e}")
        raise

def get_resource_usage(namespace: str, workload_name: str) -> Dict[str, Any]:
    """
    Get resource usage metrics for a specific workload.
    
    This is a placeholder implementation. In a real implementation, 
    this would retrieve metrics from Google Cloud Monitoring.
    
    Args:
        namespace: The namespace of the workload
        workload_name: The name of the workload (deployment)
        
    Returns:
        A dictionary with resource usage metrics
    """
    # In a real implementation, this would query Google Cloud Monitoring
    # for CPU and memory usage metrics
    
    # Placeholder data
    return {
        "cpu": {
            "current": "250m",
            "request": "500m",
            "limit": "1000m",
            "usage_percentage": 50,
            "time_series": [
                {"timestamp": "2023-05-01T00:00:00Z", "value": 200},
                {"timestamp": "2023-05-01T01:00:00Z", "value": 250},
                {"timestamp": "2023-05-01T02:00:00Z", "value": 300},
                {"timestamp": "2023-05-01T03:00:00Z", "value": 220},
                {"timestamp": "2023-05-01T04:00:00Z", "value": 180}
            ]
        },
        "memory": {
            "current": "256Mi",
            "request": "512Mi",
            "limit": "1Gi",
            "usage_percentage": 50,
            "time_series": [
                {"timestamp": "2023-05-01T00:00:00Z", "value": 200},
                {"timestamp": "2023-05-01T01:00:00Z", "value": 220},
                {"timestamp": "2023-05-01T02:00:00Z", "value": 240},
                {"timestamp": "2023-05-01T03:00:00Z", "value": 260},
                {"timestamp": "2023-05-01T04:00:00Z", "value": 256}
            ]
        }
    }

def modify_workload_resources(
    namespace: str,
    workload_name: str,
    cpu_request: str,
    cpu_limit: str,
    memory_request: str,
    memory_limit: str
) -> Dict[str, Any]:
    """
    Modify resource requests and limits for a specific workload.
    
    Args:
        namespace: The namespace of the workload
        workload_name: The name of the workload (deployment)
        cpu_request: New CPU request value
        cpu_limit: New CPU limit value
        memory_request: New memory request value
        memory_limit: New memory limit value
        
    Returns:
        The updated workload details
    """
    k8s_client = get_k8s_client()
    
    try:
        # Get the current deployment
        deployment = k8s_client.read_namespaced_deployment(
            name=workload_name,
            namespace=namespace
        )
        
        # Ensure at least one container exists
        if not deployment.spec.template.spec.containers:
            raise ValueError(f"Deployment {namespace}/{workload_name} has no containers")
        
        # Update the resources for the first container
        container = deployment.spec.template.spec.containers[0]
        
        # Initialize the resources if they don't exist
        if not container.resources:
            container.resources = client.V1ResourceRequirements(
                requests={},
                limits={}
            )
        
        # Update requests
        if not container.resources.requests:
            container.resources.requests = {}
        container.resources.requests["cpu"] = cpu_request
        container.resources.requests["memory"] = memory_request
        
        # Update limits
        if not container.resources.limits:
            container.resources.limits = {}
        container.resources.limits["cpu"] = cpu_limit
        container.resources.limits["memory"] = memory_limit
        
        # Update the deployment
        k8s_client.patch_namespaced_deployment(
            name=workload_name,
            namespace=namespace,
            body=deployment
        )
        
        logger.info(f"Successfully updated resources for {namespace}/{workload_name}")
        
        # Return the updated workload details
        return get_workload_details(namespace, workload_name)
    except client.exceptions.ApiException as e:
        logger.error(f"Error updating Kubernetes deployment {namespace}/{workload_name}: {e}")
        raise 