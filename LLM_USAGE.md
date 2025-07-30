# LLM Usage Guide

This document explains how Large Language Models (LLMs) are used in the `ai-convo-simulator` SDK, including configuration, switching models, and best practices.

---

## 1. LLMs Used

- **OpenAI GPT Models:**  
  - `gpt-4o-mini` (default for Agent A)
  - `gpt-3.5-turbo` (default for Agent B)
- **FutureAGI Evaluation Models:**  
  Used for conversation evaluation (tone, coherence, resolution) via the FutureAGI SDK.

---

## 2. Where LLMs Are Used

- **Conversation Generation:**  
  Each agent uses an LLM to generate responses based on persona, tone, and context.
- **Emotion Detection:**  
  LLMs analyze each message to detect the speaker's emotion.
- **Evaluation (Optional):**  
  FutureAGI models score tone, coherence, and resolution for each message.

---

## 3. Configuration

### API Keys

Set your OpenAI and FutureAGI API keys in `.env`:

```
OPENAI_API_KEY=sk-...
FI_API_KEY=...
FI_SECRET_KEY=...
# or
FUTUREAGI_API_KEY=...
FUTUREAGI_SECRET_KEY=...
```

### Model Selection

- By default, Agent A uses `gpt-4o-mini` and Agent B uses `gpt-3.5-turbo`.
- To change models, edit the following lines in `agentic_sdk/utils/nodes.py`:

```python
llm1 = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)  # Agent A
llm2 = ChatOpenAI(model="gpt-3.5-turbo", api_key=api_key)  # Agent B
```

Replace with any supported OpenAI model name.

---

## 4. How LLMs Are Invoked

- **Agent Nodes:**  
  Each agent node (`agent_a_node`, `agent_b_node`) builds a prompt and calls `.invoke(prompt)` on the LLM.
- **Emotion Detection:**  
  The `detect_conversation_tone` function sends a special prompt to the LLM to get a single-word emotion.
- **Evaluation:**  
  The `evaluate_with_futureagi` function calls the FutureAGI SDK, which uses its own LLM backend.

---

## 5. Best Practices

- **API Usage:**  
  LLM calls consume API credits and may incur costs. Use scripted mode for testing if you want to avoid LLM calls.
- **Model Choice:**  
  Use `gpt-4o-mini` for best quality and speed, or `gpt-3.5-turbo` for lower cost.
- **Error Handling:**  
  The SDK will log and handle most LLM errors gracefully, defaulting to safe outputs if needed.

---

## 6. Extending LLM Usage

- You can swap in other LLM providers by replacing the `ChatOpenAI` class with another LangChain-compatible LLM.
- For advanced use, subclass the agent nodes and override the prompt logic.

---

## 7. Example: Customizing LLMs

```python
from langchain_openai import ChatOpenAI

# Use a different OpenAI model for both agents
llm1 = ChatOpenAI(model="gpt-4", api_key=api_key)
llm2 = ChatOpenAI(model="gpt-3.5-turbo-16k", api_key=api_key)
```

---

## 8. References

- [OpenAI API Models](https://platform.openai.com/docs/models)
-