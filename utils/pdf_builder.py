from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from PIL import Image
import io
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

font_path = os.path.join("fonts", "DejaVuSans.ttf")
pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))


class PDFBuilder:
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.page_width, self.page_height = A4
        self.buffer = io.BytesIO()
        self.canvas = canvas.Canvas(self.buffer, pagesize=A4)
        self.cursor_y = self.page_height - 2 * cm  # Start 2 cm from top
        self.margin = 2 * cm
        self.line_height = 14  # in points (about 5 mm)

    def _new_page_if_needed(self, needed_height: float):
        if self.cursor_y - needed_height < self.margin:
            self.canvas.showPage()
            self.cursor_y = self.page_height - 2 * cm

    def add_text(self, text: str):
        lines = text.split('\n')
        total_height = len(lines) * self.line_height
        self._new_page_if_needed(total_height + self.margin)

        text_object = self.canvas.beginText(self.margin, self.cursor_y)
        text_object.setFont("DejaVuSans", 11)

        for line in lines:
            text_object.textLine(line)

        self.canvas.drawText(text_object)
        self.cursor_y -= total_height + 1 * cm

    def add_image(self, image: Image.Image, width_cm: float = 14):
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        image_width = width_cm * cm
        image_height = image.height * image_width / image.width

        self._new_page_if_needed(image_height + 1 * cm)
        self.canvas.drawImage(ImageReader(img_buffer),
                              self.margin,
                              self.cursor_y - image_height,
                              width=image_width,
                              height=image_height)

        self.cursor_y -= image_height + 1 * cm

    def save(self):
        self.canvas.showPage()
        self.canvas.save()
        with open(self.output_path, 'wb') as f:
            f.write(self.buffer.getvalue())
        self.buffer.close()
