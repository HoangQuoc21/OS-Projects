from FAT32.constant_FAT32 import *
import struct


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

def get_entry_info(disk_file, start_pos, is_sdet=False):
    """
    disk_file: nội dung của ổ đĩa dưới dạng file nhị phân
    info: dictionary chứa thông tin bootsector
    start_pos: vị trí bắt đầu đọc các entry
    is_sdet: các entry này nằm trong bảng rDET hay SDET, nêu slaf SDET sẽ bỏ qua 64 byte đầu
    
    return: dictionary chứa thông tin của tất cả các file xuất hiện trong chuỗi entry này
    """
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

    while data[0] != 0x00: #Chạy tới khi nào không gặp entry trống
        # Nếu là entry phụ (0F)
        if data[0xB] == 0x0F and data[0] != 0xE5:
            # Rút tên từ các vị trí đã nói trước ra tới khi đủ số byte hoặc găp FF
            name_part_a = data[1:1+10].decode('utf-16-le', 'ignore').split('\uffff')[0]
            name_part_b = data[0xE:0xE+12].decode('utf-16-le', 'ignore').split('\uffff')[0]
            name_part_c = data[0x1C:0x1C+4].decode('utf-16-le', 'ignore').split('\uffff')[0]

            sub_entry_stack.append(name_part_a + name_part_b + name_part_c)
        else:
            # Nếu byte đầu là E5 (đã xoá) thì bỏ qua
            if data[0] != 0xE5: #and (data[ME_STATE] == 0x10 or data[ME_STATE] == 0x20):
                
                #Nếu sub_entry_stack trống thì lấy tên file + tên mở rộng, nêu skhoong thì lấy các tên trong stck gép lại
                file_name = ''.join(reversed(sub_entry_stack)) if sub_entry_stack else data[ME_MAIN_NAME:ME_MAIN_NAME+8].decode('ascii').rstrip() + "." + data[ME_EXPAND_NAME:ME_EXPAND_NAME+3].decode('ascii').rstrip()
                
                file_attributes = get_file_attributes(data[ME_STATE])
                
                cluster_number = struct.unpack_from('<H', data, ME_CLUSTER_START)[0]

                directories.append({
                    "name": file_name,
                    "cluster_number": cluster_number,
                    "type": file_attributes
            
                })
            # Xóa entry hiện tại để tới entry tiếp theo
            sub_entry_stack.clear()

        # Đọc entry tiếp theo
        data = disk_file.read(32)
    return directories
            
# def print_tree(disk_file, info):
#     def print_directory(disk_file, directory_start, indent):
#         # Lấy danh sách thư mục và tệp trong thư mục hiện tại
#         entries = get_entry_info(disk_file, directory_start, directory_start != rdet_start)

#         for entry in entries:
#             if 'Subdirectory' in entry['type']:
#                 print(indent + "[" + entry["name"]+ "]")    
#             else:
#                 print(indent + entry["name"])
#             if 'Subdirectory' in entry['type']:
#                 sdet_start = (info["Reserved Boot Sectors"] + info["Number of FATs"] * info["Sectors per FAT"] + (entry['cluster_number'] - 2) * info["Sectors per Cluster"]) * info["Sector Size"]
#                 print_directory(disk_file, sdet_start, indent + "   ")

#     # Tính vị trí bắt đầu của phân mục gốc (Root Directory Entry Table - RDET)
#     rdet_start = (info["Reserved Boot Sectors"] + info["Number of FATs"] * info["Sectors per FAT"]) * info["Sector Size"]

def print_directory(disk_file, directory_start, indent, info):
    # Lấy danh sách thư mục và tệp trong thư mục hiện tại
    rdet_start = (info["Reserved Boot Sectors"] + info["Number of FATs"] * info["Sectors per FAT"]) * info["Sector Size"]
    entries = get_entry_info(disk_file, directory_start, directory_start != rdet_start)

    for entry in entries:
        if 'Subdirectory' in entry['type']:
            print(indent + "[" + entry["name"]+ "]")    
        else:
            print(indent + entry["name"])
        if 'Subdirectory' in entry['type']:
            sdet_start = (info["Reserved Boot Sectors"] + info["Number of FATs"] * info["Sectors per FAT"] + (entry['cluster_number'] - 2) * info["Sectors per Cluster"]) * info["Sector Size"]
            print_directory(disk_file, sdet_start, indent + "   ", info)

def print_tree_root(disk_file, info):
    rdet_start = (info["Reserved Boot Sectors"] + info["Number of FATs"] * info["Sectors per FAT"]) * info["Sector Size"]
    print_directory(disk_file, rdet_start, "", info)

def print_tree_directory(disk_file, info, sdet_start):
    print_directory(disk_file, sdet_start, "", info)
