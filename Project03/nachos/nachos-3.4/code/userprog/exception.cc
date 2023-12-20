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


// sc handle File 
int doSC_Create() // create file
{
  int virtAddr;
  char* filename;

    //  printf("\n SC_Create call...");
  //printf("\n Reading virtual address of file name.");
  DEBUG(dbgFile,"\n SC_Create call ...");
  DEBUG(dbgFile,"\n Reading virtual address of filename");
  
  // check for exception
  virtAddr = machine->ReadRegister(4);
  DEBUG (dbgFile,"\n Reading filename.");
  filename = User2System(virtAddr,MaxFileLength+1);
  if (filename == NULL)
    {
      printf("\n Not enough memory in system");
      DEBUG(dbgFile,"\n Not enough memory in system");
      machine->WriteRegister(2,-1);
      delete filename;
      return -1;
    }
  
  if (strlen(filename) == 0 || (strlen(filename) >= MaxFileLength+1))
    {
      printf("\n Too many characters in filename: %s",filename);
      DEBUG(dbgFile,"\n Too many characters in filename");
      machine->WriteRegister(2,-1);
      delete filename;
      return -1;
    }

  //printf("\n Finish reading filename.");
  //printf("\n File name: '%s'",filename);
  DEBUG(dbgFile,"\n Finish reading filename.");
  //DEBUG(dbgFile,"\n File name : '"<<filename<<"'");

  // Create file with size = 0
  if (!fileSystem->Create(filename,0))
    {
      printf("\n Error create file '%s'",filename);
      delete filename;
      machine->WriteRegister(2,-1);
      delete filename;
      return -1;
    }
  //printf("\n Create file '%s' success",filename);

  machine->WriteRegister(2,0);

  delete filename;
  return 0;
}


/*
Input: 
Output:
Purpose: End thread , because exit() was called
*/
int doSC_Exit()
{
  printf("\n\n Calling SC_Exit.");
  DEBUG(dbgFile, "\n\n Calling SC_Exit.");

  // avoid harry
  IntStatus oldLevel = interrupt->SetLevel(IntOff);

  int exitStatus;
  //ProcessHashData *processData;

  exitStatus = machine->ReadRegister(4);

  // if process exited with error, print error
  if (exitStatus != 0)
    printf("\nProcess %s exited with error level %d",currentThread->getName(),exitStatus);

  //  currentThread->Finish();
  (void) interrupt->SetLevel(oldLevel);
  interrupt->Halt();
  return 0;
}

/*
Input: file type (reg5)
       0 - standard file
       1 - read only
       2 - encrypted

Output:  -1 - error
         OpenFileID -success
 
Purpose: do Open a file
*/
int doSC_Open()
{
  //  printf("\n Calling SC_Open.");
  int virtAddr = machine->ReadRegister(4);
  int type = machine->ReadRegister(5);

  if (type < 0 || type > 2)
    {
      printf("\n SC_OpenError: unexpected file type: %d",type);
      return -1;
    }
  
  int id = currentThread->fTab->FindFreeSlot();
  if (id < 0)
    {
      printf("\n SC_OpenError: No free slot.");
      return -1;
    }

  char *filename = User2System(virtAddr,MaxFileLength+1);

  if (filename == NULL)
    {
      printf("\n Not enough memory in system");
      DEBUG(dbgFile,"\n Not enough memory in system");
      machine->WriteRegister(2,-1);
      delete filename;
      return -1;
    }

  if (strlen(filename) == 0 || (strlen(filename) >= MaxFileLength+1))
    {
      printf("\n Too many characters in filename: %s",filename);
      DEBUG(dbgFile,"\n Too many characters in filename");
      machine->WriteRegister(2,-1);
      delete filename;
      return -1;
    }

  OpenFile* of = fileSystem->Open(filename);

  if (of == NULL){
    printf("\n Error opening file:  %s",filename);
    DEBUG(dbgFile,"\n Error opening file.");
    machine->WriteRegister(2,-1);
    delete filename;
    return -1;
  }

  int rs = currentThread->fTab->fdOpen(virtAddr,type,id,of);
  
  machine->WriteRegister(2,rs);

  return rs;
}


