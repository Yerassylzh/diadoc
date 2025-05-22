import matplotlib.pyplot as plt
from datetime import datetime
from PIL import Image
import io

from db.models import Glucose


def get_glucose_plot_image(records: Glucose) -> Image.Image:
    dates = [record.createdAt for record in records]
    values = [float(record.value) for record in records]
    
    plt.figure(figsize=(12, 6))
    
    plt.plot(dates, values, 
             marker='o', 
             linestyle='-', 
             color='#1f77b4', 
             markersize=5,
             label='Уровень глюкозы')
    
    plt.axhspan(4, 7.8, color='green', alpha=0.1, label='Нормальный диапазон')

    abnormal_dates = []
    abnormal_values = []
    for date, value in zip(dates, values):
        if not 4 <= value <= 7.8:
            abnormal_dates.append(date)
            abnormal_values.append(value)
    
    if abnormal_values:
        plt.scatter(abnormal_dates, abnormal_values, 
                   color='red', 
                   zorder=5,
                   label='Ненормальные значения')
    
    plt.title('Анализ уровня глюкозы в крови', fontsize=14)
    plt.xlabel('Дата', fontsize=12)
    plt.ylabel('Глюкоза (ммоль/л)', fontsize=12)
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


# records = [
#     {'value': 112, 'createdAt': datetime(2023, 1, 1)},
#     {'value': 124, 'createdAt': datetime(2023, 1, 2)},
#     {'value': 138, 'createdAt': datetime(2023, 1, 3)},
#     {'value': 109, 'createdAt': datetime(2023, 1, 4)},
#     {'value': 143, 'createdAt': datetime(2023, 1, 5)},
#     {'value': 117, 'createdAt': datetime(2023, 1, 6)},
#     {'value': 130, 'createdAt': datetime(2023, 1, 7)},
#     {'value': 125, 'createdAt': datetime(2023, 1, 8)},
#     {'value': 147, 'createdAt': datetime(2023, 1, 9)},
#     {'value': 134, 'createdAt': datetime(2023, 1, 10)},
#     {'value': 119, 'createdAt': datetime(2023, 1, 11)},
#     {'value': 128, 'createdAt': datetime(2023, 1, 12)},
#     {'value': 140, 'createdAt': datetime(2023, 1, 13)},
#     {'value': 111, 'createdAt': datetime(2023, 1, 14)},
#     {'value': 136, 'createdAt': datetime(2023, 1, 15)},
#     {'value': 123, 'createdAt': datetime(2023, 1, 16)},
#     {'value': 115, 'createdAt': datetime(2023, 1, 17)},
#     {'value': 144, 'createdAt': datetime(2023, 1, 18)},
#     {'value': 126, 'createdAt': datetime(2023, 1, 19)},
#     {'value': 131, 'createdAt': datetime(2023, 1, 20)},
# ]

# img = get_glucose_plot_image(records)
# img.show()
