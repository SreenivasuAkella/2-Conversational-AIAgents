import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from agentic_sdk import AgentSimulator

def conversation_observer(event_type, data):
    """Observer callback to monitor conversation progress."""
    if event_type == "conversation_started":
        print(f"🚀 Conversation started - Mode: {data['mode']}, Topic: {data['topic']}")
    elif event_type == "scripted_mode_started":
        print(f"📜 Scripted mode initialized - Base tone: {data['base_tone']}")
    elif event_type == "message_processed":
        print(f"💬 Turn {data['turn']}: {data['speaker']} - Content: {data['content_preview'][:50]}...")
    elif event_type == "conversation_completed":
        print(f"✅ Conversation finished - {data['total_messages']} messages, {data['final_turn']} turns")
    elif event_type == "conversation_error":
        print(f"❌ Error occurred: {data['error']}")

def main():
    print("Running SCRIPTED conversation...")
    print("=" * 50)
    
    # Initialize simulator (new SDK pattern)
    sim = AgentSimulator()
    
    # Configure from file (separate configuration step)
    sim.configure_from_file("examples/config_scripted.yaml")
    
    # Add observer for real-time monitoring
    sim.add_observer(conversation_observer)
    
    # Show initial state
    state = sim.get_state()
    print(f"📊 Configuration loaded: {len(state['config'])} settings")
    
    # Run the conversation with observability
    sim.run(observe=True)
    
    # Show final metrics
    final_metrics = sim.get_metrics()
    print(f"📊 Final metrics: {final_metrics['total_messages']} messages processed")
    
    # Save outputs
    sim.save_transcript()
    sim.generate_audio()
    
    print("\n🎉 Scripted conversation completed!")
    print("📁 Check outputs/scripted/transcript.txt for the conversation")
    print("🎵 Check outputs/scripted/conversation.wav for the audio")
    print("🎭 Emotions are dynamically detected based on conversation content!")

if __name__ == "__main__":
    main()
