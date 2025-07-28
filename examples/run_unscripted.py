import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from my_agents import AgentSimulator

def main():
    print("Running UNSCRIPTED (AI-generated) conversation...")
    print("=" * 50)
    
    # Use the unscripted configuration  
    sim = AgentSimulator("examples/config_formal.yaml")
    
    # Run the conversation
    sim.run()
    
    # Save outputs
    sim.save_transcript()
    sim.generate_audio()
    
    print(" Unscripted conversation completed!")
    print(" Check outputs/unscripted/transcript.txt for the conversation")
    print("Check outputs/unscripted/conversation.wav for the audio")
    print("Emotions are dynamically detected based on conversation content!")

if __name__ == "__main__":
    main()
