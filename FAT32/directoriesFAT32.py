import os
from FAT32.constant_FAT32 import *
import struct
from tabulate import tabulate

def init_platform():
    platform_name = os.name
    return platform_name

def select_disk_path(platform_name, disk_path):
    if platform_name == 'nt':
        return f'\\\\.\\{disk_path}:'
    return disk_path

def get_file_attributes(hex_code):
    # Định nghĩa các thuộc tính
    attributes = {
        0: 'Read-only',
        1: 'Hidden',
        2: 'System',
        3: 'Volume label',
        4: 'Subdirectory',
        5: 'Archive',
        6: 'Device',
        7: 'Unused'
    }
    
    # Trả về danh sách các thuộc tính tương ứng
    return [attr for code, attr in attributes.items() if (hex_code >> code) & 1]

def generate_disk_file(disk_path):
    disk_file = os.open(disk_path, os.O_BINARY)
    return os.fdopen(disk_file, 'rb')

def read_value_from_offset(data, offset, format_string):
    return struct.unpack_from(format_string, data, offset)[0]

def read_boot_sector_values(data):
    values = {}
    values["FAT Type"] = data[BS_FAT_TYPE:BS_FAT_TYPE+5].decode('ascii')
    values["Sector Size"] = read_value_from_offset(data, BS_SECTOR_SIZE, '<H')
    values["Sectors per Cluster"] = read_value_from_offset(data, BS_SECTOR_CLUSTER, '<B')
    values["Reserved Boot Sectors"] = read_value_from_offset(data, BS_SECTOR_BOOT, '<H')
    values["Number of FATs"] = read_value_from_offset(data, BS_FAT, '<B')
    values["Total Sectors"] = read_value_from_offset(data, BS_TOTAL_SECTOR, '<I')
    values["Sectors per FAT"] = read_value_from_offset(data, BS_SECTOR_FAT, '<I')
    values["Root Directory Cluster Start"] = read_value_from_offset(data, BS_RDET_CLUSTER_STARTED, '<I')

    return values

def print_directory_entry(disk_file, info, start_pos, is_sdet=False):
    directories = []
    # Chuyển tới vị trí bắt đầu
    disk_file.seek(start_pos)


    # Nếu là SDET, bỏ qua 64 byte đầu ("." và "..")
    if is_sdet:
        disk_file.read(64)

    # Đọc 32 byte đầu
    data = disk_file.read(32)

    # Stach chứa tên
    sub_entry_stack = []

    table_data = []
    while data[0] != 0x00:
        # Nếu là entry phụ (0F)
        if data[0xB] == 0x0F:
            # Rút tên từ các vị trí đã nói trước ra tới khi đủ số byte hoặc găp FF
            name_part_a = data[1:1+10].decode('utf-16-le', 'ignore').split('\uffff')[0]
            name_part_b = data[0xE:0xE+12].decode('utf-16-le', 'ignore').split('\uffff')[0]
            name_part_c = data[0x1C:0x1C+4].decode('utf-16-le', 'ignore').split('\uffff')[0]

            sub_entry_stack.append(name_part_a + name_part_b + name_part_c)
        else:
            # Nếu byte đầu là E5 (đã xoá) hoặc 00 (entry trống) thì bỏ qua
            if data[0] != 0x00 and data[0] != 0xE5: #and (data[ME_STATE] == 0x10 or data[ME_STATE] == 0x20):

                file_name = ''.join(reversed(sub_entry_stack)) if sub_entry_stack else data[ME_MAIN_NAME:ME_MAIN_NAME+8].decode('ascii').rstrip() + "." + data[ME_EXPAND_NAME:ME_EXPAND_NAME+3].decode('ascii').rstrip()
                file_attributes = get_file_attributes(data[ME_STATE])
                cluster_number = struct.unpack_from('<H', data, ME_LOW_WORD)[0] + (struct.unpack_from('<H', data, ME_HIGH_WORD)[0] << 16)
                file_size = struct.unpack_from('<I', data, ME_CONTENT_SIZE)[0]
                sector_number = start_pos // info["Sector Size"] + cluster_number - 2 * info["Sectors per Cluster"]

                table_data.append([file_name, file_attributes, cluster_number, sector_number])

                directories.append({
                    "name": file_name,
                    "cluster_number": cluster_number,
                    "sector_number": sector_number,
                    "size": file_size,
                    "type": file_attributes
                })
            # Xóa entry hiện tại để tới entry tiếp theo
            sub_entry_stack.clear()

        # Đọc entry tiếp theo
        data = disk_file.read(32)
    print(tabulate(table_data, headers=["File Name", "File Attributes", "First Cluster Number", "Sector Number on Hard Disk"]))
    return directories

