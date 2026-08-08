from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas.schemas import Entrenador
from app.database import get_db
from app.models.models import Entrenador as EntrenadorModel, User as UserModel
from app.auth.dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=List[Entrenador])
def listar_entrenadores(db: Session = Depends(get_db), _: UserModel = Depends(get_current_user)):
    return db.query(EntrenadorModel).all()
