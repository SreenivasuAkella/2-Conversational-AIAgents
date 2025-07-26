
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from my_agents.audio import generate_audio, merge_audio_clips
from my_agents.transcript import save_transcript, save_text_transcript

def demo_conversation():
    """Create a demo conversation and generate audio."""
    
    # Demo conversation messages
    messages = [
        "Agent A: Hello! I'd like to discuss the impact of artificial intelligence on modern society.",
        "Agent B: That's a fascinating topic. AI is transforming many aspects of our daily lives, from healthcare to transportation.",
        "Agent A: Absolutely. One area I find particularly interesting is how AI is changing the job market. What are your thoughts?",
        "Agent B: It's a complex issue. While AI may automate some jobs, it's also creating new opportunities in fields like AI development, data science, and human-AI collaboration.",
        "Agent A: That's a balanced perspective. Do you think we need new policies to help workers adapt to these changes?",
        "Agent B: Definitely. Retraining programs and education reforms will be crucial to ensure everyone can benefit from the AI revolution."
    ]
    
    print("🤖 Generating demo conversation audio...")
    
    # Create output directories
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("outputs/audio", exist_ok=True)
    
    # Save transcript
    save_transcript(messages)
    save_text_transcript(messages)
    print("✅ Transcript saved")
    
    # Generate audio for each message
    audio_files = []
    voices = ["male", "female"]  # Alternating voices
    
    for idx, msg in enumerate(messages):
        if ":" in msg:
            speaker, content = msg.split(":", 1)
            voice = voices[0 if "A" in speaker else 1]
            path = f"outputs/audio/turn_{idx+1}.mp3"
            
            print(f"🎵 Generating audio for {speaker.strip()}: {content[:50]}...")
            audio_file = generate_audio(content.strip(), voice, "gtts", path)
            if audio_file:
                audio_files.append(audio_file)
    
    # Merge all audio files
    if audio_files:
        print("🔀 Merging audio files...")
        final_audio_path = merge_audio_clips(audio_files, "outputs/conversation.wav")
        if final_audio_path:
            print(f"🎉 Complete conversation audio saved to: {final_audio_path}")
            print(f"📄 Transcript saved to: outputs/transcript.txt")
            print("\n✅ Demo completed successfully!")
        else:
            print("❌ Failed to merge audio files")
    else:
        print("❌ No audio files were generated")

if __name__ == "__main__":
    try:
        demo_conversation()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure the required packages are installed:")
        print("pip install gtts soundfile numpy")
