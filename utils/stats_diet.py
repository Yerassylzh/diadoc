import matplotlib.pyplot as plt
from datetime import datetime
from PIL import Image
import io

from db.models import Diet


def get_calories_consumed_plot_image(records: Diet) -> Image.Image:
    dates = [record.createdAt for record in records]
    values = [float(record.calories) for record in records]
    
    plt.figure(figsize=(12, 6))

    plt.plot(dates, values, 
             marker='o', 
             linestyle='-', 
             color='#1f77b4', 
             markersize=5,
             label='Потребляемые калории')

    plt.axhspan(1600, 2800, color='green', alpha=0.1, label='Нормальный диапазон (1600-2800 ккал)')

    abnormal_dates = []
    abnormal_values = []
    for date, value in zip(dates, values):
        if value < 1600 or value > 2800:
            abnormal_dates.append(date)
            abnormal_values.append(value)
    
    if abnormal_values:
        plt.scatter(abnormal_dates, abnormal_values, 
                    color='red', 
                    zorder=5,
                    label='Выбросы')

    plt.title('Ежедневное потребление калорий', fontsize=14)
    plt.xlabel('Дата', fontsize=12)
    plt.ylabel('Потребляемые калории (ккал)', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    plt.close()

    buf.seek(0)
    return Image.open(buf)