def handle_file(disk_file, file_info, info):
    # Tính toán vị trí bắt đầu của tệp
    txt_start = (info["Reserved Boot Sectors"] + info["Number of FATs"] * info["Sectors per FAT"] + (file_info['cluster_number'] - 2) * info["Sectors per Cluster"]) * info["Sector Size"]
    # Di chuyển đến vị trí bắt đầu của tệp
    disk_file.seek(txt_start)
    # Đọc dữ liệu của tệp
    file_data = disk_file.read(file_info['size'])

    file_name = file_info['name'].rstrip('\x00')
    if file_name.lower().endswith('.txt'):
        # Giải mã và in nội dung của tệp văn bản
        print(f"The content of file {file_name}: ", file_data.decode('utf-8', 'ignore'))  #  Đảm bảo sử dụng mã hóa đúng
    else:
        file_extension = '.' + file_name.split('.')[-1]
        if file_extension in DOCUMENT_EXTENSIONS:
            print(f"The file {file_name} is supported by {DOCUMENT_EXTENSIONS[file_extension]}\n")
        else:
            print(f"The file {file_name} is not supported in this program")            

def main_FAT32(volume,disk_file):

    # Biến lưu trữ đường dẫn thư mục hiện tại
    current_path = [volume + ':\\']

    # Đọc thông tin từ phần khởi đầu (boot sector) của ổ đĩa
    data = disk_file.read(512)
    info = read_boot_sector_values(data)

    # Tính vị trí bắt đầu của phân mục gốc (Root Directory Entry Table - RDET)
    rdet_start = (info["Reserved Boot Sectors"] + info["Number of FATs"] * info["Sectors per FAT"]) * info["Sector Size"]

    # Biến để theo dõi thư mục hiện tại
    current_directory = rdet_start

    # Tạo từ điển để theo dõi thư mục cha của từng thư mục
    parent_directories = {rdet_start: None}

    while True:
        # In đường dẫn thư mục hiện tại
        print("Current path: " + "\\".join(current_path))

        # Hiển thị danh sách thư mục và tệp trong thư mục hiện tại
        directories = print_directory_entry(disk_file, info, current_directory, current_directory != rdet_start)

        # Nhập tên thư mục để duyệt hoặc '..' để quay lại thư mục cha hoặc 'exit' để thoát
        dir_name = input("\n\nEnter a directory name to explore or '..' to go back or 'exit' to quit: ") + "\x00"

        if dir_name.lower() == 'exit\x00':
            break
        elif dir_name == '..\x00':
            if parent_directories[current_directory] is not None:
                current_directory = parent_directories[current_directory]
                # Cập nhật đường dẫn khi quay lại thư mục cha
                current_path.pop()
            continue
        else:
            for directory in directories:
                if directory['name'] == dir_name:
                    if 'Archive' in directory['type']:
                        # Xử lý tệp nếu là tệp dữ liệu
                        handle_file(disk_file, directory, info)
                    else:
                        sdet_start = (info["Reserved Boot Sectors"] + info["Number of FATs"] * info["Sectors per FAT"] + (directory['cluster_number'] - 2) * info["Sectors per Cluster"]) * info["Sector Size"]
                        parent_directories[sdet_start] = current_directory
                        current_directory = sdet_start
                        # Cập nhật đường dẫn khi chuyển đến thư mục con
                        current_path.append(dir_name.rstrip('\x00'))
                    break

    print("Finished")
