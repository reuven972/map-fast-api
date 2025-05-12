import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db_session
from app.services.llm_service import LLMService
from app.services.xml_validation_service import XMLValidationService
from app.services.xml_parsing_service import XMLParsingService
from app.models.argument_map import TextInputModel, ArgumentMapResponseModel
from app.repositories.argument_map_repository import ArgumentMapRepository
from app.core.auth import get_current_user  # Hypothétique

router = APIRouter()

# Dépendances pour les services
def get_llm_service():
    return LLMService()

def get_xml_validation_service():
    return XMLValidationService()

def get_xml_parsing_service():
    return XMLParsingService()

def get_argument_map_repository(db: Session = Depends(get_db_session)):
    return ArgumentMapRepository(db)

@router.post("/transform_text_to_xml/", response_model=ArgumentMapResponseModel)
async def transform_text(
    text_input: TextInputModel,
    current_user: User = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service),
    xml_validation_service: XMLValidationService = Depends(get_xml_validation_service),
    xml_parsing_service: XMLParsingService = Depends(get_xml_parsing_service),
    repository: ArgumentMapRepository = Depends(get_argument_map_repository)
):
    try:
        # Génération du XML
        xml_output = await llm_service.generate_xml(text_input.text)
        
        # Validation
        is_valid, errors = xml_validation_service.validate_xml(xml_output)
        if not is_valid:
            logging.error(f"XML validation errors: {errors}")
            raise HTTPException(status_code=400, detail="Invalid XML structure")
        
        # Parsing
        parsed_data = xml_parsing_service.parse_xml(xml_output)
        parsed_data["source_xml"] = xml_output
        
        # Extraction des IDs
        organization_id = current_user.organization_id
        creator_id = current_user.id
        
        # Stockage
        map_id = repository.create_argument_map(
            parsed_data=parsed_data,
            organization_id=organization_id,
            creator_id=creator_id
        )
        
        return ArgumentMapResponseModel(id=map_id, xml_content=xml_output)
    
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")