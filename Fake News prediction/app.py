from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
import string
import nltk
from nltk.corpus import stopwords
import os

app = Flask(__name__)

# Load Model
MODEL_PATH = 'fake_news_model.pkl'

def preprocess_text(text):
    # Lowercase
    text = str(text).lower()
    
    # Remove punctuation
    diff = [char for char in text if char not in string.punctuation]
    text = ''.join(diff)
    
    # Remove stopwords
    # Check if stopwords are downloaded
    try:
        stop = stopwords.words('english')
    except LookupError:
        nltk.download('stopwords')
        stop = stopwords.words('english')

    text = ' '.join([word for word in text.split() if word not in stop])
    
    return text

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400

        if not os.path.exists(MODEL_PATH):
            return jsonify({'error': 'Model not trained yet. Please run train_model.py'}), 503

        # Load model lazily to allow training to happen while app starts (though ideally model exists)
        model = joblib.load(MODEL_PATH)
        
        processed_text = preprocess_text(text)
        prediction = model.predict([processed_text])[0]
        
        result = "REAL" if prediction == 'true' else "FAKE" # Adjusting based on train_model.py: true['target'] = 'true'
        # wait, train_model.py says: true['target'] = 'true', fake['target'] = 'fake'
        # prediction will be 'fake' or 'true' string.
        
        result_display = "REAL NEWS" if prediction == 'true' else "FAKE NEWS"
        confidence = "High" # Placeholder as LogisticRegression default predict doesn't give proba without predict_proba
        
        # Try to get probability if possible
        try:
            proba = model.predict_proba([processed_text])[0]
            confidence_score = max(proba) * 100
            confidence = f"{confidence_score:.1f}%"
        except:
            confidence = "N/A"

        return jsonify({
            'result': result_display,
            'raw_prediction': prediction,
            'confidence': confidence
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
