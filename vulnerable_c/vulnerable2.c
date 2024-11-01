#include <stdio.h>
#include <string.h>

void authenticate() {
    char buffer[16];
    int is_authenticated = 0;

    printf("Enter password: ");
    // 버퍼 오버플로우 방지
    // gets(buffer); 
    fgets(buffer, sizeof(buffer), stdin);

    if (is_authenticated) {
        printf("Authentication Successful! Access Granted.\n");
    } else {
        printf("Authentication Failed.\n");
    }
}

int main() {
    authenticate();
    return 0;
}
