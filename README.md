# GKE Resource Optimizer Slack Agent

A Slack-based agent for optimizing resource requests and limits (CPU and memory) for Google Kubernetes Engine (GKE) workloads, leading to cost savings, improved resource utilization, and enhanced application performance.

## Overview

The GKE Resource Optimizer is a tool designed for DevOps engineers, SREs, and developers responsible for managing GKE deployments. It simplifies and automates the process of optimizing resource requests and limits by providing intelligent recommendations based on historical data and AI-powered insights.

## Key Features

- 🤖 **Slack-based Interface**: Easy interaction via slash commands
- 🗣️ **Natural Language Support**: Use conversational language to request optimizations
- 📊 **Intelligent Workload Analysis**: AI-powered suggestions for resource optimization
- 📈 **Resource Usage Visualization**: See trends and patterns in resource utilization
- 🔄 **Automated Resource Modification**: Apply changes with proper validation and confirmation
- 🎫 **Jira Integration**: Automatic ticket creation for change documentation
- 📢 **Slack Notifications**: Keep team members informed about optimization activities

## Architecture

The GKE Resource Optimizer integrates with:
- Slack API for user interaction
- Google Cloud Monitoring and Recommender API for resource analysis
- Kubernetes API for workload modification
- Jira API for ticketing
- AI/LLM services for natural language understanding and justification generation

## Usage

### Slash Commands

- `/optimize-resources`: Initiates the resource optimization workflow
- `/resource-usage`: Displays resource usage trends for a specified workload
- `/suggest-workloads`: Suggests workloads that are good candidates for optimization

## Development

### Prerequisites

- Python 3.9+
- Google Cloud SDK
- Kubernetes access to target GKE clusters
- Slack Bot Token
- Jira API credentials

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/gke-optimizer-agent.git
cd gke-optimizer-agent

# Set up Python environment with pyenv
pyenv install 3.9.18
pyenv local 3.9.18

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your configurations
```

### Running Locally

```bash
# Make the run script executable
chmod +x run_local.sh

# Run the application
./run_local.sh
```

### Code Quality

This project uses pylint to maintain high code quality standards:

```bash
# Run the linting check
chmod +x lint.sh
./lint.sh
```

Pylint configuration is stored in `.pylintrc`. You can customize the rules to fit your team's coding standards.

## Deployment

### Docker

```bash
# Build the Docker image
docker build -t gke-optimizer-agent .

# Run the container
docker run -p 3000:8080 --env-file .env gke-optimizer-agent
```

### Kubernetes

```bash
# Deploy to Kubernetes
kubectl apply -f kubernetes/deployment.yaml
```

## License

[MIT License](LICENSE) 