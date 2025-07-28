import os
from langchain_openai import ChatOpenAI
from my_agents.utils.logger import logger
from dotenv import load_dotenv
load_dotenv()

# Get API key from environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required. Please set it in your environment or .env file")

llm1 = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)
llm2 = ChatOpenAI(model="gpt-3.5-turbo", api_key=api_key)

def detect_conversation_tone(message_content, base_tone="professional"):
    """
    Dynamically detect the emotion based on conversation content using AI analysis.
    Returns appropriate emotion descriptor based on intelligent content analysis.
    """
    try:
        # Use AI to analyze the emotional content of the message - NO predefined list
        emotion_prompt = f"""Analyze the emotional tone and mood of this message. Think about how the speaker feels based on their words, tone, and content.

Respond with ONLY a single descriptive emotion word that best captures their emotional state. Be creative and specific - don't use generic words. Think about subtle emotions and nuances.

Message: "{message_content}"

What emotion does this speaker convey? Respond with just ONE word:"""
        
        # Use a lightweight model for emotion detection with simplified settings
        emotion_response = llm1.invoke(emotion_prompt)
        detected_emotion = emotion_response.content.strip().lower() if hasattr(emotion_response, 'content') else str(emotion_response).strip().lower()
        
        # Clean up the response to ensure we get just the emotion word
        detected_emotion = detected_emotion.replace('"', '').replace("'", '').replace('.', '').strip()
        
        # Take only the first word if multiple words returned
        if ' ' in detected_emotion:
            detected_emotion = detected_emotion.split()[0]
        
        # Validate that we got a reasonable emotion word
        if len(detected_emotion) > 20 or not detected_emotion.isalpha() or len(detected_emotion) < 3:
            logger.warning(f"Invalid emotion word received: '{detected_emotion}', using thoughtful as default")
            return 'thoughtful'
            
        logger.info(f"AI detected emotion: {detected_emotion}")
        return detected_emotion
        
    except Exception as e:
        logger.error(f"AI emotion detection failed: {e}")
        # Only use simple fallback when AI completely fails
        return 'thoughtful'

def clean_agent_response(response_text):
    """
    Clean up agent responses to remove any agent name prefixes or duplications
    """
    import re
    
    # Remove agent name prefixes at the start
    response_text = re.sub(r'^Agent [AB]\s*\([^)]*\):\s*', '', response_text.strip())
    response_text = re.sub(r'^Agent [AB]:\s*', '', response_text.strip())
    response_text = re.sub(r'^Agent [AB]\s*\([^)]*\),?\s*', '', response_text.strip())
    response_text = re.sub(r'^Agent [AB],?\s*', '', response_text.strip())
    
    # Remove any remaining agent references at start of sentences
    response_text = re.sub(r'\n\s*Agent [AB]\s*\([^)]*\):\s*', '\n', response_text)
    response_text = re.sub(r'\n\s*Agent [AB]:\s*', '\n', response_text)
    
    return response_text.strip()
        
   
def agent_a_node(state):
    # Check if this is the first message
    is_first_message = len(state.messages) == 0
    
    if is_first_message:
        # Agent A initiates the conversation
        last_msg = f"Hello, let's discuss {state.config['topic']}."
        logger.info(f"Agent A initiating conversation about: {state.config['topic']}")
    else:
        last_msg = state.messages[-1] if state.messages else f"Hello, let's discuss {state.config['topic']}."
        logger.info(f"Agent A received: {last_msg}")

    # Get agent persona for context but use emotion for display
    agent_a_persona = state.config.get('agent_a_persona', 'A professional discussant')
    base_tone = state.config.get('tone', 'neutral')
    
    # Include conversation context and topic in the prompt - IMPORTANT: Don't include agent name in response
    prompt = (
        f"You are {agent_a_persona}. "
        f"Speak in a {base_tone} tone. "
        f"Context: {state.config.get('conversation_context', '')} "
        f"Topic: {state.config['topic']} "
        f"Previous message: {last_msg} "
        f"IMPORTANT: Do not start your response with your name or any agent identifier. "
        f"Just provide your direct response content without any prefixes."
    )

    response = llm1.invoke(prompt)
    response_text = response.content if hasattr(response, 'content') else str(response)
    
    # Clean up any agent name prefixes that might still appear
    response_text = clean_agent_response(response_text)
    
    logger.info(f"Agent A replied: {response_text}")

    # Detect dynamic emotion based on response content
    detected_emotion = detect_conversation_tone(response_text, base_tone)
    
    # Show Agent A with dynamic emotion in transcript
    speaker_label = f"Agent A ({detected_emotion})"
    state.messages.append(f"{speaker_label}: {response_text}")
    
    # Set next speaker and increment turn
    state.speaker = "agent_b"
    state.turn += 1
    logger.info(f"Turn {state.turn} completed. Next speaker: {state.speaker}, detected emotion: {detected_emotion}")
    
    return state

def agent_b_node(state):
    # Agent B responds to Agent A's message
    last_msg = state.messages[-1] if state.messages else "Hello"
    logger.info(f"Agent B received: {last_msg}")

    # Get agent persona for context but use emotion for display
    agent_b_persona = state.config.get('agent_b_persona', 'A professional respondent')
    base_tone = state.config.get('tone', 'neutral')
    
    # Include conversation context and topic in the prompt - IMPORTANT: Don't include agent name in response
    prompt = (
        f"You are {agent_b_persona}. "
        f"Speak in a {base_tone} tone. "
        f"Context: {state.config.get('conversation_context', '')} "
        f"Topic: {state.config['topic']} "
        f"Respond to this message: {last_msg} "
        f"IMPORTANT: Do not start your response with your name or any agent identifier. "
        f"Just provide your direct response content without any prefixes."
    )

    response = llm2.invoke(prompt)
    response_text = response.content if hasattr(response, 'content') else str(response)
    
    # Clean up any agent name prefixes that might still appear
    response_text = clean_agent_response(response_text)
    
    logger.info(f"Agent B replied: {response_text}")

    # Detect dynamic emotion based on response content
    detected_emotion = detect_conversation_tone(response_text, base_tone)
    
    # Show Agent B with dynamic emotion in transcript
    speaker_label = f"Agent B ({detected_emotion})"
    state.messages.append(f"{speaker_label}: {response_text}")
    
    # Set next speaker and increment turn
    state.speaker = "agent_a"
    state.turn += 1
    logger.info(f"Turn {state.turn} completed. Next speaker: {state.speaker}, detected emotion: {detected_emotion}")
    
    return state