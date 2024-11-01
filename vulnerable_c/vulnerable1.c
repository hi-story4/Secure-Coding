#include <stdio.h>
#include <stdlib.h>

void calculate_discount(int item_count, int item_price) {
    // int -> long long
    long long total_price = (long long)item_count * (long long)item_price;
    int discount = 0;

    if (item_count > 10) {
        discount = total_price * 0.2; 
    }

    if (total_price < 0) {
        printf("Congratulations! You've purchased items for free. Total price: %d\n", total_price);
    } else {
        printf("Total price after discount: %d\n", total_price - discount);
    }
}

int main() {
    int count, price;
    
    printf("Enter number of items: ");
    if (scanf("%d", &count) != 1 || count < 0) {
        printf("Invalid input. Item count must be a non-negative integer.\n");
        return 1;
    }

    printf("Enter price per item: ");
    if (scanf("%d", &price) != 1 || price < 0) {
        printf("Invalid input. Item price must be a non-negative integer.\n");
        return 1;
    }

    calculate_discount(count, price);
    return 0;
}
