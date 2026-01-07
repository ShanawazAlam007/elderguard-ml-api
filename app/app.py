from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Add the 'app' directory to the Python path
# This allows 'inference' to be imported directly
sys.path.append(os.path.dirname(__file__))

from inference import predict_scam

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

@app.route('/', methods=['GET'])
def root():
    """
    Root endpoint for basic service information.
    """
    return jsonify({
        "service": "Scam Text Detection API",
        "status": "running",
        "endpoints": {
            "/health": "GET",
            "/predict": "POST"
        }
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    Returns: A simple JSON response indicating the API is healthy.
    """
    return jsonify({"status": "ok"}), 200

@app.route('/predict', methods=['POST'])
def predict():
    """
    Prediction endpoint for scam text detection.
    Expects a JSON payload with a 'message' field.
    Returns: JSON containing prediction, confidence, and reason.
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    message = data.get('message')

    if not message:
        return jsonify({"error": "Missing 'message' field in request body"}), 400
    
    if not isinstance(message, str):
        return jsonify({"error": "'message' field must be a string"}), 400

    try:
        label, confidence, reason = predict_scam(message)
        return jsonify({
            "prediction": label,
            "confidence": confidence,
            "reason": reason
        }), 200
    except Exception as e:
        # Log the exception for debugging purposes in production
        app.logger.error(f"Prediction error for message '{message}': {e}", exc_info=True)
        return jsonify({
            "prediction": "SAFE", # Default to SAFE on unexpected errors
            "confidence": 0.5,
            "reason": f"An internal error occurred: {str(e)}. Defaulted to SAFE."
        }), 500

if __name__ == '__main__':
    print("INFO: Flask application starting...")
    print("INFO: Routes registered: /health (GET), /predict (POST)")
    # Get port from environment variable, default to 5000
    port = int(os.environ.get('PORT', 5000))
    # In a production environment, you might use a production-ready WSGI server like Gunicorn
    # For local development, app.run() is sufficient.
    app.run(debug=False, host='0.0.0.0', port=port)