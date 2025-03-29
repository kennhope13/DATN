from db.connect_db import connect_database
# from process.dataset_seminer import SiameseDatasetOrganizer
from process.crop_images import ROIExtractor


source_dir = r"D:\DATN\dataset\auto-20250319T172321Z-001\auto"
def process():
    # dataset_organizer = SiameseDatasetOrganizer(source_dir)
    # dataset_organizer.process_dataset()
    dataset_organizer = ROIExtractor(source_dir)
    dataset_organizer.process_dataset()

if connect_database():
    process()
else:
    print("⚠️ Kết nối thất bại!")