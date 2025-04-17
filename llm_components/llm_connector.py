import os
import logging
from typing import Optional
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain_community.llms import Ollama

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the Ollama model using an environment variable
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1:1.5b")

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


def llm_eod_summary_generator(collected_commits: str) -> str:
    """
    Generates an end-of-day summary using Ollama.
    """
    logging.info("Starting end-of-day summary generation")
    llm = ollama_llm()

    # Define the prompt template with a system message
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            "You are a helpful assistant that summarizes git commits for end-of-day reports. Be concise and informative."
        ),
        HumanMessagePromptTemplate.from_template(
            "Here are the collected commits: {collected_commits}"
        ),
    ])

    # Create the chain
    chain = prompt | llm

    try:
        logging.info("Sending request to LLM")
        response = chain.invoke({"collected_commits": collected_commits})
        logging.info(f"Generated summary: {response}")  # Log the generated summary
        return response
    except Exception as e:
        logging.error(f"Error generating summary: {e}")
        raise Exception(f"Due to {e} we could not generate the summary")


def llm_sprint_review_summary_generator(collected_commits: str, tickets: str) -> str:
    """
    Generates a sprint review summary using Ollama.
    """
    logging.info("Starting sprint review summary generation")
    llm = ollama_llm()

    # Define the prompt template with a system message
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            "You are a helpful assistant that summarizes git commits and tickets for sprint review reports. Be concise and informative."
        ),
        HumanMessagePromptTemplate.from_template(
            "Here are the collected commits: {collected_commits}. Here are the tickets: {tickets}"
        ),
    ])

    # Create the chain
    chain = prompt | llm

    try:
        logging.info("Sending request to LLM")
        response = chain.invoke({"collected_commits": collected_commits, "tickets": tickets})
        logging.info(f"Generated summary: {response}")  # Log the generated summary
        return response
    except Exception as e:
        logging.error(f"Error generating sprint review summary: {e}")
        raise Exception(f"Due to {e} we could not generate the sprint review summary")