import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler


# Sample data creation
def generate_sample_data(num_samples=1000):
    np.random.seed(42)
    # Generate random timestamps within a recent range
    start_timestamp = int(time.time()) - 10 ** 6  # 1 million seconds ago
    end_timestamp = int(time.time())
    timestamps = np.random.randint(start_timestamp, end_timestamp, num_samples)

    # Generate random occupancy values between 0 and 112
    occupancy = np.random.randint(0, 113, num_samples)

    # Create DataFrame
    data = pd.DataFrame({"timestamp": timestamps, "occupancy": occupancy})
    return data


# Feature engineering from timestamp
def extract_time_features(df):
    # Convert timestamp to datetime for feature extraction
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")
    df["hour"] = df["datetime"].dt.hour
    df["minute"] = df["datetime"].dt.minute
    df["weekday"] = df["datetime"].dt.weekday
    return df.drop(["timestamp", "datetime"], axis=1)


# Load and preprocess data
data = generate_sample_data()
data = extract_time_features(data)

# Split data into features (X) and target (y)
X = data.drop("occupancy", axis=1)
y = data["occupancy"]

# Standardize the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

# Train Logistic Regression model
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred))


# Visualize predictions
def plot_predictions(y_true, y_pred):
    plt.figure(figsize=(10, 6))
    plt.scatter(range(len(y_true)), y_true, label="Actual", alpha=0.7)
    plt.scatter(range(len(y_pred)), y_pred, label="Predicted", alpha=0.7)
    plt.title("Actual vs Predicted Occupancy")
    plt.xlabel("Sample Index")
    plt.ylabel("Occupancy")
    plt.legend()
    plt.show()


plot_predictions(y_test, y_pred)
