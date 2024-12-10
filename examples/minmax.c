#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
int main(int argc, char *argv[]) {
    if(argc < 4) {
    return 1;
    }
    int input1 = atoi(argv[1]);
    int input2 = atoi(argv[2]);
    int input3 = atoi(argv[3]);
    int least=input1;
    int most = input1;
    if(most < input2)
        most=input2;
    if(most<input3)
        most=input3;
    if(least>input2)
        most=input2; // error here: least=input2
    if(least>input3)
        least=input3;
    assert(least<=most);
    printf("Least: %d, Most: %d\n", least, most);
    return 0;
}