import logging
import os
from langchain_core.messages import HumanMessage, SystemMessage
from llm_components.llm_prompts import (eod_human_prompt, eod_system_prompt,
                                        sprint_review_human_prompt, sprint_review_system_prompt)
from langchain.chains import LLMChain
from typing import Optional
from dotenv import load_dotenv
from langchain_core.utils.utils import secret_from_env
from langchain_openai import ChatOpenAI
from pydantic import Field, SecretStr

load_dotenv()


class ChatOpenRouter(ChatOpenAI):
    openai_api_key: Optional[SecretStr] = Field(
        alias="api_key",
        default_factory=secret_from_env("OPENROUTER_API_KEY", default=None),
    )

    @property
    def lc_secrets(self) -> dict[str, str]:
        return {"openai_api_key": "OPENROUTER_API_KEY"}

    def __init__(self,
                 openai_api_key: Optional[str] = None,
                 **kwargs):
        openai_api_key = (
                openai_api_key or os.environ.get("OPENROUTER_API_KEY")
        )
        super().__init__(
            base_url=os.environ.get("OPENROUTER_BASE_URL"),
            openai_api_key=openai_api_key,
            **kwargs
        )


def get_openrouter_llm():
    openrouter_model = ChatOpenRouter(
        model_name="deepseek/deepseek-r1-distill-llama-70b:free"
    )
    return openrouter_model


def llm_eod_summary_generator(collected_commits):
    logging.info("Starting summary generation")
    chat = get_openrouter_llm()

    logging.info("Preparing prompts with commit data")
    messages = [
        HumanMessage(content=eod_human_prompt, collected_commits=collected_commits),
        SystemMessage(content=eod_system_prompt)
    ]

    try:
        logging.info("Sending request to LLM")
        response = chat.invoke(str(messages))
        raise Exception("Test exception")  # Simulate an error
        return response.content
    except Exception as e:
        logging.error(f"Error generating summary: {str(e)}")
        raise Exception(f"Due to {str(e)} we could not generate the summary")


def llm_sprint_review_summary_generator(collected_commits, tickets):
    logging.info("Starting sprint review summary generation")
    chat = get_openrouter_llm()

    logging.info("Preparing prompts with commit data and tickets")
    messages = [
        HumanMessage(content=sprint_review_human_prompt, collected_commits=collected_commits, tickets=tickets),
        SystemMessage(content=sprint_review_system_prompt)
    ]

    try:
        logging.info("Sending request to LLM")
        response = chat.invoke(str(messages))
        raise Exception("Test exception")  # Simulate an error
        return response.content
    except Exception as e:
        logging.error(f"Error generating sprint review summary: {str(e)}")
        raise Exception(f"Due to {str(e)} we could not generate the sprint review summary")