# ai-convo-simulator

SDK to simulate 2-person AI conversations with audio and text output using LangGraph.

---

## Features

- **Scripted & Unscripted Conversations:** Run deterministic (scripted) or AI-generated (unscripted) dialogues.
- **Audio & Text Output:** Generate transcripts and synthesize audio for each turn.
- **Observability:** Attach observer callbacks for real-time monitoring and logging.
- **Evaluation:** Integrate with FutureAGI for tone, coherence, and resolution analysis.
- **Flexible Configuration:** YAML-based config for easy scenario setup.
- **Extensible:** Add new agents, TTS providers, or evaluation hooks.

---

## Project Structure

```
agentic_call_simulator_sdk/
│
├── agentic_sdk/
│   ├── __init__.py
│   ├── simulator.py
│   ├── agents.py
│   ├── tts.py
│   ├── observer.py
│   ├── evaluation.py
│   └── utils.py
│
├── examples/
│   ├── config_formal.yaml
│   ├── config_scripted.yaml
│   ├── run_scripted.py
│   └── run_unscripted.py
│
├── outputs/
│   ├── logs/
│   │   └── run.log
│   ├── scripted/
│   │   ├── transcript.txt
│   │   ├── transcript.json
│   │   └── conversation.wav
│   └── unscripted/
│       ├── transcript.txt
│       ├── transcript.json
│       └── conversation.wav
│
├── .env
├── pyproject.toml
├── requirements.txt
├── setup_check.py
└── README.md
```

---

## Installation

### 1. Create a Virtual Environment (Recommended)

On Windows:
```sh
python -m venv .venv
.venv\Scripts\activate
```

On macOS/Linux:
```sh
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install from Source

```sh
git clone https://github.com/SreenivasuAkella/2-Conversational-AIAgents.git
cd 2-Conversational-AIAgents
pip install .
```

### From PyPI (when published)

```sh
pip install ai-convo-simulator
```
---

## Environment Setup

1. Copy `.env.template` to `.env` and fill in your API keys:
   ```
   OPENAI_API_KEY=sk-...
   COQUI_API_KEY=ap2_...
   ELEVENLABS_API_KEY=ap2_...
   FUTUREAGI_API_KEY=...
   FUTUREAGI_SECRET_KEY=...
   FI_API_KEY=...
   FI_SECRET_KEY=...
   ```
   > Only set the keys you need for your use case.

2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

---

## Quickstart

### Scripted Conversation

```python
from agentic_sdk import AgentSimulator

sim = AgentSimulator()
sim.configure_from_file("examples/config_scripted.yaml")
sim.run(observe=True)
sim.save_transcript()
sim.generate_audio()
```

### Unscripted (AI-generated) Conversation

```python
from agentic_sdk import AgentSimulator

sim = AgentSimulator()
sim.configure_from_file("examples/config_formal.yaml")
sim.run(observe=True)
sim.save_transcript()
sim.generate_audio()
```

### Observability Example

```python
def observer(event_type, data):
    print(f"{event_type}: {data}")

sim.add_observer(observer)
```

---

## Configuration Example

YAML config files define the simulation:

```yaml
turns: 6
topic: "Technology and Society"
tone: "formal"
mode: "unscripted"
voices:
  - "voice1"
  - "voice2"
tts_provider: "gtts"
agent_a_persona: "A thoughtful technology researcher..."
agent_b_persona: "An insightful social scientist..."
conversation_context: "A professional discussion about the relationship between technology and society..."
```

---

## Outputs

- **Text Transcript:** `outputs/{mode}/transcript.txt`
- **JSON Transcript:** `outputs/{mode}/transcript.json`
- **Audio:** `outputs/{mode}/conversation.wav`
- **Logs:** `outputs/logs/run.log`

---

## SDK Lifecycle

- **init:** `sim = AgentSimulator()`
- **configure:** `sim.configure_from_file(...)` or `sim.configure_from_dict(...)`
- **run:** `sim.run(observe=True)`
- **observe:** `sim.add_observer(callback)`
- **save:** `sim.save_transcript()`, `sim.generate_audio()`

---

## Evaluation & Observability

- Integrates with FutureAGI for tone, coherence, and resolution scoring.
- Observer pattern allows custom logging, dashboards, or live monitoring.

---

## Development & Building

- Uses `pyproject.toml` for build and dependency management.
- To use as a dependency in your own project (with Poetry):
  ```toml
  [tool.poetry.dependencies]
  ai-convo-simulator = { path = "../agentic_call_simulator_sdk" }
  ```

---

## Design Approach, Trade-offs, and Next Steps

**Approach:**  
- Modular SDK with clear lifecycle (`init`, `configure`, `run`, `observe`).
- Supports both deterministic (scripted) and generative (AI) conversations.
- Pluggable TTS and evaluation backends.

**Trade-offs:**  
- LLM-based unscripted mode requires API keys and incurs latency/cost.
- Audio quality depends on TTS provider.
- Evaluation features require additional API keys.

**Next Steps:**  
- Add more TTS/language support.
- Enhance persona/context memory.
- Add web UI and visualization tools.
- Publish to PyPI for easier installation.

---

## License

MIT License

---

## Author

- Sreenivasu Akella (210020001@iitdh.ac.in)

---

## References

- [LangGraph](https://github.com/langchain-ai/langgraph)
- [OpenAI API](https://platform.openai.com/)
- [FutureAGI](https://futureagi.com/)

---

## Example CLI Usage

```sh
python examples/run_scripted.py
python examples/run_unscripted.py
```

---