import numpy as np

# Given data
x1 = np.array([2, 3, 4, 3])
x2 = np.array([0.5, 2/3, 1, 2])
y = np.array([6.5, 21, 81, 191])

# Compute the transformed feature (x1_i / x2_i)^2
X_transformed = (x1 / x2) ** 2

# Add a column of ones for the bias term (w0)
X = np.vstack([np.ones_like(X_transformed), X_transformed]).T

# Solve for w using the least squares solution: w = (X.T @ X)^(-1) @ X.T @ y
w = np.linalg.inv(X.T @ X) @ X.T @ y

# Output the parameters
w0, w1 = w
print(f"w0: {w0}")
print(f"w1: {w1}")