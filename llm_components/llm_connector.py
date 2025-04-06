import logging
import os
from langchain_core.messages import HumanMessage, SystemMessage
from llm_components.llm_prompts import human_prompt, system_prompt
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
        model_name="meta-llama/llama-4-maverick:free"
    )
    return openrouter_model


def llm_summary_generator(collected_commits):
    logging.info("Starting summary generation")
    chat = get_openrouter_llm()

    logging.info("Preparing prompts with commit data")
    messages = [
        HumanMessage(content=human_prompt, collected_commits=collected_commits),
        SystemMessage(content=system_prompt)
    ]

    try:
        logging.info("Sending request to LLM")
        response = chat.invoke(str(messages))
        return response.content
    except Exception as e:
        logging.error(f"Error generating summary: {str(e)}")
        return f"Due to {str(e)} we could not generate the summary"
