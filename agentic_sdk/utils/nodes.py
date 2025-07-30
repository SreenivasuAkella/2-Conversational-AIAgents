import os
from langchain_openai import ChatOpenAI
from .logger import logger
from dotenv import load_dotenv
from fi.evals import Evaluator, evaluate

FUTURE_AGI_ENABLED = True

load_dotenv()

# Get API key from environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required. Please set it in your environment or .env file")

llm1 = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)
llm2 = ChatOpenAI(model="gpt-3.5-turbo", api_key=api_key)

# FutureAGI Evaluation Integration
def evaluate_with_futureagi(message: str, evaluation_type: str = "tone") -> dict:
    """
    Evaluate message using FutureAGI evaluation SDK if available
    """
    try:
        logger.info(f"🔍 FutureAGI: Attempting to import evaluation SDK...")
        logger.info(f" FutureAGI: SDK imported successfully")
        
        # Get API keys from environment (support both naming conventions)
        fi_api_key = os.getenv("FI_API_KEY") or os.getenv("FUTUREAGI_API_KEY")
        fi_secret_key = os.getenv("FI_SECRET_KEY") or os.getenv("FUTUREAGI_SECRET_KEY")
        
        logger.info(f"FutureAGI: Checking API keys...")
        logger.info(f"   API Key: {' Set' if fi_api_key else 'Missing'}")
        logger.info(f"   Secret Key: {' Set' if fi_secret_key else ' Missing'}")
        
        if not fi_api_key or not fi_secret_key:
            return {"success": False, "error": "API keys not configured - set FI_API_KEY and FI_SECRET_KEY (or FUTUREAGI_API_KEY and FUTUREAGI_SECRET_KEY)"}
        
        logger.info(f" FutureAGI: Calling evaluation API with template '{evaluation_type}'...")
        
        # Use Evaluator class with required model name
        evaluator = Evaluator(
            fi_api_key=fi_api_key,
            fi_secret_key=fi_secret_key,
        )
        
        # Try different model names if one fails
        models_to_try = ["turing_flash"]
        
        # Map evaluation types to correct template names
        template_mapping = {
            "tone": "tone",
            "coherence": "conversation_coherence",
            "resolution": "conversation_resolution",
            
        }
        
        template_name = template_mapping.get(evaluation_type, evaluation_type)
        
        for model_name in models_to_try:
            try:
                logger.info(f"   Trying model: {model_name}")
                if template_name in ["conversation_coherence", "conversation_resolution"]:
                    result = evaluator.evaluate(
                        eval_templates=template_name,
                        inputs={"output": message},
                        model_name=model_name
                    )
                else:
                    result = evaluator.evaluate(
                        eval_templates=template_name,
                        inputs={"input": message},
                        model_name=model_name
                    )
                
                # Check if we have valid results
                if hasattr(result, 'eval_results') and result.eval_results and len(result.eval_results) > 0:
                    logger.info(f" FutureAGI: Evaluation completed successfully with {model_name}")
                    return {
                        "success": True,
                        "evaluation": result.eval_results[0].output,
                        "reason": result.eval_results[0].reason,
                        "model": model_name
                    }
                else:
                    logger.warning(f" FutureAGI: No results from {model_name}")
                    continue
                    
            except Exception as model_error:
                logger.warning(f" FutureAGI: Model {model_name} failed: {model_error}")
                continue
        
        # If all models failed
        return {"success": False, "error": "All model attempts failed"}
        
    except ImportError as e:
        logger.info(f" FutureAGI: Evaluation SDK not available - {e}")
        return {"success": False, "error": "FutureAGI evaluation SDK not available - install with: pip install ai-evaluation"}
    except Exception as e:
        logger.info(f" FutureAGI: Evaluation failed - {e}")
        return {"success": False, "error": str(e)}


