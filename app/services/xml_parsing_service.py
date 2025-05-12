from lxml import etree
import uuid
import logging

class XMLParsingService:
    def parse_xml(self, xml_content: str) -> dict:
        """
        Parse XML into a dictionary suitable for database storage.
        """
        try:
            root = etree.fromstring(xml_content.encode('utf-8'))
            parsed_data = {
                "title": root.findtext("title", ""),
                "description": root.findtext("description", ""),
                "source_xml": xml_content,
                "statements": [],
                "relationships": [],
                "evidence": []
            }

            # Parse statements
            for stmt_type in ["premise", "conclusion", "rebuttal", "counter_conclusion"]:
                for elem in root.findall(f".//{stmt_type}"):
                    parsed_data["statements"].append({
                        "external_id": elem.get("id"),
                        "statement_text": elem.text or "",
                        "statement_type": stmt_type,
                        "path": None,  # TODO: Implement LTREE path calculation
                        "depth": 0     # TODO: Calculate based on relationships
                    })

            # Parse relationships
            for rel_type in ["support", "oppose"]:
                for elem in root.findall(f".//{rel_type}"):
                    rel_data = {
                        "from_external_id": elem.get("from"),
                        "to_external_id": elem.get("to"),
                        "relationship_type": rel_type
                    }
                    group_id = elem.get("group_id")
                    if group_id:
                        rel_data["convergence_group_id"] = str(uuid.uuid5(uuid.NAMESPACE_DNS, group_id))
                    parsed_data["relationships"].append(rel_data)

            # Parse evidence
            for item in root.findall(".//evidence/item"):
                parsed_data["evidence"].append({
                    "external_id": item.get("id"),
                    "title": item.findtext("title", ""),
                    "source_type": item.findtext("source", ""),
                    "source_name": "",
                    "url": item.findtext("url", ""),
                    "description": item.findtext("description", ""),
                    "credibility_rating": None
                })

            logging.info("XML parsed successfully")
            return parsed_data

        except Exception as e:
            logging.error(f"Error parsing XML: {str(e)}")
            raise