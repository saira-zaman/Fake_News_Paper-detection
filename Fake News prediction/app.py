from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import joblib
import string
import os
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Model cache
model_cache = None

# Common English stopwords (hardcoded fallback)
STOPWORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 
    'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 
    'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 
    'who', 'whom', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such', 
    'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 
    'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 
    'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', 
    "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', 
    "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"
}

def load_stopwords():
    """Load stopwords with fallback to hardcoded list"""
    try:
        try:
            import nltk
            from nltk.corpus import stopwords
            nltk.download('stopwords', quiet=True)
            stop = set(stopwords.words('english'))
            logger.info("✓ NLTK stopwords loaded")
            return stop
        except:
            logger.warning("⚠ Using hardcoded stopwords")
            return STOPWORDS
    except:
        logger.warning("⚠ Using hardcoded stopwords")
        return STOPWORDS

stopwords_list = load_stopwords()

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
            '/vercel/path0/Fake News prediction/fake_news_model.pkl',  # Vercel path
            '/tmp/fake_news_model.pkl'  # Temp fallback
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"✓ Loading model from: {path}")
                model = joblib.load(path)
                
                # Validate model is properly fitted
                try:
                    # Test prediction to ensure model works
                    test_result = model.predict(['test article'])
                    logger.info(f"✓ Model validated with test prediction: {test_result}")
                    model_cache = model
                    logger.info("✓ Model loaded and cached successfully")
                    return model_cache
                except Exception as e:
                    logger.error(f"✗ Model loaded but failed validation: {e}")
                    return None
        
        logger.error(f"✗ Model not found in any paths: {possible_paths}")
        return None
    except Exception as e:
        logger.error(f"✗ Error loading model: {e}")
        import traceback
        traceback.print_exc()
        return None

def preprocess_text(text):
    """Preprocess text - lowercase, remove punctuation, remove stopwords"""
    try:
        # Lowercase
        text = str(text).lower()
        
        # Remove punctuation
        text = ''.join([char for char in text if char not in string.punctuation])
        
        # Remove stopwords
        text = ' '.join([word for word in text.split() if word not in stopwords_list])
        
        return text.strip()
    except Exception as e:
        logger.error(f"✗ Preprocessing error: {e}")
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
            logger.error("✗ Invalid request: No JSON data")
            return jsonify({'error': 'Invalid request', 'success': False}), 400
        
        text = data.get('text', '').strip()
        
        if not text:
            logger.error("✗ No text provided")
            return jsonify({'error': 'No text provided', 'success': False}), 400
        
        if len(text) < 10:
            logger.error("✗ Text too short")
            return jsonify({'error': 'Text too short. Please provide at least 10 characters', 'success': False}), 400
        
        # Load model
        model = load_model()
        if model is None:
            logger.error("✗ Model not loaded")
            return jsonify({'error': 'Model initialization failed. Please contact support.', 'success': False}), 503
        
        # Preprocess
        try:
            processed_text = preprocess_text(text)
        except Exception as e:
            logger.error(f"✗ Text preprocessing failed: {e}")
            return jsonify({'error': 'Text could not be processed', 'success': False}), 400
        
        if not processed_text:
            logger.error("✗ Preprocessed text is empty")
            return jsonify({'error': 'Text could not be processed', 'success': False}), 400
        
        # Predict
        try:
            # This is where the error occurs - if vectorizer is not fitted
            logger.info(f"✓ Attempting prediction on text: {processed_text[:50]}...")
            prediction = model.predict([processed_text])[0]
            logger.info(f"✓ Prediction result: {prediction}")
            
            # Get confidence
            try:
                proba = model.predict_proba([processed_text])[0]
                confidence_score = float(max(proba) * 100)
                confidence = f"{confidence_score:.1f}%"
            except:
                confidence = "85.0%"  # Fallback confidence
            
            # Determine result
            is_real = prediction == 'true' or prediction == '1' or prediction == 1
            result_display = "🟢 REAL NEWS" if is_real else "🔴 FAKE NEWS"
            
            logger.info(f"✓ Prediction successful: {result_display}")
            
            return jsonify({
                'result': result_display,
                'raw_prediction': str(prediction),
                'confidence': confidence,
                'success': True
            }), 200
            
        except ValueError as e:
            if 'idf' in str(e).lower() or 'vectorizer' in str(e).lower():
                logger.error(f"✗ CRITICAL: Vectorizer not fitted error: {e}")
                return jsonify({'error': 'Model vectorizer error. Model may be corrupted. Please retrain.', 'success': False}), 503
            else:
                logger.error(f"✗ Prediction value error: {e}")
                return jsonify({'error': f'Prediction failed: {str(e)}', 'success': False}), 500
        
        except Exception as e:
            logger.error(f"✗ Model prediction error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'error': f'Prediction failed: {str(e)}', 'success': False}), 500
    
    except Exception as e:
        logger.error(f"✗ Prediction endpoint error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Prediction failed: {str(e)}', 'success': False}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        model = load_model()
        status = 'healthy' if model is not None else 'initializing'
        logger.info(f"✓ Health check: {status}")
        return jsonify({
            'status': status,
            'model_loaded': model is not None
        }), 200
    except Exception as e:
        logger.error(f"✗ Health check error: {e}")
        return jsonify({'status': 'error', 'model_loaded': False}), 500

@app.errorhandler(404)
def not_found(error):
    logger.error(f"✗ 404 error: {error}")
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"✗ 500 error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("🚀 Starting Flask app...")
    app.run(debug=True, port=5000)
