import os
import cv2
import numpy as np
import psycopg2
from skimage.feature import hog
from db.connect_db import connect_database

class ROIExtractor:
    def __init__(self, source_dir):
        self.source_dir = source_dir
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

    def read_roi(self, file_path):
        try:
            with open(file_path, 'r') as f:
                coords = list(map(int, f.readline().strip().split(',')))
                if len(coords) == 8:
                    x_min = min(coords[0], coords[2], coords[4], coords[6])
                    y_min = min(coords[1], coords[3], coords[5], coords[7])
                    x_max = max(coords[0], coords[2], coords[4], coords[6])
                    y_max = max(coords[1], coords[3], coords[5], coords[7])
                    return x_min, y_min, x_max - x_min, y_max - y_min
                elif len(coords) == 4:
                    return tuple(coords)
        except Exception as e:
            print(f"Lỗi khi đọc ROI từ {file_path}: {e}")
        return None

    def extract_hog_features(self, image):
        resized_img = cv2.resize(image, (128, 128))
        features, _ = hog(resized_img, pixels_per_cell=(8, 8), cells_per_block=(2, 2),
                          orientations=9, visualize=True, block_norm='L2-Hys')
        return features

    def process_user_folder(self, user_folder):
        full_user_path = os.path.join(self.source_dir, user_folder)
        raw_files = sorted([f for f in os.listdir(full_user_path) if f.endswith('.raw')])
        txt_files = sorted([f for f in os.listdir(full_user_path) if f.startswith('roi_') and f.endswith('.txt')])

        for raw_file, txt_file in zip(raw_files, txt_files):
            raw_path = os.path.join(full_user_path, raw_file)
            txt_path = os.path.join(full_user_path, txt_file)

            image = self.read_raw_image(raw_path)
            if image is None:
                continue

            roi = self.read_roi(txt_path)
            if roi:
                x, y, w, h = roi
                cropped_image = image[y:y+h, x:x+w]
            else:
                cropped_image = image

            png_filename = f"{user_folder}_{raw_file.replace('.raw', '_roi.png')}"
            is_success, buffer = cv2.imencode(".png", cropped_image)
            if not is_success:
                continue

            # Trích xuất đặc trưng HOG
            hog_features = self.extract_hog_features(cropped_image)

            # Lưu vào PostgreSQL
            self.cursor.execute(
                "INSERT INTO crop_images (file_name_crop, user_folder_crop, image_data_crop, hog_features) VALUES (%s, %s, %s, %s)",
                (png_filename, user_folder, buffer.tobytes(), hog_features.tolist())
            )
            self.conn.commit()

            print(f"✅ Đã lưu ảnh ROI vào DB: {png_filename}")

    def process_dataset(self):
        user_images = {}  # Dictionary lưu danh sách ảnh đã xử lý cho từng user

        for user_folder in os.listdir(self.source_dir):
            full_user_path = os.path.join(self.source_dir, user_folder)
            
            if os.path.isdir(full_user_path):
                processed_images = self.process_user_folder(user_folder)
                
                if processed_images:  # Chỉ lưu nếu có ảnh đã xử lý
                    user_images[user_folder] = processed_images
        
        print(f"✅ Đã lưu ảnh trực tiếp vào bảng `images` trong PostgreSQL!")
        
        return user_images  # ✅ Trả về dictionary chứa danh sách ảnh đã lưu


