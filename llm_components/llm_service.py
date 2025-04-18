import os
import logging
from typing import Type, Dict, Any
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.runnables import Runnable
from langchain_community.llms import Ollama
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from services.interfaces import ILlmService # Import the interface
# Import only prompts from llm_prompts
from .llm_prompts import (
    eod_system_prompt,
    eod_human_prompt,
    sprint_review_system_prompt,
    sprint_review_human_prompt,
)
# Import models from central models.py
from models import DailySummary, SprintReviewSummary

load_dotenv()

# Set up logging (consider moving to a central config if not already done)
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LlmService(ILlmService):
    """Concrete implementation of the LLM service interface."""

    def __init__(self, model_name: str = None):
        self._model_name = model_name or os.getenv("OLLAMA_MODEL", "deepseek-r1:7b")
        self._llm = self._initialize_llm()
        logging.info(f"LlmService initialized with model: {self._model_name}")

    def _initialize_llm(self) -> Ollama:
        """Initializes the Ollama LLM instance."""
        try:
            llm = Ollama(model=self._model_name)
            logging.info(f"Ollama LLM instance created for model: {self._model_name}")
            return llm
        except Exception as e:
            logging.error(f"Error initializing Ollama LLM ({self._model_name}): {e}")
            raise # Re-raise the exception to be handled upstream

    def _create_chain(self, system_prompt_template: str, human_prompt_template: str, output_parser: PydanticOutputParser) -> Runnable:
        """Creates a LangChain runnable chain."""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt_template),
            HumanMessagePromptTemplate.from_template(human_prompt_template)
        ])
        return prompt | self._llm | output_parser

    def _invoke_chain(self, chain: Runnable, input_data: Dict[str, Any], pydantic_model: Type[BaseModel]) -> BaseModel:
        """Invokes the LangChain chain and handles errors."""
        parser = PydanticOutputParser(pydantic_object=pydantic_model)
        format_instructions = parser.get_format_instructions()
        input_data["format_instructions"] = format_instructions

        logging.info(f"Sending request to LLM for {pydantic_model.__name__}. Input keys: {list(input_data.keys())}")
        try:
            response = chain.invoke(input_data)
            logging.info(f"LLM generated {pydantic_model.__name__} object successfully.")
            return response
        except Exception as e:
            logging.error(f"Error generating {pydantic_model.__name__}: {e}")
            # Consider more specific exception types if needed
            raise Exception(f"Failed to generate {pydantic_model.__name__}: {e}")


    def generate_eod_summary(self, collected_commits: str) -> DailySummary:
        """Generates an end-of-day summary."""
        logging.info("LlmService: Starting EOD summary generation.")
        parser = PydanticOutputParser(pydantic_object=DailySummary)
        chain = self._create_chain(eod_system_prompt, eod_human_prompt, parser)
        input_data = {"collected_commits": collected_commits}
        return self._invoke_chain(chain, input_data, DailySummary)


    def generate_sprint_review(self, collected_commits: str, tickets: str) -> SprintReviewSummary:
        """Generates a sprint review summary."""
        logging.info("LlmService: Starting Sprint Review summary generation.")
        parser = PydanticOutputParser(pydantic_object=SprintReviewSummary)
        chain = self._create_chain(sprint_review_system_prompt, sprint_review_human_prompt, parser)
        input_data = {
            "collected_commits": collected_commits,
            "tickets": tickets
        }
        return self._invoke_chain(chain, input_data, SprintReviewSummary)