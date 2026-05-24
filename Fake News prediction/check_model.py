import joblib
import os

print('=== CHECKING MODEL INTEGRITY ===\n')

if os.path.exists('fake_news_model.pkl'):
    try:
        model = joblib.load('fake_news_model.pkl')
        print(f'✓ Model loaded: {type(model)}')
        print(f'✓ Model steps: {list(model.named_steps.keys())}')
        
        vectorizer = model.named_steps['tfidf']
        classifier = model.named_steps['model']
        print(f'✓ Vectorizer: {type(vectorizer).__name__}')
        print(f'✓ Classifier: {type(classifier).__name__}')
        
        # Check if fitted
        has_idf = hasattr(vectorizer, 'idf_')
        print(f'✓ Vectorizer fitted: {has_idf}')
        
        if has_idf:
            print(f'✓ IDF vector shape: {vectorizer.idf_.shape}')
            print(f'✓ Vocabulary size: {len(vectorizer.vocabulary_)}')
        else:
            print('✗ WARNING: Vectorizer NOT fitted!')
        
        # Test prediction
        test_text = 'this is a fake news article about something'
        pred = model.predict([test_text])
        print(f'✓ Test prediction: {pred}')
        
        print('\n✅ MODEL IS OK!')
        
    except Exception as e:
        print(f'✗ MODEL ERROR: {e}')
        import traceback
        traceback.print_exc()
else:
    print('✗ Model file NOT found!')
