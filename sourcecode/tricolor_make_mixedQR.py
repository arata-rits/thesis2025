import cv2
import numpy as np
from tkinter import Tk, Label, Button, filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
import qrcode


# QRコードを作成
qr = qrcode.QRCode(
    version=1,  # サイズのバージョン
    error_correction=qrcode.constants.ERROR_CORRECT_H,  # エラー訂正レベル
    box_size=15,  # 各ボックスのサイズ
    border=10,  # ボーダーのサイズ
)
# qr.add_data(data)
qr.make(fit=True)

# 画像を生成
img = qr.make_image(fill='black', back_color='white')

# 画像を保存
img.save("chinese2.png")

class ImageProcessor:
    def __init__(self):
        self.images = []
        self.labels = ["Red", "Blue", "Green"]
        self.current_label_index = 0

    def load_image(self, file_path):
        image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            print(f"Failed to load image: {file_path}")
            return None
        return image

    def process_image(self, image, color):
        processed_image = np.zeros((image.shape[0], image.shape[1], 3), dtype=np.uint8)
        processed_image[image == 0] = color  # Set black pixels to the specified color
        processed_image[image == 255] = [0, 0, 0]  # Set white pixels to black
        return processed_image

    def add_image(self, file_path):
        color_map = {
            0: ([0, 0, 255], "qr_red_loaded.png"),
            1: ([255, 0, 0], "qr_blue_loaded.png"),
            2: ([0, 255, 0], "qr_green_loaded.png")
        }

        image = self.load_image(file_path)
        if image is not None:
            color, filename = color_map[self.current_label_index]
            processed_image = self.process_image(image, color)
            cv2.imwrite(filename, processed_image)
            self.images.append(processed_image)
            self.current_label_index += 1

        if len(self.images) == 3:
            self.combine_images()

    def combine_images(self):
        if len(self.images) == 3:
            mixed_image = cv2.add(cv2.add(self.images[0], self.images[1]), self.images[2])
            resized_image = cv2.resize(mixed_image, (288, 288))
            #image_mixed = "./Desktop/tricolor_panel/image1/mixedQR1.png"
            cv2.imwrite("image_mixed.png", resized_image)
            print("Processed and saved the mixed image as image_mixed.png")
        else:
            print("Error: Not enough images to combine.")

def select_file(image_processor):
    file_path = filedialog.askopenfilename()
    #file_path = "./Desktop/tricolor_panel/"
    if file_path:
        image_processor.add_image(file_path)

def main():
    image_processor = ImageProcessor()

    root = Tk()
    root.title("Image Processor")

    label_text = f"Please load the {image_processor.labels[image_processor.current_label_index]} image"
    label = Label(root, text=label_text)
    label.pack(padx=10, pady=10)

    def update_label():
        nonlocal label_text
        if image_processor.current_label_index < len(image_processor.labels):
            label_text = f"Please load the {image_processor.labels[image_processor.current_label_index]} image"
            label.config(text=label_text)
        else:
            label.config(text="Processing complete.")

    def load_next_image():
        select_file(image_processor)
        update_label()

    button = Button(root, text="Load Image", command=load_next_image)
    button.pack(padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()


