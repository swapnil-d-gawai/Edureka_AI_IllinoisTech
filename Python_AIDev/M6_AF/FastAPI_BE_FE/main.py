from threading import Lock

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator


class Employee(BaseModel):
    id: int | None = None
    name: str
    position: str
    email: str


class EmployeeUpdate(BaseModel):
    # The model makes PUT a validated partial update: omitted fields keep their value.
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1)
    position: str | None = Field(default=None, min_length=1)
    email: str | None = Field(default=None, min_length=1)

    @field_validator("name", "position", "email", mode="before")
    @classmethod
    def reject_null_values(cls, value):
        if value is None:
            raise ValueError("field may be omitted, but cannot be null")
        return value


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

# Keep a high-water mark so deleting a row never causes an ID to be reused.
next_employee_id = max((employee.id or 0 for employee in employees), default=0) + 1
employee_id_lock = Lock()

@app.get("/employees")
def get_employees():
    return {"employees": employees}

@app.get("/employees/{employee_id}")
def get_employee(employee_id: int):
    for employee in employees:
        if employee.id == employee_id:
            return {"employee": employee}
    return JSONResponse(status_code=404, content={"error": "Employee not found"})

@app.post("/employees")
def create_employee(employee: Employee):
    global next_employee_id
    with employee_id_lock:
        # Check existing values too, so the allocation remains collision-free.
        next_employee_id = max(
            next_employee_id,
            max((item.id or 0 for item in employees), default=0) + 1,
        )
        employee.id = next_employee_id
        next_employee_id += 1
        employees.append(employee)
    return {"employee": employee}

@app.put("/employees/{employee_id}")
def update_employee(employee_id: int, updated_employee: EmployeeUpdate):
    for index, employee in enumerate(employees):
        if employee.id == employee_id:
            updated_data = employee.model_dump()
            updated_data.update(updated_employee.model_dump(exclude_unset=True))
            # The URL owns the resource identity; clients cannot replace it in PUT.
            updated_data["id"] = employee_id
            updated_record = Employee(**updated_data)
            employees[index] = updated_record
            return {"employee": updated_record}
    return JSONResponse(status_code=404, content={"error": "Employee not found"})

@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int):
    for employee in employees:
        if employee.id == employee_id:
            employees.remove(employee)
            return {"message": "Employee deleted successfully"}
    return JSONResponse(status_code=404, content={"error": "Employee not found"})