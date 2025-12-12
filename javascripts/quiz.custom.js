// quiz.custom.js — MkDocs Quiz enhancements
// - Submit-all + reset, score top & bottom (pass >= 70%)
// - Shuffle questions & answers
// - One attempt per question (locks after submit)
// - Whole-row click selection
// - Inline explainers: [why: ...] per option; fallback to question content for correct answers
// - Minimal marking: mark only the chosen row (green if correct, red if wrong)

(function () {
  const TOP_BAR_ID = "quiz-top-actions";
  const BOTTOM_BAR_ID = "quiz-bottom-actions";
  const SCORE_TOP_ID = "quiz-score-top";
  const SCORE_BOTTOM_ID = "quiz-score-bottom";
  const GROUP_ID = "quiz-group";
  const EXPLAIN_CLASS = "quiz-explain-inline";
  const PASS_PCT = 70;

  /* ---------------- DOM helpers ---------------- */

  function rowFor(input) {
    // Prefer the label that visually wraps the option
    const wrapLabel = input.closest("label");
    if (wrapLabel) return wrapLabel;
    // Otherwise try the parent or adjacent label
    const parent = input.parentElement;
    if (parent && parent.querySelector("label")) return parent;
    const sib = input.nextElementSibling;
    if (sib && sib.tagName === "LABEL") return sib.parentElement || sib;
    return parent || input;
  }

  function getAnswerInputs(fieldset) {
    return Array.from(fieldset.querySelectorAll('input[name="answer"]'));
  }

  // Extract ANY [why: ...] from the label HTML (wherever it appears),
  // store as data-why on the row, and strip it from the visible HTML.
  function extractWhy(row) {
    const html = row.innerHTML;
    const first = html.match(/\[why:\s*([\s\S]*?)\]/i);
    if (first) row.dataset.why = (row.dataset.why || first[1].trim());
    const cleaned = html.replace(/\s*\[why:\s*([\s\S]*?)\]\s*/gi, "");
    if (cleaned !== html) row.innerHTML = cleaned;
  }

  function primeRows(fieldset) {
    getAnswerInputs(fieldset).forEach((inp) => {
      const row = rowFor(inp);
      row.classList.add("quiz-row");
      extractWhy(row);

      // Make the whole row clickable without blocking the input's own events
      row.addEventListener("click", (e) => {
        if (fieldset.classList.contains("locked")) return;
        // Let native clicks on the input work normally
        if (e.target === inp) return;
        // Ignore clicks on links
        if (e.target.closest("a")) return;

        if (inp.type === "radio") {
          inp.checked = true;
        } else if (inp.type === "checkbox") {
          inp.checked = !inp.checked;
        }
        // Bubble change for any listeners
        inp.dispatchEvent(new Event("change", { bubbles: true }));
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

  // Shuffle answer rows within a fieldset
  function shuffleAnswers(fieldset) {
    const rows = Array.from(new Set(getAnswerInputs(fieldset).map((inp) => rowFor(inp))));
    shuffle(rows).forEach((row) => fieldset.appendChild(row));
  }

  // Ensure all .quiz blocks live under a container so we can reorder questions
  function ensureGroup(quizzes) {
    let group = document.getElementById(GROUP_ID);
    if (!group) {
      group = document.createElement("div");
      group.id = GROUP_ID;
      const first = quizzes[0];
      first.parentNode.insertBefore(group, first);
      quizzes.forEach((q) => group.appendChild(q));
    }
    return group;
  }

  function shuffleQuestions(group) {
    const qs = Array.from(group.querySelectorAll(".quiz"));
    shuffle(qs).forEach((q) => group.appendChild(q));
  }

  function clearMarks(fieldset) {
    fieldset.querySelectorAll(".quiz-row.correct, .quiz-row.wrong")
      .forEach((el) => el.classList.remove("correct", "wrong"));
  }

  function removeInlineExplainers(quizBlock) {
    quizBlock.querySelectorAll("." + EXPLAIN_CLASS).forEach((el) => el.remove());
  }

  function computeCorrect(fieldset, form) {
    const selected = form.querySelectorAll('input[name="answer"]:checked');
    const correct = fieldset.querySelectorAll('input[name="answer"][correct]');
    // Correct only if at least one selected, counts match, and every selected is marked correct
    let ok = selected.length > 0 && selected.length === correct.length;
    selected.forEach((s) => { if (!s.hasAttribute("correct")) ok = false; });
    return ok;
  }

  // Build and insert an inline explainer card after the host row.
  // variant = 'correct' | 'wrong'
  // Prefers per-option data-why; for correct w/o why, falls back to question <section> content.
  function addInlineExplainer(quizBlock, hostRow, variant) {
    if (!hostRow) return;
    const why = hostRow.dataset?.why?.trim();

    const section = quizBlock.querySelector("section");
    const hasSection = section && section.innerHTML.trim().length > 0;

    // Wrong without a per-option reason -> no explainer
    if (!why && variant !== "correct") return;
    // Correct without why and without section -> nothing
    if (!why && variant === "correct" && !hasSection) return;

    const card = document.createElement("div");
    card.className = `${EXPLAIN_CLASS} ${variant}`;
    card.setAttribute("role", "note");

    const head = document.createElement("div");
    head.className = EXPLAIN_CLASS + "__head";
    head.innerHTML =
      variant === "correct"
        ? `<span class="${EXPLAIN_CLASS}__icon" aria-hidden="true">✓</span><strong>That's right!</strong>`
        : `<span class="${EXPLAIN_CLASS}__icon" aria-hidden="true">✗</span><strong>Not quite</strong>`;

    const body = document.createElement("div");
    body.className = EXPLAIN_CLASS + "__body";

    if (why) {
      const p = document.createElement("p");
      p.textContent = why;
      body.appendChild(p);
    } else if (variant === "correct" && hasSection) {
      const div = document.createElement("div");
      div.innerHTML = section.innerHTML; // trusted author content
      body.appendChild(div);
    }

    card.appendChild(head);
    card.appendChild(body);
    hostRow.insertAdjacentElement("afterend", card);
  }

  function markPerQuestion(quizBlock, fieldset, form, ok) {
    clearMarks(fieldset);
    removeInlineExplainers(quizBlock);

    // Hide the plugin's section explainer; we show our own inline card
    const defaultSection = quizBlock.querySelector("section");
    if (defaultSection) defaultSection.classList.add("hidden");

    const chosen = form.querySelector('input[name="answer"]:checked');
    if (!chosen) return;

    const row = rowFor(chosen);
    if (ok) {
      row.classList.add("correct");
      addInlineExplainer(quizBlock, row, "correct");
    } else {
      row.classList.add(chosen.hasAttribute("correct") ? "correct" : "wrong");
      addInlineExplainer(quizBlock, row, "wrong");
    }
  }

  function lockQuestion(fieldset, form) {
    getAnswerInputs(fieldset).forEach((inp) => (inp.disabled = true));
    fieldset.classList.add("locked");
    const submit = form.querySelector('button[type="submit"], input[type="submit"]');
    if (submit) submit.disabled = true;
    form.dataset.attempted = "1";
  }

  function unlockQuestion(quizBlock, fieldset, form) {
    getAnswerInputs(fieldset).forEach((inp) => { inp.disabled = false; inp.checked = false; });
    fieldset.classList.remove("locked");
    clearMarks(fieldset);
    removeInlineExplainers(quizBlock);
    const submit = form.querySelector('button[type="submit"], input[type="submit"]');
    if (submit) submit.disabled = false;
    form.dataset.attempted = "0";
    const explain = quizBlock.querySelector("section");
    if (explain) explain.classList.add("hidden");
  }

  // Remove plugin's per-question submit handler; keep the DOM but disable it
  function stripPluginSubmit(form) {
    const clone = form.cloneNode(true);           // clone to drop existing handlers
    form.parentNode.replaceChild(clone, form);
    const nativeBtn = clone.querySelector('button[type="submit"], input[type="submit"]');
    if (nativeBtn) nativeBtn.classList.add("quiz-native-submit"); // hidden via CSS
    // Also prevent default if someone triggers submit on the form
    clone.addEventListener("submit", (e) => e.preventDefault());
    return clone;
  }

  /* ---------------- actions / score ---------------- */

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
    submitAll.textContent = "Submit All";

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
    const percent = total > 0 ? Math.round((correct / total) * 100) : 0;
    const txt = `Score: ${correct}/${total} (${percent}%)`;
    [el1, el2].forEach((el) => {
      el.textContent = txt;
      el.classList.toggle("good", percent >= PASS_PCT);
      el.classList.toggle("bad", percent < PASS_PCT);
      el.style.display = "inline-flex";
    });
  }

  /* ---------------- bootstrap ---------------- */

  function init() {
    const quizzes = Array.from(document.querySelectorAll(".quiz"));
    if (!quizzes.length) return;

    const group = ensureGroup(quizzes);
    shuffleQuestions(group);

    const quizBlocks = Array.from(group.querySelectorAll(".quiz"));
    const forms = quizBlocks
      .map((q) => q.querySelector("form"))
      .filter(Boolean)
      .map((form) => stripPluginSubmit(form));

    const fieldsets = forms.map((f) => f.querySelector("fieldset"));

    // Prep answers and shuffle
    fieldsets.forEach((fs) => {
      primeRows(fs);
      shuffleAnswers(fs);
    });

    const { reset, scoreTop } = mountTopBar(group);
    const { submitAll, scoreBottom } = mountBottomBar(group);

    submitAll.onclick = () => {
      let correctCount = 0;
      const total = fieldsets.length;

      fieldsets.forEach((fs, i) => {
        const block = quizBlocks[i];
        const form = forms[i];
        const ok = computeCorrect(fs, form);
        if (ok) correctCount += 1;
        markPerQuestion(block, fs, form, ok);
        lockQuestion(fs, form);
      });

      setScore(scoreTop, scoreBottom, correctCount, total);
      submitAll.disabled = true;
      // Jump to top so the score pill is immediately visible
      window.scrollTo({ top: 0, behavior: "smooth" });
    };

    reset.onclick = () => {
      fieldsets.forEach((fs, i) => unlockQuestion(quizBlocks[i], fs, forms[i]));
      shuffleQuestions(group);
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

  // Support MkDocs Material's SPA navigation
  if (typeof document$ !== "undefined" && document$.subscribe) {
    document$.subscribe(init);
  } else {
    document.addEventListener("DOMContentLoaded", init);
  }
})();
