import ctypes

def get_volume_type(volume_name):
    drive = volume_name.upper() + ":\\"
    volume_name = ctypes.c_wchar_p(drive)
    file_system_name_buffer = ctypes.create_unicode_buffer(1024)
    volume_serial_number = ctypes.c_ulong()
    max_component_length = ctypes.c_ulong()
    file_system_flags = ctypes.c_ulong()

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

    if result == 1:
        file_system_name = file_system_name_buffer.value
        if "FAT32" in file_system_name:
            return "FAT32"
        elif "NTFS" in file_system_name:
            return "NTFS"
        else:
            return "Unknown"
    else:
        return "Volume not found"
