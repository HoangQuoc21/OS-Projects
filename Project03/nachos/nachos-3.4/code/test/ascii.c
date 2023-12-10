#include"syscall.h"

void intToHex(int num, char* str) {
    int i = 0;
    int temp1  = 0; 
    char temp = '\0';



    /* Xử lý trường hợp số 0 riêng biệt */
    if (num == 0) {
        str[i++] = '0';
        str[i] = '\0';
        return;
    }

    /* Chuyển đổi số thành chuỗi hexa */
    while (num != 0) {
        temp1  = 0; 
        temp1 = num % 16; 
        if(temp1 < 10) { 
            str[i++] = temp1 + 48; 
        } 
        else { 
            str[i++] = temp1 + 55; 
        } 
        num = num/16; 
    } 

    str[i] = '\0'; // Kết thúc chuỗi
    
    /* Đảo ngược chuỗi */
    temp = str[0];
    str[0] = str[1];
    str[1] = temp;
}


int main() {
    // In tiêu đề của bảng mã ASCII
    const char* charToPrint = "\0";
    int i = 0;
    char dec[4], hexa[4]; // Buffer cho số thập phân

    PrintString("DEC\tHEX\tASCII");
    PrintChar('\n');

    // Chỉ in ra các ksi tự có thể in được
    for (i = 32; i < 128; ++i) {
        // Thay thế giá trị đặc biệt nếu có
        switch (i) {
            case 32:
                charToPrint = "SPACE";
                break;
            case 127:
                charToPrint = "DEL";
                break;
            default:
                dec[0] = (char)i;
                dec[1] = '\0';
                charToPrint = dec;
        }

        PrintInt(i);
        PrintString("\t");

        intToHex(i, hexa);
        PrintString(hexa);
        PrintString("\t");

        PrintString(charToPrint);
        PrintChar('\n');

    }
    Halt();
}
