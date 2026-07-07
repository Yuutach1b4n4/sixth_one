import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk


class VisionProcessor:
    
    def __init__(self):
        self.image = None
        self.processed_image = None

    def load_image(self, path: str) -> bool:
        self.image = cv2.imread(path)
        if self.image is None:
            return False
        self.processed_image = self.image.copy()
        return True

    def find_and_draw_circles(self, min_area: float):
        
        if self.image is None:
            return None, 0

        self.processed_image = self.image.copy()

        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detected_count = 0

        for c in contours:
            area = cv2.contourArea(c)
            
            if area > min_area:
                (x, y), radius = cv2.minEnclosingCircle(c)
                center = (int(x), int(y))
                radius = int(radius)
                
                cv2.circle(self.processed_image, center, radius, (0, 0, 255), 3)  
                detected_count += 1

        return self.processed_image, detected_count

    def save_image(self, path: str) -> bool:
        if self.processed_image is not None:
            return cv2.imwrite(path, self.processed_image)
        return False

class App(tk.Tk):
    
    def __init__(self):
        super().__init__()
        self.title("Поиск круглых контуров")
        self.geometry("900x650")

        self.processor = VisionProcessor()

        self._init_ui()

    def _init_ui(self):
        control_panel = ttk.Frame(self, padding=10)
        control_panel.pack(side=tk.TOP, fill=tk.X)

        btn_load = tk.Button(control_panel, text="Загрузить изображение", command=self._load_file)
        btn_load.pack(side=tk.LEFT, padx=5)

        lbl_spin = tk.Label(control_panel, text="Мин. площадь (px):", bg="#f0f0f0")
        lbl_spin.pack(side=tk.LEFT, padx=(10, 2))

        self.spin_area = tk.Spinbox(control_panel, from_=0, to=100000, increment=50, width=8)
        self.spin_area.pack(side=tk.LEFT, padx=5)
        self.spin_area.delete(0, "end")
        self.spin_area.insert(0, "500")

        btn_run = tk.Button(control_panel, text="Запустить поиск", command=self._process_and_update, bg="#d4edda")
        btn_run.pack(side=tk.LEFT, padx=15)

        btn_save = tk.Button(control_panel, text="Сохранить результат", command=self._save_file)
        btn_save.pack(side=tk.RIGHT, padx=5)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab_original = ttk.Frame(self.notebook)
        self.tab_processed = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_original, text="Оригинал")
        self.notebook.add(self.tab_processed, text="Обработка")

        self.lbl_original = tk.Label(self.tab_original)
        self.lbl_original.pack(fill=tk.BOTH, expand=True)

        self.lbl_processed = tk.Label(self.tab_processed)
        self.lbl_processed.pack(fill=tk.BOTH, expand=True)

    def _load_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp *.webp")]
        )
        if file_path:
            if self.processor.load_image(file_path):
                self._display_image(self.processor.image, self.lbl_original)
                self._process_and_update()
            else:
                messagebox.showerror("Ошибка", "Не удалось прочитать изображение.")

    def _process_and_update(self):
        if self.processor.image is None:
            return

        try:
            min_area = float(self.spin_area.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное числовое значение площади.")
            return

        processed, count = self.processor.find_and_draw_circles(min_area)
        
        if processed is not None:
            self._display_image(processed, self.lbl_processed)
            self.title(f"Поиск круглых контуров — Обнаружено предметов: {count}")
            self.notebook.select(self.tab_processed)

    def _display_image(self, bgr_img, label_widget):
        rgb_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(rgb_img)
        img_pil.thumbnail((800, 500))
        
        img_tk = ImageTk.PhotoImage(image=img_pil)
        label_widget.configure(image=img_tk)
        label_widget.image = img_tk

    def _save_file(self):
        if self.processor.processed_image is None:
            messagebox.showwarning("Внимание", "Нечего сохранять.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG scheme", "*.png"), ("JPEG picture", "*.jpg")]
        )
        if file_path:
            if self.processor.save_image(file_path):
                messagebox.showinfo("Успех", "Файл сохранен!")
            else:
                messagebox.showerror("Ошибка", "Не удалось записать файл.")

if __name__ == "__main__":
    app = App()
    app.mainloop()