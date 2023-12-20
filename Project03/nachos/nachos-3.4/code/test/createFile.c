#include "syscall.h"

#define CONSOLE_INPUT 0
#define CONSOLE_OUTPUT 1
#define MAX_LENGTH 32

int main() {
    char buffer[256];
    int openFileId;
	int fileSize;
	char c;
	char fileName[MAX_LENGTH];
	int i; //Index for loop
	PrintString("\n\t\t\tHIEN THI NOI DUNG FILE\n\n");
	PrintString("Nhap vao ten file can doc: ");
	
	// read string file name
	ReadString(fileName, MAX_LENGTH);
	
    // open file
	openFileId = Open(fileName, 1);
	
	if (openFileId != -1) 
	{
		// read and save to buffer
		Read(buffer,256, openFileId);
        // print string
		PrintString("Noi dung file:\n");
		PrintString(buffer);
		Close(openFileId); // Close file
	}
	else
	{
		PrintString("Khong the mo file!\n\n");
	}
	
    Halt();
}