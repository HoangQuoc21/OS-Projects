#include"syscall.h"

int main() {
	int n, a[101], isAsc, temp, i, j;
	do {	
		PrintString("n: ");
		n = ReadInt();
	} while (n <= 0 || n > 100);
	for (i = 0; i < n; i++)
	{
		a[i] = ReadInt();
	}
	
	PrintString("Order (1: Ascending, 0: Descending): ");
	isAsc = ReadInt();

	for (i = 0 ; i< n;i++) {
		for (j = 0; j < n - 1; j++) {			
			if ((!isAsc && a[j] < a[j + 1]) || (isAsc && a[j] > a[j + 1])) {
				temp = a[j];
				a[j] = a[j + 1];
				a[j + 1] = temp;
			}
		}
	}
	
	for (i = 0; i < n; i++)
	{
		PrintInt(a[i]);
		PrintChar(' ');
	}
	PrintChar('\n');
	Halt();
}
