#include <stdio.h>
#include <stdlib.h>

void print_message(char *message) {
    // printf(message); 
    // printf("\n");
    printf("%s\n", message);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <message>\n", argv[0]);
        return 1;
    }

    print_message(argv[1]);
    return 0;
}
