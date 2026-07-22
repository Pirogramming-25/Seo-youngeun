function getCookie(name) {
  const item = document.cookie
    .split(";")
    .map((value) => value.trim())
    .find((value) => value.startsWith(`${name}=`));
  return item ? decodeURIComponent(item.split("=").slice(1).join("=")) : null;
}

function initAiTool() {
  const form = document.querySelector("#ai-form");
  if (!form) return;

  const input = document.querySelector("#text-input");
  const button = document.querySelector("#run-button");
  const loading = document.querySelector("#loading");
  const error = document.querySelector("#error");
  const result = document.querySelector("#result");
  const content = document.querySelector("#result-content");
  const history = document.querySelector("#history-list");
  const counter = document.querySelector("#counter");

  input.addEventListener("input", () => {
    counter.textContent = `${input.value.length} / ${input.maxLength}자`;
  });

  const percent = (value) => `${(value * 100).toFixed(2)}%`;
  const escapeHtml = (value) => {
    const element = document.createElement("div");
    element.textContent = value;
    return element.innerHTML;
  };

  function scoreBlock(title, data) {
    const rows = data.scores
      .map((item) => `<li><span>${escapeHtml(item.label)}</span><b>${percent(item.score)}</b></li>`)
      .join("");
    return `<h3>${title}</h3><ul class="scores">${rows}</ul>`;
  }

  function render(data) {
    let html = "";
    if (data.summary) {
      html += `<h3>요약 결과</h3><p>${escapeHtml(data.summary)}</p>`;
      if (data.summary_ratio !== undefined) {
        html += `<dl><dt>원문 길이</dt><dd>${data.original_length}자</dd><dt>요약문 길이</dt><dd>${data.summary_length}자</dd><dt>요약 비율</dt><dd>${data.summary_ratio.toFixed(2)}%</dd></dl>`;
      }
    }
    if (data.sentiment) html += scoreBlock("감정 분석", data.sentiment);
    if (data.toxicity) html += scoreBlock("유해 표현 분석", data.toxicity);
    if (data.scores) {
      let title = "점수";
      if (data.label && form.dataset.task === "sentiment") {
        title = `감정: ${escapeHtml(data.label)} / 신뢰도: ${percent(data.score)}`;
      } else if (data.label && form.dataset.task === "moderate") {
        title = `최고 위험 레이블: ${escapeHtml(data.label)} / 위험 점수: ${percent(data.score)}`;
      }
      html += scoreBlock(title, data);
    }
    content.innerHTML = html;
    result.hidden = false;
  }

  function addHistory(item) {
    history.querySelector(".empty")?.remove();
    const row = document.createElement("li");
    row.innerHTML = `<p>${escapeHtml(item.input_text.slice(0, 90))}</p><strong>${escapeHtml(item.output_text.slice(0, 160))}</strong>`;
    history.prepend(row);
    while (history.children.length > 5) history.lastElementChild.remove();
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    error.hidden = true;
    result.hidden = true;
    loading.hidden = false;
    button.disabled = true;
    input.disabled = true;

    try {
      const response = await fetch(form.dataset.endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ text: input.value }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "요청에 실패했습니다.");
      render(data.result);
      addHistory(data.history);
    } catch (requestError) {
      error.textContent = requestError.message;
      error.hidden = false;
    } finally {
      loading.hidden = true;
      button.disabled = false;
      input.disabled = false;
    }
  });
}
