# constant.py

# Boot Sector Offsets
BS_FAT_TYPE = 0x52
BS_SECTOR_SIZE = 0x0B
BS_SECTOR_CLUSTER = 0x0D
BS_SECTOR_BOOT = 0X0E
BS_FAT = 0x10
BS_TOTAL_SECTOR = 0x20
BS_SECTOR_FAT = 0x24
BS_RDET_CLUSTER_STARTED = 0x2C

# Main Entry Offsets
ME_STATE = 0xB
ME_MAIN_NAME = 0x0
ME_EXPAND_NAME = 0x8
ME_CREATE_AT = 0x10
ME_UPDATE_AT = 0x18
ME_CLUSTER_START = 0x1A
ME_HIGH_WORD =  0x14
ME_LOW_WORD = 0x1A
ME_CONTENT_SIZE = 0x1C

# Sub Entry Offsets
MS_A = 0x1
MS_B = 0xE
MS_C = 0x1C

# File Extensions to Applications
DOCUMENT_EXTENSIONS = {
    '.jpeg': 'Photos',
    '.jpg': 'Photos',
    '.gif': 'Photos',
    '.png': 'Photos',
    '.pdf': 'PDF reader',
    '.doc': 'Word',
    '.docx': 'Word',
    '.html': 'Google',
    '.htm': 'Google',
    '.xls': 'Excel',
    '.xlsx': 'Excel',
    '.mp4': 'Movies and TV',
    '.mp3': 'Play music',
    '.avi': 'Movies and TV',
    '.ppt': 'Power Point',
    '.pptx': 'Power Point',
    '.zip': 'WinRar Archiver'
}

# Command Constants
STACK_COMMANDS = ['cd', 'cat', 'ls', 'cls', 'help', 'exit', 'root']
FILE_COMMANDS = ['exit', 'detail', 'cls']

# Attribute Constants
FILENAME = 0x30
DATA = 0x80
