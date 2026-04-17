#!/usr/bin/python3
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Common style configuration
def setup_plot_style():
    sns.set_style("whitegrid")
    plt.rcParams.update({'font.size': 14})

# Synthetic dataset
np.random.seed(0)
X = np.random.rand(300, 3)*10
y = 2.5*X[:,0]-1.2*X[:,1]+0.8*X[:,2]+2.0*np.sin(X[:,0])+np.random.normal(0, 1.2, 300)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.30, random_state=42
)

# Models
lr = LinearRegression()
ml = RandomForestRegressor(n_estimators=300, random_state=42)

lr.fit(X_train, y_train)
ml.fit(X_train, y_train)

# Predictions
y_pred_lr = lr.predict(X_test)
y_pred_ml = ml.predict(X_test)

# Print statistics
def print_stats(name, y_true, y_pred):
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    print(f"{name}")
    print(f"  RMSE: {rmse:.4f}")
    print(f"  MAE : {mae:.4f}")
    print(f"  R²  : {r2:.4f}")

# print("=== MODEL PERFORMANCE ===")
# print_stats("Linear Regression", y_test, y_pred_lr)
# print_stats("Random Forest", y_test, y_pred_ml)

# Set up the plotting style
setup_plot_style()

# Create the plot
plt.figure(figsize=(12, 8))

# Define colours
colours = ['#2E86AB', '#A23B72']  # Blue, Purple
labels = ['Linear Regression ($r^2=0.9651$)', 'Machine Learning ($r^2=0.9582$)']

# Scatter plots
plt.scatter(y_test, y_pred_lr, alpha=0.65, s=70,
            color=colours[0], label=labels[0], edgecolor='black', linewidth=0.4)
plt.scatter(y_test, y_pred_ml, alpha=0.65, s=70,
            color=colours[1], label=labels[1], edgecolor='black', linewidth=0.4)

# Ideal line
ymin = min(np.min(y_test), np.min(y_pred_lr), np.min(y_pred_ml))
ymax = max(np.max(y_test), np.max(y_pred_lr), np.max(y_pred_ml))
plt.plot([ymin, ymax], [ymin, ymax], '--', color='black',
         linewidth=2.0, label='Ideal')

# Customise the plot
plt.xlabel(r"Real Values", fontsize=16, fontweight='bold')
plt.ylabel(r"Predicted Values", fontsize=16, fontweight='bold')
plt.title("Linear Regression and Machine Learning",
          fontsize=18, fontweight='bold', pad=20)

# Set axis limits and formatting
padding = 0.05*(ymax-ymin)
plt.xlim(ymin-padding, ymax+padding)
plt.ylim(ymin-padding, ymax+padding)
plt.gca().xaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f'))
plt.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f'))

# Add legend
plt.legend(loc='upper left', frameon=True, fancybox=True, shadow=True,
           fontsize=14, framealpha=0.9)

# Add grid customisation
plt.grid(True, alpha=0.3)

# Adjust layout and save
plt.tight_layout()
plt.savefig("real_vs_predicted_ml_vs_lr.pdf", dpi=300, bbox_inches='tight')
# plt.show()

