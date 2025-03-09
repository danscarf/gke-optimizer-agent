#!/usr/bin/env python3
"""
GKE Resource Optimizer Slack Agent

Main application entry point.
"""

import os
import logging
from dotenv import load_dotenv
from flask import Flask
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

# Import handlers
from handlers.slack_commands import register_slack_commands
from handlers.slack_interactions import register_slack_interactions

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize the Slack app
slack_app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# Flask app for handling Slack events
flask_app = Flask(__name__)
handler = SlackRequestHandler(slack_app)

# Register Slack command and interaction handlers
register_slack_commands(slack_app)
register_slack_interactions(slack_app)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    """Handle Slack events and commands"""
    return handler.handle(request)

@flask_app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    logger.info("Starting GKE Resource Optimizer Slack Agent")
    port = int(os.environ.get("PORT", 3000))
    flask_app.run(host="0.0.0.0", port=port) 