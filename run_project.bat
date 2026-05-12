@echo off
echo Installing dependencies...
pip install pandas scikit-learn nltk joblib

echo.
echo Training the model...
python train_model.py

if exist fake_news_model.pkl (
    echo.
    echo Model trained successfully! Launching Application...
    python gui_app.py
) else (
    echo.
    echo Training failed. Please check the errors above.
)

pause
