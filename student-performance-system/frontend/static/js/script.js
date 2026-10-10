/* ============================================================
   SPS · static/js/script.js — Flask prediction page
   (frontend/templates/index.html). Same-origin /predict.
   Sections: 1 helpers · 2 interpretation · 3 form submit
   ============================================================ */

// ---------- 1. Helpers ----------
function toggleOther(selectId, inputId) {
    var select = document.getElementById(selectId);
    var input = document.getElementById(inputId);
    if (!select || !input) return;
    if (select.value === "other") {
        input.style.display = "block";
        input.required = true;
    } else {
        input.style.display = "none";
        input.required = false;
        input.value = "";
    }
}

// ---------- 2. Grade interpretation ----------
function getInterpretation(grade) {
    if (grade < 10) return "The student is at risk. Immediate attention to basics, attendance and study routine is needed.";
    if (grade < 13) return "Average performance. Consistent study and revision will push the grade higher.";
    if (grade < 16) return "Good performance. Maintain the routine and practice weak topics.";
    return "Excellent performance. Keep the momentum and try advanced material.";
}

// ---------- 3. Prediction form submit ----------
document.addEventListener("DOMContentLoaded", function () {
    var form = document.getElementById("predictionForm");
    if (!form) return;

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        var loading = document.getElementById("loading");
        var resultCard = document.getElementById("result");
        var formError = document.getElementById("formError");
        if (loading) loading.style.display = "block";
        if (resultCard) resultCard.style.display = "none";
        if (formError) { formError.classList.remove("show"); formError.textContent = ""; }

        function showError(msg) {
            if (formError) {
                formError.textContent = msg;
                formError.classList.add("show");
                formError.scrollIntoView({ behavior: "smooth", block: "nearest" });
            }
        }

        function val(id) {
            var el = document.getElementById(id);
            return el ? el.value : "";
        }
        function intVal(id) {
            return parseInt(val(id), 10);
        }

        var payload = {
            school: val("school"),
            sex: val("sex"),
            age: intVal("age"),
            address: val("address"),
            famsize: val("famsize"),
            Pstatus: val("Pstatus"),
            Medu: intVal("Medu"),
            Fedu: intVal("Fedu"),
            Mjob: val("Mjob"),
            Fjob: val("Fjob"),
            reason: val("reason"),
            guardian: val("guardian"),
            traveltime: intVal("traveltime"),
            studytime: intVal("studytime"),
            failures: intVal("failures"),
            schoolsup: val("schoolsup"),
            famsup: val("famsup"),
            paid: val("paid"),
            activities: val("activities"),
            nursery: val("nursery"),
            higher: val("higher"),
            internet: val("internet"),
            romantic: val("romantic"),
            famrel: intVal("famrel"),
            freetime: intVal("freetime"),
            goout: intVal("goout"),
            Dalc: intVal("Dalc"),
            Walc: intVal("Walc"),
            health: intVal("health"),
            absences: intVal("absences")
        };

        try {
            var res = await fetch("/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            var data = await res.json();
            if (!res.ok) {
                showError(data.error || "Prediction failed. Check inputs.");
                return;
            }
            document.getElementById("grade").textContent = data.predicted_grade;
            document.getElementById("level").textContent = data.performance_level;
            document.getElementById("interpretation").textContent = getInterpretation(data.predicted_grade);
            var list = document.getElementById("recommendations");
            list.innerHTML = "";
            (data.recommendations || []).forEach(function (r) {
                var li = document.createElement("li");
                li.textContent = r;
                list.appendChild(li);
            });
            if (resultCard) {
                resultCard.style.display = "block";
                resultCard.scrollIntoView({ behavior: "smooth" });
            }
        } catch (err) {
            showError("Server error. Is Flask running?");
        } finally {
            if (loading) loading.style.display = "none";
        }
    });
});


// --------------------------------------------------
// 4. Recent predictions (live /history)
// --------------------------------------------------
document.addEventListener("DOMContentLoaded", function () {
    var rows = document.getElementById("histRows");
    if (!rows) return; // not on a page with history

    var count = document.getElementById("histCount");
    var refresh = document.getElementById("refreshHist");

    function esc(s) {
        return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
            return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
        });
    }

    async function loadHistory() {
        rows.innerHTML = '<tr><td colspan="5" class="hist-empty">Loading…</td></tr>';
        try {
            var res = await fetch("/history");
            var data = await res.json();
            var list = data.history || [];
            if (count) count.textContent = list.length + " prediction(s)";
            if (!list.length) {
                rows.innerHTML = '<tr><td colspan="5" class="hist-empty">No predictions yet — submit the form above.</td></tr>';
                return;
            }
            rows.innerHTML = "";
            list.slice(0, 10).forEach(function (r) {
                var tr = document.createElement("tr");
                tr.innerHTML =
                    "<td>#" + r.id + "</td>" +
                    "<td><b>" + r.predicted_grade + "</b> / 20</td>" +
                    "<td>" + esc(r.performance_level) + "</td>" +
                    "<td>" + esc(r.created_at || "") + "</td>" +
                    '<td><button type="button" class="del-btn" data-del="' + r.id + '">Delete</button></td>';
                rows.appendChild(tr);
            });
        } catch (err) {
            rows.innerHTML = '<tr><td colspan="5" class="hist-empty">Could not load history. Is Flask running?</td></tr>';
        }
    }

    rows.addEventListener("click", async function (e) {
        var btn = e.target.closest("[data-del]");
        if (!btn) return;
        if (!confirm("Delete prediction #" + btn.dataset.del + "?")) return;
        await fetch("/history/" + btn.dataset.del, { method: "DELETE" });
        loadHistory();
    });

    if (refresh) refresh.addEventListener("click", loadHistory);

    loadHistory();
});
