import os

def displaySubfolderTree(absobuteFilePath):
    print("Subfolder tree of " + absobuteFilePath + ":");
    for root, dirs, files in os.walk(absobuteFilePath):
        level = root.replace(absobuteFilePath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print('{}{}'.format(indent, os.path.basename(root)));
        subindent = ' ' * 4 * (level + 1);
        for f in files:
            print('{}{}'.format(subindent, f));

if __name__ == "__main__":
    #xóa màn hình
    os.system("cls");
    absobuteFilePath = input("Enter absolute file path: ");
    displaySubfolderTree(absobuteFilePath);