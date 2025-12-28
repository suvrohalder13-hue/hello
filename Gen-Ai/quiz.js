// Quiz Page JavaScript

let currentQuiz = null;
let currentAnswers = [];
let quizStartTime = null;
let timerInterval = null;

document.addEventListener('DOMContentLoaded', function() {
    const quizForm = document.getElementById('quiz-form');
    quizForm.addEventListener('submit', generateQuiz);
});

async function generateQuiz(e) {
    e.preventDefault();

    const subject = document.getElementById('quiz-subject').value;
    const numQuestions = parseInt(document.getElementById('num-questions').value);

    if (!subject) {
        showToast('Please select a subject', 'warning');
        return;
    }

    // Show loading
    document.getElementById('quiz-setup').style.display = 'none';
    document.getElementById('loading').style.display = 'block';
    document.getElementById('quiz-container').style.display = 'none';

    try {
        const result = await apiCall('/api/quiz', 'POST', {
            subject: subject,
            num_questions: numQuestions
        });

        currentQuiz = result;
        currentAnswers = new Array(result.questions.length).fill(null);
        quizStartTime = Date.now();

        displayQuiz(result);
        document.getElementById('loading').style.display = 'none';
        document.getElementById('quiz-container').style.display = 'block';
        startTimer();

    } catch (error) {
        document.getElementById('loading').style.display = 'none';
        showError('Error generating quiz: ' + error.message);
    }
}

function displayQuiz(quiz) {
    document.getElementById('quiz-subject-display').textContent = quiz.subject;

    const container = document.getElementById('questions-container');
    container.innerHTML = '';

    quiz.questions.forEach((q, index) => {
        const questionDiv = document.createElement('div');
        questionDiv.className = 'mb-4 pb-3 border-bottom';

        let optionsHtml = '';
        Object.entries(q.options).forEach(([key, value]) => {
            optionsHtml += `
                <div class="form-check">
                    <input class="form-check-input" type="radio" name="question-${index}" 
                           id="option-${index}-${key}" value="${key}" 
                           onchange="selectAnswer(${index}, '${key}')">
                    <label class="form-check-label" for="option-${index}-${key}">
                        <strong>${key}.</strong> ${value}
                    </label>
                </div>
            `;
        });

        questionDiv.innerHTML = `
            <h6 class="mb-3"><strong>Q${index + 1}:</strong> ${q.question}</h6>
            <div class="options ml-3">
                ${optionsHtml}
            </div>
        `;

        container.appendChild(questionDiv);
    });
}

function selectAnswer(questionIndex, answer) {
    currentAnswers[questionIndex] = answer;
}

function startTimer() {
    let seconds = 0;
    timerInterval = setInterval(() => {
        seconds++;
        document.getElementById('timer').textContent = formatTime(seconds);
    }, 1000);
}

function submitQuiz() {
    if (!currentQuiz) return;

    // Check if all questions are answered
    const unanswered = currentAnswers.filter(a => a === null).length;
    if (unanswered > 0) {
        if (!confirm(`You have ${unanswered} unanswered question(s). Submit anyway?`)) {
            return;
        }
    }

    clearInterval(timerInterval);

    // Calculate score
    let score = 0;
    const correctAnswers = currentQuiz.questions.map(q => q.correct);

    currentAnswers.forEach((answer, index) => {
        if (answer === correctAnswers[index]) {
            score++;
        }
    });

    const timeTaken = Math.floor((Date.now() - quizStartTime) / 1000);

    // Save to backend
    saveQuizResult(score, correctAnswers, timeTaken);

    // Display results
    displayResults(score, currentQuiz.questions.length, timeTaken);
}

async function saveQuizResult(score, correctAnswers, timeTaken) {
    try {
        await apiCall('/api/submit-quiz', 'POST', {
            quiz_id: currentQuiz.quiz_id,
            subject: currentQuiz.subject,
            answers: currentAnswers,
            correct_answers: correctAnswers,
            time_taken: timeTaken
        });
    } catch (error) {
        console.error('Error saving quiz result:', error);
    }
}

function displayResults(score, total, timeTaken) {
    const percentage = (score / total * 100).toFixed(1);

    document.getElementById('quiz-container').style.display = 'none';
    document.getElementById('results-section').style.display = 'block';

    document.getElementById('final-score').textContent = score;
    document.getElementById('final-total').textContent = total;
    document.getElementById('percentage').textContent = percentage;
    document.getElementById('final-time').textContent = formatTime(timeTaken);

    // Result message
    let message = '';
    if (percentage >= 80) {
        message = '<p class="text-success"><strong>Excellent! Great job!</strong></p>';
    } else if (percentage >= 60) {
        message = '<p class="text-info"><strong>Good! Keep practicing!</strong></p>';
    } else {
        message = '<p class="text-warning"><strong>Need more practice. Review concepts!</strong></p>';
    }
    document.getElementById('result-message').innerHTML = message;

    // Display answer review
    displayAnswerReview(score);

    showToast(`Quiz Complete! Score: ${percentage}%`, 'success');
}

function displayAnswerReview(score) {
    const reviewDiv = document.getElementById('review-section');
    reviewDiv.innerHTML = '';

    currentQuiz.questions.forEach((q, index) => {
        const userAnswer = currentAnswers[index];
        const correctAnswer = q.correct;
        const isCorrect = userAnswer === correctAnswer;

        const reviewItem = document.createElement('div');
        reviewItem.className = `mb-3 p-3 rounded ${isCorrect ? 'bg-success bg-opacity-10' : 'bg-danger bg-opacity-10'}`;

        const statusIcon = isCorrect ? '✓' : '✗';
        const statusClass = isCorrect ? 'text-success' : 'text-danger';

        reviewItem.innerHTML = `
            <h6 class="${statusClass}"><strong>${statusIcon} Q${index + 1}:</strong> ${q.question}</h6>
            <div class="mt-2">
                ${userAnswer ? 
                    `<p>Your Answer: <strong>${userAnswer}. ${q.options[userAnswer]}</strong></p>` 
                    : '<p>Your Answer: <strong class="text-danger">Not answered</strong></p>'
                }
                <p>Correct Answer: <strong>${correctAnswer}. ${q.options[correctAnswer]}</strong></p>
                ${q.explanation ? `<p class="text-muted"><em>${q.explanation}</em></p>` : ''}
            </div>
        `;

        reviewDiv.appendChild(reviewItem);
    });
}

function resetQuiz() {
    currentQuiz = null;
    currentAnswers = [];
    quizStartTime = null;
    clearInterval(timerInterval);

    document.getElementById('quiz-setup').style.display = 'block';
    document.getElementById('results-section').style.display = 'none';
    document.getElementById('quiz-container').style.display = 'none';
    document.getElementById('loading').style.display = 'none';

    // Reset form
    document.getElementById('quiz-form').reset();

    showToast('Ready for another quiz!', 'info');
}

function showError(message) {
    const errorDiv = document.getElementById('error-section');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    document.getElementById('loading').style.display = 'none';
    document.getElementById('quiz-setup').style.display = 'block';
}
