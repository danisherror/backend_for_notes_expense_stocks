from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from auth.auth import decode_jwt_token, get_current_user
from database.database import notes_collection
from models.model import NoteCreate, NoteUpdate, NoteResponse
from bson import ObjectId
from datetime import datetime

router = APIRouter()


@router.post("/notes", response_model=NoteResponse)
async def create_note(note: NoteCreate, token: str = Depends(get_current_user)):
    note_dict = note.dict()
    note_dict["owner"] = token
    note_dict["created_at"] = datetime.utcnow()
    note_dict["last_modified"] = datetime.utcnow()
    result= notes_collection.insert_one(note_dict)
    return NoteResponse(**note_dict, id=str(result.inserted_id))


@router.get("/notes", response_model=List[NoteResponse])
async def get_notes(token: str = Depends(get_current_user)):
    notes = notes_collection.find({"owner": token})
    if not notes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No notes found"
        )
    return [NoteResponse(**note, id=str(note["_id"])) for note in notes]


@router.get("/notes/{note_id}",response_model=NoteResponse)
async def get_notes(note_id: str, token: str = Depends(get_current_user)):
    notes = notes_collection.find_one(ObjectId(note_id))
    if not notes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No notes found"
        )
    else:
        return NoteResponse(**notes, id=str(notes["_id"]))


@router.put("/notes/{note_id}", response_model=NoteResponse)
async def update_notes(
    note_id: str, note: NoteUpdate, token: str = Depends(get_current_user)
):
    note.last_modified = datetime.utcnow()
    update_data = {k: v for k, v in note.dict().items() if v is not None}
    notes = notes_collection.find_one_and_update(
        {"_id":ObjectId(note_id)}, {"$set": update_data}, return_document=True
    )
    if not notes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No notes found"
        )
    return NoteResponse(**notes, id=str(notes["_id"]))


@router.delete("/notes/{note_id}",response_model=dict)
async def delete_note(note_id: str, token: str = Depends(get_current_user)):
    notes = notes_collection.find_one_and_delete({"_id":ObjectId(note_id)})
    if not notes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No notes found"
        )
    return {"Message": "Expense deleted successfully"}

