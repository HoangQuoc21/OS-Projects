import os

def hex_to_dec(hex_string):
    return int(hex_string, 16)

def read_ntfs_volume(volume_path):
    with open(volume_path, 'rb') as f:
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
        
        byte_offset = hex_to_dec('0x38') # vị trí bắt đầu của MFT dự phòng
        mft_mirr = int.from_bytes(boot_sector[byte_offset:byte_offset + 8], byteorder='little')

        mft_offset = mft_start_cluster * bytes_per_sector * sectors_per_cluster

        # Đến vị trí bắt đầu của MFT và đọc lấy thông tin
        f.seek(mft_offset)
        mft = f.read(bytes_per_sector * sectors_per_cluster)

    print(bytes_per_sector)
    print(sectors_per_cluster)
    print(total_sectors)
    print(mft_start_cluster)
        # Return the MFT and other volume information
    #return mft, bytes_per_sector, sectors_per_cluster, reserved_sectors, total_sectors