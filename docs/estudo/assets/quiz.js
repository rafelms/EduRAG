// Quiz de recuperação: cada <div class="question" data-answer="N"> tem botões
// .options > button e um <p class="feedback"> com data-ok e data-bad.
// N é o índice (a partir de 0) da alternativa certa.
(function () {
  const css = `
  .quiz .question { margin: 1.4rem 0; }
  .quiz .prompt { font-weight: 600; margin-bottom: .5rem; }
  .quiz .options { display: grid; gap: .4rem; }
  .quiz button { font: inherit; font-size: .92rem; text-align: left; padding: .5rem .75rem; border: 1px solid var(--rule);
    background: var(--bg); color: var(--fg); border-radius: 4px; cursor: pointer; }
  .quiz button:hover:not(:disabled) { border-color: var(--accent); }
  .quiz button.right { background: var(--ok-bg); border-color: var(--ok); color: var(--ok); }
  .quiz button.wrong { background: var(--bad-bg); border-color: var(--bad); color: var(--bad); }
  .quiz .feedback { font-size: .9rem; margin: .5rem 0 0; min-height: 1em; }
  .quiz .score { font-weight: 600; margin-top: 1rem; }`;
  const style = document.createElement("style");
  style.textContent = css;
  document.head.appendChild(style);

  document.querySelectorAll(".quiz").forEach((quiz) => {
    const questions = quiz.querySelectorAll(".question");
    let answered = 0, correct = 0;
    const score = document.createElement("p");
    score.className = "score";
    quiz.appendChild(score);

    questions.forEach((q) => {
      const answer = Number(q.dataset.answer);
      const buttons = q.querySelectorAll(".options button");
      const feedback = q.querySelector(".feedback");
      buttons.forEach((btn, i) => {
        btn.addEventListener("click", () => {
          const ok = i === answer;
          buttons.forEach((b) => (b.disabled = true));
          btn.classList.add(ok ? "right" : "wrong");
          if (!ok) buttons[answer].classList.add("right");
          feedback.textContent = ok ? feedback.dataset.ok : feedback.dataset.bad;
          answered++;
          if (ok) correct++;
          if (answered === questions.length) {
            score.textContent = `Você acertou ${correct} de ${questions.length}.` +
              (correct === questions.length ? "" : " Releia a seção da que errou e tente de novo amanhã.");
          }
        });
      });
    });
  });
})();
