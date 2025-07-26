from my_agents import AgentSimulator

sim = AgentSimulator("examples/config_formal.yaml")
sim.run()
sim.save_transcript()
print("Conversation completed and saved.")