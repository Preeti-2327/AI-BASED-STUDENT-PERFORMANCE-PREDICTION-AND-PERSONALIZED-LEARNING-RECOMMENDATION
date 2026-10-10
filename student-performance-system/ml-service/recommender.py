"""Personalized recommendations. Works for both UCI (G3 0-20)
and Kaggle (Exam_Score 0-100) schemas — thresholds scale automatically."""

KAGGLE_TIPS = {
    "Hours_Studied": "Study hours drive scores more than anything else. Aim for consistent daily hours instead of last-minute cramming.",
    "Attendance": "Low attendance is the silent killer. Attend every class — each missed day compounds.",
    "Sleep_Hours": "Protect 7-8 hours of sleep. Late-night study without sleep destroys recall.",
    "Previous_Scores": "Your previous scores show the trend. Fix the weakest topics first, not the favorite ones.",
    "Tutoring_Sessions": "Use tutoring sessions for your weakest subject only — focused help beats generic revision.",
    "Motivation_Level": "Motivation dips are normal. Set a 25-minute timer and start small; momentum follows action.",
}


def _get(student, key, default=None):
    try:
        return student.get(key, default)
    except AttributeError:
        return default


def generate_recommendations(student, predicted_grade, scale_max=20, level=None):
    recommendations = []

    # Level-driven message (same cutoffs as dataset schema — caller passes it).
    # Fallback: normalize to 0-100 with generic cutoffs.
    if level is None:
        norm = (predicted_grade / scale_max * 100) if scale_max else predicted_grade
        if norm < 60:
            level = "Needs Improvement"
        elif norm < 75:
            level = "Average"
        elif norm < 90:
            level = "Good"
        else:
            level = "Excellent"

    # -----------------------------------------
    # 1. Performance-based recommendation
    # -----------------------------------------

    if level == "Needs Improvement":
        recommendations.append(
            "Your predicted performance is low. "
            "Create a daily study schedule and focus on basic concepts."
        )

    elif level == "Average":
        recommendations.append(
            "Your performance is average. "
            "Increase your study consistency and revise difficult topics."
        )

    elif level == "Good":
        recommendations.append(
            "Your performance is good. "
            "Maintain your study routine and practice regularly."
        )

    else:
        recommendations.append(
            "Your performance is excellent. "
            "Continue your current study routine and challenge yourself "
            "with advanced topics."
        )

    # -----------------------------------------
    # 2. Kaggle-schema signals (Hours_Studied, Attendance, ...)
    # -----------------------------------------

    hours = _get(student, "Hours_Studied")
    if hours is not None:
        try:
            hours = float(hours)
            if hours < 10:
                recommendations.append(
                    "Very low study hours. Raise to a steady daily routine — "
                    + KAGGLE_TIPS["Hours_Studied"]
                )
            elif hours < 20:
                recommendations.append(
                    "Moderate study hours. Push higher gradually. "
                    + KAGGLE_TIPS["Hours_Studied"]
                )
            else:
                recommendations.append(
                    "Strong study hours. Keep the routine stable."
                )
        except (TypeError, ValueError):
            pass

    attendance = _get(student, "Attendance")
    if attendance is not None:
        try:
            attendance = float(attendance)
            if attendance < 70:
                recommendations.append(
                    f"Attendance is {attendance:g}%. " + KAGGLE_TIPS["Attendance"]
                )
            elif attendance < 90:
                recommendations.append("Attendance is slipping. Target 90%+.")
            else:
                recommendations.append("Excellent attendance. Keep it up.")
        except (TypeError, ValueError):
            pass

    sleep = _get(student, "Sleep_Hours")
    if sleep is not None:
        try:
            if float(sleep) < 6:
                recommendations.append(KAGGLE_TIPS["Sleep_Hours"])
        except (TypeError, ValueError):
            pass

    prev = _get(student, "Previous_Scores")
    if prev is not None:
        try:
            if float(prev) < 60:
                recommendations.append(KAGGLE_TIPS["Previous_Scores"])
        except (TypeError, ValueError):
            pass

    # -----------------------------------------
    # 3. UCI-schema signals (studytime, absences, ...)
    # -----------------------------------------

    if _get(student, "studytime") is not None:
        try:
            st = int(_get(student, "studytime"))
            if st <= 1:
                recommendations.append(
                    "Increase your study time. "
                    "Try to maintain at least a regular daily study routine."
                )
            elif st == 2:
                recommendations.append(
                    "Your study time is moderate. "
                    "Try increasing it gradually for better performance."
                )
            else:
                recommendations.append(
                    "Your study time is good. "
                    "Continue maintaining your current routine."
                )
        except (TypeError, ValueError):
            pass

    if _get(student, "absences") is not None:
        try:
            ab = int(_get(student, "absences"))
            if ab > 10:
                recommendations.append(
                    "You have a high number of absences. "
                    "Improve attendance and avoid missing important classes."
                )
            elif ab > 5:
                recommendations.append(
                    "Try to reduce your absences and maintain regular attendance."
                )
            else:
                recommendations.append(
                    "Your attendance level is good. Keep attending classes regularly."
                )
        except (TypeError, ValueError):
            pass

    if _get(student, "failures") is not None:
        try:
            if int(_get(student, "failures")) > 0:
                recommendations.append(
                    "You have previous academic failures. "
                    "Give extra attention to difficult subjects and consider "
                    "additional practice or teacher support."
                )
            else:
                recommendations.append(
                    "You have no previous failures. "
                    "Continue your current academic approach."
                )
        except (TypeError, ValueError):
            pass

    if _get(student, "schoolsup") == "no":
        recommendations.append(
            "Consider using additional academic support when needed, "
            "such as teacher guidance, tutorials, or study groups."
        )

    # -----------------------------------------
    # Return recommendations
    # -----------------------------------------

    return recommendations
