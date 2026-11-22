# Demonstrate polymorphism in Python

class Dog:
    def speak(self):
        print("Woof!")

class Cat:
    def speak(self):
        print("Meow!")

def make_animal_speak(animal):
    animal.speak()

if __name__ == "__main__":
    dog = Dog()
    cat = Cat()

    make_animal_speak(dog)
    make_animal_speak(cat)