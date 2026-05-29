from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import joblib
import os
import logging
import sys
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Model cache
model_cache = None

# Common English stopwords (hardcoded fallback) - No longer needed since TfidfVectorizer handles preprocessing
# Removed to reduce code complexity

def load_stopwords():
    """Removed - TfidfVectorizer handles preprocessing internally"""
    return set()

stopwords_list = set()

def load_model():
    """Load model with caching and better error handling"""
    global model_cache
    if model_cache is not None:
        return model_cache
    
    try:
        # Try multiple paths for different deployment scenarios
        possible_paths = [
            'fake_news_model.pkl',
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fake_news_model.pkl'),
            os.path.join(os.getcwd(), 'fake_news_model.pkl'),
            os.path.join(os.getcwd(), 'Fake News prediction', 'fake_news_model.pkl'),
            '/vercel/path0/fake_news_model.pkl',  # Vercel root path
            '/vercel/path0/Fake News prediction/fake_news_model.pkl',  # Vercel nested path
            '/tmp/fake_news_model.pkl'  # Temp fallback
        ]
        
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")
        logger.info(f"Attempting to load model from {len(possible_paths)} possible locations...")
        
        for path in possible_paths:
            try:
                if os.path.exists(path):
                    logger.info(f"✓ Found model at: {path}")
                    model = joblib.load(path)
                    logger.info(f"✓ Model loaded from: {path}")
                    
                    # Validate model is properly fitted by checking it can predict
                    try:
                        test_pred = model.predict(['test'])
                        logger.info(f"✓ Model validation successful - test prediction: {test_pred}")
                        model_cache = model
                        return model_cache
                    except Exception as validation_err:
                        logger.error(f"✗ Model loaded from {path} but validation failed: {validation_err}")
            except Exception as e:
                logger.debug(f"  Could not load from {path}: {e}")
        
        logger.error(f"✗ Model not found in any of these locations:")
        for path in possible_paths:
            logger.error(f"  - {path}")
        return None
    except Exception as e:
        logger.error(f"✗ Error loading model: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def preprocess_text(text):
    """Return text as-is - TfidfVectorizer handles preprocessing"""
    try:
        # Just trim whitespace - let the pipeline handle vectorization
        text = str(text).strip()
        if not text:
            raise ValueError("Text is empty after cleaning")
        return text
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
        
        # Predict (model pipeline handles preprocessing internally)
        try:
            logger.info(f"✓ Attempting prediction on text: {text[:50]}...")
            prediction = model.predict([text])[0]
            logger.info(f"✓ Prediction result: {prediction}")
            
            # Get confidence scores
            try:
                proba = model.predict_proba([text])[0]
                confidence_score = float(max(proba) * 100)
                confidence = f"{confidence_score:.1f}%"
            except Exception as conf_err:
                logger.warning(f"Could not get confidence score: {conf_err}")
                confidence = "N/A"  # Fallback confidence
            
            # Determine result - handle both 'true'/'fake' and 1/0 outputs
            is_real = str(prediction).lower() in ['true', '1', 'real']
            result_display = "🟢 REAL NEWS" if is_real else "🔴 FAKE NEWS"
            
            logger.info(f"✓ Prediction successful: {result_display}")
            
            return jsonify({
                'result': result_display,
                'raw_prediction': str(prediction),
                'confidence': confidence,
                'success': True
            }), 200
            
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


@app.route('/api/extract-text', methods=['POST'])
def extract_text():
    """Extract text from uploaded file (txt, pdf, docx). Returns JSON {success, text}.
    The client uses this to upload DOCX/PDF and get extracted text for analysis.
    """
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400

        f = request.files['file']
        filename = f.filename or ''
        if not filename:
            return jsonify({'success': False, 'error': 'Invalid file name'}), 400

        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

        # Limit file size server-side (optional) - reject > 10MB
        try:
            f.stream.seek(0, io.SEEK_END)
            size = f.stream.tell()
            f.stream.seek(0)
            if size > 10 * 1024 * 1024:
                return jsonify({'success': False, 'error': 'File too large (max 10MB)'}), 400
        except Exception:
            # If seeking fails, continue and rely on client-side check
            pass

        text = ''
        # TXT
        if ext in ('txt', 'text'):
            data = f.read()
            try:
                text = data.decode('utf-8')
            except Exception:
                text = data.decode('latin-1', errors='ignore')

        # DOCX
        elif ext == 'docx':
            try:
                from docx import Document
                f.stream.seek(0)
                doc = Document(f.stream)
                paras = [p.text for p in doc.paragraphs if p.text]
                text = '\n'.join(paras)
            except Exception as e:
                logger.error(f"DOCX extraction error: {e}")
                return jsonify({'success': False, 'error': 'Failed to extract text from DOCX'}), 500

        # PDF
        elif ext == 'pdf':
            try:
                from PyPDF2 import PdfReader
                f.stream.seek(0)
                reader = PdfReader(f.stream)
                pages = []
                for page in reader.pages:
                    try:
                        ptext = page.extract_text()
                        if ptext:
                            pages.append(ptext)
                    except Exception:
                        continue
                text = '\n'.join(pages)
            except Exception as e:
                logger.error(f"PDF extraction error: {e}")
                return jsonify({'success': False, 'error': 'Failed to extract text from PDF'}), 500

        else:
            return jsonify({'success': False, 'error': 'Unsupported file type'}), 400

        if not text or text.strip() == '':
            return jsonify({'success': False, 'error': 'No text extracted from file'}), 400

        return jsonify({'success': True, 'text': text}), 200

    except Exception as e:
        logger.error(f"✗ Extract-text endpoint error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

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
