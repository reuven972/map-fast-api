my_fastapi_app/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Point d'entrée de l'application
│   ├── core/
│   │   ├── config.py           # Gestion des variables d'environnement (ex: clés API LangChain)
│   │   └── logging.py          # Configuration centralisée des logs
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           └── argument_map.py  # Routes API pour les cartes argumentatives
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py            # Interaction avec le LLM via LangChain
│   │   ├── xml_validation_service.py  # Validation XML
│   │   └── xml_parsing_service.py     # Parsing XML
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── argument_map_repository.py # Logique CRUD pour les cartes argumentatives
│   ├── models/
│   │   ├── __init__.py
│   │   └── argument_map.py     # Modèles Pydantic pour validation
│   ├── xml_definitions/        # Schémas pour validation XML
│   │   ├── argument_map.xsd     # Schémas XSD pour validation XML
│   │   └── business_rules.sch   # Schémas SCH pour règles métier
│   └── database/
│       ├── __init__.py
│       └── db.py              # Configuration de la connexion à PostgreSQL
├── tests/
│   ├── __init__.py
│   ├── api/
│   │   └── test_argument_map_endpoints.py
│   └── services/
│       ├── test_llm_service.py
│       ├── test_xml_validation_service.py
│       └── test_xml_parsing_service.py
├── requirements.txt           # Dépendances du projet
└── .env                       # Variables d'environnement