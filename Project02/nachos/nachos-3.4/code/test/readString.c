#include "syscall.h"

int main(){
	char string[50];
	int length = 50;
	ReadString(string, length);
	PrintString(string);
	return 0;
}
