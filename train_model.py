import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

data = pd.read_csv("du_lieu.csv")

features = data[['temp', 'humidity', 'soil', 'light']]
labels = data['label']

train_features, test_features, train_labels, test_labels = train_test_split(
    features, labels, test_size=0.2, random_state=42
)

model = RandomForestClassifier()

model.fit(train_features, train_labels)

test_predictions = model.predict(test_features)
train_predictions = model.predict(train_features)

train_accuracy = accuracy_score(train_labels, train_predictions)
print("Train Accuracy:", train_accuracy)

test_accuracy = accuracy_score(test_labels, test_predictions)
print("Test Accuracy:", test_accuracy)

with open("model.pkl", "wb") as file:
    pickle.dump(model, file)