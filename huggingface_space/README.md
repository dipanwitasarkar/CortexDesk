---
title: Windows AI Assistant LLM Server
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# Windows AI Assistant LLM Server

This Space runs an LLM server that the Windows AI Assistant can connect to.

## Model
- **Model**: mistralai/Mistral-7B-Instruct-v0.2
- **Hardware**: T4 small (free tier)
- **API**: OpenAI-compatible

## Endpoints

### Health Check
```
GET /health
```

### Chat Completions (OpenAI-compatible)
```
POST /v1/chat/completions
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 0.7,
  "max_tokens": 512
}
```

### Simple Generate
```
POST /generate
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 0.7,
  "max_tokens": 512
}
```

## Usage in Windows AI Assistant

Configure your Windows AI Assistant backend:

```env
DELL_LLM_ENDPOINT=https://<your-space-name>.hf.space/v1
DELL_LLM_API_KEY=
DELL_LLM_MODEL=mistralai/Mistral-7B-Instruct-v0.2
DELL_LLM_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

Replace `<your-space-name>` with your actual Space name.
