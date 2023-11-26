#include "syscall.h"

int main(){
	char string[50];
	int length = 50;
	PrintString("Input your string: ");
	ReadString(string, length);
	PrintString(string);
	PrintChar('\n');
	Halt();
}
