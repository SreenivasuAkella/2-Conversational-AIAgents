from my_agents import AgentSimulator

sim = AgentSimulator("examples/config_formal.yaml")
sim.run()
sim.save_transcript()
sim.generate_audio()
print("Conversation completed and saved with audio.")