# factors.py

number = int(input("Enter a number: "))

print(f"Factors of {number}:")

for i in range(1, number + 1):
    if number % i == 0:
        if i % 2 == 0:
            print(f"{i} is even")
        else:
            print(f"{i} is odd")