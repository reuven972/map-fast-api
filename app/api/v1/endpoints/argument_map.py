import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db_session
from app.services.llm_service import get_llm_service, LLMService
from app.services.xml_validation_service import get_xml_validation_service, XMLValidationService
from app.services.xml_parsing_service import get_xml_parsing_service, XMLParsingService
from app.schemas.argument_map import TextInputModel, ArgumentMapResponseModel, XMLInputModel
from app.repositories.argument_map_repository import ArgumentMapRepository
# from app.core.auth import get_current_user

router = APIRouter()

def get_argument_map_repository(db: Session = Depends(get_db_session)):
    return ArgumentMapRepository(db)

@router.post("/transform_text_to_xml/", response_model=ArgumentMapResponseModel)
async def transform_text(
    text_input: TextInputModel,
    # current_user: User = Depends(get_current_user), 
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
        # organization_id = current_user.organization_id
        #creator_id = current_user.id
        organization_id = None
        creator_id = None
        
        
        # Stockage
        created_map_object = repository.create_argument_map(
            parsed_data=parsed_data,
            organization_id=organization_id,
            creator_id=creator_id
        )
        
        return ArgumentMapResponseModel(id=str(created_map_object.id),uuid=str(created_map_object.uuid), xml_content=xml_output)
    
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    


@router.post(
    "/import_xml/",
    response_model=ArgumentMapResponseModel,
    summary="Importer une carte argumentative à partir de XML",
    description="Cet endpoint permet d'importer une carte argumentative en fournissant un contenu XML valide."
)
async def import_xml(
    xml_input: XMLInputModel,
    xml_validation_service: XMLValidationService = Depends(get_xml_validation_service),
    xml_parsing_service: XMLParsingService = Depends(get_xml_parsing_service),
    repository: ArgumentMapRepository = Depends(get_argument_map_repository)
):
    try:
        # Valider le XML
        is_valid, errors = xml_validation_service.validate_xml(xml_input.xml_content)
        if not is_valid:
            error_detail = "XML invalide : " + "; ".join(errors)
            logging.warning(f"Import XML échoué - Validation : {error_detail} - Contenu XML reçu : {xml_input.xml_content[:500]}")
            raise HTTPException(status_code=400, detail=error_detail)

        # Parser le XML en données structurées
        parsed_data = xml_parsing_service.parse_xml(xml_input.xml_content)
        parsed_data["source_xml"] = xml_input.xml_content

        # Définir les IDs (à remplacer par la logique d'authentification)
        # TODO: À remplacer par current_user.organization_id et current_user.id une fois l'authentification implémentée
        organization_id = None
        creator_id = None

        # Sauvegarder dans la base de données
        created_map_object = repository.create_argument_map(
            parsed_data=parsed_data,
            organization_id=organization_id,
            creator_id=creator_id
        )

        # Retourner la réponse
        return ArgumentMapResponseModel(
            id=str(created_map_object.id),
            uuid=str(created_map_object.uuid),
            xml_content=xml_input.xml_content
        )

    except Exception as e:
        logging.error(f"Erreur inattendue : {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")