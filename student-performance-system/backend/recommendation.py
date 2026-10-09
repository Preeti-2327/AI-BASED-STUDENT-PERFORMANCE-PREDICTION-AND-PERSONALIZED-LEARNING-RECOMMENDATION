def generate_recommendations(student, predicted_grade):

    recommendations = []

    # -----------------------------------------
    # 1. Performance-based recommendation
    # -----------------------------------------

    if predicted_grade < 10:
        recommendations.append(
            "Your predicted performance is low. "
            "Create a daily study schedule and focus on basic concepts."
        )

    elif predicted_grade < 13:
        recommendations.append(
            "Your performance is average. "
            "Increase your study consistency and revise difficult topics."
        )

    elif predicted_grade < 16:
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
    # 2. Study time recommendation
    # -----------------------------------------

    if student["studytime"] <= 1:

        recommendations.append(
            "Increase your study time. "
            "Try to maintain at least a regular daily study routine."
        )

    elif student["studytime"] == 2:

        recommendations.append(
            "Your study time is moderate. "
            "Try increasing it gradually for better performance."
        )

    else:

        recommendations.append(
            "Your study time is good. "
            "Continue maintaining your current routine."
        )

    # -----------------------------------------
    # 3. Attendance / Absence recommendation
    # -----------------------------------------

    if student["absences"] > 10:

        recommendations.append(
            "You have a high number of absences. "
            "Improve attendance and avoid missing important classes."
        )

    elif student["absences"] > 5:

        recommendations.append(
            "Try to reduce your absences and maintain regular attendance."
        )

    else:

        recommendations.append(
            "Your attendance level is good. Keep attending classes regularly."
        )

    # -----------------------------------------
    # 4. Previous failures
    # -----------------------------------------

    if student["failures"] > 0:

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

    # -----------------------------------------
    # 5. School support
    # -----------------------------------------

    if student["schoolsup"] == "no":

        recommendations.append(
            "Consider using additional academic support when needed, "
            "such as teacher guidance, tutorials, or study groups."
        )

    # -----------------------------------------
    # Return recommendations
    # -----------------------------------------

    return recommendations