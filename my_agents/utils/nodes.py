from langchain_community.chat_models import ChatOpenAI
from my_agents.utils.logger import logger
from dotenv import load_dotenv
load_dotenv()
llm1 = ChatOpenAI(model="gpt-4o-mini")
llm2= ChatOpenAI(model="gpt-3.5-turbo")

def agent_a_node(state):
    last_msg = state.messages[-1] if state.messages else f"Hello, let's discuss {state.config['topic']}."
    logger.info(f"Agent A received: {last_msg}")
    response = llm1.predict(f"[Tone: {state.config['tone']}] {last_msg}")
    logger.info(f"Agent A replied: {response}")
    state.messages.append(f"Agent A: {response}")
    state.speaker = "agent_b"
    state.turn += 1
    return state

def agent_b_node(state):
    last_msg = state.messages[-1]
    logger.info(f"Agent B received: {last_msg}")
    response = llm2.predict(f"[Tone: {state.config['tone']}] {last_msg}")
    logger.info(f"Agent B replied: {response}")
    state.messages.append(f"Agent B: {response}")
    state.speaker = "agent_a"
    state.turn += 1
    return state