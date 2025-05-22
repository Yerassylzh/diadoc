import matplotlib.pyplot as plt
from datetime import datetime
from PIL import Image
import io

from db.models import PhysicalHealth

def get_calories_plot_image(records: PhysicalHealth) -> Image.Image:
    dates = [record.createdAt for record in records]
    values = [float(record.calories) for record in records]
    
    plt.figure(figsize=(12, 6))

    plt.plot(dates, values, 
             marker='o', 
             linestyle='-', 
             color='#ff7f0e', 
             markersize=5,
             label='Сожженные калории')
    
    plt.axhspan(100, 800, color='green', alpha=0.1, label='Нормальный диапазон (200-600 ккал)')
    
    abnormal_dates = []
    abnormal_values = []
    for date, value in zip(dates, values):
        if value < 100 or value > 800:
            abnormal_dates.append(date)
            abnormal_values.append(value)
    
    if abnormal_values:
        plt.scatter(abnormal_dates, abnormal_values, 
                   color='red', 
                   zorder=5,
                   label='Выбросы')
    
    plt.title('Калории, сожженные Во время Физической Активности', fontsize=14)
    plt.xlabel('Дата', fontsize=12)
    plt.ylabel('Сожженные калории', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    plt.close()
    
    buf.seek(0)
    img = Image.open(buf)
    
    return img
