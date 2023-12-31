#include "syscall.h"
#define MAX_LENGTH 32

int main()
{
	int openFileId;
	int fileSize;
	char c; //Ky tu de in ra
	char buffer[256];
	char fileName[MAX_LENGTH];
	int i = 0; //Index for loop
	PrintString("\n\t\t\t-----HIEN THI NOI DUNG FILE-----\n\n");
	PrintString(" - Nhap vao ten file can doc: ");
	
	//Goi ham ReadString de doc vao ten file
	//Co the su dung Open(stdin), nhung de tiet kiem thoi gian test ta dung ReadString
	ReadString(fileName, MAX_LENGTH);
	// PrintString(fileName);
	openFileId = Open(fileName, 0); // Goi ham Open de mo file 
	// PrintInt(openFileId);
	fileSize = Seek(-1, openFileId);
	// test write
	Write(", test chuc nang write file", 27, openFileId);

	if (openFileId != -1) //Kiem tra Open co loi khong
	{
		//Seek den cuoi file de lay duoc do dai noi dung (fileSize)
		fileSize = Seek(-1, openFileId);
		PrintString("Size of file: ");
		PrintInt(fileSize);
		PrintString("\n");
		i = 0;
		// Seek den dau tap tin de tien hanh Read
		Seek(0, openFileId);
		
		PrintString(" -> Noi dung file:\n");
		for (i = 0; i < fileSize; i++) // Cho vong lap chay tu 0 - fileSize
		{
			Read(&c, 1, openFileId); // Goi ham Read de doc tung ki tu noi dung file
			PrintChar(c); // Goi ham PrintChar de in tung ki tu ra man hinh
		}		
		PrintString("\n");
		Close(openFileId); // Goi ham Close de dong file
	}
	else
	{
		PrintString(" -> Mo file khong thanh cong!!\n\n");
	}
	return 0;
}
