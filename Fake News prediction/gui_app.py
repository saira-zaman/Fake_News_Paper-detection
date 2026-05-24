import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import joblib
import pandas as pd
import string
import nltk
from nltk.corpus import stopwords
import os
import threading

# Color Scheme
PRIMARY_COLOR = "#2C3E50"
SECONDARY_COLOR = "#3498DB"
SUCCESS_COLOR = "#27AE60"
DANGER_COLOR = "#E74C3C"
WARNING_COLOR = "#F39C12"
LIGHT_BG = "#ECF0F1"
TEXT_COLOR = "#2C3E50"
WHITE = "#FFFFFF"

# Ensure stopwords are downloaded
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    try:
        nltk.download('stopwords', quiet=True)
    except:
        pass

model_cache = None

def load_model():
    """Load model with error handling"""
    global model_cache
    try:
        if model_cache is not None:
            return model_cache
            
        if os.path.exists('fake_news_model.pkl'):
            model_cache = joblib.load('fake_news_model.pkl')
            return model_cache
        else:
            model_path = os.path.join(os.path.dirname(__file__), 'fake_news_model.pkl')
            if os.path.exists(model_path):
                model_cache = joblib.load(model_path)
                return model_cache
        return None
    except Exception as e:
        raise Exception(f"Model loading failed: {str(e)}")

def preprocess_text(text):
    """Preprocess text with error handling"""
    try:
        text = str(text).lower()
        diff = [char for char in text if char not in string.punctuation]
        text = ''.join(diff)
        stop = stopwords.words('english')
        text = ' '.join([word for word in text.split() if word not in stop])
        return text
    except Exception as e:
        raise Exception(f"Text preprocessing failed: {str(e)}")

def predict_news():
    """Predict news in background thread"""
    threading.Thread(target=predict_news_thread, daemon=True).start()

def predict_news_thread():
    """Background thread for prediction"""
    article_content = text_area.get("1.0", "end-1c").strip()
    
    if not article_content:
        messagebox.showwarning("Input Error", "Please enter news article text to analyze.")
        return

    if len(article_content) < 10:
        messagebox.showwarning("Input Error", "Please enter at least 10 characters of text.")
        return

    try:
        # Show processing status
        result_label.config(text="⏳ Analyzing...", fg=WARNING_COLOR)
        confidence_label.config(text="")
        root.update()
        
        # Load model
        model = load_model()
        if model is None:
            messagebox.showerror("Model Error", "Model file not found.\nPlease run 'train_model.py' first.")
            result_label.config(text="")
            return

        # Preprocess
        processed_text = preprocess_text(article_content)
        
        # Predict with probability
        prediction = model.predict([processed_text])[0]
        probabilities = model.predict_proba([processed_text])[0]
        
        # Get probability scores
        fake_prob = probabilities[0] if prediction == 'fake' else probabilities[1]
        real_prob = probabilities[1] if prediction == 'fake' else probabilities[0]
        confidence = max(probabilities) * 100
        
        # Display result
        if prediction == 'fake':
            result_label.config(text="⚠️ FAKE NEWS DETECTED", fg=DANGER_COLOR)
            result_box.config(bg=DANGER_COLOR)
            status_text = "This article appears to be FAKE NEWS"
        else:
            result_label.config(text="✓ REAL NEWS", fg=SUCCESS_COLOR)
            result_box.config(bg=SUCCESS_COLOR)
            status_text = "This article appears to be REAL NEWS"
        
        confidence_label.config(
            text=f"{status_text}\nConfidence: {confidence:.1f}%",
            fg=TEXT_COLOR
        )
        
    except Exception as e:
        messagebox.showerror("Error", f"Prediction failed: {str(e)}")
        result_label.config(text="")
        confidence_label.config(text="")

def clear_text():
    """Clear input and results"""
    text_area.delete("1.0", tk.END)
    result_label.config(text="")
    confidence_label.config(text="")
    result_box.config(bg=LIGHT_BG)

# Setup UI
root = tk.Tk()
root.title("Fake News Detection System")
root.geometry("800x750")
root.configure(bg=PRIMARY_COLOR)