def detect_conversation_tone(message_content, base_tone="professional"):
    """
    Dynamically detect the emotion based on conversation content using AI analysis.
    Uses OpenAI as primary (superior) emotion detector, with FutureAGI as secondary analysis.
    """
    try:
        emotion_prompt = f"""Analyze the emotional tone and mood of this message. Think about how the speaker feels based on their words, tone, and content.

Respond with ONLY a single descriptive emotion word that best captures their emotional state. Be creative and specific - don't use generic words. Think about subtle emotions and nuances.

Message: "{message_content}"

What emotion does this speaker convey? Respond with just ONE word:"""
        
        emotion_response = llm1.invoke(emotion_prompt)
        detected_emotion = emotion_response.content.strip().lower() if hasattr(emotion_response, 'content') else str(emotion_response).strip().lower()
        
        detected_emotion = detected_emotion.replace('"', '').replace("'", '').replace('.', '').strip()
        
        if ' ' in detected_emotion:
            detected_emotion = detected_emotion.split()[0]
        
        if len(detected_emotion) > 20 or not detected_emotion.isalpha() or len(detected_emotion) < 3:
            logger.warning(f"Invalid emotion word received: '{detected_emotion}', using thoughtful as default")
            detected_emotion = 'thoughtful'
        
        logger.info(f" OpenAI detected emotion: {detected_emotion}")
        
        # SECONDARY: Try FutureAGI for additional analysis (non-blocking)
        try:
            futureagi_result = evaluate_with_futureagi(message_content, "tone")
            if futureagi_result.get("success"):
                logger.info(f" FutureAGI Tone Analysis: {futureagi_result['evaluation']} (Reason: {futureagi_result['reason']})")
            else:
                logger.info(f" FutureAGI tone analysis not available: {futureagi_result.get('error', 'Unknown error')}")
        except Exception as e:
            logger.info(f" FutureAGI tone analysis failed: {e}")
        
        return detected_emotion
        
    except Exception as e:
        logger.error(f"AI emotion detection failed: {e}")
        return 'thoughtful'


def clean_agent_response(response_text):
    """
    Clean up agent responses to remove any agent name prefixes or duplications
    """
    import re
    
    
    response_text = re.sub(r'^Agent [AB]\s*\([^)]*\):\s*', '', response_text.strip())
    response_text = re.sub(r'^Agent [AB]:\s*', '', response_text.strip())
    response_text = re.sub(r'^Agent [AB]\s*\([^)]*\),?\s*', '', response_text.strip())
    response_text = re.sub(r'^Agent [AB],?\s*', '', response_text.strip())
    
    response_text = re.sub(r'\n\s*Agent [AB]\s*\([^)]*\):\s*', '\n', response_text)
    response_text = re.sub(r'\n\s*Agent [AB]:\s*', '\n', response_text)
    
    return response_text.strip()
        
   
def agent_a_node(state):
    """
    Agent A conversation node with FutureAGI observability integration
    """
    session_id = state.config.get('session_id', f"session_{id(state)}")
    conversation_id = state.config.get('conversation_id', f"conv_{state.config.get('topic', 'general').replace(' ', '_')}")
    
    if FUTURE_AGI_ENABLED:
        logger.info(f" FutureAGI Session: {session_id}, Conversation: {conversation_id}")
    
    is_first_message = len(state.messages) == 0
    
    if is_first_message:
        last_msg = f"Hello, let's discuss {state.config['topic']}."
        logger.info(f" Agent A initiating conversation about: {state.config['topic']}")
    else:
        last_msg = state.messages[-1] if state.messages else f"Hello, let's discuss {state.config['topic']}."
        logger.info(f" Agent A received: {last_msg[:100]}...")

    agent_a_persona = state.config.get('agent_a_persona', 'A professional discussant')
    base_tone = state.config.get('tone', 'neutral')
    
    prompt = (
        f"You are {agent_a_persona}. "
        f"Speak in a {base_tone} tone. "
        f"Context: {state.config.get('conversation_context', '')} "
        f"Topic: {state.config['topic']} "
        f"Previous message: {last_msg} "
        f"IMPORTANT: Do not start your response with your name or any agent identifier. "
        f"Just provide your direct response content without any prefixes."
    )

    logger.info(f" Agent A generating response (Turn {state.turn + 1})")
    
    response = llm1.invoke(prompt)
    response_text = response.content if hasattr(response, 'content') else str(response)
    
    response_text = clean_agent_response(response_text)
    
    logger.info(f" Agent A replied: {response_text[:100]}...")

    logger.info(f"Detecting emotion for Agent A response...")
    detected_emotion = detect_conversation_tone(response_text, base_tone)
    
    # Evaluate conversation quality using FutureAGI if available
    if not is_first_message:
        coherence_result = evaluate_with_futureagi(response_text, "coherence")
        if coherence_result.get("success"):
            logger.info(f" FutureAGI Coherence: {coherence_result['evaluation']} (Reason: {coherence_result['reason']})")
        else:
            logger.info(f" FutureAGI coherence evaluation failed: {coherence_result.get('error', 'Unknown error')}")
        
        resolution_result = evaluate_with_futureagi(response_text, "resolution")
        if resolution_result.get("success"):
            logger.info(f"FutureAGI Resolution: {resolution_result['evaluation']} (Reason: {resolution_result['reason']})")
        else:
            logger.info(f"FutureAGI resolution evaluation failed: {resolution_result.get('error', 'Unknown error')}")
        
        
    
    speaker_label = f"Agent A ({detected_emotion})"
    state.messages.append(f"{speaker_label}: {response_text}")
    
    logger.info(f" Turn {state.turn + 1} completed:")
    logger.info(f"   Speaker: Agent A")
    logger.info(f"   Emotion: {detected_emotion}")
    logger.info(f"   Message length: {len(response_text)} chars")
    if FUTURE_AGI_ENABLED:
        logger.info(f"   Session: {session_id}")
    
    state.speaker = "agent_b"
    state.turn += 1
    
    return state

