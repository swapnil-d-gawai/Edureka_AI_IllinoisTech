# even_digit_numbers.py

results = []

for number in range(1000, 3001):
    digits = str(number)

    all_even = True

    for digit in digits:
        if int(digit) % 2 != 0:
            all_even = False
            break

    if all_even:
        results.append(digits)

print(",".join(results))