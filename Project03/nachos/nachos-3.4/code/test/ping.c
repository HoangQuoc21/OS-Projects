#include "syscall.h"

int main()
{
    int i;

    if(CreateSemaphore("ping", 1) == -1) Exit(-1);
    if(CreateSemaphore("pong", 0) == -1) Exit(-1);
    Exec("./test/pong");
    for(i = 0; i < 1000; i++) {
        Down("ping");
        PrintChar('A');
        Up("pong");
    }
}

