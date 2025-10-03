// ------------------ SIDEBAR TOGGLE ------------------
function showSection(id, btn) {
  document.querySelectorAll(".form-section").forEach(sec => {
    sec.classList.remove("active");
    sec.style.display = "none";
  });
  const activeSec = document.getElementById(id);
  activeSec.style.display = "block";
  setTimeout(() => activeSec.classList.add("active"), 10);

  document.querySelectorAll(".sidebar button").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
}

// ------------------ STATUS MESSAGES ------------------
function showStatus(id, message) {
  const status = document.getElementById(id);
  status.style.display = "block";
  status.innerText = message;
  setTimeout(() => { status.style.display = "none"; }, 3000);
}

// ------------------ ADMIN SESSION ------------------
document.getElementById("logoutBtn").addEventListener("click", () => {
  localStorage.removeItem("isAdmin");
  window.location.href = "login.html";
});

if (localStorage.getItem("isAdmin") !== "true") {
  window.location.href = "login.html";
}

// ------------------ DASHBOARD STATS ------------------
async function updateStats() {
  try {
    const res = await fetch("http://127.0.0.1:8000/admin/stats");
    if (!res.ok) throw new Error("Failed to fetch stats");
    const data = await res.json();
    document.getElementById("faqCount").innerText = data.faqs || 0;
    document.getElementById("csvCount").innerText = data.csv || 0;
    document.getElementById("pdfCount").innerText = data.pdf || 0;
  } catch (err) { console.error(err); }
}

// ------------------ ADD FAQ ------------------
async function addFAQ() {
  const question = document.getElementById("faqQuestion").value.trim();
  const answer = document.getElementById("faqAnswer").value.trim();
  if (!question || !answer) { 
    alert("Enter both question and answer"); 
    return; 
  }

  try {
    const formData = new FormData();
    formData.append("question", question);
    formData.append("new_answer", answer);

    const res = await fetch("http://127.0.0.1:8000/admin/update_faq", { 
      method: "PUT",
      body: formData
    });

    if (res.ok) {
      showStatus("faqStatus", "✅ FAQ added/updated!");
      document.getElementById("faqQuestion").value = "";
      document.getElementById("faqAnswer").value = "";
      await updateStats();
      await loadFAQs();
    } else {
      const errData = await res.json();
      showStatus("faqStatus", `❌ Error: ${errData.detail || "Operation failed"}`);
    }
  } catch (err) { 
    showStatus("faqStatus", "❌ Server error"); 
    console.error(err); 
  }
}

// ------------------ UPLOAD CSV ------------------
async function uploadCSV() {
  const file = document.getElementById("csvFile").files[0];
  if (!file) { alert("Select CSV"); return; }

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("http://127.0.0.1:8000/admin/upload_faq", { method: "POST", body: formData });
    if (res.ok) {
      const data = await res.json();
      showStatus("csvStatus", `✅ Uploaded: ${file.name}`);
      document.getElementById("csvFile").value = "";
      await loadFAQs();
      await updateStats();
    } else {
      const errData = await res.json();
      showStatus("csvStatus", `❌ Upload failed: ${errData.detail || "Unknown"}`);
    }
  } catch (err) { showStatus("csvStatus", "❌ Server error"); console.error(err); }
}

// ------------------ UPLOAD PDF ------------------
async function uploadPDF() {
  const file = document.getElementById("pdfFile").files[0];
  if (!file) { alert("Select PDF"); return; }

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("http://127.0.0.1:8000/admin/upload_pdf", { method: "POST", body: formData });
    if (res.ok) {
      const data = await res.json();
      showStatus("pdfStatus", `✅ Uploaded: ${file.name}`);
      document.getElementById("pdfFile").value = "";
      await loadFAQs();
      await updateStats();
    } else {
      const errData = await res.json();
      showStatus("pdfStatus", `❌ Upload failed: ${errData.detail || "Unknown error"}`);
    }
  } catch (err) { showStatus("pdfStatus", "❌ Server error"); console.error(err); }
}

// ------------------ MANAGE FAQ ------------------
async function loadFAQs() {
  try {
    const res = await fetch("http://127.0.0.1:8000/admin/get_faqs");
    if (!res.ok) throw new Error("Failed to fetch FAQs");
    const data = await res.json();
    const list = document.getElementById("faqList");
    list.innerHTML = "";

    data.faqs.forEach(faq => {
      const faqDiv = document.createElement("div");
      faqDiv.className = "faq-item";
      faqDiv.innerHTML = `
        <p><strong>Q:</strong> ${faq.question}</p>
        <p><strong>A:</strong> ${faq.answer}</p>
        <button class="updateBtn">Update</button>
        <button class="deleteBtn">Delete</button>
      `;

      // Delete FAQ
      faqDiv.querySelector(".deleteBtn").addEventListener("click", async () => {
        if (!confirm("Delete this FAQ?")) return;
        try {
          const delRes = await fetch(`http://127.0.0.1:8000/admin/delete_faq?question=${encodeURIComponent(faq.question)}`, { method: "DELETE" });
          if (delRes.ok) {
            showStatus("faqStatus", `❌ Deleted: ${faq.question}`);
            await loadFAQs();
            await updateStats();
          } else {
            showStatus("faqStatus", "❌ Delete failed");
          }
        } catch (err) {
          console.error(err);
          showStatus("faqStatus", "❌ Server error");
        }
      });

      // Update FAQ
      faqDiv.querySelector(".updateBtn").addEventListener("click", async () => {
        const newAnswer = prompt("Enter new answer:", faq.answer);
        if (!newAnswer) return;
        try {
          const formData = new FormData();
          formData.append("question", faq.question);
          formData.append("new_answer", newAnswer);

          const updRes = await fetch("http://127.0.0.1:8000/admin/update_faq", { 
            method: "PUT",
            body: formData
          });

          if (updRes.ok) {
            showStatus("faqStatus", `✅ Updated: ${faq.question}`);
            await loadFAQs();
            await updateStats();
          } else {
            showStatus("faqStatus", "❌ Update failed");
          }
        } catch (err) {
          console.error(err);
          showStatus("faqStatus", "❌ Server error");
        }
      });

      list.appendChild(faqDiv);
    });
  } catch (err) { console.error(err); showStatus("faqStatus", "❌ Error loading FAQs"); }
}

// ------------------ SEARCH FAQ ------------------
document.getElementById("faqSearch").addEventListener("input", (e) => {
  const query = e.target.value.toLowerCase();
  document.querySelectorAll("#faqList .faq-item").forEach(item => {
    item.style.display = item.innerText.toLowerCase().includes(query) ? "block" : "none";
  });
});



// ------------------ INITIALIZE ------------------
window.addEventListener("DOMContentLoaded", () => {
  updateStats();
  loadFAQs();
});
