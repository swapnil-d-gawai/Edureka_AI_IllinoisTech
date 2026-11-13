# letters_digits.py

sentence = input("Enter a sentence: ")

letters = 0
digits = 0

for character in sentence:
    if character.isalpha():
        letters += 1
    elif character.isdigit():
        digits += 1

print(f"LETTERS: {letters}")
print(f"DIGITS: {digits}")