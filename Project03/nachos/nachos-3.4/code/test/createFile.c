#include "syscall.h"

int main()
{
    char data[] = "doi mat em nhu la bo cau, con dau, con bay, con bay, con dau";
    char buffer[256];
	SpaceId id_file;
	int f_Success, bytes_read;
	

	f_Success = CreateFile("idkman.txt");
	if(f_Success == -1)
		return 1;
	
	id_file = Open("idkman.txt", 0);

    
	Write(data, strlen(data), id_file);
	
	Close(id_file);

	id_file = Open("idkman.txt", 0);

    bytes_read = Read(buffer, strlen(data), id_file); 
    PrintString(buffer);
    Close(id_file);

    Halt();    
}