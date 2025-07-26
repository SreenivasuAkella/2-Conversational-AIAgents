from langchain_openai import ChatOpenAI
from my_agents.utils.logger import logger
from dotenv import load_dotenv
import os
load_dotenv()

# Get API key from environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required. Please set it in your environment or .env file")

llm1 = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)
llm2 = ChatOpenAI(model="gpt-3.5-turbo", api_key=api_key)

def agent_a_node(state):
    last_msg = state.messages[-1] if state.messages else f"Hello, let's discuss {state.config['topic']}."
    logger.info(f"Agent A received: {last_msg}")
    response = llm1.invoke(f"[Tone: {state.config['tone']}] {last_msg}")
    response_text = response.content if hasattr(response, 'content') else str(response)
    logger.info(f"Agent A replied: {response_text}")
    state.messages.append(f"Agent A: {response_text}")
    state.speaker = "agent_b"
    state.turn += 1
    return state

def agent_b_node(state):
    last_msg = state.messages[-1]
    logger.info(f"Agent B received: {last_msg}")
    response = llm2.invoke(f"[Tone: {state.config['tone']}] {last_msg}")
    response_text = response.content if hasattr(response, 'content') else str(response)
    logger.info(f"Agent B replied: {response_text}")
    state.messages.append(f"Agent B: {response_text}")
    state.speaker = "agent_a"
    state.turn += 1
    return state