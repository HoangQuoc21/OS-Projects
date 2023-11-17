import os

def init_platform():
    platformName = os.name
    if platformName == 'nt':
            print('=============== You are running on NT WINDOWS ===============')
    elif platformName == 'posix':
        print('================= You are running on posix =================')
    else:
        raise Exception(f'We are not implement in {platformName} platform')
    return platformName

def select_disk_path(platform_name, disk_path):
    if platform_name == 'nt':
        return f'\\\\.\\{disk_path}:'
    return disk_path

def generate_disk_file(disk_path):
    disk_file = os.open(disk_path, os.O_BINARY)
    return os.fdopen(disk_file, 'rb')