import os
import logging
import json
from typing import List
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_community.llms import Ollama
from langchain.output_parsers import PydanticOutputParser
from .llm_prompts import (
    DailySummary,
    TicketSummary,
    SprintReviewSummary, # Import the new wrapper model
    eod_system_prompt,
    eod_human_prompt,
    sprint_review_system_prompt,
    sprint_review_human_prompt,
)

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the Ollama model using an environment variable
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1:7b")

def ollama_llm():
    """
    Initialize Ollama LLM
    """
    try:
        llm = Ollama(model=OLLAMA_MODEL)
        logging.info(f"Ollama LLM initialized with model: {OLLAMA_MODEL}")
        return llm
    except Exception as e:
        logging.error(f"Error initializing Ollama LLM: {e}")
        raise


def llm_eod_summary_generator(collected_commits: str) -> DailySummary:
    """
    Generates an end-of-day summary using Ollama with structured output parsing.
    
    Returns:
        DailySummary: A Pydantic model containing the structured EOD summary
    """
    logging.info("Starting end-of-day summary generation")
    llm = ollama_llm()

    # Initialize the Pydantic output parser
    parser = PydanticOutputParser(pydantic_object=DailySummary)
    
    # Get format instructions from the parser
    format_instructions = parser.get_format_instructions()
    logging.info(f"Format instructions for EOD: {format_instructions}")

    # Define the prompt template, including format instructions
    prompt = ChatPromptTemplate.from_messages([
        # Use the system prompt directly, as it already contains the placeholder
        SystemMessagePromptTemplate.from_template(eod_system_prompt),
        HumanMessagePromptTemplate.from_template(eod_human_prompt)
    ])

    # Create the chain with output parser
    chain = prompt | llm | parser

    try:
        logging.info("Sending request to LLM")
        response = chain.invoke({
            "collected_commits": collected_commits,
            "format_instructions": format_instructions
        })
        logging.info("Generated EOD summary successfully")
        return response
    except Exception as e:
        logging.error(f"Error generating EOD summary: {e}")
        raise Exception(f"Failed to generate EOD summary: {e}")


def llm_sprint_review_summary_generator(collected_commits: str, tickets: str) -> SprintReviewSummary:
    """
    Generates a sprint review summary using Ollama with structured output parsing.
    
    Returns:
        SprintReviewSummary: A Pydantic model containing a list of structured ticket summaries.
    """
    logging.info("Starting sprint review summary generation")
    llm = ollama_llm()

    # Initialize the Pydantic output parser with the wrapper model
    parser = PydanticOutputParser(pydantic_object=SprintReviewSummary)
    
    # Get format instructions from the parser
    format_instructions = parser.get_format_instructions()
    logging.info(f"Format instructions for sprint review: {format_instructions}")

    # Define the prompt template, including format instructions
    prompt = ChatPromptTemplate.from_messages([
        # Use the system prompt directly, as it already contains the placeholder
        SystemMessagePromptTemplate.from_template(sprint_review_system_prompt),
        HumanMessagePromptTemplate.from_template(sprint_review_human_prompt)
    ])

    # Create the chain with output parser
    chain = prompt | llm | parser

    try:
        logging.info("Sending request to LLM")
        response = chain.invoke({
            "collected_commits": collected_commits,
            "tickets": tickets,
            "format_instructions": format_instructions
        })
        logging.info(f"LLM generated SprintReviewSummary object successfully.")
        return response
    except Exception as e:
        logging.error(f"Error generating sprint review summary: {e}")
        raise Exception(f"Failed to generate sprint review summary: {e}")