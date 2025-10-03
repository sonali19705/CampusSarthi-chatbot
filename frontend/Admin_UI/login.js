const popup = document.getElementById('popupError');

function showError(message) {
  popup.textContent = message;
  popup.classList.add('show');
  setTimeout(() => popup.classList.remove('show'), 3000);
}

document.getElementById("loginBtn").addEventListener("click", async () => {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();

  if (!username || !password) {
    showError("Enter username and password!");
    return;
  }

  try {
    const res = await fetch("http://127.0.0.1:8000/admin/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });

    if (res.ok) {
      localStorage.setItem("isAdmin", "true");
      window.location.href = "/admin_ui/admin.html"; // redirect to admin dashboard
    } else {
      const data = await res.json();
      showError(data.detail || "Invalid credentials!");
    }
  } catch (err) {
    showError("Server error!");
    console.error(err);
  }
});
