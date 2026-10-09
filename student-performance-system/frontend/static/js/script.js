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

function getInterpretation(grade) {
    if (grade < 10) return "The student is at risk. Immediate attention to basics, attendance and study routine is needed.";
    if (grade < 13) return "Average performance. Consistent study and revision will push the grade higher.";
    if (grade < 16) return "Good performance. Maintain the routine and practice weak topics.";
    return "Excellent performance. Keep the momentum and try advanced material.";
}

document.addEventListener("DOMContentLoaded", function () {
    var form = document.getElementById("predictionForm");
    if (!form) return;

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        var loading = document.getElementById("loading");
        var resultCard = document.getElementById("result");
        if (loading) loading.style.display = "block";
        if (resultCard) resultCard.style.display = "none";

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
                alert(data.error || "Prediction failed. Check inputs.");
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
            alert("Server error. Is Flask running?");
        } finally {
            if (loading) loading.style.display = "none";
        }
    });
});
