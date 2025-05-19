from sqlalchemy.orm import Session
from app.database.models import ArgumentMap, Statement, StatementRelationship, Evidence
import uuid
import logging

class ArgumentMapRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_argument_map(self, parsed_data: dict, organization_id: int | None, creator_id: int | None) -> ArgumentMap:
        """
        Create an argument map and its associated statements, relationships, and evidence.
        
        Args:
            parsed_data: Dictionary containing title, description, statements, relationships, and evidence.
            organization_id: ID of the organization.
            creator_id: ID of the user creating the map.
        
        Returns:
            str: ID of the created argument map.
        """
        try:
            # Create the argument map
            argument_map = ArgumentMap(
                organization_id=organization_id,
                creator_id=creator_id,
                title=parsed_data.get("title", ""),
                description=parsed_data.get("description", ""),
                source_xml=parsed_data.get("source_xml", "")
            )
            self.db_session.add(argument_map)
            self.db_session.flush()  # Get the ID without committing

            # Create statements
            statements_map = {}  # Map external_id to database ID
            for stmt in parsed_data.get("statements", []):
                statement = Statement(
                    argument_map_id=argument_map.id,
                    external_id=stmt.get("external_id"),
                    statement_text=stmt.get("statement_text"),
                    statement_type=stmt.get("statement_type"),
                    path=stmt.get("path"),  # Assume path is calculated in xml_parsing_service
                    depth=stmt.get("depth", 0)
                )
                self.db_session.add(statement)
                self.db_session.flush()
                statements_map[stmt["external_id"]] = statement.id

            # Create relationships
            for rel in parsed_data.get("relationships", []):
                relationship = StatementRelationship(
                    argument_map_id=argument_map.id,
                    from_statement_id=statements_map.get(rel["from_external_id"]),
                    to_statement_id=statements_map.get(rel["to_external_id"]),
                    relationship_type=rel["relationship_type"],
                    convergence_group_id=uuid.UUID(rel["convergence_group_id"]) if rel.get("convergence_group_id") else None,
                    strength=rel.get("strength")
                )
                self.db_session.add(relationship)

            # Create evidence
            for ev in parsed_data.get("evidence", []):
                evidence = Evidence(
                    argument_map_id=argument_map.id,
                    external_id=ev["external_id"],
                    title=ev["title"],
                    source_type=ev.get("source_type"),
                    source_name=ev.get("source_name"),
                    url=ev.get("url"),
                    description=ev.get("description"),
                    credibility_rating=ev.get("credibility_rating")
                )
                self.db_session.add(evidence)

            logging.info(f"Created argument map with ID {argument_map.id}")
            return argument_map

        except Exception as e:
            logging.error(f"Error preparing argument map for database: {str(e)}")
            raise

    def get_argument_map(self, map_id: int) -> ArgumentMap | None:
        """
        Retrieve an argument map by ID.
        """
        return self.db_session.query(ArgumentMap).filter(ArgumentMap.id == map_id).first()