# Top Frame with Header
top_frame = tk.Frame(root, bg=SECONDARY_COLOR, height=80)
top_frame.pack(fill=tk.X, pady=0)
top_frame.pack_propagate(False)

header = tk.Label(
    top_frame, 
    text="🔍 Fake News Detector", 
    font=("Segoe UI", 28, "bold"),
    bg=SECONDARY_COLOR,
    fg=WHITE
)
header.pack(pady=15)

subtitle = tk.Label(
    top_frame,
    text="Analyze news articles to detect authenticity",
    font=("Segoe UI", 10),
    bg=SECONDARY_COLOR,
    fg=LIGHT_BG
)
subtitle.pack()

# Main Content Frame
content_frame = tk.Frame(root, bg=PRIMARY_COLOR)
content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

# Input Label
input_label = tk.Label(
    content_frame,
    text="📝 Enter or Paste News Article:",
    font=("Segoe UI", 12, "bold"),
    bg=PRIMARY_COLOR,
    fg=LIGHT_BG
)
input_label.pack(anchor=tk.W, pady=(0, 8))

# Text Area with scrollbar
text_frame = tk.Frame(content_frame, bg=WHITE)
text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

text_area = scrolledtext.ScrolledText(
    text_frame,
    height=12,
    width=85,
    font=("Consolas", 10),
    bg=WHITE,
    fg=TEXT_COLOR,
    relief=tk.FLAT,
    bd=0,
    padx=10,
    pady=10
)
text_area.pack(fill=tk.BOTH, expand=True)

# Button Frame
button_frame = tk.Frame(content_frame, bg=PRIMARY_COLOR)
button_frame.pack(fill=tk.X, pady=(0, 15))

analyze_btn = tk.Button(
    button_frame,
    text="🔬 Analyze News",
    font=("Segoe UI", 11, "bold"),
    bg=SECONDARY_COLOR,
    fg=WHITE,
    command=predict_news,
    relief=tk.FLAT,
    cursor="hand2",
    padx=20,
    pady=10
)
analyze_btn.pack(side=tk.LEFT, padx=(0, 10))

clear_btn = tk.Button(
    button_frame,
    text="🗑️ Clear",
    font=("Segoe UI", 11, "bold"),
    bg=WARNING_COLOR,
    fg=WHITE,
    command=clear_text,
    relief=tk.FLAT,
    cursor="hand2",
    padx=20,
    pady=10
)
clear_btn.pack(side=tk.LEFT)

# Result Box
result_box = tk.Frame(content_frame, bg=LIGHT_BG, relief=tk.FLAT)
result_box.pack(fill=tk.X, pady=(0, 10))

result_label = tk.Label(
    result_box,
    text="",
    font=("Segoe UI", 18, "bold"),
    bg=LIGHT_BG,
    fg=TEXT_COLOR,
    pady=15
)
result_label.pack()

confidence_label = tk.Label(
    result_box,
    text="",
    font=("Segoe UI", 11),
    bg=LIGHT_BG,
    fg=TEXT_COLOR,
    pady=10
)
confidence_label.pack()

# Footer Frame
footer_frame = tk.Frame(root, bg=PRIMARY_COLOR)
footer_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=20, pady=10)

footer_label = tk.Label(
    footer_frame,
    text="💡 Tip: Use longer text for better accuracy | Powered by Logistic Regression",
    font=("Segoe UI", 9),
    bg=PRIMARY_COLOR,
    fg=LIGHT_BG
)
footer_label.pack()

# Hover effects for buttons
def on_analyze_hover(event):
    analyze_btn.config(bg="#2980B9")

def on_analyze_leave(event):
    analyze_btn.config(bg=SECONDARY_COLOR)

def on_clear_hover(event):
    clear_btn.config(bg="#D68910")

def on_clear_leave(event):
    clear_btn.config(bg=WARNING_COLOR)

analyze_btn.bind("<Enter>", on_analyze_hover)
analyze_btn.bind("<Leave>", on_analyze_leave)
clear_btn.bind("<Enter>", on_clear_hover)
clear_btn.bind("<Leave>", on_clear_leave)

# Start application
try:
    root.mainloop()
except Exception as e:
    messagebox.showerror("Fatal Error", f"Application error: {str(e)}")
    root.destroy()
