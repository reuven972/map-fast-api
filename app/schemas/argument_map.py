# app/models/argument_map.py
from pydantic import BaseModel, Field
from typing import Optional  # Pour des champs optionnels futurs, si nécessaire

class TextInputModel(BaseModel):
    """
    Modèle pour l'entrée de texte à transformer en carte argumentative.
    """
    text: str = Field(
        ...,
        min_length=1,
        description="Le texte brut à transformer en carte argumentative."
    )

class ArgumentMapResponseModel(BaseModel):
    """
    Modèle pour la réponse contenant les détails de la carte argumentative créée.
    """
    id: str = Field(
        ...,
        description="L'identifiant unique de la carte argumentative (ID primaire de la base de données)."
    )
    uuid: str = Field(
        ...,
        description="L'identifiant UUID public de la carte argumentative."
    )
    xml_content: str = Field(
        ...,
        description="Le contenu XML généré pour la carte argumentative."
    )

    class Config:
        from_attributes = True # Pydantic V2 way

class XMLInputModel(BaseModel):
    """
    Modèle pour l'entrée de contenu XML à importer pour créer une carte argumentative.
    """
    xml_content: str = Field(
        ...,
        description="Le contenu XML à importer pour créer la carte argumentative."
    )