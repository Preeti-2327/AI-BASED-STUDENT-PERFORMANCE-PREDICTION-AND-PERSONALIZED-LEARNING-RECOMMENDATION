# 🎓 AI-Based Student Performance Prediction and Personalized Learning Recommendation

An end-to-end machine learning project that **predicts student academic performance** and **recommends personalized learning resources** based on each student's strengths, weaknesses, and study behavior.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Dataset](#-dataset)
- [Methodology](#-methodology)
- [Installation](#-installation)
- [Usage](#-usage)
- [Results](#-results)
- [Future Scope](#-future-scope)
- [Contributing](#-contributing)
- [License](#-license)
- [Author](#-author)

---

## 🔍 Overview

Every student learns differently. Traditional one-size-fits-all teaching often fails to identify struggling students early. This project uses **Machine Learning** to:

1. **Predict** a student's final performance (grade / pass-fail / score) from academic and behavioral data.
2. **Identify** students at risk of underperforming.
3. **Recommend** personalized learning paths, topics, and resources to help each student improve.

---

## ✨ Features

- 📊 **Performance Prediction** – Predicts grades/scores using multiple ML models.
- ⚠️ **At-Risk Detection** – Flags students who need early intervention.
- 🎯 **Personalized Recommendations** – Suggests study material and focus areas tailored to each student.
- 📈 **Data Visualization** – Insightful charts for attendance, study hours, marks distribution, and correlations.
- 🖥️ **Interactive Web App** – Simple UI to enter student data and view predictions and recommendations.
- 🔬 **Model Comparison** – Evaluates several algorithms and selects the best performer.

---

## 🛠 Tech Stack

| Category            | Tools                                             |
| ------------------- | ------------------------------------------------- |
| Language            | Python 3.9+                                       |
| Data Processing     | Pandas, NumPy                                     |
| Machine Learning    | Scikit-learn, XGBoost                             |
| Recommendation      | Content-based filtering / Cosine Similarity       |
| Visualization       | Matplotlib, Seaborn, Plotly                       |
| Web App             | Streamlit                                         |
| Environment         | Jupyter Notebook, VS Code                         |

---

## 📁 Project Structure

```
AI-BASED-STUDENT-PERFORMANCE-PREDICTION-AND-PERSONALIZED-LEARNING-RECOMMENDATION/
│
├── data/
│   ├── raw/                  # Original dataset
│   └── processed/            # Cleaned & preprocessed data
│
├── notebooks/
│   ├── 01_EDA.ipynb          # Exploratory Data Analysis
│   ├── 02_Preprocessing.ipynb
│   ├── 03_Model_Training.ipynb
│   └── 04_Recommendation.ipynb
│
├── src/
│   ├── data_preprocessing.py
│   ├── train_model.py
│   ├── predict.py
│   └── recommender.py
│
├── models/                   # Saved trained models (.pkl)
│
├── app/
│   └── app.py                # Streamlit web application
│
├── requirements.txt
├── README.md
└── LICENSE
```

> 📝 Adjust the folder names above to match your actual repository structure.

---

## 📂 Dataset

- **Source:** [UCI Student Performance Dataset](https://archive.ics.uci.edu/ml/datasets/student+performance) / Kaggle / Custom dataset
- **Records:** *(add number of rows)*
- **Key Features:**
  - Demographics (age, gender, address)
  - Academic history (previous grades, failures)
  - Study habits (study time, absences, attendance)
  - Social factors (family support, internet access, free time)
  - Target: Final grade (G3) / Pass–Fail / Performance category

---

## ⚙️ Methodology

```
Data Collection → Data Cleaning → EDA → Feature Engineering
      → Model Training → Evaluation → Recommendation Engine → Deployment
```

1. **Data Preprocessing** – Handling missing values, encoding categorical variables, scaling features.
2. **Exploratory Data Analysis** – Understanding patterns and feature correlations.
3. **Model Training** – Logistic Regression, Decision Tree, Random Forest, SVM, XGBoost, etc.
4. **Evaluation** – Accuracy, Precision, Recall, F1-Score, Confusion Matrix, RMSE / R² (for regression).
5. **Recommendation Engine** – Maps weak areas to suitable topics, courses, and study strategies using content-based filtering.
6. **Deployment** – Streamlit app for real-time predictions.

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/AI-BASED-STUDENT-PERFORMANCE-PREDICTION-AND-PERSONALIZED-LEARNING-RECOMMENDATION.git
cd AI-BASED-STUDENT-PERFORMANCE-PREDICTION-AND-PERSONALIZED-LEARNING-RECOMMENDATION
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 💻 Usage

### Run the notebooks

```bash
jupyter notebook
```

### Train the model

```bash
python src/train_model.py
```

### Launch the web app

```bash
streamlit run app/app.py
```

Then open **http://localhost:8501** in your browser, enter the student details, and get:

- ✅ Predicted performance
- ⚠️ Risk level
- 🎯 Personalized learning recommendations

---

## 📊 Results

| Model               | Accuracy | Precision | Recall | F1-Score |
| ------------------- | -------- | --------- | ------ | -------- |
| Logistic Regression | –        | –         | –      | –        |
| Decision Tree       | –        | –         | –      | –        |
| Random Forest       | –        | –         | –      | –        |
| XGBoost             | –        | –         | –      | –        |

> 🔧 Fill in your actual results after training. Add screenshots of the app and key plots here.

```
![Dashboard Screenshot](assets/dashboard.png)
```

---

## 🔮 Future Scope

- Integration with real-time Learning Management Systems (LMS)
- Deep learning models (LSTM / Neural Networks) for sequential performance tracking
- Explainable AI (SHAP / LIME) to show *why* a prediction was made
- Teacher dashboard with class-level analytics
- Adaptive quizzes and reinforcement-learning-based recommendations
- Mobile application support

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m "Add your feature"`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Your Name**
- GitHub: [@your-username](https://github.com/your-username)
- LinkedIn: [Your Name](https://linkedin.com/in/your-profile)
- Email: your.email@example.com

---

⭐ If you found this project useful, please consider giving it a star!
