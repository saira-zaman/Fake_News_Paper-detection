function analyzeNews() {
    const text = document.getElementById('newsText').value;
    if (!text.trim()) {
        alert("Please enter some text to analyze.");
        return;
    }

    // Show loader
    document.getElementById('resultSection').classList.remove('hidden');
    document.getElementById('loader').classList.remove('hidden');
    document.getElementById('resultContent').classList.add('hidden');

    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: text }),
    })
        .then(response => response.json())
        .then(data => {
            // Hide loader
            document.getElementById('loader').classList.add('hidden');
            document.getElementById('resultContent').classList.remove('hidden');

            const iconBox = document.getElementById('resultIcon');
            const title = document.getElementById('resultTitle');
            const desc = document.getElementById('resultDesc');

            if (data.prediction === 'REAL') {
                iconBox.innerHTML = '<i class="fas fa-check-circle real-news"></i>';
                title.textContent = "Likely Authentic";
                title.className = "real-news";
                desc.innerHTML = `Our analysis suggests this article uses patterns consistent with real news.<br><strong>Confidence: ${data.confidence.toFixed(1)}%</strong>`;
            } else {
                iconBox.innerHTML = '<i class="fas fa-exclamation-triangle fake-news"></i>';
                title.textContent = "Likely Fake";
                title.className = "fake-news";
                desc.innerHTML = `This content exhibits patterns often found in unreliable or fake news sources.<br><strong>Confidence: ${data.confidence.toFixed(1)}%</strong>`;
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert("An error occurred while analyzing.");
            document.getElementById('loader').classList.add('hidden');
        });
}

function clearText() {
    document.getElementById('newsText').value = '';
    document.getElementById('resultSection').classList.add('hidden');
}
