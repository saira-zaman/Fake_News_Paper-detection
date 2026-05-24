from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import joblib
import string
import nltk
from nltk.corpus import stopwords
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Model cache
model_cache = None
MODEL_PATH = 'fake_news_model.pkl'

# Ensure NLTK data is available
def ensure_nltk_data():
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        try:
            nltk.download('stopwords', quiet=True)
        except Exception as e:
            logger.warning(f"NLTK download failed: {e}")

ensure_nltk_data()

def load_model():
    """Load model with caching and better error handling"""
    global model_cache
    if model_cache is not None:
        return model_cache
    
    try:
        # Try multiple paths
        possible_paths = [
            'fake_news_model.pkl',
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fake_news_model.pkl'),
            os.path.join(os.getcwd(), 'fake_news_model.pkl'),
            os.path.join(os.getcwd(), 'Fake News prediction', 'fake_news_model.pkl'),
            '/vercel/path0/Fake News prediction/fake_news_model.pkl'  # Vercel path
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Loading model from: {path}")
                model_cache = joblib.load(path)
                logger.info("✓ Model loaded successfully")
                return model_cache
        
        logger.error(f"Model not found in any of these paths: {possible_paths}")
        return None
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return None

def preprocess_text(text):
    """Preprocess text with error handling"""
    try:
        # Lowercase
        text = str(text).lower()
        
        # Remove punctuation
        diff = [char for char in text if char not in string.punctuation]
        text = ''.join(diff)
        
        # Remove stopwords
        try:
            stop = stopwords.words('english')
        except LookupError:
            nltk.download('stopwords', quiet=True)
            stop = stopwords.words('english')
        
        text = ' '.join([word for word in text.split() if word not in stop])
        return text
    except Exception as e:
        logger.error(f"Preprocessing error: {e}")
        raise

@app.route('/')
def home():
    """Serve home page"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Home route error: {e}")
        return jsonify({'error': 'Page not found'}), 404

@app.route('/api/predict', methods=['POST'])
def predict():
    """API endpoint for predictions"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request'}), 400
        
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if len(text) < 10:
            return jsonify({'error': 'Text too short. Please provide at least 10 characters'}), 400
        
        # Load model
        model = load_model()
        if model is None:
            return jsonify({'error': 'Model initializing. Please try again in a moment.', 'success': False}), 503
        
        # Preprocess
        processed_text = preprocess_text(text)
        
        if not processed_text:
            return jsonify({'error': 'Text could not be processed'}), 400
        
        # Predict
        prediction = model.predict([processed_text])[0]
        
        # Get probabilities
        try:
            proba = model.predict_proba([processed_text])[0]
            confidence_score = max(proba) * 100
            confidence = f"{confidence_score:.1f}%"
        except:
            confidence = "N/A"
        
        # Determine result
        result_display = "🟢 REAL NEWS" if prediction == 'true' else "🔴 FAKE NEWS"
        
        return jsonify({
            'result': result_display,
            'raw_prediction': prediction,
            'confidence': confidence,
            'success': True
        }), 200
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': f'Prediction failed: {str(e)}', 'success': False}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    model = load_model()
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
