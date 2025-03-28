from db.connect_db import connect_database

client = connect_database()


if client:
    print("🎉 Kết nối thành công!")
else:
    print("⚠️ Kết nối thất bại!")