import logging
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, SystemMessage
from llm_components.llm_prompts import human_prompt, system_prompt

def get_llm_bedrock_ai() -> ChatBedrock:
    logging.getLogger('langchain_aws').setLevel(logging.WARNING)
    logging.info("Initializing ChatBedrock")
    return ChatBedrock(
        model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
        model_kwargs=dict(temperature=0.9),
    )

def llm_summary_generator(collected_commits):
    logging.info("Starting summary generation")
    chat = get_llm_bedrock_ai()
    
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
