import os

structure = {
    "app": {
        "__init__.py": "",
        "main.py": "# FastAPI app entry point\n",
        "core": {
            "__init__.py": "",
            "config.py": "# Configuration for environment variables\n",
            "logging.py": "# Centralized logging setup\n"
        },
        "api": {
            "__init__.py": "",
            "v1": {
                "__init__.py": "",
                "endpoints": {
                    "__init__.py": "",
                    "argument_map.py": "# API endpoints for argument maps\n"
                }
            }
        },
        "services": {
            "__init__.py": "",
            "llm_service.py": "# LangChain LLM interaction service\n",
            "xml_validation_service.py": "# XML validation service\n",
            "xml_parsing_service.py": "# XML parsing service\n"
        },
        "repositories": {
            "__init__.py": "",
            "argument_map_repository.py": "# CRUD logic for argument maps\n"
        },
        "models": {
            "__init__.py": "",
            "argument_map.py": "# Pydantic models for argument maps\n"
        },
        "database": {
            "__init__.py": "",
            "db.py": "# PostgreSQL database connection setup\n"
            # Removed models.py as it was not in the described structure
        },
        "schemas": {
            "__init__.py": "",
            "xml": {
                "argument_map.xsd": "<xs:schema xmlns:xs='http://www.w3.org/2001/XMLSchema'>\n  <!-- Placeholder XSD -->\n</xs:schema>",
                "business_rules.sch": "<sch:schema xmlns:sch='http://purl.oclc.org/dsdl/schematron'>\n  <!-- Placeholder Schematron rules -->\n</sch:schema>"
            }
        }
    },
    "tests": {
        "__init__.py": "",
        "api": {
            "__init__.py": "",
            "test_argument_map_endpoints.py": "# Tests for argument map API endpoints\n"
        },
        "services": {
            "__init__.py": "",
            "test_llm_service.py": "# Tests for LLM service\n",
            "test_xml_validation_service.py": "# Tests for XML validation service\n",
            "test_xml_parsing_service.py": "# Tests for XML parsing service\n"
        }
    },
    "requirements.txt": "# Project dependencies\nfastapi\npydantic\nsqlalchemy\npsycopg2-binary\nlangchain\n",
    ".env": "# Environment variables\nDATABASE_URL=postgresql://user:password@localhost:5432/dbname\n"
}

def create_structure(base_path, structure):
    try:
        for name, content in structure.items():
            path = os.path.join(base_path, name)
            if isinstance(content, dict):
                os.makedirs(path, exist_ok=True)
                create_structure(path, content)
            else:
                with open(path, "w") as f:
                    f.write(content)
                # Optionally set restrictive permissions for .env
                if name == ".env":
                    os.chmod(path, 0o600)
    except PermissionError as e:
        print(f"Permission error: {e}")
    except OSError as e:
        print(f"OS error: {e}")

if __name__ == "__main__":
    create_structure(".", structure)
    print("Project structure created successfully!")