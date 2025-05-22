import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Set random seed for reproducibility
np.random.seed(42)

# Generate date range (6 months)
start_date = datetime(2023, 1, 1)
dates = [start_date + timedelta(days=i) for i in range(180)]

# Base calories with weekly pattern
base_calories = np.array([2200 if date.weekday() < 5 else 2500 for date in dates])

# Add random variation
random_variation = np.random.normal(0, 150, len(dates))

# Add special events (holidays, vacations)
special_days = [
    datetime(2023, 1, 1),   # New Year
    datetime(2023, 2, 14),  # Valentine's
    datetime(2023, 4, 9),   # Easter
    datetime(2023, 7, 4),   # Independence Day
    datetime(2023, 12, 25)  # Christmas
]
special_effects = np.array([300 if date.date() in [d.date() for d in special_days] else 0 for date in dates])

# Add a vacation period (2 weeks in summer)
vacation = np.array([400 if datetime(2023, 7, 15).date() <= date.date() <= datetime(2023, 7, 28).date() else 0 for date in dates])

# Add a diet period (1 month in spring)
diet = np.array([-200 if datetime(2023, 3, 15).date() <= date.date() <= datetime(2023, 4, 15).date() else 0 for date in dates])

# Combine all components
calories = base_calories + random_variation + special_effects + vacation + diet

# Create DataFrame
calorie_data = pd.DataFrame({
    'Date': dates,
    'Calories': calories.round().astype(int),
    'DayOfWeek': [date.strftime('%A') for date in dates]
})

# Add a rolling average (7-day)
calorie_data['7DayAvg'] = calorie_data['Calories'].rolling(7).mean().round()

# Display sample
print(calorie_data.head(10))

# Plot the data
plt.figure(figsize=(14, 7))
plt.plot(calorie_data['Date'], calorie_data['Calories'], 
         label='Daily Calories', alpha=0.6, linewidth=1)
plt.plot(calorie_data['Date'], calorie_data['7DayAvg'], 
         label='7-Day Average', color='red', linewidth=2)

# Formatting
plt.title('6-Month Calorie Intake with Special Events', fontsize=16)
plt.xlabel('Date', fontsize=12)
plt.ylabel('Calories', fontsize=12)
plt.xticks(rotation=45)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.tight_layout()

# Save the plot
plt.savefig('calorie_tracking.png')
print("Plot saved as 'calorie_tracking.png'")

# Save data to CSV
calorie_data.to_csv('calorie_data.csv', index=False)
print("Data saved as 'calorie_data.csv'")