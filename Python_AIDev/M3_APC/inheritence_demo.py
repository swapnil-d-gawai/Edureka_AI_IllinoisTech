# Demonstrate different types of inheritance in Python
# Single Inheritance
class Parent:
    def func1(self):
        print("This is a parent class function")

class Child(Parent):
    def func2(self):
        print("This is a child class function")

# Multiple Inheritance
class Mother:
    def mother_func(self):
        print("This is a mother class function")

class Father:
    def father_func(self):
        print("This is a father class function")

class ChildMultiple(Mother, Father):
    def child_func(self):
        print("This is a child class function")

# Multilevel Inheritance
class GrandParent:
    def grandparent_func(self):
        print("This is a grandparent class function")

class ParentLevel(GrandParent):
    def parent_func(self):
        print("This is a parent class function")

class ChildLevel(ParentLevel):
    def child_func(self):
        print("This is a child class function")

# Hierarchical Inheritance
class Base:
    def base_func(self):
        print("This is a base class function")

class Child1(Base):
    def child1_func(self):
        print("This is child1 class function")

class Child2(Base):
    def child2_func(self):
        print("This is child2 class function")

# Hybrid Inheritance
class HybridBase:
    def hybrid_base_func(self):
        print("This is a hybrid base class function")

class HybridChild1(HybridBase):
    def hybrid_child1_func(self):
        print("This is a hybrid child1 class function")

class HybridChild2(HybridBase):
    def hybrid_child2_func(self):
        print("This is a hybrid child2 class function")

class HybridGrandChild(HybridChild1, HybridChild2):
    def hybrid_grandchild_func(self):
        print("This is a hybrid grandchild class function") 

# Example usage
if __name__ == "__main__":
    c = Child()
    c.func1()
    c.func2()

    cm = ChildMultiple()
    cm.mother_func()
    cm.father_func()
    cm.child_func()

    cl = ChildLevel()
    cl.grandparent_func()
    cl.parent_func()
    cl.child_func()

    c1 = Child1()
    c1.base_func()
    c1.child1_func()

    c2 = Child2()
    c2.base_func()
    c2.child2_func()

    hg = HybridGrandChild()
    hg.hybrid_base_func()
    hg.hybrid_child1_func()
    hg.hybrid_child2_func()
    hg.hybrid_grandchild_func()
    # Demonstrating method resolution order (MRO)
    print(HybridGrandChild.__mro__)