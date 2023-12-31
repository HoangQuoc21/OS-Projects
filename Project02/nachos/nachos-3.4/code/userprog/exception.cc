// exception.cc
//	Entry point into the Nachos kernel from user programs.
//	There are two kinds of things that can cause control to
//	transfer back to here from user code:
//
//	syscall -- The user code explicitly requests to call a procedure
//	in the Nachos kernel.  Right now, the only function we support is
//	"Halt".
//
//	exceptions -- The user code does something that the CPU can't handle.
//	For instance, accessing memory that doesn't exist, arithmetic errors,
//	etc.
//
//	Interrupts (which can also cause control to transfer from user
//	code into the Nachos kernel) are handled elsewhere.
//
// For now, this only handles the Halt() system call.
// Everything else core dumps.
//
// Copyright (c) 1992-1993 The Regents of the University of California.
// All rights reserved.  See copyright.h for copyright notice and limitation
// of liability and disclaimer of warranty provisions.

#include "copyright.h"
#include "system.h"
#include "syscall.h"

//----------------------------------------------------------------------
// ExceptionHandler
// 	Entry point into the Nachos kernel.  Called when a user program
//	is executing, and either does a syscall, or generates an addressing
//	or arithmetic exception.
//
// 	For system calls, the following is the calling convention:
//
// 	system call code -- r2
//		arg1 -- r4
//		arg2 -- r5
//		arg3 -- r6
//		arg4 -- r7
//
//	The result of the system call, if any, must be put back into r2.
//
// And don't forget to increment the pc before returning. (Or else you'll
// loop making the same system call forever!
//
//	"which" is the kind of exception.  The list of possible exceptions
//	are in machine.h.
//----------------------------------------------------------------------

void IncreasePC()
{
	int pcAfter = machine->ReadRegister(NextPCReg) + 4;
	machine->WriteRegister(PrevPCReg, machine->ReadRegister(PCReg));
	machine->WriteRegister(PCReg, machine->ReadRegister(NextPCReg));
	machine->WriteRegister(NextPCReg, pcAfter);
}
/*add syscall handlers*/
void HandleReadInt()
{
	/*int: [-2147483648 , 2147483647] --> max length = 11*/
	const int maxlen = 11;
	char num_string[maxlen] = {0};
	long long ret = 0;
	for (int i = 0; i < maxlen; i++)
	{
		char c = 0;
		gSynchConsole->Read(&c, 1);
		if (c >= '0' && c <= '9')
			num_string[i] = c;
		else if (i == 0 && c == '-')
			num_string[i] = c;
		else
			break;
	}
	int i = (num_string[0] == '-') ? 1 : 0;
	while (i < maxlen && num_string[i] >= '0' && num_string[i] <= '9')
		ret = ret * 10 + num_string[i++] - '0';
	ret = (num_string[0] == '-') ? (-ret) : ret;
	machine->WriteRegister(2, (int)ret);
}
void HandlePrintInt()
{
	int n = machine->ReadRegister(4);
	/*int: [-2147483648 , 2147483647] --> max length = 11*/
	const int maxlen = 11;
	char num_string[maxlen] = {0};
	int tmp[maxlen] = {0}, i = 0, j = 0;
	if (n < 0)
	{
		n = -n;
		num_string[i++] = '-';
	}
	do
	{
		tmp[j++] = n % 10;
		n /= 10;
	} while (n);
	while (j)
		num_string[i++] = '0' + (char)tmp[--j];
	gSynchConsole->Write(num_string, i);
	machine->WriteRegister(2, 0);
}

void HandleReadChar()
{
	int maxBytes = 255;
	char *buffer = new char[255];
	int numBytes = gSynchConsole->Read(buffer, maxBytes);

	if (numBytes > 1) // unvalid if input more than 1 character
	{
		printf("INPUT ONLY 1 character !!!");
		DEBUG('a', "\nERROR: INPUT ONLY 1 character !!!");
		machine->WriteRegister(2, 0);
	}
	else if (numBytes == 0) // null character
	{
		printf("NULL character !!!");
		DEBUG('a', "\nERROR: NULL character !!!");
		machine->WriteRegister(2, 0);
	}
	else
	{
		// gotten string has only 1 char, get the char at index = 0,
		  // return it to reg2
		char c = buffer[0];
		machine->WriteRegister(2, c);
	}

	delete buffer;
}

