import os
from datetime import datetime, timedelta
from constant_NTFS import DOCUMENT_EXTENSIONS

FILE_NAME = 48
EPOCH_AS_FILETIME = 116444736000000000  # January 1, 1970 as MS file time

def filetime_to_dt(ft):
    '''
         Đổi số nano giây ra ngày giờ
     '''
    us = (ft - EPOCH_AS_FILETIME) // 10
    return datetime(1970, 1, 1) + timedelta(microseconds=us)

def dec(hex: str) -> int: 
    """
    Hàm đổi số hex ra số hệ thập phân (tham số nhận vào là chuỗi)
    Vd:
    >>> dec('0B')
    >>> dec('0C')
    """
    return int(hex, 16)

def read_sectors(file, sector_begin, n_sector=1, bps=512) -> bytes:
    """
    Hàm đọc `n_sector` sectors, bắt đầu tại sector có chỉ số `sector_begin`.
    `bps`: số byte cho mỗi sector.
    Trả về: buffer đọc được.
    
    Ví dụ: đọc 4 sector bắt đầu từ sector 256
    >>> read_sectors(file, 256, 4)
    """
    file.seek(bps * sector_begin)
    return file.read(bps * n_sector)

def read_bytes_buffer(buffer, offset, size=1) -> bytes:
    """
    Hàm đọc chuỗi từ buffer tại vị trí `offset` với kích thước `size`.
    Nếu offset ở hệ 16 thì viết thêm tiền tố `0x`. Vd: `0x0DC`.
    
    Ví dụ: đọc tên file trên entry chính (8 byte tại offset `00`).
    >>> read_string(buffer, '00', 8)
    >>> read_string(buffer, 0, 8)
    """
        
    return buffer[offset:offset+size]

def read_number_buffer(buffer, offset, size) -> int:
    """
    Hàm đọc số nguyên không dấu từ buffer tại vị trí `offset` với kích thước `size`.
    Nếu offset viết theo hex, truyền vào dưới dạng chuỗi (vd: '0B', '0D', ...)
    Nếu offset viết ở hệ 10, truyền vào dưới dạng số (vd: 110, 4096, ...)
    Hàm này đã xử lý số little endian.
    
    Cách dùng tương tự `read_string_buffer`
    """
    buffer = read_bytes_buffer(buffer, offset, size)
    return dec(buffer[::-1].hex())


def read_sector_chain(file_object, sector_list, bps=512):
    """
    Hàm đọc một dãy các sector từ mảng.
    Trả về: buffer đọc được.
    """
    buffer = b''
    for sector in sector_list:
        buffer += read_sectors(file_object, sector, 1, bps)
    return buffer



def hex_to_dec(hex_string):
    return int(hex_string, 16)

def read_ntfs_volume(f):
    # with open(volume_path, 'rb') as f:
        # Đọc NTFS patrition boot sector 
        boot_sector = f.read(512)

        # Đọc lấy thông tin từ 512 bytes của boot sector
        byte_offset = hex_to_dec('0x0B') # số bytes trên mỗi sector
        bytes_per_sector = int.from_bytes(boot_sector[byte_offset:byte_offset + 2], byteorder='little')

        byte_offset = hex_to_dec('0x0D') # số sector ở mỗi cluster
        sectors_per_cluster = int.from_bytes(boot_sector[byte_offset:byte_offset + 1], byteorder='little')

        byte_offset = hex_to_dec('0x0E') # sector dự phòng
        reserved_sectors = int.from_bytes(boot_sector[byte_offset:byte_offset + 2], byteorder='little')

        byte_offset = hex_to_dec('0x28') # tổng số sector
        total_sectors = int.from_bytes(boot_sector[byte_offset:byte_offset + 8], byteorder='little')

        byte_offset = hex_to_dec('0x30') # vị trí bắt đầu của MFT
        mft_start_cluster = int.from_bytes(boot_sector[byte_offset:byte_offset + 8], byteorder='little')
        mft_begin = sectors_per_cluster * mft_start_cluster
        
        byte_offset = hex_to_dec('0x38') # vị trí bắt đầu của MFT dự phòng
        mft_mirr = int.from_bytes(boot_sector[byte_offset:byte_offset + 8], byteorder='little')

        mft_offset = mft_start_cluster * bytes_per_sector * sectors_per_cluster

        # Đến vị trí bắt đầu của MFT và đọc lấy thông tin
        f.seek(mft_offset)
        mft = f.read(bytes_per_sector * sectors_per_cluster)

        print('Bytes per sector:', bytes_per_sector)
        print('Sectors per cluster:', sectors_per_cluster)
        print('Total sectors:', total_sectors)
        print('MFT start cluster:', mft_start_cluster)
            # Return the MFT and other volume information
        #return mft, bytes_per_sector, sectors_per_cluster, reserved_sectors, total_sectors
        return bytes_per_sector, mft, mft_begin, total_sectors, sectors_per_cluster


