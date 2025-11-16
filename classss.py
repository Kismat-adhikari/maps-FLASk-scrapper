import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Sample dataset: 5 data points, 2 features
X = np.array([
    [1, 2],
    [2, 1],
    [3, 4],
    [4, 3],
    [5, 5]
])

y = np.array([3, 4, 6, 7, 10])  # Target values

# Add intercept (bias) term: column of 1s
X_b = np.c_[np.ones((X.shape[0], 1)), X]  # shape: (5, 3)

# Normal equation: beta = (X^T X)^(-1) X^T y
beta = np.linalg.inv(X_b.T.dot(X_b)).dot(X_b.T).dot(y)

# Predicted values
y_pred = X_b.dot(beta)

print("Beta Coefficients:", beta)

# 3D Plotting
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

# Plot original data points
ax.scatter(X[:, 0], X[:, 1], y, color='blue', label='Actual data')

# Create a mesh grid for the regression plane
x_surf, y_surf = np.meshgrid(
    np.linspace(X[:, 0].min(), X[:, 0].max(), 10),
    np.linspace(X[:, 1].min(), X[:, 1].max(), 10)
)

# Calculate corresponding z values using the regression coefficients
z_surf = beta[0] + beta[1] * x_surf + beta[2] * y_surf

# Plot the regression plane
ax.plot_surface(x_surf, y_surf, z_surf, alpha=0.5, color='red', label='Regression plane')

# Labels and title
ax.set_xlabel('Feature 1')
ax.set_ylabel('Feature 2')
ax.set_zlabel('Target')
ax.set_title('Multiple Linear Regression with Two Features')

plt.legend()
plt.show()
