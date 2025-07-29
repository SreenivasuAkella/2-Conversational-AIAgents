from langgraph.graph import StateGraph
from agentic_sdk.state import ConversationState
from agentic_sdk.utils.nodes import agent_a_node, agent_b_node
from agentic_sdk.config import load_config, ConversationMode
from agentic_sdk.transcript import save_transcript, save_text_transcript
from agentic_sdk.audio import generate_audio, merge_audio_clips
import os
from typing import List

class AgentSimulator:
    def __init__(self, config_path: str = None, config: dict = None):
        """Initialize AgentSimulator with configuration.
        
        Args:
            config_path: Path to configuration file
            config: Configuration dictionary (alternative to config_path)
        """
        self.config = None
        self.state = None
        self.app = None
        self._observers = []  # For observability callbacks
        
        if config_path:
            self.configure_from_file(config_path)
        elif config:
            self.configure_from_dict(config)
    
    def configure_from_file(self, config_path: str):
        """Configure the simulator from a file path."""
        self.config = load_config(config_path)
        self._initialize_state()
        
    def configure_from_dict(self, config: dict):
        """Configure the simulator from a configuration dictionary."""
        # Convert dict to config object if needed
        self.config = config  # Assuming config object or dict handling
        self._initialize_state()
    
    def _initialize_state(self):
        """Initialize conversation state after configuration."""
        self.state = ConversationState(max_turns=self.config.turns, config=self.config.dict())

        # Only set up LangGraph for unscripted conversations
        if self.config.mode == ConversationMode.UNSCRIPTED:
            self._setup_unscripted_conversation()
        else:
            self.app = None  # No graph needed for scripted conversations

    def _setup_unscripted_conversation(self):
        """Set up the LangGraph for AI-generated conversations with proper turn-taking logic."""
        builder = StateGraph(ConversationState)
        builder.add_node("agent_a", agent_a_node)
        builder.add_node("agent_b", agent_b_node)

        # Agent A always starts the conversation
        builder.set_entry_point("agent_a")

        def router(state: ConversationState):
            """
            Determine who speaks next based on turn count and current speaker.
            Rules:
            - Agent A starts (turn 0)
            - Agents alternate turns
            - Conversation ends when max_turns is reached
            """
            if state.turn >= state.max_turns:
                print(f"Conversation ending: reached max turns ({state.max_turns})")
                return None  # This maps to '__end__'
            
            next_speaker = state.speaker
            print(f"Turn {state.turn}: Next speaker is {next_speaker}")
            return next_speaker

        # Conditional edges with proper turn-taking
        builder.add_conditional_edges("agent_a", router, {
            "agent_b": "agent_b",
            None: "__end__"
        })

        builder.add_conditional_edges("agent_b", router, {
            "agent_a": "agent_a", 
            None: "__end__"
        })

        self.app = builder.compile()
        print("Unscripted conversation graph initialized with turn-taking logic")

    def add_observer(self, callback):
        """Add an observer callback for monitoring conversation progress.
        
        Args:
            callback: Function that accepts (event_type, data) parameters
        """
        self._observers.append(callback)
    
    def remove_observer(self, callback):
        """Remove an observer callback."""
        if callback in self._observers:
            self._observers.remove(callback)
    
    def _notify_observers(self, event_type: str, data: dict):
        """Notify all observers of an event."""
        for callback in self._observers:
            try:
                callback(event_type, data)
            except Exception as e:
                print(f"Observer callback error: {e}")

    def run(self, observe: bool = True):
        """Run the conversation based on the configured mode.
        
        Args:
            observe: Whether to emit observation events during execution
        """
        if not self.config:
            raise ValueError("AgentSimulator must be configured before running")
            
        if observe:
            self._notify_observers("conversation_started", {
                "mode": self.config.mode.value,
                "topic": self.config.topic,
                "max_turns": self.config.turns
            })
        
        try:
            if self.config.mode == ConversationMode.SCRIPTED:
                result = self._run_scripted_conversation(observe)
            else:
                result = self._run_unscripted_conversation(observe)
                
            if observe:
                self._notify_observers("conversation_completed", {
                    "total_messages": len(self.state.messages),
                    "final_turn": self.state.turn
                })
                
            return result
        except Exception as e:
            if observe:
                self._notify_observers("conversation_error", {"error": str(e)})
            raise

    def _run_scripted_conversation(self, observe: bool = True):
        """Run a scripted conversation using predefined messages with dynamic tone detection."""
        if observe:
            self._notify_observers("scripted_mode_started", {"base_tone": self.config.tone})
            
        print("Running scripted conversation...")
        print(f"Topic: {self.config.topic}")
        print(f"Base tone: {self.config.tone}")
        print("-" * 50)
        
        if not self.config.scripted_messages:
            raise ValueError("Scripted mode requires 'scripted_messages' in configuration")
        
        # Import tone detection function
        from agentic_sdk.utils.nodes import detect_conversation_tone
        
        # Convert scripted messages to show dynamic emotion format
        base_tone = self.config.tone
        formatted_messages = []
        
        for i, msg in enumerate(self.config.scripted_messages[:self.config.turns]):
            if ":" in msg:
                speaker, content = msg.split(":", 1)
                
                # Detect dynamic emotion based on message content
                detected_emotion = detect_conversation_tone(content.strip(), base_tone)
                
                # Convert "Agent A:" to "Agent A (detected_emotion):"
                if "Agent A" in speaker:
                    formatted_speaker = f"Agent A ({detected_emotion})"
                elif "Agent B" in speaker:
                    formatted_speaker = f"Agent B ({detected_emotion})"
                    
                formatted_messages.append(f"{formatted_speaker}:{content}")
                
                if observe:
                    self._notify_observers("message_processed", {
                        "turn": i+1,
                        "speaker": formatted_speaker,
                        "emotion": detected_emotion,
                        "content_preview": content.strip()[:100]
                    })
                    
                print(f"Turn {i+1}: {formatted_speaker} - detected emotion: {detected_emotion}")
            else:
                formatted_messages.append(msg)
        
        self.state.messages = formatted_messages
        self.state.turn = len(self.state.messages)
        
        print(f"✅ Loaded {len(self.state.messages)} scripted messages with dynamic tone detection")
        return self.state

    def _run_unscripted_conversation(self, observe: bool = True):
        """Run an AI-generated conversation using LangGraph with proper turn management."""
        if observe:
            self._notify_observers("unscripted_mode_started", {
                "target_turns": self.state.max_turns,
                "topic": self.config.topic
            })
            
        print("Running unscripted (AI-generated) conversation...")
        print(f"Target turns: {self.state.max_turns}")
        print(f"Topic: {self.config.topic}")
        print(f"Tone: {self.config.tone}")
        print("-" * 50)
        
        if not self.app:
            raise ValueError("LangGraph not initialized for unscripted conversation")
        
        # Initialize conversation state
        self.state.turn = 0
        self.state.speaker = "agent_a"  # Agent A always starts
        self.state.messages = []
        
        print("🎬 Starting conversation with Agent A...")
        
        try:
            # Run the conversation through LangGraph
            final_state = self.app.invoke(self.state)
            
            # Convert result back to ConversationState if it's a dict
            if isinstance(final_state, dict):
                self.state = ConversationState(**final_state)
            else:
                self.state = final_state
                
            print(f"✅ Conversation completed with {len(self.state.messages)} exchanges")
            
        except Exception as e:
            print(f"❌ Error during conversation: {e}")
            raise
        
        return self.state

    def get_state(self):
        """Get current conversation state for observation."""
        return {
            "messages": self.state.messages if self.state else [],
            "turn": self.state.turn if self.state else 0,
            "max_turns": self.state.max_turns if self.state else 0,
            "config": self.config.dict() if self.config else {}
        }
    
    def get_metrics(self):
        """Get conversation metrics for monitoring."""
        if not self.state:
            return {"status": "not_initialized"}
            
        return {
            "total_messages": len(self.state.messages),
            "current_turn": self.state.turn,
            "progress": self.state.turn / self.state.max_turns if self.state.max_turns > 0 else 0,
            "mode": self.config.mode.value if self.config else "unknown",
            "completed": self.state.turn >= self.state.max_turns
        }

    def save_transcript(self):
        """Save the conversation transcript in both JSON and text formats in mode-specific folders."""
        # Determine the output folder based on conversation mode
        mode_folder = f"outputs/{self.config.mode.value}"
        
        # Save in mode-specific folders
        save_transcript(self.state.messages, f"{mode_folder}/transcript.json")
        save_text_transcript(self.state.messages, f"{mode_folder}/transcript.txt")
        
        print(f"📄 Transcript saved to {mode_folder}/transcript.txt and {mode_folder}/transcript.json")

    def generate_audio(self):
        """Generate audio files for each message and merge them into a single conversation audio in mode-specific folders."""
        # Determine the output folder based on conversation mode
        mode_folder = f"outputs/{self.config.mode.value}"
        audio_folder = f"{mode_folder}/audio"
        
        audio_files = []
        os.makedirs(audio_folder, exist_ok=True)
        
        print("Generating audio for conversation...")
        
        for idx, msg in enumerate(self.state.messages):
            if ":" in msg:
                speaker, content = msg.split(":", 1)
                # Extract Agent A or Agent B from speaker label like "Agent A (persona)"
                if "Agent A" in speaker:
                    voice = self.config.voices[0] if len(self.config.voices) > 0 else "voice1"
                elif "Agent B" in speaker:
                    voice = self.config.voices[1] if len(self.config.voices) > 1 else "voice2"
                    
                path = f"{audio_folder}/turn_{idx+1}.mp3"
                
                print(f"Generating audio for {speaker.strip()}: {content[:50]}...")
                audio_file = generate_audio(content.strip(), voice, self.config.tts_provider, path)
                if audio_file:
                    audio_files.append(audio_file)
        
        # Merge all audio files into one conversation
        if audio_files:
            final_audio_path = merge_audio_clips(audio_files, f"{mode_folder}/conversation.wav")
            if final_audio_path:
                print(f"🎵 Complete conversation audio saved to: {final_audio_path}")
            else:
                print("Failed to merge audio files")
        else:
            print("No audio files were generated successfully")
