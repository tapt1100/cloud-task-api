import os
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DB_PATH = os.getenv("DB_PATH", "tasks.db")
app = FastAPI(title="Cloud Task API")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )"""
        )


init_db()


class TaskIn(BaseModel):
    title: str
    done: bool = False


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/tasks", status_code=201)
def create_task(task: TaskIn):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (task.title, int(task.done)),
        )
        return {"id": cur.lastrowid, **task.model_dump()}


@app.get("/tasks")
def list_tasks():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM tasks").fetchall()
    return [{**dict(r), "done": bool(r["done"])} for r in rows]


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return {**dict(row), "done": bool(row["done"])}


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskIn):
    with get_conn() as conn:
        cur = conn.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (task.title, int(task.done), task_id),
        )
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"id": task_id, **task.model_dump()}


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task not found")
