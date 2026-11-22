"""A beginner-friendly example of a Python class."""


class Student:
	"""A class is a blueprint for creating student objects."""

	def __init__(self, name, course):
		# __init__ runs when a new Student is created.
		# self refers to the particular student object.
		self.name = name
		self.course = course

	def introduce(self):
		"""Display information about this student."""
		print(f"Hi, I'm {self.name}. I'm studying {self.course}.")


# Create two objects (students) from the Student class.
student1 = Student("Ava", "Python")
student2 = Student("Noah", "Data Science")

# Call a method on each object.
student1.introduce()
student2.introduce()

# Each object keeps its own attribute values.
print(f"{student1.name} is taking {student1.course}.")
print(f"{student2.name} is taking {student2.course}.")
