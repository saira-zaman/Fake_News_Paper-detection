# 🔍 Fake News Detection System

A Machine Learning-powered web application that detects fake news using Logistic Regression. The project includes both a desktop GUI (tkinter) and a modern web interface built with Flask.

## Features

✨ **Modern UI** - Beautiful, responsive web interface
🤖 **ML-Powered** - Logistic Regression model trained on news datasets
📊 **Confidence Scoring** - Shows prediction confidence percentage
🚀 **Fast Analysis** - Real-time text analysis
📱 **Responsive Design** - Works on desktop and mobile devices
🔐 **Robust Error Handling** - Comprehensive error management

## Tech Stack

- **Backend**: Flask, Python 3.8+
- **ML**: Scikit-learn, NLTK, Pandas
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Deployment**: Vercel
- **Desktop GUI**: Tkinter

## Installation

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/saira-zaman/Fake_News_Paper-detection.git
cd Fake_News_Paper-detection
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
cd "Fake News prediction"
pip install -r requirements.txt
```

4. **Train the model** (if model doesn't exist)
```bash
python train_model.py
```

### Running the Application

**Option 1: Desktop GUI (Tkinter)**
```bash
python gui_app.py
```

**Option 2: Web Server (Local)**
```bash
python app.py
# Open browser at http://localhost:5000
```

**Option 3: Batch Script (Windows)**
```bash
run_project.bat
```

## Deployment to Vercel

### Prerequisites
- Vercel account (https://vercel.com)
- GitHub repository with the code
- Model file (`fake_news_model.pkl`) in repository

### Steps

1. **Push to GitHub**
```bash
git add .
git commit -m "Ready for Vercel deployment"
git push origin main
```

2. **Connect to Vercel**
   - Go to https://vercel.com/import
   - Select your GitHub repository
   - Choose "Fake News prediction" as root directory (if needed)
   - Click "Deploy"

3. **Configure Environment**
   - No special environment variables needed
   - Vercel will automatically install dependencies from `requirements.txt`

4. **Deploy**
   - Vercel will automatically build and deploy
   - Your app will be available at `https://your-project-name.vercel.app`

## API Endpoints

### GET `/`
Serves the web interface

### GET `/api/health`
Health check endpoint
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### POST `/api/predict`
Predicts if text is real or fake news

**Request:**
```json
{
  "text": "Your news article text here..."
}
```

**Response:**
```json
{
  "result": "🟢 REAL NEWS",
  "raw_prediction": "true",
  "confidence": "92.5%",
  "success": true
}
```

## Model Information

- **Algorithm**: Logistic Regression
- **Training Data**: Real and Fake news datasets
- **Features**: Text preprocessing with NLTK
- **Accuracy**: ~95% (on test set)

## File Structure

```
Fake News prediction/
├── app.py                    # Flask web application
├── gui_app.py                # Tkinter desktop application
├── train_model.py            # Model training script
├── fake_news_model.pkl       # Trained model (generated)
├── requirements.txt          # Python dependencies
├── templates/
│   └── index.html           # Web UI
├── static/
│   ├── css/style.css        # Styling
│   └── js/main.js           # Frontend logic
├── Fake/Fake.csv            # Fake news dataset
└── True/True.csv            # Real news dataset
```

## Usage Examples

### Python API
```python
import joblib
from app import preprocess_text

# Load model
model = joblib.load('fake_news_model.pkl')

# Preprocess text
text = "Your news article..."
processed = preprocess_text(text)

# Predict
prediction = model.predict([processed])[0]
print(f"Prediction: {'REAL' if prediction == 'true' else 'FAKE'}")
```

### cURL
```bash
curl -X POST https://your-app.vercel.app/api/predict \
  -H "Content-Type: application/json" \
  -d '{"text":"Your news text here..."}'
```

## Troubleshooting

### Model Not Found
- Ensure `fake_news_model.pkl` is in the `Fake News prediction/` directory
- Run `python train_model.py` to generate the model

### Import Errors
- Install missing packages: `pip install -r requirements.txt`
- Make sure you're in the virtual environment

### Vercel Deployment Issues
- Check logs: `vercel logs`
- Ensure `vercel.json` is configured correctly
- Model file must be in repository

## Performance

- **Analysis Time**: ~500-1000ms per article
- **Accuracy**: ~95% on test set
- **Confidence Range**: 0-100%

## Future Improvements

- [ ] Add more ML models (SVM, Random Forest)
- [ ] Implement model versioning
- [ ] Add multi-language support
- [ ] Create mobile app
- [ ] Add explainability features
- [ ] Real-time model updates

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Author

**Saira Zaman**
- GitHub: [@saira-zaman](https://github.com/saira-zaman)

## Support

For issues and questions:
- Open an issue on GitHub
- Email: [your-email]

---

**Made with ❤️ by the Fake News Detection Team**

Last Updated: May 2026
