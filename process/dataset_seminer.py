import os
import numpy as np
import cv2
import psycopg2
from db.connect_db import connect_database

class SiameseDatasetOrganizer:
    def __init__(self, source_dir):
        self.source_dir = source_dir   
        self.supported_raw_extensions = ['.raw', '.bin']

        # Kết nối PostgreSQL
        self.conn = connect_database()
        self.cursor = self.conn.cursor()

    def read_raw_image(self, file_path):
        raw_data = np.fromfile(file_path, dtype=np.uint8)
        possible_shapes = [(512, 512), (640, 480), (480, 640), (256, 256), (1024, 1024)]
        for shape in possible_shapes:
            try:
                return raw_data.reshape(shape)
            except ValueError:
                continue
        return None

    def process_user_folder(self, user_folder):
        full_user_path = os.path.join(self.source_dir, user_folder)
        processed_images = []
        
        for filename in os.listdir(full_user_path):
            base_name, ext = os.path.splitext(filename)
            if ext.lower() in self.supported_raw_extensions:
                raw_file_path = os.path.join(full_user_path, filename)
                
                image = self.read_raw_image(raw_file_path)
                if image is None:
                    continue
                
                # Chuyển ảnh sang PNG
                png_filename = f"{user_folder}_{base_name}.png"
                is_success, buffer = cv2.imencode(".png", image)
                if not is_success:
                    continue
                
                # Lưu ảnh vào PostgreSQL
                self.cursor.execute(
                    "INSERT INTO images (file_name, user_folder, image_data) VALUES (%s, %s, %s)",
                    (png_filename, user_folder, buffer.tobytes())
                )
                self.conn.commit()  # Lưu thay đổi vào database
                processed_images.append(png_filename)
        
        return processed_images

    def process_dataset(self):
        user_images = {}
        for user_folder in os.listdir(self.source_dir):
            full_user_path = os.path.join(self.source_dir, user_folder)
            if os.path.isdir(full_user_path):
                processed_images = self.process_user_folder(user_folder)
                if processed_images: 
                    user_images[user_folder] = processed_images
        print(f"Đã lưu ảnh trực tiếp vào bảng `images` trong PostgreSQL!")
        return user_images
