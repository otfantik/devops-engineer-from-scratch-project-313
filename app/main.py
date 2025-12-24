# app/main.py
import os
from flask import Flask, jsonify

if os.environ.get('SENTRY_DSN'):
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    
    sentry_sdk.init(
        dsn=os.environ.get('SENTRY_DSN'),
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

app = Flask(__name__)

@app.route("/ping")
def ping():
    """Health check endpoint"""
    return "pong"

@app.route("/error")
def trigger_error():
    if os.environ.get('SENTRY_DSN'):
        1 / 0
    return "Sentry is not configured"

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500
