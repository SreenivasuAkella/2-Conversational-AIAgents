# File: my_agent/agent.py (MODIFIED with LangGraph end routing fix)

from langgraph.graph import StateGraph
from my_agents.state import ConversationState
from my_agents.utils.nodes import agent_a_node, agent_b_node
from my_agents.config import load_config
from my_agents.transcript import save_transcript, save_text_transcript
from my_agents.audio import generate_audio, merge_audio_clips
import os

class AgentSimulator:
    def __init__(self, config_path: str):
        self.config = load_config(config_path)
        self.state = ConversationState(max_turns=self.config.turns, config=self.config.dict())

        builder = StateGraph(ConversationState)
        builder.add_node("agent_a", agent_a_node)
        builder.add_node("agent_b", agent_b_node)

        builder.set_entry_point("agent_a")

        def router(state: ConversationState):
            if state.turn >= state.max_turns:
                return None  # This maps to '__end__'
            return state.speaker

        # Conditional edges now include None -> '__end__'
        builder.add_conditional_edges("agent_a", router, {
            "agent_b": "agent_b",
            None: "__end__"
        })

        builder.add_conditional_edges("agent_b", router, {
            "agent_a": "agent_a",
            None: "__end__"
        })

        self.app = builder.compile()

    def run(self):
        final_state = self.app.invoke(self.state)
        # Fix: Handle dict output from LangGraph and convert back to ConversationState
        if isinstance(final_state, dict):
            self.state = ConversationState(**final_state)
        else:
            self.state = final_state
        return self.state

    def save_transcript(self):
        save_transcript(self.state.messages)
        save_text_transcript(self.state.messages)

    def generate_audio(self):
        """Generate audio files for each message and merge them into a single conversation audio."""
        audio_files = []
        os.makedirs("outputs/audio", exist_ok=True)
        
        print("Generating audio for conversation...")
        
        for idx, msg in enumerate(self.state.messages):
            if ":" in msg:
                speaker, content = msg.split(":", 1)
                # Use different voices for different agents
                voice = self.config.voices[0 if "A" in speaker else 1]
                path = f"outputs/audio/turn_{idx+1}.mp3"
                
                print(f"Generating audio for {speaker.strip()}: {content[:50]}...")
                audio_file = generate_audio(content.strip(), voice, self.config.tts_provider, path)
                if audio_file:
                    audio_files.append(audio_file)
        
        # Merge all audio files into one conversation
        if audio_files:
            final_audio_path = merge_audio_clips(audio_files, "outputs/conversation.wav")
            if final_audio_path:
                print(f"Complete conversation audio saved to: {final_audio_path}")
            else:
                print("Failed to merge audio files")
        else:
            print("No audio files were generated successfully")
