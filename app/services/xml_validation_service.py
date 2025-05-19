import logging
from functools import lru_cache
from lxml import etree
from lxml.isoschematron import Schematron  # Add this import
import os
from app.core.config import settings

class XMLValidationService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._load_schemas()

    def _load_schemas(self):
        """Load XSD and Schematron schemas."""
        # Load XSD schema
        self.xsd_path = os.path.join(settings.BASE_DIR, 'app', 'xml_definitions', 'argument_map.xsd')
        try:
            with open(self.xsd_path, 'rb') as f:
                xsd_doc = etree.parse(f)
                self.xsd_schema = etree.XMLSchema(xsd_doc)
            self.logger.debug(f"XSD schema loaded from {self.xsd_path}")
        except (etree.XMLSchemaParseError, FileNotFoundError) as e:
            self.logger.error(f"Failed to load XSD schema: {str(e)}")
            raise

        # Load and compile Schematron schema
        self.sch_path = os.path.join(settings.BASE_DIR, 'app', 'xml_definitions', 'business_rules.sch')
        try:
            with open(self.sch_path, 'rb') as f:
                sch_doc = etree.parse(f)
                self.schematron_validator = Schematron(sch_doc, store_report=True)
            self.logger.debug(f"Schematron schema compiled from {self.sch_path}")
        except (etree.SchematronParseError, FileNotFoundError) as e:
            self.logger.error(f"Failed to load Schematron schema: {str(e)}")
            raise

    def validate_xml(self, xml_content: str) -> tuple[bool, list[str]]:
        """Validate XML content against XSD and Schematron schemas."""
        errors = []

        # Parse XML content
        try:
            xml_doc = etree.fromstring(xml_content.encode('utf-8'))
        except etree.XMLSyntaxError as e:
            self.logger.error(f"XML parsing failed: {str(e)}")
            errors.append(f"XML Syntax Error: {str(e)}")
            return False, errors

        # Step 1: Validate against XSD
        if not self.xsd_schema.validate(xml_doc):
            errors.extend([
                f"XSD Error (Line {err.line}, Col {err.column}): {err.message}"
                for err in self.xsd_schema.error_log
            ])
            self.logger.debug("XSD validation failed")

        # Step 2: Validate against Schematron
        if self.schematron_validator:
            if not self.schematron_validator.validate(xml_doc):
                svrl_report = self.schematron_validator.validation_report
                svrl_ns = {'svrl': 'http://purl.oclc.org/dsdl/svrl'}
                failed_asserts = svrl_report.xpath('//svrl:failed-assert', namespaces=svrl_ns)
                for fa in failed_asserts:
                    error_text = fa.xpath('svrl:text/text()', namespaces=svrl_ns)
                    if error_text:
                        errors.append(error_text[0].strip())
                if failed_asserts:
                    self.logger.debug("Schematron validation failed")

        is_valid = len(errors) == 0
        if is_valid:
            self.logger.info("XML validation successful")
        else:
            self.logger.warning(f"XML validation failed with errors: {errors}")

        return is_valid, errors
    
@lru_cache()
def get_xml_validation_service():
    return XMLValidationService()