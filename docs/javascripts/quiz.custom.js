(function () {
  const TOP_BAR_ID = "quiz-top-actions";
  const BOTTOM_BAR_ID = "quiz-bottom-actions";
  const SCORE_TOP_ID = "quiz-score-top";
  const SCORE_BOTTOM_ID = "quiz-score-bottom";
  const GROUP_ID = "quiz-group";

  /* ---------------- helpers ---------------- */
  function rowFor(input) {
    const wrapLabel = input.closest("label");
    if (wrapLabel) return wrapLabel;
    const parent = input.parentElement;
    if (parent && parent.querySelector("label")) return parent;
    const sib = input.nextElementSibling;
    if (sib && sib.tagName === "LABEL") return sib.parentElement || sib;
    return parent || input;
  }

  function getAnswerInputs(fieldset) {
    return Array.from(fieldset.querySelectorAll('input[name="answer"]'));
  }

  function primeRows(fieldset) {
    getAnswerInputs(fieldset).forEach((inp) => {
      const row = rowFor(inp);
      row.classList.add("quiz-row");

      // Whole-row click to toggle selection
      row.addEventListener("click", (e) => {
        if (fieldset.classList.contains("locked")) return;
        if (e.target.closest("a")) return;
        if (e.target !== inp) {
          if (inp.type === "radio") inp.checked = true;
          else if (inp.type === "checkbox") inp.checked = !inp.checked;
          inp.dispatchEvent(new Event("change", { bubbles: true }));
          e.preventDefault();
        }
      });
    });
  }

  // Fisher–Yates shuffle
  function shuffle(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }

  // Shuffle the answer rows within one question (fieldset)
  function shuffleAnswers(fieldset) {
    const inputs = getAnswerInputs(fieldset);
    const rows = Array.from(new Set(inputs.map((inp) => rowFor(inp))));
    shuffle(rows).forEach((row) => fieldset.appendChild(row));
  }

  // Create a wrapper around all quiz blocks so we can reorder safely
  function ensureGroup(quizzes) {
    let group = document.getElementById(GROUP_ID);
    if (!group) {
      group = document.createElement("div");
      group.id = GROUP_ID;
      const first = quizzes[0];
      first.parentNode.insertBefore(group, first);
      quizzes.forEach((q) => group.appendChild(q)); // preserve initial order
    }
    return group;
  }

  // Shuffle the questions (i.e., the .quiz blocks) inside the group
  function shuffleQuestions(group) {
    const qs = Array.from(group.querySelectorAll(".quiz"));
    shuffle(qs).forEach((q) => group.appendChild(q));
  }

  function clearMarks(fieldset) {
    fieldset.querySelectorAll(".quiz-row.correct, .quiz-row.wrong")
      .forEach((el) => el.classList.remove("correct", "wrong"));
  }

  function computeCorrect(fieldset, form) {
    const selected = form.querySelectorAll('input[name="answer"]:checked');
    const correct = fieldset.querySelectorAll('input[name="answer"][correct]');
    let ok = selected.length === correct.length && selected.length > 0;
    selected.forEach((s) => { if (!s.hasAttribute("correct")) ok = false; });
    return ok;
  }

  // Minimal marking: when correct, only show the chosen correct option(s)
  function markPerQuestion(fieldset, form, ok) {
    clearMarks(fieldset);
    const explain = fieldset.parentElement.querySelector("section");

    if (ok) {
      const selected = form.querySelectorAll('input[name="answer"]:checked');
      selected.forEach((s) => rowFor(s).classList.add("correct"));
      if (explain && explain.textContent.trim()) explain.classList.remove("hidden");
      else if (explain) explain.classList.add("hidden");
    } else {
      const selected = form.querySelectorAll('input[name="answer"]:checked');
      selected.forEach((s) =>
        rowFor(s).classList.add(s.hasAttribute("correct") ? "correct" : "wrong")
      );
      if (explain) explain.classList.add("hidden");
    }
  }

  function lockQuestion(fieldset, form) {
    getAnswerInputs(fieldset).forEach((inp) => (inp.disabled = true));
    fieldset.classList.add("locked");
    const submit = form.querySelector('button[type="submit"], input[type="submit"]');
    if (submit) submit.disabled = true;
    form.dataset.attempted = "1";
  }

  function unlockQuestion(fieldset, form) {
    getAnswerInputs(fieldset).forEach((inp) => {
      inp.disabled = false;
      inp.checked = false;
    });
    fieldset.classList.remove("locked");
    clearMarks(fieldset);
    const submit = form.querySelector('button[type="submit"], input[type="submit"]');
    if (submit) submit.disabled = false;
    form.dataset.attempted = "0";
    const explain = fieldset.parentElement.querySelector("section");
    if (explain) explain.classList.add("hidden");
  }

  function stripPluginSubmit(form) {
    const clone = form.cloneNode(true);
    form.parentNode.replaceChild(clone, form);
    const nativeBtn = clone.querySelector('button[type="submit"], input[type="submit"]');
    if (nativeBtn) nativeBtn.classList.add("quiz-native-submit"); // hidden via CSS
    return clone;
  }

  /* -------- page chrome (top/bottom bars + score) -------- */
  function mountTopBar(group) {
    let bar = document.getElementById(TOP_BAR_ID);
    if (bar) bar.remove();
    bar = document.createElement("div");
    bar.id = TOP_BAR_ID;
    bar.className = "quiz-actions quiz-actions--top";

    const scoreTop = document.createElement("div");
    scoreTop.id = SCORE_TOP_ID;
    scoreTop.className = "quiz-score";
    scoreTop.style.display = "none";

    const reset = document.createElement("button");
    reset.type = "button";
    reset.className = "quiz-btn quiz-btn--ghost";
    reset.textContent = "Reset";

    bar.appendChild(scoreTop);
    bar.appendChild(reset);
    group.parentNode.insertBefore(bar, group);
    return { reset, scoreTop };
  }

  function mountBottomBar(group) {
    let bar = document.getElementById(BOTTOM_BAR_ID);
    if (bar) bar.remove();
    bar = document.createElement("div");
    bar.id = BOTTOM_BAR_ID;
    bar.className = "quiz-actions quiz-actions--bottom";

    const submitAll = document.createElement("button");
    submitAll.type = "button";
    submitAll.className = "quiz-btn quiz-btn--primary";
    submitAll.textContent = "Submit";

    const scoreBottom = document.createElement("div");
    scoreBottom.id = SCORE_BOTTOM_ID;
    scoreBottom.className = "quiz-score";
    scoreBottom.style.display = "none";

    bar.appendChild(submitAll);
    bar.appendChild(scoreBottom);
    group.parentNode.insertBefore(bar, group.nextSibling);
    return { submitAll, scoreBottom };
  }

  function setScore(el1, el2, correct, total) {
    const percent = Math.round((correct / total) * 100);
    const txt = `Score: ${correct}/${total} (${percent}%)`;
    [el1, el2].forEach((el) => {
      el.textContent = txt;
      el.classList.toggle("good", percent >= 70);
      el.classList.toggle("bad", percent < 70);
      el.style.display = "inline-flex";
    });
  }

  /* ---------------- bootstrap ---------------- */
  function init() {
    const quizzes = Array.from(document.querySelectorAll(".quiz"));
    if (!quizzes.length) return;

    // Wrap all quiz blocks into a dedicated group and shuffle their order
    const group = ensureGroup(quizzes);
    shuffleQuestions(group);

    // Re-query quizzes after shuffle
    const quizBlocks = Array.from(group.querySelectorAll(".quiz"));

    // Prepare forms / fieldsets
    const forms = quizBlocks
      .map((q) => q.querySelector("form"))
      .filter(Boolean)
      .map((form) => stripPluginSubmit(form));

    const fieldsets = forms.map((f) => f.querySelector("fieldset"));

    // Build row affordances and shuffle answers for each question
    fieldsets.forEach((fs) => { primeRows(fs); shuffleAnswers(fs); });

    // Bars anchored to the group
    const { reset, scoreTop } = mountTopBar(group);
    const { submitAll, scoreBottom } = mountBottomBar(group);

    // Submit
    submitAll.onclick = () => {
      let correctCount = 0;
      const total = fieldsets.length;

      fieldsets.forEach((fs, i) => {
        const form = forms[i];
        const ok = computeCorrect(fs, form);
        if (ok) correctCount += 1;
        markPerQuestion(fs, form, ok);
        lockQuestion(fs, form);
      });

      setScore(scoreTop, scoreBottom, correctCount, total);
      submitAll.disabled = true;
    };

    // Reset (also reshuffle questions & answers)
    reset.onclick = () => {
      fieldsets.forEach((fs, i) => unlockQuestion(fs, forms[i]));
      shuffleQuestions(group);

      // After reshuffle, we should also reshuffle answers in each question
      Array.from(group.querySelectorAll(".quiz fieldset")).forEach((fs) => shuffleAnswers(fs));

      [scoreTop, scoreBottom].forEach((el) => {
        el.style.display = "none";
        el.textContent = "";
        el.classList.remove("good", "bad");
      });
      const btn = document.querySelector(`#${BOTTOM_BAR_ID} .quiz-btn--primary`);
      if (btn) btn.disabled = false;
      window.scrollTo({ top: 0, behavior: "smooth" });
    };
  }

  // Material for MkDocs SPA aware
  if (typeof document$ !== "undefined" && document$.subscribe) {
    document$.subscribe(init);
  } else {
    document.addEventListener("DOMContentLoaded", init);
  }
})();
