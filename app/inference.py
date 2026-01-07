import joblib
import numpy as np
import re
import os

# Load the pre-trained model and vectorizer
# Ensure these paths are correct relative to where app.py will be run
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.pkl')
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), 'vectorizer.pkl')

try:
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    print(f"INFO: Models loaded successfully from {MODEL_PATH} and {VECTORIZER_PATH}")
except FileNotFoundError as e:
    print(f"Error loading model or vectorizer: {e}")
    print(f"Expected model at: {MODEL_PATH}")
    print(f"Expected vectorizer at: {VECTORIZER_PATH}")
    # Exit or raise an exception to prevent the app from starting without models
    raise SystemExit("Required model files not found. Exiting.") from e

# Define greeting words for the override rule
GREETINGS = {'hi', 'hello', 'hii', 'hey', 'hi there', 'hello there', 'good morning', 'good afternoon', 'good evening'}

def preprocess_message(message):
    """
    Cleans and preprocesses the input message for inference.
    """
    if not isinstance(message, str):
        return ""
    message = message.lower()
    # Remove special characters, numbers, and extra spaces
    message = re.sub(r'[^a-z\s]', '', message)
    message = re.sub(r'\s+', ' ', message).strip()
    return message

def predict_scam(message: str):
    """
    Predicts if a message is 'SCAM' or 'SAFE' using a pre-trained model
    and rule-augmented logic.

    Args:
        message (str): The input message text.

    Returns:
        tuple: (label, confidence, reason)
            label (str): 'SAFE' or 'SCAM'.
            confidence (float): Prediction confidence (0.0 to 1.0).
            reason (str): Explanation for the prediction.
    """
    original_message = message
    preprocessed_message = preprocess_message(original_message)

    # --- Rule-augmented Logic ---

    # 1. Empty or very short message check
    if not preprocessed_message:
        return 'SAFE', 1.0, 'Message was empty or contained only special characters; classified as SAFE by rule.'
    
    # 2. Greeting override
    if preprocessed_message in GREETINGS:
        return 'SAFE', 0.99, 'Classified as SAFE by greeting rule.'
    
    # 3. Single-token SAFE rule (after preprocessing)
    if len(preprocessed_message.split()) == 1 and preprocessed_message not in GREETINGS:
        # If it's a single word and not a greeting, let the model decide, but with a slight bias
        pass # The model will handle this, we just won't apply an override

    # --- ML Model Inference ---
    try:
        message_vectorized = vectorizer.transform([preprocessed_message])
        
        # Get probability estimates for both classes
        # model.predict_proba returns probabilities for [class_0, class_1]
        # We need to know which class is 'SCAM' (1) and which is 'SAFE' (0)
        # Assuming 0 is SAFE and 1 is SCAM, based on typical binary classification setup
        # It's good practice to verify this from training phase, but typically it's alphabetical or order of unique classes found.
        # For LogisticRegression, `classes_` attribute will confirm order.
        scam_idx = list(model.classes_).index(1) if 1 in model.classes_ else 0 # Assuming 1 is SCAM
        safe_idx = list(model.classes_).index(0) if 0 in model.classes_ else 1 # Assuming 0 is SAFE


        probabilities = model.predict_proba(message_vectorized)[0]
        scam_probability = probabilities[scam_idx]
        safe_probability = probabilities[safe_idx]

        # Get the predicted class (0 or 1)
        predicted_class = model.predict(message_vectorized)[0]
        
        label = 'SCAM' if predicted_class == 1 else 'SAFE'
        confidence = scam_probability if predicted_class == 1 else safe_probability
        
        # --- Context-aware Thresholding (Example Implementation) ---
        # Adjust confidence for "SCAM" if it's very close to SAFE and message is short
        if label == 'SCAM' and confidence < 0.65 and len(preprocessed_message.split()) < 5:
            return 'SAFE', 0.60, f'Re-classified as SAFE due to low SCAM confidence ({confidence:.2f}) on a short message.'

        # Add a default reason for model predictions
        reason = f'Classified by ML model with {confidence:.2f} confidence.'
        if label == 'SCAM' and confidence > 0.8:
            reason = f'Highly likely SCAM based on ML model prediction ({confidence:.2f} confidence).'
        elif label == 'SAFE' and confidence > 0.8:
            reason = f'Highly likely SAFE based on ML model prediction ({confidence:.2f} confidence).'

        return label, round(float(confidence), 2), reason

    except Exception as e:
        print(f"Error during ML inference: {e}")
        return 'SAFE', 0.5, f'Error during prediction: {str(e)}. Defaulted to SAFE.'

# Example of how to use it (for local testing, remove in production app.py usage)
if __name__ == '__main__':
    # Test cases
    print(predict_scam("hi"))
    print(predict_scam("hello"))
    print(predict_scam("how are you"))
    print(predict_scam("urgent action required"))
    print(predict_scam("your account is blocked"))
    print(predict_scam("OTP required immediately"))
    print(predict_scam("You have won a lottery, click here to claim!"))
    print(predict_scam("Just checking in"))
    print(predict_scam(".")) # Test empty/special char after preprocess
    print(predict_scam("free")) # Short word, let model decide
    print(predict_scam("win prize")) # Test context-aware thresholding