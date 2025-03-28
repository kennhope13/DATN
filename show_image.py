import psycopg2
import os
import cv2
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# Kết nối PostgreSQL
conn = psycopg2.connect(os.getenv("POSTGRES_URL"))
cursor = conn.cursor()

# Truy vấn dữ liệu
image_id = 1  # Thay bằng ID của ảnh bạn muốn xem
cursor.execute("SELECT image_data FROM images WHERE id = %s;", (image_id,))
record = cursor.fetchone()

if record:
    image_data = record[0]
    image_np = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

    # Hiển thị ảnh
    cv2.imshow("Image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("Không tìm thấy ảnh!")

# Đóng kết nối
cursor.close()
conn.close()
