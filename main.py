# Import các thư viện cần thiết:

# Các hàm trong GetVolType.py được sử dụng để xác định loại ổ đĩa
from GetVolType import *

# Các hàm trong FAT32.py được sử dụng để xử lý ổ đĩa FAT32
from FAT32.general import *
from FAT32.directoriesFAT32 import main_FAT32

# Các hàm trong NTFS.py được sử dụng để xử lý ổ đĩa NTFS
from NTFS.NTFS import *

# Hàm in data đầu vào theo dạng hexa (thập lục phân)
def print_hexa(data):
    print(' '.join('{:02X}'.format(b) for b in data))

#Luồng chính của chương trình
try:
    platform_name = init_platform()
    volume = input('Type your disk name (C,D,F,...): ')
    rs = get_volume_type(volume) #Lưu chuỗi trả về "NTFS" hoặc "FAT32"

    # Chọn đúng đường dẫn ổ đĩa dựa trên hệ điều hành
    disk_path = select_disk_path(platform_name, volume)

    # Tạo một tệp để mở ổ đĩa và đọc nội dung
    disk_file = generate_disk_file(disk_path)

    if rs == 'FAT32':
        main_FAT32(volume, disk_file)
    elif rs == 'NTFS':
        read_entry_info(disk_path)
        
#Xủ lý các lỗi có thể xảy ra        
except Exception as e:
    print(f"Error: {e.args}")
