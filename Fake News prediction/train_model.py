import pandas as pd
import string
import nltk
from nltk.corpus import stopwords
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os

# Download stopwords if not present
nltk.download('stopwords', quiet=True)

def load_data():
    print("Loading data...")
    # Paths - data can be in parent dir or current dir
    fake_path = "../Fake/Fake.csv" if os.path.exists("../Fake/Fake.csv") else "Fake/Fake.csv"
    true_path = "True/True.csv"
    output_path = "output/output.csv"
    
    print("Looking for data files...")
    print(f"Fake path: {fake_path}")
    print(f"True path: {true_path}")
    
    if not os.path.exists(fake_path):
        print(f"[ERROR] {fake_path} not found.")
        return None
    if not os.path.exists(true_path):
        print(f"[ERROR] {true_path} not found.")
        return None
    
    print("[OK] Loading datasets...")
        
    fake = pd.read_csv(fake_path)
    true = pd.read_csv(true_path)
    
    # Try loading output.csv if it exists, otherwise ignore (optional data)
    try:
        if os.path.exists(output_path):
            web_scrapper_data = pd.read_csv(output_path)
            # Ensure it has the same structure if we are going to use it, 
            # or simply use fake/true as the main dataset. 
            # The notebook concatenates it. Let's inspect columns briefly in code or just proceed safely.
            # Notebook logic:
            # fake['target'] = 'fake'
            # true['target'] = 'true'
            # data = pd.concat([fake, true, web_scrapper_data])
            # This implies web_scrapper_data likely has 'text' and 'target' cols or similar structure if it works in concat without error.
            # For simplicity and robustness, I will stick to Fake and True if output is weird, 
            # but let's try to include it as per notebook.
        else:
            web_scrapper_data = pd.DataFrame()
    except Exception as e:
        print(f"Skipping output.csv due to error: {e}")
        web_scrapper_data = pd.DataFrame()

    fake['target'] = 'fake'
    true['target'] = 'true'
    
    # Concatenate
    data = pd.concat([fake, true, web_scrapper_data]).reset_index(drop=True)
    return data

def preprocess_data(data):
    """Minimal preprocessing - just combine title and text, remove unnecessary columns"""
    print("Preprocessing data...")
    from sklearn.utils import shuffle
    data = shuffle(data)
    data = data.reset_index(drop=True)
    
    # Merge title and text if title exists
    if 'title' in data.columns:
        print("  Merging Title and Text...")
        data['text'] = data['title'].fillna('') + " " + data['text'].fillna('')

    # Drop irrelevant columns if they exist
    for col in ["title", "subject", "date"]:
        if col in data.columns:
            data.drop([col], axis=1, inplace=True)
    
    # IMPORTANT: Don't manually preprocess text - let TfidfVectorizer handle it
    # This ensures consistency between training and prediction
    print("  Preprocessing complete (TF-IDF vectorizer will handle text cleaning)")
    
    return data

def train_model():
    data = load_data()
    if data is None:
        return

    data = preprocess_data(data)
    
    print("Training model...")
    X_train, X_test, y_train, y_test = train_test_split(data['text'], data.target, test_size=0.2, random_state=42)
    
    # Pipeline with TF-IDF Vectorizer for preprocessing and style detection
    # min_df=5 removes rare words (like specific names not seen often) to reduce overfitting to specific events
    # ngram_range=(1, 3) captures phrases "official sources said", "death toll", etc.
    # lowercase=True ensures consistent lowercasing
    # strip_accents='unicode' handles special characters
    
    pipe = Pipeline([
        ('tfidf', TfidfVectorizer(
            ngram_range=(1, 3),
            min_df=5,
            max_df=0.9,
            lowercase=True,
            stop_words='english',
            strip_accents='unicode',
            max_features=5000
        )),
        ('model', PassiveAggressiveClassifier(
            max_iter=50,
            random_state=42,
            n_jobs=-1
        ))
    ])
    
    print("Fitting pipeline...")
    model = pipe.fit(X_train, y_train)
    
    print("Evaluating model...")
    prediction = model.predict(X_test)
    acc = accuracy_score(y_test, prediction)
    print(f"✓ Model Accuracy: {acc*100:.2f}%")
    
    # Save model
    joblib.dump(model, 'fake_news_model.pkl')
    print("✓ Model saved as 'fake_news_model.pkl'")
    
    # Print model info for debugging
    print("\n" + "="*50)
    print("MODEL PIPELINE INFO:")
    print("="*50)
    print(f"Pipeline steps: {pipe.named_steps.keys()}")
    print(f"TF-IDF Vocabulary size: {len(pipe.named_steps['tfidf'].vocabulary_)}")
    print(f"Model type: {type(pipe.named_steps['model'])}")
    print("="*50 + "\n")

if __name__ == "__main__":
    train_model()
