from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from auth.auth import get_current_user
from database.database import notes_collection
from models.model import NoteCreate, NoteUpdate, NoteResponse
from bson import ObjectId
from datetime import datetime

class NotesController:
    def __init__(self):
        self.router = APIRouter()

        # Register the routes
        self.router.post("/notes", response_model=NoteResponse)(self.create_note)
        self.router.get("/notes", response_model=List[NoteResponse])(self.get_notes)
        self.router.get("/notes/{note_id}", response_model=NoteResponse)(self.get_note)
        self.router.put("/notes/{note_id}", response_model=NoteResponse)(self.update_note)
        self.router.delete("/notes/{note_id}", response_model=dict)(self.delete_note)

    async def create_note(
        self, note: NoteCreate, token: str = Depends(get_current_user)
    ):
        note_dict = note.dict()
        note_dict["owner"] = token
        note_dict["created_at"] = datetime.utcnow()
        note_dict["last_modified"] = datetime.utcnow()
        result = notes_collection.insert_one(note_dict)
        return NoteResponse(**note_dict, id=str(result.inserted_id))

    async def get_notes(self, token: str = Depends(get_current_user)):
        notes = notes_collection.find({"owner": token})
        if not notes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No notes found"
            )
        return [NoteResponse(**note, id=str(note["_id"])) for note in notes]

    async def get_note(
        self, note_id: str, token: str = Depends(get_current_user)
    ):
        note = notes_collection.find_one(ObjectId(note_id))
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No note found"
            )
        return NoteResponse(**note, id=str(note["_id"]))

    async def update_note(
        self, note_id: str, note: NoteUpdate, token: str = Depends(get_current_user)
    ):
        note.last_modified = datetime.utcnow()
        update_data = {k: v for k, v in note.dict().items() if v is not None}
        updated_note = notes_collection.find_one_and_update(
            {"_id": ObjectId(note_id)}, {"$set": update_data}, return_document=True
        )
        if not updated_note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No note found"
            )
        return NoteResponse(**updated_note, id=str(updated_note["_id"]))

    async def delete_note(
        self, note_id: str, token: str = Depends(get_current_user)
    ):
        deleted_note = notes_collection.find_one_and_delete({"_id": ObjectId(note_id)})
        if not deleted_note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No note found"
            )
        return {"Message": "Note deleted successfully"}

# Instantiate the controller and access its router
notes_controller = NotesController()
router = notes_controller.router
