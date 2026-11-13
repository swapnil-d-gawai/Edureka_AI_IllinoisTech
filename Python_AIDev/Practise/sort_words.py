# sort_words.py

words = input("Enter words separated by spaces: ")

word_list = words.split()
word_list.sort()

print("Words in alphabetical order:")
print(" ".join(word_list))