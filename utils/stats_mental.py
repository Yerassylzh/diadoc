import matplotlib.pyplot as plt
from datetime import datetime
from PIL import Image
import io

from db.models import MentalHealth

def get_mental_wellness_plot_image(records: MentalHealth) -> Image.Image:
    dates = [record.createdAt for record in records]
    values = [int(record.rating) for record in records]

    plt.figure(figsize=(12, 6))

    plt.plot(dates, values,
             marker='o',
             linestyle='-',
             color='#6a0dad',
             markersize=6,
             linewidth=2,
             label='Оценка ментального благополучия (1-5)')

    plt.axhspan(4.5, 5.0, color='green', alpha=0.1, label='Отлично')
    plt.axhspan(3.5, 4.5, color='lightgreen', alpha=0.1, label='Хорошо')
    plt.axhspan(2.5, 3.5, color='yellow', alpha=0.1, label='Средний')
    plt.axhspan(1.5, 2.5, color='orange', alpha=0.1, label='Низкий')
    plt.axhspan(1.0, 1.5, color='red', alpha=0.1, label='Очень низкий')

    low_dates = [d for d, v in zip(dates, values) if v <= 2]
    low_values = [v for v in values if v <= 2]

    if low_values:
        plt.scatter(low_dates, low_values, color='red', zorder=5, label='Низкие баллы')

    plt.title('Ментального благополучие с течением времени', fontsize=14)
    plt.xlabel('Дата', fontsize=12)
    plt.ylabel('Оценка настроения (1-5)', fontsize=12)
    plt.ylim(0.5, 5.5)
    plt.xticks(rotation=45)
    plt.yticks([1, 2, 3, 4, 5])
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(loc='upper left')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    plt.close()

    buf.seek(0)
    return Image.open(buf)
