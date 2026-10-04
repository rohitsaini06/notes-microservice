import os
import socket
from typing import Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Notes Microservice", version="1.0.0")

# In-memory store (resets on restart; fine for a demo microservice)
notes: Dict[int, dict] = {}
_next_id = 1


class NoteIn(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field("", max_length=1000)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/whoami")
def whoami():
    """Returns the container hostname - handy to show which instance served you."""
    return {"hostname": socket.gethostname(), "version": os.getenv("APP_VERSION", "dev")}


@app.post("/notes", status_code=201)
def create_note(note: NoteIn):
    global _next_id
    item = {"id": _next_id, **note.model_dump()}
    notes[_next_id] = item
    _next_id += 1
    return item


@app.get("/notes")
def list_notes():
    return list(notes.values())


@app.get("/notes/{note_id}")
def get_note(note_id: int):
    if note_id not in notes:
        raise HTTPException(status_code=404, detail="Note not found")
    return notes[note_id]


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int):
    if note_id not in notes:
        raise HTTPException(status_code=404, detail="Note not found")
    del notes[note_id]
