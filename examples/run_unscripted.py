import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from agentic_sdk import AgentSimulator

def conversation_observer(event_type, data):
    """Observer callback to monitor conversation progress."""
    if event_type == "conversation_started":
        print(f" Conversation started - Mode: {data['mode']}, Topic: {data['topic']}")
    elif event_type == "unscripted_mode_started":
        print(f" AI mode initialized - Target turns: {data['target_turns']}")
    elif event_type == "message_processed":
        print(f" Turn {data['turn']}: {data['speaker']} ({data['emotion']})")
    elif event_type == "conversation_completed":
        print(f"Conversation finished - {data['total_messages']} messages, {data['final_turn']} turns")
    elif event_type == "conversation_error":
        print(f" Error occurred: {data['error']}")

def main():
    print("Running UNSCRIPTED (AI-generated) conversation...")
    print("=" * 50)
    
    # Initialize simulator (new SDK pattern)
    sim = AgentSimulator()
    
    # Configure from file (separate configuration step)
    sim.configure_from_file("examples/config_formal.yaml")
    
    # Add observer for real-time monitoring
    sim.add_observer(conversation_observer)
    
    # Check initial state
    print(f"Initial metrics: {sim.get_metrics()}")
    
    # Run the conversation with observability
    sim.run(observe=True)
    
    # Check final metrics
    final_metrics = sim.get_metrics()
    print(f" Final metrics: Progress {final_metrics['progress']:.1%}, Completed: {final_metrics['completed']}")
    
    # Save outputs
    sim.save_transcript()
    sim.generate_audio()
    
    print("\nUnscripted conversation completed!")
    print(" Check outputs/unscripted/transcript.txt for the conversation")
    print(" Check outputs/unscripted/conversation.wav for the audio")

if __name__ == "__main__":
    main()
