import pandas as pd
import string
import nltk
from nltk.corpus import stopwords
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os

# Download stopwords if not present
nltk.download('stopwords')

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
    print("Preprocessing...")
    from sklearn.utils import shuffle
    data = shuffle(data)
    data = data.reset_index(drop=True)
    
    # Merge title and text if title exists
    if 'title' in data.columns:
        print("Merging Title and Text...")
        data['text'] = data['title'].fillna('') + " " + data['text'].fillna('')

    # Drop irrelevant columns if they exist
    for col in ["title", "subject", "date"]:
        if col in data.columns:
            data.drop([col], axis=1, inplace=True)
            
    # Text cleaning
    data['text'] = data['text'].apply(lambda x: str(x).lower())
    
    def punctuation_removal(text):
        all_list = [char for char in text if char not in string.punctuation]
        clean_str = ''.join(all_list)
        return clean_str

    data['text'] = data['text'].apply(punctuation_removal)
    
    # Stopwords removal
    stop = stopwords.words('english')
    # Using a faster way to remove stopwords might be better for large datasets but let's stick to notebook logic 
    # to maintain consistency, although the lambda with split/join is slow.
    data['text'] = data['text'].apply(lambda x: ' '.join([word for word in x.split() if word not in stop]))
    
    return data

def train_model():
    data = load_data()
    if data is None:
        return

    data = preprocess_data(data)
    
    print("Training model...")
    X_train, X_test, y_train, y_test = train_test_split(data['text'], data.target, test_size=0.2, random_state=42)
    
    # Pipeline with N-gams for style detection
    # min_df=5 removes rare words (like specific names not seen often) to reduce overfitting to specific events
    # ngram_range=(1, 3) captures phrases "official sources said", "death toll", etc.
    from sklearn.feature_extraction.text import TfidfVectorizer
    
    pipe = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 3), min_df=5, max_df=0.9)),
        ('model', PassiveAggressiveClassifier(max_iter=50))
    ])
    
    model = pipe.fit(X_train, y_train)
    
    prediction = model.predict(X_test)
    acc = accuracy_score(y_test, prediction)
    print(f"Model Accuracy: {acc*100:.2f}%")
    
    # Save model
    joblib.dump(model, 'fake_news_model.pkl')
    print("Model saved as 'fake_news_model.pkl'")

if __name__ == "__main__":
    train_model()
