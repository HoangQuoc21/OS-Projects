import ctypes

def get_volume_type(volume_name):
    # Xác định đường dẫn ổ đĩa dựa trên tên ổ đĩa được cung cấp
    drive = volume_name.upper() + ":\\"

    # Chuyển đổi đường dẫn ổ đĩa thành kiểu dữ liệu c_wchar_p của ctypes
    volume_name = ctypes.c_wchar_p(drive)
    
    # Khai báo các biến để lưu thông tin hệ thống tệp
    file_system_name_buffer = ctypes.create_unicode_buffer(1024)
    volume_serial_number = ctypes.c_ulong()
    max_component_length = ctypes.c_ulong()
    file_system_flags = ctypes.c_ulong()

    # Gọi hàm API Windows để lấy thông tin về ổ đĩa
    result = ctypes.windll.kernel32.GetVolumeInformationW(
        volume_name,
        None,
        0,
        ctypes.pointer(volume_serial_number),
        ctypes.pointer(max_component_length),
        ctypes.pointer(file_system_flags),
        file_system_name_buffer,
        ctypes.sizeof(file_system_name_buffer)
    )

    # Kiểm tra kết quả trả về từ hàm
    if result == 1:
        # Trích xuất tên hệ thống tệp và xác định loại hệ thống tệp
        file_system_name = file_system_name_buffer.value
        if "FAT32" in file_system_name:
            return "FAT32"
        elif "NTFS" in file_system_name:
            return "NTFS"
        else:
            return "Unknown"
    else:
        return "Volume not found"
