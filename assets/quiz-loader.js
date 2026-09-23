/* Download the question bank only when someone starts the quiz. */
(function () {
  var start = document.getElementById('quiz-start');
  if (!start) return;
  start.addEventListener('click', function loadQuiz() {
    start.removeEventListener('click', loadQuiz);
    start.disabled = true;
    var script = document.createElement('script');
    script.src = '/assets/quiz.js';
    script.onload = function () { start.disabled = false; start.click(); };
    script.onerror = function () { start.disabled = false; start.addEventListener('click', loadQuiz); };
    document.head.appendChild(script);
  });
}());
