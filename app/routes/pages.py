"""
Page-serving routes (HTML templates).
"""
from flask import Blueprint, render_template

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def index():
    """Serve the main dashboard."""
    return render_template("index.html")


@pages_bp.route("/help")
def help_page():
    """Serve the built-in help page."""
    return render_template("help.html")


@pages_bp.route("/analytics")
def analytics_page():
    """Serve the analytics dashboard."""
    return render_template("analytics.html")
