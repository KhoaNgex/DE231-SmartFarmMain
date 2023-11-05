import pickle

with open("model.pkl", "rb") as file:
    model = pickle.load(file)
new_data_point = [[25, 70, 50, 500]]  
prediction = model.predict(new_data_point)
print("Prediction:", prediction)