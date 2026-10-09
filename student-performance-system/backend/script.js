// ==========================================
// SHOW / HIDE "OTHER" INPUT FIELDS
// ==========================================

function toggleOther(selectId, inputId) {

    const select = document.getElementById(selectId);
    const input = document.getElementById(inputId);

    if (select.value === "other") {

        input.style.display = "block";
        input.required = true;

    } else {

        input.style.display = "none";
        input.required = false;
        input.value = "";

    }
}


// ==========================================
// PREDICTION FORM
// ==========================================

document
    .getElementById("predictionForm")
    .addEventListener("submit", async function (event) {

        event.preventDefault();

        // Show loading message
        document.getElementById("loading").style.display = "block";


        // ==========================================
        // COLLECT ALL 30 STUDENT INPUTS
        // ==========================================

        const student = {

            // -------------------------------
            // PERSONAL INFORMATION
            // -------------------------------

            school: document.getElementById("school").value,

            sex: document.getElementById("sex").value,

            age: Number(
                document.getElementById("age").value
            ),

            address: document.getElementById("address").value,

            famsize: document.getElementById("famsize").value,

            Pstatus: document.getElementById("Pstatus").value,


            // -------------------------------
            // FAMILY & EDUCATION
            // -------------------------------

            Medu: Number(
                document.getElementById("Medu").value
            ),

            Fedu: Number(
                document.getElementById("Fedu").value
            ),

            Mjob: document.getElementById("Mjob").value,

            Fjob: document.getElementById("Fjob").value,

            guardian: document.getElementById("guardian").value,

            reason: document.getElementById("reason").value,


            // -------------------------------
            // ACADEMIC INFORMATION
            // -------------------------------

            traveltime: Number(
                document.getElementById("traveltime").value
            ),

            studytime: Number(
                document.getElementById("studytime").value
            ),

            failures: Number(
                document.getElementById("failures").value
            ),

            absences: Number(
                document.getElementById("absences").value
            ),


            // -------------------------------
            // SUPPORT & ACTIVITIES
            // -------------------------------

            schoolsup: document.getElementById("schoolsup").value,

            famsup: document.getElementById("famsup").value,

            paid: document.getElementById("paid").value,

            activities: document.getElementById("activities").value,

            nursery: document.getElementById("nursery").value,

            higher: document.getElementById("higher").value,

            internet: document.getElementById("internet").value,

            romantic: document.getElementById("romantic").value,


            // -------------------------------
            // LIFESTYLE
            // -------------------------------

            famrel: Number(
                document.getElementById("famrel").value
            ),

            freetime: Number(
                document.getElementById("freetime").value
            ),

            goout: Number(
                document.getElementById("goout").value
            ),

            Dalc: Number(
                document.getElementById("Dalc").value
            ),

            Walc: Number(
                document.getElementById("Walc").value
            ),

            health: Number(
                document.getElementById("health").value
            )

        };


        // Display submitted data in browser console
        console.log(
            "Student data being sent:",
            student
        );


        // ==========================================
        // SEND DATA TO FLASK
        // ==========================================

        try {

            const response = await fetch(
                "/predict",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify(student)
                }
            );


            // Convert response to JSON
            const data = await response.json();


            console.log(
                "Server response:",
                data
            );


            // Hide loading message
            document.getElementById("loading").style.display = "none";


            // ==========================================
            // CHECK BACKEND ERROR
            // ==========================================

            if (data.error) {

                alert(
                    "Error: " + data.error
                );

                return;
            }


            // ==========================================
            // SHOW RESULT CARD
            // ==========================================

            document.getElementById(
                "result"
            ).style.display = "block";


            // ==========================================
            // DISPLAY PREDICTED GRADE
            // ==========================================

            document.getElementById(
                "grade"
            ).textContent =
                data.predicted_grade;


            // ==========================================
            // DISPLAY PERFORMANCE LEVEL
            // ==========================================

            document.getElementById(
                "level"
            ).textContent =
                data.performance_level;


            // ==========================================
            // PERFORMANCE INTERPRETATION
            // ==========================================

            let interpretation = "";


            if (data.performance_level === "Needs Improvement") {

                interpretation =
                    "The predicted performance indicates that the student " +
                    "may need additional academic support. Focus on " +
                    "consistent study habits, regular attendance, and " +
                    "strengthening difficult subjects.";

            }

            else if (data.performance_level === "Average") {

                interpretation =
                    "The predicted performance is average. With more " +
                    "consistent study, regular revision, and improved " +
                    "academic habits, the student can improve their result.";

            }

            else if (data.performance_level === "Good") {

                interpretation =
                    "The student is expected to perform well. Maintaining " +
                    "a consistent study routine and continuing regular " +
                    "practice can help achieve even better results.";

            }

            else if (data.performance_level === "Excellent") {

                interpretation =
                    "The student is predicted to perform at an excellent " +
                    "level. Continue the current study habits and consider " +
                    "challenging yourself with advanced learning activities.";

            }

            else {

                interpretation =
                    "The prediction has been generated successfully.";

            }


            document.getElementById(
                "interpretation"
            ).textContent = interpretation;


            // ==========================================
            // PERSONALIZED RECOMMENDATIONS
            // ==========================================

            const recommendationList =
                document.getElementById(
                    "recommendations"
                );


            // Clear previous recommendations
            recommendationList.innerHTML = "";


            // Add recommendations from Flask
            if (
                data.recommendations &&
                data.recommendations.length > 0
            ) {

                data.recommendations.forEach(
                    function (recommendation) {

                        const li =
                            document.createElement("li");

                        li.textContent =
                            recommendation;

                        recommendationList.appendChild(li);

                    }
                );

            }


            // ==========================================
            // SCROLL TO RESULT
            // ==========================================

            document.getElementById(
                "result"
            ).scrollIntoView({
                behavior: "smooth"
            });

        }


        // ==========================================
        // CONNECTION ERROR
        // ==========================================

        catch (error) {

            document.getElementById(
                "loading"
            ).style.display = "none";


            console.error(
                "Error:",
                error
            );


            alert(
                "Unable to connect to the Flask server. " +
                "Please make sure Flask is running."
            );

        }

    });