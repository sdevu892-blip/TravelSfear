document.addEventListener("DOMContentLoaded", () => {
  const chatForm = document.getElementById("chatForm");
  const chatBox = document.getElementById("chatBox");
  if (chatForm) {
    chatForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const input = document.getElementById("message");
      const message = input.value.trim();
      if (!message) return;
      chatBox.innerHTML += `<div class="chat-msg chat-user">${escapeHtml(message)}</div>`;
      input.value = "";
      const response = await fetch("/api/chatbot", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({message})
      });
      const data = await response.json();
      chatBox.innerHTML += `<div class="chat-msg chat-ai">${escapeHtml(data.reply || "Sorry, I could not answer.")}</div>`;
      chatBox.scrollTop = chatBox.scrollHeight;
    });
  }

  const weatherForm = document.getElementById("weatherForm");
  if (weatherForm) {
    weatherForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const city = document.getElementById("city").value;
      const box = document.getElementById("weatherResult");
      box.innerHTML = "Loading...";
      const response = await fetch(`/api/weather?city=${encodeURIComponent(city)}`);
      const data = await response.json();
      if (data.error) {
        box.innerHTML = `<div class="alert alert-danger">${escapeHtml(data.error)}</div>`;
      } else {
        box.innerHTML = `<div class="card"><div class="card-body">
          <h4>${escapeHtml(data.city)}</h4>
          <h2>${data.temperature}°C</h2>
          <p>${escapeHtml(data.description)}</p>
          ${data.humidity !== undefined ? `<p>Humidity: ${data.humidity}%</p>` : ""}
          ${data.demo ? `<small class="text-muted">${escapeHtml(data.description)}</small>` : ""}
        </div></div>`;
      }
    });
  }
});

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, m => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"
  }[m]));
}
