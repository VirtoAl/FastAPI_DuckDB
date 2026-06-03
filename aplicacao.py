import duckdb
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Connect to database file (persists data)
con = duckdb.connect('banco_dados.db')

# Create table on startup
con.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name VARCHAR,
    email VARCHAR,
    age INTEGER
)
""")

class User(BaseModel):
    name: str
    email: str
    age: int

@app.post("/users/")
def create_user(user: User):
    con.execute(
        "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
        (user.name, user.email, user.age)
    )
    return {"message": "User created", "user": user}

@app.get("/users/")
def list_users():
    result = con.execute("SELECT * FROM users").fetchall()
    return {"users": result}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    result = con.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return {"user": result}

@app.put("/users/{user_id}")
def update_user(user_id: int, user: User):
    con.execute(
        "UPDATE users SET name = ?, email = ?, age = ? WHERE id = ?",
        (user.name, user.email, user.age, user_id)
    )
    return {"message": "User updated"}

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    con.execute("DELETE FROM users WHERE id = ?", (user_id,))
    return {"message": "User deleted"}