def clusterChainToSectors(sectors_per_cluster, clusterChain):
    # Hàm đổi danh sách các cluster thành danh sách các sector
    sectors = []
    for cluster in clusterChain:
        for i in range(sectors_per_cluster):
            sectors.append(cluster * sectors_per_cluster + i)
    return sectors


def read_entry_info(volume_path):
    with open(volume_path, 'rb') as f:
        bytes_per_sector, mft, mft_begin, total_sectors, sectors_per_cluster = read_ntfs_volume(f)
        sectors_index = 0
        skipped_entry = 0

        # Mỗi lần đọc 2 sectors (vì 1 sector bằng 512 bytes => 2 sectors = 1024 bytes, bằng 1 MFT Entry)
        # print('Read buffer successfully!!!')
        j = 0
        # while sectors_index < total_sectors: 
        while sectors_index < total_sectors:
            # print('Sector index: ', sectors_index)
            j +=1
            skipped = False
            attribute_type_id = 0
            attribute_offset = 0 
            #
            buffer = read_sectors(f, mft_begin + sectors_index,2)
            signature = read_bytes_buffer(buffer, 0, 4)
            # print('Read signature successfully!!!')

            # 4 bytes đầu của MFT là  dấu hiệu nhận biết MFT entry có phải là "FILE" ko, trả về byte
            if signature != b'FILE': #  b là ép kiểu 'FILE' ra byte
                sectors_index +=2
                skipped_entry +=1

                if skipped_entry > 100:
                    break

                continue

            total_bytes_read = 0
            attribute_offset= read_number_buffer(buffer, 0x14, 2)
            # print('Read attribute_offset successfully!!!')
            
            #Đọc 2 bytes tại offset 20, 21 (0x14, 0x15) của MFT Entry để lấy offset của attribute đầu tiên
            i = 0
            # while True:
            while True:
                #Vị trí từ 00 - 03: dấu hiệu nhận biết '$FILE_NAME hoặc là các attribute khác'
                i +=1
                attribute_type_id = read_number_buffer(buffer, attribute_offset, 4)
                if attribute_type_id in (0xFFFFFFFF, 0x0) or total_bytes_read >= 1024:
                    break
                
                #Vị trí từ 04 - 07: size bằng byte của attribute
                attribute_length = read_number_buffer(buffer, attribute_offset + 4, 4)
                # print("Attribute type id: ", attribute_type_id)
                # print("Attribute length: ", attribute_length)
                # print("--------------")

                total_bytes_read += attribute_length

                #Vị trí từ 08 - 08: cờ báo resident
                resident_flag = read_number_buffer(buffer, attribute_offset + 8, 1)

                if resident_flag > 1:
                    break
                
                #Vị trí từ 16 - 19: kích thước nội dung của attribute
                attribute_content_size = read_number_buffer(buffer, attribute_offset + 16, 4)

                #Vị trí từ 20 - 21: nơi bắt đầu phần nội dung của attribute
                attribute_content_offset = read_number_buffer(buffer, attribute_offset + 20, 2)

                if (attribute_type_id == 48):   #FILE_NAME
                    # Đọc chiều dài tên tại byte thứ 64 (từ phần nội dung attr)
                    name_length = read_number_buffer(buffer, attribute_offset + attribute_content_offset + 64, 1)
                    # Đọc tên tại byte thứ 66 (từ phần nội dung attr)
                    file_name = read_bytes_buffer(buffer, attribute_offset + attribute_content_offset + 66, name_length* 2)
                    file_name = file_name.decode('utf-16le')
                    if '$' in file_name:
                        skipped = True
                        break

                    # thời gian tạo tập tin, đọc byte thứ 8-15
                    time_create = filetime_to_dt(read_number_buffer(buffer, attribute_offset + attribute_content_offset + 8, 8))
                    # thời gian tập tin có sự thay đổi, đọc byte thứ 16-23
                    time_modified = filetime_to_dt(read_number_buffer(buffer, attribute_offset + attribute_content_offset + 16, 8))
                    # thời gian truy cập tập tin mới nhất, đọc byte thứ 32-39
                    time_accessed = filetime_to_dt(read_number_buffer(buffer, attribute_offset + attribute_content_offset + 32, 8))
                real_file_size = 0
                if (attribute_type_id == 128):  # Attribute loại $DATA
                    # Nếu data là resident
                    if resident_flag == 0:
                        # Nếu $DATA là resident thì kích thước file chính là kích thước của attribute trong MFT entry
                        real_file_size = attribute_content_size
                        # Đọc phần nội dung
                        fileContent = read_bytes_buffer(buffer, attribute_offset + attribute_content_offset, attribute_content_size)
                        # Sector bắt đầu cũng chính là số sector của attribute
                        file_Sector = sectors_index
                    # Nếu data là non-resident
                    elif resident_flag == 1:
                        file_run_offset = read_number_buffer(buffer, attribute_offset + 0x20, 2)
                        # Nếu attribute là nonresident thì nó có chứa thêm size thực của attribute
                        real_file_size = read_number_buffer(buffer, attribute_offset + 0x30, 7)
                        
                        if file_name.lower().endswith('.txt'):
                            # print('Run into txt')
                            # 1 byte tại offset 1 của data của $DATA: số lượng cluster
                            file_cluster_numer = read_number_buffer(buffer, attribute_offset + file_run_offset + 1, 1)
                            # 2 byte tại offset 2 của data của $DATA: chỉ số cluster đầu của vùng chứa data thực
                            file_cluster_begin = read_number_buffer(buffer, attribute_offset + file_run_offset + 2, 2)
                            # Lập danh sách các cluster chứa data thực
                            file_cluster_list = [c for c in range(file_cluster_begin, file_cluster_begin + file_cluster_numer)]
                            # Lập danh sách các sector chứa data thực 
                            file_sector_list = clusterChainToSectors(sectors_per_cluster, file_cluster_list)
                            # Đọc nội dung thực 
                            fileContent = read_sector_chain(f, file_sector_list, bytes_per_sector)
                        else:
                            file_extension = '.' + file_name.split('.')[-1]
                            if file_extension in DOCUMENT_EXTENSIONS:
                                print(f"The file \"{file_name}\" is supported by {DOCUMENT_EXTENSIONS[file_extension]}")
                            else:
                                print(f"The file {file_name} is not supported in this program")            

                attribute_offset = (attribute_offset + attribute_length)

            if not skipped and '$' not in file_name:
                print('Tên: {}\n'
                            'Size: {} bytes\n'
                            'Sector begin: {}\n'.format(file_name, real_file_size, sectors_index))
                if file_name.lower().endswith('.txt'):
                    print(fileContent.decode('utf-8'))
                print('--------------------------------------------------------------')

            # Tăng vị trí sector lên 2 <=> 1024 bytes
            sectors_index += 2

                #whie True:
            #  while sectors_index < total_sectors: 
