// Query Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('question-form');
    form.addEventListener('submit', askQuestion);

    // Check URL parameters for pre-selected subject
    const urlParams = new URLSearchParams(window.location.search);
    const subject = urlParams.get('subject');
    if (subject) {
        document.getElementById('subject').value = subject;
    }
});

async function askQuestion(e) {
    e.preventDefault();

    const subject = document.getElementById('subject').value;
    const question = document.getElementById('question').value;

    if (!subject || !question) {
        showToast('Please fill all fields', 'warning');
        return;
    }

    // Show loading
    document.getElementById('loading').style.display = 'block';
    document.getElementById('answer-section').style.display = 'none';
    document.getElementById('error-section').style.display = 'none';

    try {
        const result = await apiCall('/api/ask', 'POST', {
            question: question,
            subject: subject,
            top_k: 3
        });

        displayAnswer(result);
        document.getElementById('loading').style.display = 'none';
        document.getElementById('answer-section').style.display = 'block';
    } catch (error) {
        document.getElementById('loading').style.display = 'none';
        showError('Error: ' + error.message);
    }
}

function displayAnswer(result) {
    // Display answer
    document.getElementById('answer-text').textContent = result.answer;

    // Display confidence
    const confidence = (result.confidence * 100).toFixed(1);
    const confidenceEl = document.getElementById('confidence');
    confidenceEl.textContent = confidence + '%';

    // Color code confidence
    if (confidence >= 80) {
        confidenceEl.className = 'text-success font-weight-bold';
    } else if (confidence >= 60) {
        confidenceEl.className = 'text-warning font-weight-bold';
    } else {
        confidenceEl.className = 'text-danger font-weight-bold';
    }

    // Display sources
    const sourcesDiv = document.getElementById('sources');
    sourcesDiv.innerHTML = '';
    
    if (result.sources && result.sources.length > 0) {
        result.sources.forEach((source, index) => {
            const sourceEl = document.createElement('div');
            sourceEl.className = 'mb-2 p-2 bg-light rounded';
            sourceEl.innerHTML = `<strong>Source ${index + 1}:</strong> <br><small>${source}</small>`;
            sourcesDiv.appendChild(sourceEl);
        });
    } else {
        sourcesDiv.innerHTML = '<p class="text-muted">No sources available</p>';
    }
}

function resetForm() {
    document.getElementById('question-form').reset();
    document.getElementById('answer-section').style.display = 'none';
    document.getElementById('loading').style.display = 'none';
    document.getElementById('error-section').style.display = 'none';
}

function showError(message) {
    const errorDiv = document.getElementById('error-section');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    showToast('Error: ' + message, 'danger');
}
