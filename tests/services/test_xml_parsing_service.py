import pytest
from app.services.xml_parsing_service import XMLParsingService

def test_parse_xml_with_prefixed_namespace():
    """
    Teste le parsing d'un XML avec un namespace préfixé.
    Vérifie l'extraction correcte du titre, des statements, des relationships et des evidences.
    """
    xml_content = """
    <arg:argument_map xmlns:arg="http://example.com/argument_map">
        <arg:title>Test Map</arg:title>
        <arg:description>Test Description</arg:description>
        <arg:statements>
            <arg:premise id="p1">Premise 1</arg:premise>
            <arg:conclusion id="c1">Conclusion</arg:conclusion>
        </arg:statements>
        <arg:relationships>
            <arg:support from="p1" to="c1" group_id="group1"/>
        </arg:relationships>
        <arg:evidence>
            <arg:item id="e1">
                <arg:title>Evidence Title</arg:title>
                <arg:source_type>Article</arg:source_type>
                <arg:credibility_rating>0.8</arg:credibility_rating>
            </arg:item>
        </arg:evidence>
    </arg:argument_map>
    """
    service = XMLParsingService()
    result = service.parse_xml(xml_content)

    # Vérification du titre et de la description
    assert result["title"] == "Test Map"
    assert result["description"] == "Test Description"
    assert result["source_xml"] == xml_content

    # Vérification des statements
    assert len(result["statements"]) == 2
    assert result["statements"][0] == {
        "external_id": "p1",
        "statement_text": "Premise 1",
        "statement_type": "premise",
        "path": "c1.p1",  # p1 soutient c1, donc chemin = c1.p1
        "depth": 1
    }
    assert result["statements"][1] == {
        "external_id": "c1",
        "statement_text": "Conclusion",
        "statement_type": "conclusion",
        "path": "c1",  # c1 est la racine
        "depth": 0
    }

    # Vérification des relationships
    assert len(result["relationships"]) == 1
    assert result["relationships"][0]["from_external_id"] == "p1"
    assert result["relationships"][0]["to_external_id"] == "c1"
    assert result["relationships"][0]["relationship_type"] == "support"
    assert "convergence_group_id" in result["relationships"][0]  # UUID généré à partir de group1

    # Vérification des evidences
    assert len(result["evidence"]) == 1
    assert result["evidence"][0] == {
        "external_id": "e1",
        "title": "Evidence Title",
        "source_type": "Article",
        "source_name": "",
        "url": "",
        "description": "",
        "credibility_rating": 0.8
    }

def test_parse_xml_with_default_namespace():
    """
    Teste le parsing d'un XML avec un namespace par défaut.
    Vérifie que le parsing fonctionne correctement.
    """
    xml_content = """
    <argument_map xmlns="http://example.com/argument_map">
        <title>Default NS Map</title>
        <statements>
            <premise id="p1">Premise 1</premise>
            <rebuttal id="r1">Rebuttal 1</rebuttal>
        </statements>
        <relationships>
            <oppose from="r1" to="p1"/>
        </relationships>
    </argument_map>
    """
    service = XMLParsingService()
    result = service.parse_xml(xml_content)

    # Vérification du titre
    assert result["title"] == "Default NS Map"
    assert result["description"] == ""

    # Vérification des statements (isolés, car oppose n'est pas hiérarchique)
    assert len(result["statements"]) == 2
    assert result["statements"][0] == {
        "external_id": "p1",
        "statement_text": "Premise 1",
        "statement_type": "premise",
        "path": "p1",
        "depth": 0
    }
    assert result["statements"][1] == {
        "external_id": "r1",
        "statement_text": "Rebuttal 1",
        "statement_type": "rebuttal",
        "path": "r1",
        "depth": 0
    }

    # Vérification des relationships
    assert len(result["relationships"]) == 1
    assert result["relationships"][0] == {
        "from_external_id": "r1",
        "to_external_id": "p1",
        "relationship_type": "oppose"
    }

def test_parse_xml_missing_ids():
    """
    Teste le comportement lorsque des IDs sont manquants dans les statements ou relationships.
    """
    xml_content = """
    <arg:argument_map xmlns:arg="http://example.com/argument_map">
        <arg:title>Missing IDs Test</arg:title>
        <arg:statements>
            <arg:premise>Premise sans ID</arg:premise>
            <arg:conclusion id="c1">Conclusion</arg:conclusion>
        </arg:statements>
        <arg:relationships>
            <arg:support from="p1" to="" />
        </arg:relationships>
    </arg:argument_map>
    """
    service = XMLParsingService()
    result = service.parse_xml(xml_content)

    # Vérification : seul le statement avec ID est inclus
    assert len(result["statements"]) == 1
    assert result["statements"][0]["external_id"] == "c1"

    # Vérification : relationship invalide ignorée
    assert len(result["relationships"]) == 0

def test_parse_xml_invalid_credibility_rating():
    """
    Teste la gestion d'une valeur invalide pour credibility_rating dans evidence.
    """
    xml_content = """
    <arg:argument_map xmlns:arg="http://example.com/argument_map">
        <arg:title>Evidence Test</arg:title>
        <arg:evidence>
            <arg:item id="e1">
                <arg:title>Evidence Title</arg:title>
                <arg:credibility_rating>invalid</arg:credibility_rating>
            </arg:item>
        </arg:evidence>
    </arg:argument_map>
    """
    service = XMLParsingService()
    result = service.parse_xml(xml_content)

    # Vérification : credibility_rating devient None si invalide
    assert len(result["evidence"]) == 1
    assert result["evidence"][0]["credibility_rating"] is None