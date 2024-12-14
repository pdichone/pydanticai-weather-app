#validating api inputs w/o Pydantic
def create_user(data):
    if not isinstance(data.get('age'), int):
        raise ValueError("Age must be an integer")
    if not isinstance(data.get('name'), str):
        raise ValueError("Name must be a string")
    return data


# With Pydantic
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

user = User(name="Alice", age=25)
print(user.model_dump())  # {'name': 'Alice', 'age': 25}
