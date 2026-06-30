import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib

# Generate training data
np.random.seed(42)

days = 500
previous_sales = np.random.randint(5, 50, size=days)
stock_levels = np.random.randint(20, 200, size=days)

# Simulate realistic demand pattern
demand = previous_sales * 0.6 + stock_levels * 0.1 + np.random.randint(0, 10, size=days)

data = pd.DataFrame({
    "Previous_Sales": previous_sales,
    "Stock": stock_levels,
    "Demand": demand
})

X = data[["Previous_Sales", "Stock"]]
y = data["Demand"]

# Train model
model = RandomForestRegressor(n_estimators=100)
model.fit(X, y)

# Save model
joblib.dump(model, "model.pkl")

print("Model trained and saved as model.pkl")