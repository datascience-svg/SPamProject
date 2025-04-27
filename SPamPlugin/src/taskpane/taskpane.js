document.addEventListener("DOMContentLoaded", () => {
    const analyzeBtn = document.getElementById("analyzeBtn");
    const analyzeLatestBtn = document.getElementById("analyzeLatestBtn");
    const resultDiv = document.getElementById("result");
    const loading = document.getElementById("loading");
    const historyDiv = document.getElementById("history");

    const API_BASE = "http://localhost:8000";

    function setLoading(state) {
        loading.classList.toggle("hidden", !state);
    }

    async function loadHistory() {
        try {
            const response = await fetch(`${API_BASE}/history`);
            const history = await response.json();
            historyDiv.innerHTML = "";
            history.reverse().forEach(mail => {
                const item = document.createElement("div");
                item.className = "history-item";
                item.innerHTML = `<strong>${mail.subject}</strong> - ${mail.prediction.toUpperCase()}<br><em>${mail.from}</em>`;
                historyDiv.appendChild(item);
            });
        } catch (err) {
            console.error("Erreur de récupération de l'historique", err);
        }
    }

    analyzeBtn.addEventListener("click", async () => {
        const content = document.getElementById("mailContent").value.trim();
        if (!content) return alert("Veuillez coller le contenu à analyser !");
        setLoading(true);

        try {
            const response = await fetch(`${API_BASE}/analyze-text`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ content })
            });
            const data = await response.json();
            resultDiv.innerHTML = `<strong>Résultat :</strong> ${data.prediction.toUpperCase()}`;
            await loadHistory();
        } catch (error) {
            console.error("Erreur analyse texte", error);
        } finally {
            setLoading(false);
        }
    });

    analyzeLatestBtn.addEventListener("click", async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE}/analyze-latest`);
            const result = await response.json();
            resultDiv.innerHTML = `<strong>Dernier mail analysé :</strong> ${result.subject} → ${result.prediction.toUpperCase()}`;
            await loadHistory();
        } catch (error) {
            console.error("Erreur analyse dernier mail", error);
        } finally {
            setLoading(false);
        }
    });

    // Initial
    loadHistory();
});