def agent_b_node(state):
    """
    Agent B conversation node with FutureAGI observability integration
    """
    session_id = state.config.get('session_id', f"session_{id(state)}")
    conversation_id = state.config.get('conversation_id', f"conv_{state.config.get('topic', 'general').replace(' ', '_')}")
    
    last_msg = state.messages[-1] if state.messages else "Hello"
    logger.info(f" Agent B received: {last_msg[:100]}...")

    agent_b_persona = state.config.get('agent_b_persona', 'A professional respondent')
    base_tone = state.config.get('tone', 'neutral')
    
    prompt = (
        f"You are {agent_b_persona}. "
        f"Speak in a {base_tone} tone. "
        f"Context: {state.config.get('conversation_context', '')} "
        f"Topic: {state.config['topic']} "
        f"Respond to this message: {last_msg} "
        f"IMPORTANT: Do not start your response with your name or any agent identifier. "
        f"Just provide your direct response content without any prefixes."
    )

    logger.info(f" Agent B generating response (Turn {state.turn + 1})")
    
    response = llm2.invoke(prompt)
    response_text = response.content if hasattr(response, 'content') else str(response)
    
    response_text = clean_agent_response(response_text)
    
    logger.info(f" Agent B replied: {response_text[:100]}...")

    logger.info(f"Detecting emotion for Agent B response...")
    detected_emotion = detect_conversation_tone(response_text, base_tone)
    
    coherence_result = evaluate_with_futureagi(response_text, "coherence")
    if coherence_result.get("success"):
        logger.info(f" FutureAGI Coherence: {coherence_result['evaluation']} (Reason: {coherence_result['reason']})")
    else:
        logger.info(f" FutureAGI coherence evaluation failed: {coherence_result.get('error', 'Unknown error')}")
    
    resolution_result = evaluate_with_futureagi(response_text, "resolution")
    if resolution_result.get("success"):
        logger.info(f" FutureAGI Resolution: {resolution_result['evaluation']} (Reason: {resolution_result['reason']})")
    else:
        logger.info(f" FutureAGI resolution evaluation failed: {resolution_result.get('error', 'Unknown error')}")
    
    speaker_label = f"Agent B ({detected_emotion})"
    state.messages.append(f"{speaker_label}: {response_text}")
    
    # Enhanced logging for FutureAGI observability
    logger.info(f" Turn {state.turn + 1} completed:")
    logger.info(f"   Speaker: Agent B")
    logger.info(f"   Emotion: {detected_emotion}")
    logger.info(f"   Message length: {len(response_text)} chars")
    if FUTURE_AGI_ENABLED:
        logger.info(f"   Session: {session_id}")
    
    state.speaker = "agent_a"
    state.turn += 1
    
    return state