void HandlePrintChar()
{
	// get the char from reg4
	char c = (char)machine->ReadRegister(4);

	// print the char
	gSynchConsole->Write(&c, 1);
}

void HandleReadString() {
    int buffer = machine->ReadRegister(4);
    int length = machine->ReadRegister(5);
    char *buf = NULL;
    if (length > 0) {
        buf = new char[length];
        if (buf == NULL) {
            char msg[] = "Not enough memory in system.\n";
            gSynchConsole->Write(msg,strlen(msg));
        }
        else
            memset(buf, 0, length);
    }
    if (buf != NULL) {
        /*make sure string is null terminated*/
        gSynchConsole->Read(buf,length-1);
        int n = strlen(buf)+1;
        for (int i = 0; i < n; i++) {
            machine->WriteMem(buffer + i, 1, (int)buf[i]);
        }
        delete[] buf;
    }	    
    machine->WriteRegister(2, 0);
}
void HandlePrintString() {
    int buffer = machine->ReadRegister(4), i = 0;
    /*limit the length of strings to print both null and non-null terminated strings*/
    const int maxlen = 256;
    char s[maxlen] = {0};
    while (i < maxlen) {
        int oneChar = 0;
        machine->ReadMem(buffer+i, 1, &oneChar);
        if (oneChar == 0) break;
        s[i++] = (char)oneChar;
    }
    gSynchConsole->Write(s,i);
    machine->WriteRegister(2, 0);
}

void ExceptionHandler(ExceptionType which)
{
	int type = machine->ReadRegister(2);
	switch (which)
	{
	case NoException:
		return;
	case SyscallException:
		switch (type)
		{
		case SC_Halt:
			DEBUG('a', "Shutdown, initiated by user program.\n");
			interrupt->Halt();
		case SC_ReadInt:
			HandleReadInt();
			IncreasePC();
			break;
		case SC_PrintInt:
			HandlePrintInt();
			IncreasePC();
			break;
		case SC_ReadChar:
			HandleReadChar();
			IncreasePC();
			break;
		case SC_PrintChar:
			HandlePrintChar();
			IncreasePC();
			break;
		case SC_ReadString:
			HandleReadString();
			IncreasePC();
			break;
		case SC_PrintString:
			HandlePrintString();
			IncreasePC();
			break;
		}

		break;
	case PageFaultException:
		DEBUG('a', "No valid translation found.\n");
		printf("No valid translation found.\n");
		interrupt->Halt();
		break;
	case ReadOnlyException:
		DEBUG('a', "Write attempted to page marked \"read - only\".\n");
		printf("Write attempted to page marked \"read-only\".\n");
		interrupt->Halt();
		break;
	case BusErrorException:
		DEBUG('a', "Translation resulted in an invalid physical address.\n");
		printf("Translation resulted in an invalid physical address.\n");
		interrupt->Halt();
		break;

	//=================== QUOC WROTE THIS =====================
	case AddressErrorException:
		DEBUG('a', "Unaligned reference or one that was beyond the end of the address space.\n");
		printf("Unaligned reference or one that was beyond the end of the address space.\n");
		interrupt->Halt();
		break;
	case OverflowException:
		DEBUG('a', "Integer overflow in add or sub.\n");
		printf("Integer overflow in add or sub.\n");
		interrupt->Halt();
		break;
	case IllegalInstrException:
		DEBUG('a', "Unimplemented or reserved instr.\n");
		printf("Unimplemented or reserved instr.\n");
		interrupt->Halt();
		break;
	case NumExceptionTypes:
		DEBUG('a', "NumExceptionTypes.\n");
		printf("NumExceptionTypes.\n");
		interrupt->Halt();
		break;
	//=======================================================
	default:
		printf("Unexpected user mode exception %d %d\n", which, type);
		ASSERT(FALSE);
	}
}
