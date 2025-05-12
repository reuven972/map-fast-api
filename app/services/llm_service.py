import logging
import re
from functools import lru_cache
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from app.core.config import settings

# Configure logger
logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        """
        Initialize the LLM service with LangChain using ChatOpenAI and LCEL.
        """
        try:
            # Initialize ChatOpenAI with configurable model
            self.llm = ChatOpenAI(
                api_key=settings.OPENAI_API_KEY,
                model_name=settings.OPENAI_MODEL_NAME  # Configurable via settings
            )
            # Detailed prompt to guide XML generation
            detailed_template = """
You are an expert XML data structuring assistant. Your task is to convert the provided text analysis into a structured XML format conforming to the specified schema summary.

XML Schema Summary:

Root: <argument_map>

Contains: <title>, <statements>, <relationships>, <evidence> (optional)

Statements: <premise id="UNIQUE_ID">, <conclusion id="UNIQUE_ID">, <rebuttal id="UNIQUE_ID">, <counter_conclusion id="UNIQUE_ID">

Relationships: <support from="ID" to="ID" group_id="OPTIONAL_ID"/>, <oppose from="ID" to="ID"/>

Evidence: <item id="UNIQUE_EVIDENCE_ID" for="STATEMENT_ID"> contains <title>, <source>, <url>, <description>

Instructions:

Generate unique IDs (e.g., p1, c1, e1) for all statements and evidence items.

Ensure 'from' and 'to' attributes in relationships reference existing statement IDs.

Use 'group_id' for linked premises supporting the same conclusion.

Base the structure on the analysis provided in {text}.

Create a concise <title>.

Output only the well-formed XML document.

Analysis Text:
{text}

XML Output:
"""
            # Create PromptTemplate
            self.prompt = PromptTemplate(
                input_variables=["text"],
                template=detailed_template
            )
            # Create LCEL chain: prompt | llm
            self.chain = self.prompt | self.llm
            logger.info("LLMService initialized successfully with LCEL.")
        except Exception as e:
            logger.error(f"Error initializing LLMService: {str(e)}")
            raise

    async def generate_xml(self, text: str) -> str:
        """
        Generate XML from the provided text using the LLM asynchronously.

        Args:
            text (str): The text to transform into XML.

        Returns:
            str: The generated XML content.

        Raises:
            Exception: If an error occurs during generation.
        """
        try:
            # Asynchronous execution with LCEL chain
            result = await self.chain.ainvoke({"text": text})
            # Extract content from AIMessage object
            raw_content = result.content

            # Extract valid XML between <argument_map> tags
            match = re.search(r"<argument_map>.*</argument_map>", raw_content, re.DOTALL)
            if match:
                xml_content = match.group(0)
                logger.info("XML generated and extracted successfully.")
            else:
                logger.warning("No <argument_map> tags found in LLM output. Returning raw content.")
                xml_content = raw_content  # Fallback to raw content

            return xml_content
        except Exception as e:
            logger.error(f"Error generating XML: {str(e)}")
            raise

# Dependency function with Singleton pattern via lru_cache
@lru_cache()
def get_llm_service() -> LLMService:
    """
    Provide a singleton instance of LLMService for FastAPI dependency injection.
    Uses lru_cache to ensure a single, reused instance.
    """
    return LLMService()