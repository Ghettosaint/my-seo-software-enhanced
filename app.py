"""
Flask application entry point for the modified SEO analyser.

This script defines a simple web interface to the analysis routine
implemented in ``seo_analyzer``.  It exposes three main routes:

* ``/``: displays the main form for entering a URL and shows the
  analysis results.  Access to this route is gated by a one‑day free
  trial: on first visit a trial start timestamp is stored in the
  session; after 24 hours, unauthenticated users are redirected to
  ``/subscribe``.
* ``/subscribe``: shows a page with a PayPal subscription link.  Once
  the payment is completed the user is expected to return to
  ``/payment_success`` to unlock the app.  In a real deployment the
  PayPal IPN or Webhook would update the subscription status.
* ``/api/analyze``: accepts a JSON payload with a ``url`` field and
  returns the analysis report in JSON format.
* ``/payment_success``: marks the session as subscribed and redirects
  to the main page.

Sessions are signed using the ``SECRET_KEY`` environment variable.
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta
import os
import asyncio

from seo_analyzer import analyze_url

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-secret')

# CORS could be enabled here if you plan to host a separate frontend.


def _trial_expired() -> bool:
    """Check whether the user’s one‑day trial has expired."""
    trial_start_str = session.get('trial_start')
    if not trial_start_str:
        return False
    try:
        start_dt = datetime.fromisoformat(trial_start_str)
    except Exception:
        return False
    return datetime.utcnow() > start_dt + timedelta(days=1)


@app.before_request
def start_trial_if_needed():
    """Ensure a trial start timestamp is set for new visitors."""
    if 'trial_start' not in session:
        session['trial_start'] = datetime.utcnow().isoformat()


@app.route('/')
def index() -> str:
    """Render the main page or redirect to the subscribe page."""
    # If the trial expired and the user is not subscribed, redirect to subscribe
    if _trial_expired() and not session.get('subscribed'):
        return redirect(url_for('subscribe'))
    return render_template('index.html')


@app.route('/subscribe')
def subscribe() -> str:
    """Display the subscription page."""
    return render_template('subscribe.html')


@app.route('/payment_success')
def payment_success() -> str:
    """Mark the user as subscribed and return to the main page.

    In a production system this endpoint would be called by PayPal
    following a successful payment.  For demonstration purposes this
    route simply toggles a session flag.
    """
    session['subscribed'] = True
    # Reset trial start to avoid repeated redirection
    session['trial_start'] = datetime.utcnow().isoformat()
    return redirect(url_for('index'))


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """Handle analysis requests from the frontend.

    Expects JSON with a ``url`` field.  If no URL is provided an
    error response is returned.  The analysis is executed in a new
    event loop because Flask runs synchronously.  The report is
    returned as JSON.
    """
    data = request.get_json() or {}
    url = data.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        report = loop.run_until_complete(analyze_url(url))
        loop.close()
        return jsonify(report)
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


if __name__ == '__main__':
    # Running the app directly is convenient for local development.  In
    # production the WSGI server specified in render.yaml should be used.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
