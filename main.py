import os

# def my_list_files(startpath):
#     i = 0
#     for root, dirs, files in os.walk(startpath):
#         # dirs are folders
#         print('root{}: '.format(i+1), root)
#         print('replace',root.replace(startpath,''))
#         level = root.replace(startpath, '').count(os.sep)
#         print('level', level)
#         print('dirs{}: '.format(i+1), dirs)
#         print('files{}: '.format(i+1), files)
#         i +=1

# def list_first_level(startpath):
#     for item in os.listdir(startpath):
#         print(f''.format())
#         indent = ' '* 4
#         print(f'{os.path}')
#         if os.path.isdir(item):
#             print(item)
#         else:
#             print(item)


stack_of_root = []
def list_files(startpath):
    file_of_level = [] # Tất cả file/folder tính từ level đang duyệt đến level cao nhất (level của startpath, như mảng 2 chiều)
    i = 0
    while True:
        if not os.path.isdir(startpath): #Kiểm tra xem startpath là file hay folder
            print('Handle file!!')
            # Hàm xử lý file
            startpath = stack_of_root.pop()
            continue
        root, dirs, files = next(os.walk(startpath))
        stack_of_root.append(root)
        print('root: ', root)
        #root là đường dẫn tuyệt đối hiện tại, dirs là các folder, files là các tập tin
        file_of_current_level = [] # Tất cả file/folder của level hiện tại (mảng 1 chiều)
        level = root.replace(startpath, '').count(os.sep)
            # print(level)
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for dir in dirs:
            print('{}{}'.format(subindent, dir))
            file_of_current_level.append(dir)
        for file in files:
            print('{}{}'.format(subindent, file))
            file_of_current_level.append(file)
        file_of_level.append(file_of_current_level)
        # print(file_of_level)
        name = ''
        while True:
            name = input('Enter file or folder you want to access: ')
            if name not in file_of_current_level:
                print('Entered wrong name of file or folder!!')
                # break
            else:
                startpath = os.path.join(startpath, name)
                break #Enter right name
        # break

if __name__ == "__main__":
    absolutePath = input('Enter absolute path: ');
    list_files(absolutePath)
