from lxml import etree
from functools import lru_cache
import uuid
import logging
import re
from collections import deque
from typing import Dict, Set, List

class XMLParsingService:
    def __init__(self):
        self.invalid_id_gen_counter = 0  # Instance variable for unique invalid IDs
        self.namespace_uri = "http://example.com/argument_map"  # URI du namespace

    def parse_xml(self, xml_content: str) -> dict:
        """
        Parse XML content into a dictionary suitable for database storage
        and assign hierarchical paths and depths.
        """
        try:
            self.invalid_id_gen_counter = 0  # Reset counter for each parse
            root_element = etree.fromstring(xml_content.encode('utf-8'))
            parsed_data = {
                "title": root_element.findtext(f"{{{self.namespace_uri}}}title", ""),
                "description": root_element.findtext(f"{{{self.namespace_uri}}}description", ""),
                "source_xml": xml_content,
                "statements": [],
                "relationships": [],
                "evidence": []
            }

            # Parse statements with ID validation
            for stmt_type in ["premise", "conclusion", "rebuttal", "counter_conclusion"]:
                for elem in root_element.findall(f".//{{{self.namespace_uri}}}{stmt_type}"):
                    ext_id = elem.get("id")
                    if not ext_id:
                        logging.error(f"Statement element {elem.tag} is missing an 'id' attribute. Skipping.")
                        continue
                    parsed_data["statements"].append({
                        "external_id": ext_id,
                        "statement_text": elem.text or "",
                        "statement_type": stmt_type,
                        "path": None,
                        "depth": 0
                    })

            # Parse relationships with robust checks
            for rel_type in ["support", "oppose"]:
                for elem in root_element.findall(f".//{{{self.namespace_uri}}}{rel_type}"):
                    from_id_val = elem.get("from")
                    to_id_val = elem.get("to")
                    if not from_id_val or not to_id_val:
                        logging.error(f"Relationship element {elem.tag} is missing 'from' or 'to' attribute. Skipping: from='{from_id_val}', to='{to_id_val}'")
                        continue
                    rel_data = {
                        "from_external_id": from_id_val,
                        "to_external_id": to_id_val,
                        "relationship_type": rel_type
                    }
                    # Parse group_id if present
                    group_id = elem.get("group_id")
                    if group_id:
                        rel_data["convergence_group_id"] = str(uuid.uuid5(uuid.NAMESPACE_DNS, group_id))
                    parsed_data["relationships"].append(rel_data)

            # Parse evidence with float conversion
            for item in root_element.findall(f".//{{{self.namespace_uri}}}evidence/{{{self.namespace_uri}}}item"):
                cred_rating_text = item.findtext(f"{{{self.namespace_uri}}}credibility_rating")
                cred_rating_float = None
                if cred_rating_text is not None:
                    try:
                        cred_rating_float = float(cred_rating_text)
                    except ValueError:
                        logging.warning(f"Invalid float value for credibility_rating: '{cred_rating_text}' for evidence item {item.get('id')}")
                parsed_data["evidence"].append({
                    "external_id": item.get("id"),
                    "title": item.findtext(f"{{{self.namespace_uri}}}title", ""),
                    "source_type": item.findtext(f"{{{self.namespace_uri}}}source_type", ""),
                    "source_name": item.findtext(f"{{{self.namespace_uri}}}source_name", ""),
                    "url": item.findtext(f"{{{self.namespace_uri}}}url", ""),
                    "description": item.findtext(f"{{{self.namespace_uri}}}description", ""),
                    "credibility_rating": cred_rating_float
                })

            # Assign paths and depths
            self.assign_paths_and_depths(parsed_data)
            logging.info("XML parsed successfully, paths and depths assigned")
            return parsed_data
        except Exception as e:
            logging.error(f"Error parsing XML: {str(e)}")
            raise

    def clean_ltree_label(self, label_str: str) -> str:
        """
        Cleans an external_id to make it a valid ltree label.
        If the label is empty after cleaning, generates a unique label using an instance counter.
        """
        cleaned = re.sub(r'[^a-zA-Z0-9_]', '_', label_str)
        if not cleaned:
            unique_id = f"invalid_id_{self.invalid_id_gen_counter}"
            logging.warning(f"Invalid label '{label_str}' replaced with '{unique_id}'")
            self.invalid_id_gen_counter += 1  # Increment when used
            return unique_id
        return cleaned

    def assign_paths_and_depths(self, parsed_data: dict) -> None:
        """
        Assigns hierarchical paths (ltree) and depths to statements based on relationships.
        
        Limitations: Cyclic structures are not supported and may result in incomplete ltree paths
        for nodes within a cycle. The argument map is assumed to be a DAG (Directed Acyclic Graph).
        """
        statements = parsed_data["statements"]
        relationships = parsed_data["relationships"]
        statement_dict: Dict[str, dict] = {stmt["external_id"]: stmt for stmt in statements}
        hierarchical_relationship_types = {"support"}
        children_dict: Dict[str, List[str]] = {}
        from_ids: Set[str] = set()

        # Build children dictionary with validated IDs
        for rel in relationships:
            if rel["relationship_type"] in hierarchical_relationship_types:
                to_id = rel["to_external_id"]
                from_id = rel["from_external_id"]
                if to_id in statement_dict and from_id in statement_dict:
                    children_dict.setdefault(to_id, []).append(from_id)
                    from_ids.add(from_id)
                else:
                    logging.warning(f"Relationship from '{from_id}' to '{to_id}' references a nonexistent statement ID. Ignored.")

        # Identify roots
        roots = [stmt["external_id"] for stmt in statements if stmt["external_id"] not in from_ids]
        visited: Set[str] = set()

        # BFS for path and depth assignment
        for root_id in roots:
            if root_id not in statement_dict:
                continue
            queue = deque([(root_id, self.clean_ltree_label(root_id), 0)])
            while queue:
                current_id, current_path, current_depth = queue.popleft()
                if current_id in visited:
                    continue
                if current_id not in statement_dict:
                    logging.warning(f"ID {current_id} in queue but missing from statement_dict.")
                    continue
                visited.add(current_id)
                statement_dict[current_id]["path"] = current_path
                statement_dict[current_id]["depth"] = current_depth
                children = sorted(children_dict.get(current_id, []))
                for child_id in children:
                    if child_id not in visited:
                        cleaned_child_id = self.clean_ltree_label(child_id)
                        queue.append((child_id, f"{current_path}.{cleaned_child_id}", current_depth + 1))

        # Handle isolated statements
        for stmt in statements:
            if stmt["external_id"] not in visited:
                stmt["path"] = self.clean_ltree_label(stmt["external_id"])
                stmt["depth"] = 0
                logging.info(f"Isolated statement {stmt['external_id']} assigned path {stmt['path']}")
@lru_cache()
def get_xml_parsing_service() -> 'XMLParsingService':
    """
    Provides a singleton instance of XMLParsingService for FastAPI dependency injection.
    """
    return XMLParsingService()