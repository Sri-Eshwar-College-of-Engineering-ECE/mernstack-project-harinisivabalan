import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error



np.random.seed(42)
days = 200

sales = np.random.randint(20, 100, size=days)
stock = 1000 - np.cumsum(sales)

data = pd.DataFrame({
    "Sales": sales,
    "Stock": stock
})

# Create Previous Sales column
data["Previous_Sales"] = data["Sales"].shift(1)
data.dropna(inplace=True)

print("Sample Data:\n")
print(data.head())



X = data[["Previous_Sales", "Stock"]]
y = data["Sales"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)



model = RandomForestRegressor()
model.fit(X_train, y_train)

predictions = model.predict(X_test)

print("\nModel Evaluation:")
print("Mean Absolute Error:", mean_absolute_error(y_test, predictions))



current_stock = 150
last_day_sales = data.iloc[-1]["Sales"]

predicted_demand = model.predict([[last_day_sales, current_stock]])

print("\nPredicted Demand for Next Day:", int(predicted_demand[0]))



if predicted_demand > current_stock:
    print("⚠ Shortage Expected!")
else:
    print("✅ Stock Sufficient.")



plt.figure()
plt.plot(data["Sales"])
plt.title("Sales Over Time")
plt.xlabel("Days")
plt.ylabel("Sales")
plt.show()