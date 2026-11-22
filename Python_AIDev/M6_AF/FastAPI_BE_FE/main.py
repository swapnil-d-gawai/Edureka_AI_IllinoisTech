from fastapi import FastAPI
from pydantic import BaseModel


class Employee(BaseModel):
    id: int | None = None
    name: str
    position: str
    email: str

#Create FastAPI application
app = FastAPI(
    title="Employee Management System",
    description="A REST API to manage employee records"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Employee Management System API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

#Temporary data to store employee records
employees: list[Employee] = [
    Employee(id=1, name="John Doe", position="Software Engineer", email="john.doe@example.com"),
    Employee(id=2, name="Jane Smith", position="Project Manager", email="jane.smith@example.com"),
    Employee(id=3, name="Alice Johnson", position="Designer", email="alice.johnson@example.com"),
    Employee(id=4, name="Bob Brown", position="QA Engineer", email="bob.brown@example.com"),
    Employee(id=5, name="Charlie Davis", position="DevOps Engineer", email="charlie.davis@example.com"),
]

@app.get("/employees")
def get_employees():
    return {"employees": employees}

@app.get("/employees/{employee_id}")
def get_employee(employee_id: int):
    for employee in employees:
        if employee.id == employee_id:
            return {"employee": employee}
    return {"error": "Employee not found"}

@app.post("/employees")
def create_employee(employee: Employee):
    employee.id = len(employees) + 1
    employees.append(employee)
    return {"employee": employee}

@app.put("/employees/{employee_id}")
def update_employee(employee_id: int, updated_employee: dict):
    for employee in employees:
        if employee.id == employee_id:
            updated_data = {**employee.dict(), **updated_employee}
            updated_record = Employee(**updated_data)
            employees[employees.index(employee)] = updated_record
            return {"employee": updated_record}
    return {"error": "Employee not found"}

@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int):
    for employee in employees:
        if employee.id == employee_id:
            employees.remove(employee)
            return {"message": "Employee deleted successfully"}
    return {"error": "Employee not found"}