import os
from FAT32.constant_FAT32 import *
import struct
from tabulate import tabulate

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

#data: đọc dữ liệu từ file nhị phân (Data), bắt đầu từ [offset], và lưu kết quả theo [format_string]
def read_value_from_offset(data, offset, format_string):
    """
    Một số format_string được sử dụng trong bài này:
    '<': sử dụng thứ tự little endian, 
    'H': unsigned short, 2 byte; 
    'B': unsigned char, 1 byte; 
    'I': unsigned int, 4 byte
    """
    return struct.unpack_from(format_string, data, offset)[0] #trả về một tuple ([number],)

#Hàm đọc các giá trị của bootsector từ dãy nhị phân
def read_boot_sector_values(data):
    """
    data: chuỗi 512 byte đầu đọc được từ ổ đĩa
    
    return: dictionary với key là tên thông tin, value là giá trị khớp thông tin đó
    """
    values = {}
    values["FAT Type"] = data[BS_FAT_TYPE:BS_FAT_TYPE+5].decode('ascii')
    values["Sector Size"] = read_value_from_offset(data, BS_SECTOR_SIZE, '<H') #Số byte/sector
    values["Sectors per Cluster"] = read_value_from_offset(data, BS_SECTOR_CLUSTER, '<B') #<B
    values["Reserved Boot Sectors"] = read_value_from_offset(data, BS_SECTOR_BOOT, '<H')
    values["Number of FATs"] = read_value_from_offset(data, BS_FAT, '<B')
    values["Total Sectors"] = read_value_from_offset(data, BS_TOTAL_SECTOR, '<I') 
    values["Sectors per FAT"] = read_value_from_offset(data, BS_SECTOR_FAT, '<I') 
    values["Root Directory Cluster Start"] = read_value_from_offset(data, BS_RDET_CLUSTER_STARTED, '<I')

    return values

def print_boot_sector_values(values):
    for key, value in values.items():
        print(f"{key}: {value}")

def read_cluster_chain(fat_table_buffer, n): 
    """
    Hàm dò bảng FAT để tìm ra dãy các cluster cho một entry nhất định, bắt đầu từ cluster thứ `n` truyền vào.
    """
    # End-of-cluster sign
    eoc_sign = [0x00000000, 0xFFFFFF0, 0xFFFFFFF, 0XFFFFFF7, 0xFFFFFF8, 0xFFFFFFF0]
    if n in eoc_sign:
        return []
    
    next_cluster = n
    chain = [next_cluster]

    while True:
        #Đọc nội dung của cluster
        next_cluster = read_value_from_offset(fat_table_buffer, next_cluster * 4, '<I')
        if next_cluster in eoc_sign:
            break 
        else:
            chain.append(next_cluster)
    return chain 
    
def cluster_chain_to_sector_chain(info, cluster_chain) -> list: 
    """
    Hàm chuyển dãy các cluster sang dãy các sector
    Biết rằng 1 cluster có Sc sectors 
    Với cluster k thì nó bắt đầu chiếm từ sector thứ `data_begin_sector + k * Sc`, và chiếm Sc sectors
    """
    sector_chain = []
    #sb+nf*sf
    data_begin_sector = info["Reserved Boot Sectors"] + info["Number of FATs"] * info["Sectors per FAT"]
    sc = info["Sectors per Cluster"]
    
    for cluster in cluster_chain:
        begin_sector = data_begin_sector + (cluster - 2) * sc
        for sector in range(begin_sector, begin_sector + sc):
            sector_chain.append(sector)
    return sector_chain

#Hàm in chuỗi các entry ra
def print_directory_entry(disk_file, info, start_pos, fat,is_sdet=False):
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

    table_data = []
    while data[0] != 0x00: #Chạy tới khi nào không gặp entry trống
        # Nếu là entry phụ (0F)
        if data[0xB] == 0x0F:
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
                
                #cluster_number = struct.unpack_from('<H', data, ME_LOW_WORD)[0] + (struct.unpack_from('<H', data, ME_HIGH_WORD)[0] << 16)
                cluster_number = struct.unpack_from('<H', data, ME_CLUSTER_START)[0]

                file_size = struct.unpack_from('<I', data, ME_CONTENT_SIZE)[0]
                
                #sector_number = start_pos // info["Sector Size"] + cluster_number - 2 * info["Sectors per Cluster"]

                cl_list = read_cluster_chain(fat,cluster_number)
                sector_number = cluster_chain_to_sector_chain(info,cl_list)

                table_data.append([file_name, file_attributes, sector_number,file_size])

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
    print(tabulate(table_data, headers=["File Name", "File Attributes","Sector Number on Hard Disk", "Size"]))
    return directories

# Hàm này để xử lý file, nếu file là ".txt" thì sẽ đọc ra nội dung file, còn nếu là các loại file khác mà nằm trong "DOCUMENT_EXTENSIONS" thì sẽ in ra loại ứng dụng hỗ trợ đọc, còn không thì sẽ thông báo không hỗ trợ
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

def getFatTable(file, sb, sf):
    # Seek to the specified offset
    file.seek(sb)
    
    # Read the FAT data of size 'sf' bytes
    fat = file.read(sf)
    
    return fat

def main_FAT32(volume,disk_file):

    # Biến lưu trữ đường dẫn thư mục hiện tại
    current_path = [volume + ':\\']

    # Đọc thông tin từ phần khởi đầu (boot sector) của ổ đĩa
    data_first512byte = disk_file.read(512)
    info = read_boot_sector_values(data_first512byte)

    print_boot_sector_values(info)
    print("\n")

    # Tính vị trí bắt đầu của phân mục gốc (Root Directory Entry Table - RDET)
    rdet_start = (info["Reserved Boot Sectors"] + info["Number of FATs"] * info["Sectors per FAT"]) * info["Sector Size"]

    # Biến để theo dõi thư mục hiện tại
    current_directory = rdet_start

    # Tạo từ điển để theo dõi thư mục cha của từng thư mục
    parent_directories = {rdet_start: None}
    fat = getFatTable(disk_file, info['Reserved Boot Sectors'], info['Sectors per FAT'])

    while True:
        # In đường dẫn thư mục hiện tại
        print("Current path: " + "\\".join(current_path))

        # Hiển thị danh sách thư mục và tệp trong thư mục hiện tại
        directories = print_directory_entry(disk_file, info, current_directory, fat ,current_directory != rdet_start)

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
