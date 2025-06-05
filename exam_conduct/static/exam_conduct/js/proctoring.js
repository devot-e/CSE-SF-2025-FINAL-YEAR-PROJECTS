document.addEventListener('DOMContentLoaded', function() {
    // Timer implementation
    let timeLeft = duration;
    const timerElement = document.getElementById('timer');

    function updateTimer() {
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        timerElement.textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;

        if (timeLeft <= 0) {
            submitExam();
        } else {
            timeLeft--;
            setTimeout(updateTimer, 1000);
        }
    }

    updateTimer();

    // Proctoring implementation
    let fullscreen = false;

    function checkFullscreen() {
        if (!document.fullscreenElement) {
            if (fullscreen) {
                // User exited fullscreen
                recordViolation('fullscreen_exit');
                showWarning();
            }
            fullscreen = false;
        } else {
            fullscreen = true;
        }
    }

    function recordViolation(type) {
        fetch(`/exam/session/${sessionId}/proctoring/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({type: type})
        });
    }

    function showWarning() {
        const warning = document.getElementById('warning-message');
        warning.style.display = 'block';
        setTimeout(() => {
            warning.style.display = 'none';
        }, 3000);
    }

    // Event listeners
    document.addEventListener('fullscreenchange', checkFullscreen);
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            recordViolation('tab_switch');
            showWarning();
        }
    });

    // Submit exam
    document.getElementById('submit-btn').addEventListener('click', submitExam);

    function submitExam() {
        const form = document.getElementById('exam-form');
        const answers = {};

        document.querySelectorAll('.question').forEach(question => {
            const qId = question.dataset.id;
            const selected = question.querySelector('input[type="radio"]:checked');
            answers[qId] = selected ? selected.value : null;
        });

        fetch(`/exam/session/${sessionId}/submit/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({answers: answers})
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.href = '/exam-complete/'; // Create this view
            }
        });
    }

    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
