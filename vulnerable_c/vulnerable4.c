#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

void win() {
    system("/bin/sh");
}

void process_input() {
    char username[32];
    char input_buffer[64];

    printf("Enter input: ");
    // Buffer overflow 방지
    scanf("%31s", input_buffer);
    // length check
    if (strlen(input_buffer) < 32) {
        strcpy(username, input_buffer);
    }

}

int main() {
    process_input();
    printf("Execution finished.\n");
    return 0;
}
