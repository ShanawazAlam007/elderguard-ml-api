# Scam Text Detection API

## Project Overview
This project provides a robust, production-ready backend API for detecting scam text messages using a pre-trained Machine Learning model augmented with rule-based logic. It's designed to be easily deployable and consumed by a Next.js frontend or any other client application. The API classifies incoming messages as either "SAFE" or "SCAM" and provides a confidence score and a human-readable reason for the prediction.

## Features
-   **ML-Powered Predictions:** Utilizes a pre-trained `model.pkl` (e.g., Logistic Regression) and `vectorizer.pkl` (e.g., TF-IDF Vectorizer) for core classification.
-   **Rule-Augmented Logic:** Enhances prediction accuracy and user experience with:
    -   **Greeting Override:** Automatically classifies common greetings (e.g., "hi", "hello") as SAFE.
    -   **Context-Aware Thresholding:** Re-evaluates low-confidence SCAM predictions for short messages, potentially re-classifying them as SAFE.
-   **RESTful API:** Clean and predictable API endpoints for easy integration.
-   **Health Check:** A dedicated `/health` endpoint to monitor API status.
-   **Production-Ready:** Designed for deployment on platforms like Render, Railway, or Vercel (for serverless functions, though Flask might need specific setup).
-   **CORS Enabled:** Supports cross-origin requests for frontend integration.

## API Endpoints

### 1. GET /health
Checks the status of the API.

-   **Method:** `GET`
-   **URL:** `/health`
-   **Response:** `application/json`
    ```json
    {
      "status": "healthy",
      "message": "API is running"
    }
    ```

### 2. POST /predict
Analyzes a text message to determine if it is a scam.

-   **Method:** `POST`
-   **URL:** `/predict`
-   **Request Body:** `application/json`
    ```json
    {
      "message": "your text message here"
    }
    ```
-   **Response:** `application/json`
    ```json
    {
      "prediction": "SAFE" or "SCAM",
      "confidence": 0.00 to 1.00,
      "reason": "Explanation for the prediction"
    }
    ```

## Example `curl` Request

To test the `/predict` endpoint:

```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"message": "urgent action required your account is blocked"}' \
     http://localhost:5000/predict
```

Example output:

```json
{
  "confidence": 0.95,
  "prediction": "SCAM",
  "reason": "Highly likely SCAM based on ML model prediction (0.95 confidence)."
}
```

```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"message": "hi there"}' \
     http://localhost:5000/predict
```

Example output:

```json
{
  "confidence": 0.99,
  "prediction": "SAFE",
  "reason": "Classified as SAFE by greeting rule."
}
```

## How to Run Locally

1.  **Clone the repository (or navigate to `scam_text_api` directory):**
    ```bash
    # If this was a fresh repo
    # git clone <repository-url>
    # cd scam_text_api
    ```
    *(Assuming you are already in the `scam_text_api` directory)*

2.  **Create a Python virtual environment:**
    ```bash
    python3 -m venv venv
    ```

3.  **Activate the virtual environment:**
    -   **On macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
    -   **On Windows:**
        ```bash
        .\venv\Scripts\activate
        ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Run the Flask application:**
    ```bash
    # From the scam_text_api directory
    python app/app.py
    ```
    The API will be available at `http://localhost:5000`.

6.  **Optional: Configure the port (e.g., to run on port 8080):**
    ```bash
    export PORT=8080
    python app/app.py
    ```

## How Frontend (Next.js) Can Connect

A Next.js frontend can interact with this API using `fetch` or `axios`.

```javascript
// Example in a Next.js component or API route
async function predictScam(message) {
  try {
    const response = await fetch('http://localhost:5000/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: message }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error predicting scam:", error);
    return {
      prediction: "ERROR",
      confidence: 0.0,
      reason: error.message || "Failed to connect to API"
    };
  }
}

// Example usage
// predictScam("You've won a prize! Click here.").then(result => console.log(result));
```
Remember to replace `http://localhost:5000` with your deployed API URL in production.

## Deployment Readiness

This project is designed to be deployment-ready for platforms that support Python Flask applications (e.g., Render, Railway, Heroku, Google Cloud Run, AWS Elastic Beanstalk).

**Key considerations for deployment:**
-   **Environment Variables:** Ensure the `PORT` environment variable is set in your deployment environment.
-   **WSGI Server:** For production, it's recommended to use a production-ready WSGI server like Gunicorn. You can typically run it with a command like:
    ```bash
    gunicorn -w 4 'app.app:app' -b 0.0.0.0:${PORT:-5000}
    ```
    (Ensure `gunicorn` is added to `requirements.txt` if you plan to use it for deployment.)
    *Note: For this project, `gunicorn` was not explicitly requested in `requirements.txt`, but it's a standard practice for production Flask deployments.*
-   **Logging:** Configure proper logging in a production environment.
-   **HTTPS:** Always use HTTPS in production.

## Final Check

-   No ML model retraining.
-   Original files are not moved.
-   Only required files are copied.
-   Code is clean, minimal, and production-safe.
-   Frontend-compatible API.