feat_names = X.columns

feat_imp = pd.DataFrame({"Feature": feat_names, "Importance": importances})
feat_imp = feat_imp.sort_values(by="Importance", ascending=False)

plt.figure(figsize=(8, 5))
plt.barh(feat_imp["Feature"], feat_imp["Importance"])
plt.xlabel("Importance")
plt.title("Feature Importance in Suicide Risk Prediction")
plt.gca().invert_yaxis()
plt.show()

# -------------------------------
# 9. Save Predictions for Dashboard
# -------------------------------
results = X_test.copy()
results["Actual_Risk"] = y_test
results["Predicted_Risk"] = y_pred

results.to_csv("student_risk_predictions.csv", index=False)
print("✅ Predictions saved to student_risk_predictions.csv")

# -------------------------------
# 10. Save Trained Model
# -------------------------------
import joblib
joblib.dump(model, "suicide_risk_model.pkl")
print("✅ Model saved as suicide_risk_model.pkl")
















































































# ===============================
# Suicide Risk Prediction for Students
# ===============================

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

# -------------------------------
# 1. Load dataset
# -------------------------------
df = pd.read_csv("Depression Student Dataset.csv")  # change filename to yours

# Preview data
print(df.head())

# -------------------------------
# 2. Assign Risk Levels
# -------------------------------
def assign_risk(row):
    if row["Depression"].lower() == "no":
        return "Low"

    score = 0

    # Suicidal Thoughts
    if row["Suicidal_Thoughts"].lower() == "yes":
        score += 3

    # Academic Pressure (1–5)
    if row["Academic_Pressure"] >= 4:
        score += 1

    # Financial Stress (1–5)
    if row["Financial_Stress"] >= 4:
        score += 1

    # Sleep Duration
    if row["Sleep_Duration"] == "less than 5 hours":
        score += 2
    elif row["Sleep_Duration"] == "5 - 6 hours":
        score += 1

    # Study Satisfaction (1–5)
    if row["Study_Satisfaction"] <= 2:
        score += 1

    # Family History of Mental Illness
    if row["Family_History_of_Mental_Illness"].lower() == "yes":
        score += 1

    # Dietary Habits
    if row["Dietary_Habits"].lower() == "unhealthy":
        score += 1
    elif row["Dietary_Habits"].lower() == "moderate":
        score += 0.5

    if score >= 4:
        return "High"
    else:
        return "Medium"


# Apply function
df["Risk_Level"] = df.apply(assign_risk, axis=1)

print(df["Risk_Level"].value_counts())

# -------------------------------
# 3. Encode categorical variables
# -------------------------------
from sklearn.preprocessing import LabelEncoder

# Added "Depression" here
categorical_cols = ["Gender", "Sleep_Duration", "Dietary_Habits",
                    "Suicidal_Thoughts", "Family_History_of_Mental_Illness",
                    "Depression"]

le = LabelEncoder()
for col in categorical_cols:
    df[col] = le.fit_transform(df[col])

# Target encoding
df["Risk_Level"] = df["Risk_Level"].map({"Low": 0, "Medium": 1, "High": 2})

# -------------------------------
# 4. Features and Target
# -------------------------------
X = df[["Gender", "Age", "Academic_Pressure", "Study_Satisfaction",
        "Sleep_Duration", "Dietary_Habits", "Suicidal_Thoughts",
        "Study_Hours", "Financial_Stress",
        "Family_History_of_Mental_Illness", "Depression"]]   # 👈 Added Depression here

y = df["Risk_Level"]

# -------------------------------
# 5. Train-Test Split
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, stratify=y, random_state=42
)

# -------------------------------
# 6. Train Model
# -------------------------------
model = RandomForestClassifier(class_weight="balanced", random_state=42)
model.fit(X_train, y_train)

# -------------------------------
# 7. Evaluate
# -------------------------------
y_pred = model.predict(X_test)

print("Classification Report:\n")
print(classification_report(y_test, y_pred))

print("Confusion Matrix:\n")
print(confusion_matrix(y_test, y_pred))

# -------------------------------
# 8. Feature Importance
# -------------------------------
import matplotlib.pyplot as plt

importances = model.feature_importances_
