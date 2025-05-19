from pydantic import BaseModel

class User(BaseModel):
    id: int # ou str, selon votre BDD
    username: str
    email: Optional[str] = None # Exemple d'autres champs
    organization_id: int # ou str, selon votre BDD
    role: Optional[str] = None # Exemple

    # Si vous utilisez un ORM et que vous chargez l'utilisateur depuis la BDD
    # class Config:
    #     orm_mode = True