/*
Input: OpenfileID = reg4
Output: 0- success , -1 - fail
Purpose: do close file 
*/
int doSC_Close() // close file
{
  int id = machine->ReadRegister(4);
  if (id < 0 || id >= currentThread->fTab->GetMax())
    {
      printf("\n CloseError: Unexpected file id: %d",id);
      return -1;
    }
  if (!currentThread->fTab->IsExist(id)){
    printf("\n CloseError: closing file id %d is not opened",id);
    return -1;
  }

  //currentThread->
  currentThread->fTab->fdClose(id);
  return 0;
}

/*
Input: User space address = reg4, buffer size = reg5, OpenfileID = reg6
Output: -1: error
        numbytes were read
Purpose: do read from file or console
*/
int doSC_Read()
{
  //  printf("\n Calling SC_Read.");
  int virtAddr = machine->ReadRegister(4);
  int size = machine->ReadRegister(5);
  int id = machine->ReadRegister(6);
  
  if (size <= 0)
    {
      printf("\nSC_ReadError: unexpected buffer size: %d",size);
      return -1;
    }

  if (id < 0 || id >= currentThread->fTab->GetMax())
    {
      printf("\n ReadError: Unexpected file id: %d",id);
      return -1;
    }
  if (!currentThread->fTab->IsExist(id)){
    printf("\n ReadError: reading file id %d is not opened",id);
    return -1;
  }

  int rs = currentThread->fTab->fdRead(virtAddr,size,id);
  
  machine->WriteRegister(2,rs);

  return rs;
}


/*
Input: User space address = reg4, buffer size= reg5, OpenFileID = reg6
Output: = -1 - error
        or = numbytes were writen
Purpose: do write to file or console
*/
int doSC_Write()
{
  //  printf("\n Calling SC_Write.");
  int virtAddr = machine->ReadRegister(4);
  int size = machine->ReadRegister(5);
  int id = machine->ReadRegister(6);

  if (size < 0)
    {
      printf("\nSC_WriteError: unexpected buffer size: %d",size);
      return -1;
    }
  else if (size == 0)
    return 0;

  if (id < 0 || id >= currentThread->fTab->GetMax())
    {
      printf("\n WriteError: Unexpected file id: %d",id);
      return -1;
    }
  if (!currentThread->fTab->IsExist(id)){
    printf("\n WriteError: writing file id %d is not opened",id);
    return -1;
  }

  int rs = currentThread->fTab->fdWrite(virtAddr,size,id);
  
  machine->WriteRegister(2,rs);

  return rs;
}

/*
Input: offset = reg4, OpenFileID = reg5
Output: currentOffset, or -1 - fail
Purpose: do seek the pointer of a file. If seek to offset -1 mean SEEK_END 
*/
int doSC_Seek()
{
  int id = machine->ReadRegister(5);
  if (id < 0 || id >= currentThread->fTab->GetMax())
    {
      printf("\n SC_SeekError: Unexpected file id: %d",id);
      return -1;
    }
  if (!currentThread->fTab->IsExist(id)){
    printf("\n SC_SeekError: seeking file id %d is not opened",id);
    return -1;
  }

  int offset = machine->ReadRegister(4);
  currentThread->fTab->fdSeek(offset,id);

  return 0;
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
		
		case SC_Create:
			doSC_Create();
			IncreasePC();
			break;

		case SC_Open:
			doSC_Open();
			IncreasePC();
			break;

		case SC_Read:
			doSC_Read();
			IncreasePC();
			break;

		case SC_Write:
			doSC_Write();
			IncreasePC();
			break;

		case SC_Seek:
			doSC_Seek();
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
