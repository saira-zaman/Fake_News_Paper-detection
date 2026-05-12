import tkinter as tk
from tkinter import messagebox
import joblib
import pandas as pd
import string
import nltk
from nltk.corpus import stopwords
import os

# Ensure stopwords are downloaded
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def preprocess_text(text):
    # Lowercase
    text = str(text).lower()
    
    # Remove punctuation
    diff = [char for char in text if char not in string.punctuation]
    text = ''.join(diff)
    
    # Remove stopwords
    stop = stopwords.words('english')
    text = ' '.join([word for word in text.split() if word not in stop])
    
    return text

def predict_news():
    article_content = text_area.get("1.0", "end-1c")
    
    if not article_content.strip():
        messagebox.showwarning("Input Error", "Please enter some text to analyze.")
        return

    try:
        if not os.path.exists('fake_news_model.pkl'):
            # Try to see if we can locate it relative to script if run from elsewhere
            model_path = os.path.join(os.path.dirname(__file__), 'fake_news_model.pkl')
            if not os.path.exists(model_path):
                messagebox.showerror("Model Error", "Model file 'fake_news_model.pkl' not found.\nPlease run 'train_model.py' first to generate the model.")
                return
            model = joblib.load(model_path)
        else:
            model = joblib.load('fake_news_model.pkl')
    except Exception as e:
        messagebox.showerror("Model Error", f"Could not load model: {e}")
        return

    # Preprocess
    processed_text = preprocess_text(article_content)
    
    # Predict
    # The model pipe expects an iterable of strings
    prediction = model.predict([processed_text])[0]
    
    # Show result
    result_text = "FAKE" if prediction == 'fake' else "REAL"
    color = "red" if result_text == "FAKE" else "green"
    
    result_label.config(text=f"Prediction: {result_text}", fg=color)


# Setup basic UI
root = tk.Tk()
root.title("Fake News Classification")
root.geometry("600x400")

# Header
header = tk.Label(root, text="Fake News Detector", font=("Helvetica", 24, "bold"))
header.pack(pady=10)

# Input Area
input_label = tk.Label(root, text="Paste News Article Text Below:", font=("Helvetica", 12))
input_label.pack(pady=5)

text_area = tk.Text(root, height=10, width=60, font=("Helvetica", 10))
text_area.pack(pady=5)

# Buttons
analyze_btn = tk.Button(root, text="Analyze News", font=("Helvetica", 12, "bold"), bg="blue", fg="white", command=predict_news)
analyze_btn.pack(pady=10)

# Result
result_label = tk.Label(root, text="", font=("Helvetica", 16, "bold"))
result_label.pack(pady=10)

# Footer
footer = tk.Label(root, text="Project: Fake News Detection using Logistic Regression", font=("Helvetica", 8))
footer.pack(side=tk.BOTTOM, pady=5)

root.mainloop()
