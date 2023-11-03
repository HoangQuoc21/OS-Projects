from FAT32.general import *
from FAT32.directoriesFAT32 import main_FAT32
from GetVolType import *

platform_name = init_platform()
volume = input('Type your disk path: ')
rs = get_volume_type(volume)

# Chọn đúng đường dẫn ổ đĩa dựa trên hệ điều hành
disk_path = select_disk_path(platform_name, volume)

# Tạo một tệp để mở ổ đĩa và đọc nội dung
disk_file = generate_disk_file(disk_path)

def print_hexa(data):
    print(' '.join('{:02X}'.format(b) for b in data))

if rs == 'FAT32':
    main_FAT32(volume, disk_file)
elif rs == 'NTFS':
    #in kết quả thử
    data = disk_file.read(10000)
    print_hexa(data)
else:
    print("Unknown volume type or Unfound volume!")