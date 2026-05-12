# Fake News Detection Using Logistic Regression

A machine learning project that detects and classifies news articles as **fake** or **true** using Logistic Regression algorithm.

## 🎯 Project Overview

This project implements an intelligent fake news detection system that analyzes textual content and predicts whether a news article is authentic or fabricated. It features both a command-line interface and a graphical user interface for easy interaction.

## ✨ Features

- **Logistic Regression Model** - Fast and efficient classification algorithm
- **Pre-trained Model** - Ready-to-use `fake_news_model.pkl` for instant predictions
- **Multiple Interfaces**:
  - Command-line interface (CLI)
  - Graphical User Interface (GUI)
  - Web-based Flask application
- **Large Dataset** - Trained on comprehensive fake and true news datasets
- **High Accuracy** - Reliable classification performance
- **Easy to Deploy** - Simple Python setup and execution

## 📋 Requirements

- Python 3.7 or higher
- Libraries:
  - `numpy` - Numerical computations
  - `pandas` - Data manipulation
  - `scikit-learn` - Machine learning algorithms
  - `jupyter` - Interactive notebooks
  - `flask` - Web framework
  - `tkinter` - GUI framework (usually included with Python)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/saira-zaman/Fake_News_Paper-detection.git
cd Fake_News_Paper-detection
```

### 2. Install Dependencies
```bash
pip install numpy pandas scikit-learn jupyter flask
```

## 📖 How to Use

### Option 1: Run the Web Application
```bash
python app.py
```
Then open your browser and navigate to `http://localhost:5000`

### Option 2: Run the GUI Application
```bash
python gui_app.py
```

### Option 3: Run the Batch Script
```bash
run_project.bat
```

### Option 4: Training a New Model
```bash
python train_model.py
```

## 📁 Project Structure

```
Fake News Detection/
│
├── app.py                 # Flask web application
├── gui_app.py             # Tkinter GUI application
├── train_model.py         # Model training script
├── project.ipynb          # Jupyter notebook with analysis
├── fake_news_model.pkl    # Pre-trained model file
│
├── Fake/                  # Fake news dataset
│   └── Fake.csv
├── True/                  # True news dataset
│   └── True.csv
│
├── static/                # Static files for web app
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
│
├── templates/             # HTML templates for Flask
│   └── index.html
│
├── output/                # Output results
│   └── output.csv
│
└── README.md              # This file
```

## 🧠 Model Information

- **Algorithm**: Logistic Regression
- **Training Data**: Fake.csv and True.csv datasets
- **Features**: TF-IDF vectorization of text content
- **Output**: Binary classification (Fake/True)
- **Format**: Pickle file (fake_news_model.pkl)

## 📊 Dataset

- **Fake News Dataset**: `Fake/Fake.csv` (~59 MB)
- **True News Dataset**: `True/True.csv` (~51 MB)
- **Total Samples**: Thousands of labeled news articles

## 🔄 Workflow

1. **Data Loading** → Load fake and true news datasets
2. **Text Processing** → Clean and preprocess text
3. **Feature Extraction** → Convert text to TF-IDF vectors
4. **Model Training** → Train Logistic Regression classifier
5. **Prediction** → Classify new articles as fake or true

## 💡 Usage Examples

### Using the GUI
1. Launch `gui_app.py`
2. Enter or paste news text
3. Click "Predict"
4. View the classification result

### Using the Web App
1. Run `app.py`
2. Open browser to `http://localhost:5000`
3. Paste article text
4. Submit for analysis
5. View prediction result

## ⚙️ Configuration

### For Flask App (app.py)
- Default host: `localhost`
- Default port: `5000`
- Debug mode: Can be toggled in code

### For Training (train_model.py)
- Test size: 20%
- Random state: 42
- Model: Logistic Regression

## 📈 Performance

The model achieves reliable accuracy on both training and test datasets. For detailed performance metrics, refer to `project.ipynb`.

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change port in app.py or use:
python app.py --port 5001
```

### Model File Not Found
- Ensure `fake_news_model.pkl` is in the project root
- Retrain the model using `train_model.py`

### Missing Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt  # if available
```

## 📝 Notes

- Large CSV files (>50MB) are included. Consider using Git LFS for optimal performance
- The pre-trained model is optimized for English text
- Text preprocessing includes lowercasing and stop word removal

## 👤 Author

**Saira Zaman**

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest improvements
- Submit pull requests

## 📧 Contact

For questions or suggestions, please reach out via GitHub.

---

**Last Updated**: May 2026

**Happy Detecting!** 🔍✅
