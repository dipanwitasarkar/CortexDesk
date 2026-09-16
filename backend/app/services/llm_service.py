from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.core.config import settings
from app.core.database import get_async_db
from app.models.memory import LLMConfiguration, LLMProvider
from sqlalchemy import select
from typing import List, Dict, Any, Optional
import logging
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        # Initialize with default configuration from settings
        self.use_local = False
        self.use_runpod = False
        self.use_groq = False
        self.use_huggingface = False
        self.tokenizer = None
        self.model = None
        self.embedding_model = None
        self.chat_model = None
        self.hf_client = None
        self.model_name = settings.llm_model
        self.embedding_model_name = settings.llm_embedding_model
        self.temperature = 0.7
        self.max_tokens = 1000
        
        # Load default configuration
        self._load_configuration(
            provider="local" if settings.llm_endpoint == "local" else "custom",
            model_name=settings.llm_model,
            endpoint=settings.llm_endpoint,
            api_key=settings.llm_api_key,
            temperature=0.7,
            max_tokens=1000
        )
    
    def _load_configuration(
        self,
        provider: str,
        model_name: str,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ):
        """Load LLM configuration"""
        self.provider = provider
        self.model_name = model_name
        self.endpoint = endpoint
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Reset state
        self.use_local = False
        self.use_runpod = False
        self.use_groq = False
        self.use_huggingface = False
        
        # Load based on provider
        if provider == "local":
            logger.info("Using local model (gpt2)")
            self.use_local = True
            
            # Load local model
            try:
                logger.info(f"Loading local model: {model_name}")
                self.tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
                self.model = AutoModelForCausalLM.from_pretrained(model_name, local_files_only=True)
                self.model.eval()
                logger.info("Local model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load local model: {e}")
                raise
            
            # Load local embedding model
            try:
                embedding_model_name = self.embedding_model_name or "sentence-transformers/all-MiniLM-L6-v2"
                logger.info(f"Loading local embedding model: {embedding_model_name}")
                self.embedding_model = SentenceTransformer(embedding_model_name)
                logger.info("Local embedding model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load local embedding model: {e}")
                self.embedding_model = None
                
        elif provider == "groq":
            logger.info("Using Groq API (OpenAI-compatible)")
            self.use_groq = True
            self.chat_model = ChatOpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=api_key,
                model=model_name,
                temperature=temperature,
                streaming=True
            )
            self.embedding_model = None
            
        elif provider == "runpod":
            logger.info("Using RunPod Public Endpoints (OpenAI-compatible)")
            self.use_runpod = True
            self.chat_model = ChatOpenAI(
                base_url=endpoint,
                api_key=api_key,
                model=model_name,
                temperature=temperature,
                streaming=True
            )
            self.embedding_model = None
            
        elif provider == "openai":
            logger.info("Using OpenAI API")
            self.chat_model = ChatOpenAI(
                base_url="https://api.openai.com/v1",
                api_key=api_key,
                model=model_name,
                temperature=temperature,
                streaming=True
            )
            self.embedding_model = OpenAIEmbeddings(
                base_url="https://api.openai.com/v1",
                api_key=api_key,
                model="text-embedding-ada-002"
            )
            
        elif provider == "anthropic":
            logger.info("Using Anthropic API")
            # Anthropic requires different client, placeholder for now
            logger.warning("Anthropic provider not fully implemented yet")
            self.chat_model = ChatOpenAI(
                base_url=endpoint or "https://api.anthropic.com",
                api_key=api_key,
                model=model_name,
                temperature=temperature,
                streaming=True
            )
            self.embedding_model = None
            
        elif provider == "azure":
            logger.info("Using Azure OpenAI Service")
            self.chat_model = ChatOpenAI(
                base_url=endpoint,
                api_key=api_key,
                model=model_name,
                temperature=temperature,
                streaming=True
            )
            self.embedding_model = OpenAIEmbeddings(
                base_url=endpoint,
                api_key=api_key,
                model="text-embedding-ada-002"
            )
            
        elif provider == "custom":
            logger.info(f"Using custom endpoint: {endpoint}")
            self.chat_model = ChatOpenAI(
                base_url=endpoint,
                api_key=api_key,
                model=model_name,
                temperature=temperature,
                streaming=True
            )
            self.embedding_model = OpenAIEmbeddings(
                base_url=endpoint,
                api_key=api_key,
                model="text-embedding-ada-002"
            )
            
        else:
            logger.warning(f"Unknown provider: {provider}, falling back to local")
            self._load_configuration("local", "gpt2", None, None, temperature, max_tokens)
    
    async def load_user_configuration(self, user_id: int = 1):
        """Load LLM configuration from database for a user"""
        async for db in get_async_db():
            result = await db.execute(
                select(LLMConfiguration)
                .where(LLMConfiguration.user_id == user_id)
                .where(LLMConfiguration.is_active == True)
            )
            config = result.scalar_one_or_none()
            
            if config:
                logger.info(f"Loading user's LLM configuration: {config.provider}")
                self._load_configuration(
                    provider=config.provider.value,
                    model_name=config.model_name,
                    endpoint=config.endpoint,
                    api_key=config.api_key,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens
                )
            else:
                logger.info("No active LLM configuration found, checking for local configuration")
                # Check if user has a local configuration
                local_result = await db.execute(
                    select(LLMConfiguration)
                    .where(LLMConfiguration.user_id == user_id)
                    .where(LLMConfiguration.provider == LLMProvider.LOCAL)
                )
                local_config = local_result.scalar_one_or_none()
                
                if local_config:
                    # Activate the local configuration
                    local_config.is_active = True
                    await db.commit()
                    logger.info(f"Activated existing local configuration for user {user_id}")
                    self._load_configuration("local", local_config.model_name, local_config.endpoint, local_config.api_key, local_config.temperature, local_config.max_tokens)
                else:
                    # Create default local configuration
                    logger.info("No local configuration found, creating default")
                    default_config = LLMConfiguration(
                        user_id=user_id,
                        provider=LLMProvider.LOCAL,
                        model_name="gpt2",
                        endpoint=None,
                        api_key=None,
                        temperature=0.7,
                        max_tokens=1000,
                        is_active=True
                    )
                    db.add(default_config)
                    await db.commit()
                    await db.refresh(default_config)
                    
                    # Load the default configuration
                    self._load_configuration("local", "gpt2", None, None, 0.7, 1000)

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate a response from the LLM"""
        if self.use_local:
            return await self._generate_local_response(messages, temperature, max_tokens)
        elif self.use_runpod or self.use_groq:
            return await self._generate_openai_response(messages, temperature, max_tokens)
        elif self.use_huggingface:
            return await self._generate_hf_response(messages, temperature, max_tokens)
        else:
            return await self._generate_openai_response(messages, temperature, max_tokens)

    async def generate_simple_response(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Simple wrapper for generating responses with a single message"""
        messages = []
        
        # Add context if provided
        if context:
            messages.append({
                "role": "system",
                "content": f"Context: {str(context)}"
            })
        
        # Add chat history if provided
        if chat_history:
            messages.extend(chat_history)
        
        # Add current message
        messages.append({
            "role": "user",
            "content": message
        })
        
        return await self.generate_response(messages)

    async def _generate_local_response(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate response using local gpt2 model"""
        try:
            # Convert messages to a simple prompt
            prompt = self._messages_to_prompt(messages)
            
            # Tokenize
            inputs = self.tokenizer(prompt, return_tensors="pt")
            
            # Set generation parameters
            gen_kwargs = {
                "max_new_tokens": max_tokens if max_tokens else 100,
                "do_sample": True,
                "temperature": temperature if temperature else self.temperature,
                "top_k": 50,
                "top_p": 0.95,
                "pad_token_id": self.tokenizer.eos_token_id
            }
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(**inputs, **gen_kwargs)
            
            # Decode
            response_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the prompt from the response
            if prompt in response_text:
                response_text = response_text.replace(prompt, "").strip()
            
            return response_text
            
        except Exception as e:
            logger.error(f"Local model generation error: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"

    async def _generate_hf_response(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate response using Hugging Face Inference API"""
        try:
            # Try conversational API first (for chat models)
            kwargs = {}
            if temperature is not None:
                kwargs["temperature"] = temperature
            if max_tokens is not None:
                kwargs["max_tokens"] = max_tokens
            
            response = self.hf_client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            
            # Extract the response
            if hasattr(response, 'choices') and len(response.choices) > 0:
                return response.choices[0].message.content
            elif isinstance(response, dict):
                return response.get('generated_text', str(response))
            else:
                return str(response)
                
        except Exception as e:
            logger.error(f"Hugging Face conversational API error: {e}")
            # Fallback to text generation
            try:
                prompt = self._messages_to_prompt(messages)
                kwargs = {}
                if temperature is not None:
                    kwargs["temperature"] = temperature
                if max_tokens is not None:
                    kwargs["max_new_tokens"] = max_tokens
                
                response = self.hf_client.text_generation(
                    model=self.model,
                    prompt=prompt,
                    **kwargs
                )
                
                if isinstance(response, list) and len(response) > 0:
                    return response[0].get("generated_text", str(response[0]))
                elif isinstance(response, dict):
                    return response.get("generated_text", str(response))
                else:
                    return str(response)
            except Exception as e2:
                logger.error(f"Hugging Face text generation fallback error: {e2}")
                raise

    async def _generate_openai_response(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate response using OpenAI-compatible endpoint"""
        langchain_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                langchain_messages.append(SystemMessage(content=msg["content"]))
            elif msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))
        
        kwargs = {}
        if temperature is not None:
            kwargs["temperature"] = temperature
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        
        response = await self.chat_model.ainvoke(langchain_messages, **kwargs)
        return response.content

    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert messages to a single prompt for Hugging Face"""
        prompt_parts = []
        for msg in messages:
            if msg["role"] == "system":
                prompt_parts.append(f"System: {msg['content']}")
            elif msg["role"] == "user":
                prompt_parts.append(f"User: {msg['content']}")
            elif msg["role"] == "assistant":
                prompt_parts.append(f"Assistant: {msg['content']}")
        return "\n".join(prompt_parts)

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        if self.use_local:
            # Use local sentence-transformers model
            if self.embedding_model is not None:
                try:
                    import numpy as np
                    embedding = self.embedding_model.encode(text, convert_to_numpy=True)
                    # Ensure it's a list of floats
                    return embedding.tolist()
                except Exception as e:
                    logger.error(f"Local embedding error: {e}")
                    return self._fallback_embedding(text)
            else:
                # Fallback if embedding model failed to load
                return self._fallback_embedding(text)
        elif self.use_runpod or self.use_groq:
            # RunPod and Groq don't have embedding API, use fallback
            return self._fallback_embedding(text)
        elif self.use_huggingface:
            return await self._generate_hf_embedding(text)
        else:
            embedding = await self.embedding_model.aembed_query(text)
            return embedding

    async def _generate_hf_embedding(self, text: str) -> List[float]:
        """Generate embedding using Hugging Face Inference API"""
        try:
            embedding = self.hf_client.feature_extraction(
                model=self.embedding_model_name,
                text=text
            )
            # Handle different response formats
            if isinstance(embedding, list) and len(embedding) > 0:
                return embedding[0] if isinstance(embedding[0], list) else embedding
            elif isinstance(embedding, dict):
                return embedding.get("embeddings", [])
            else:
                return list(embedding) if hasattr(embedding, '__iter__') else []
        except Exception as e:
            logger.error(f"Hugging Face embedding error: {e}")
            # Fallback to simple hash-based embedding if API fails
            return self._fallback_embedding(text)

    def _fallback_embedding(self, text: str) -> List[float]:
        """Fallback embedding using simple hash"""
        import hashlib
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        # Convert to 384-dimensional vector (matching all-MiniLM-L6-v2)
        embedding = []
        for i in range(384):
            byte_index = i % len(hash_bytes)
            value = hash_bytes[byte_index] / 255.0
            embedding.append(value)
        return embedding

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        if self.use_local:
            # Use local sentence-transformers model
            if self.embedding_model is not None:
                try:
                    embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
                    return embeddings.tolist()
                except Exception as e:
                    logger.error(f"Local batch embedding error: {e}")
                    embeddings = []
                    for text in texts:
                        embedding = self._fallback_embedding(text)
                        embeddings.append(embedding)
                    return embeddings
            else:
                # Fallback if embedding model failed to load
                embeddings = []
                for text in texts:
                    embedding = self._fallback_embedding(text)
                    embeddings.append(embedding)
                return embeddings
        elif self.use_runpod or self.use_groq:
            # RunPod and Groq don't have embedding API, use fallback
            embeddings = []
            for text in texts:
                embedding = self._fallback_embedding(text)
                embeddings.append(embedding)
            return embeddings
        elif self.use_huggingface:
            embeddings = []
            for text in texts:
                embedding = await self._generate_hf_embedding(text)
                embeddings.append(embedding)
            return embeddings
        else:
            embeddings = await self.embedding_model.aembed_documents(texts)
            return embeddings

    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        callback: callable
    ):
        """Stream response from LLM with callback for each chunk"""
        if self.use_local:
            # Local model doesn't support streaming, fall back to non-streaming
            response = await self.generate_response(messages)
            await callback(response)
        elif self.use_runpod or self.use_groq or not self.use_huggingface:
            # RunPod, Groq, and OpenAI-compatible endpoints support streaming
            langchain_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    langchain_messages.append(SystemMessage(content=msg["content"]))
                elif msg["role"] == "user":
                    langchain_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    langchain_messages.append(AIMessage(content=msg["content"]))
            
            async for chunk in self.chat_model.astream(langchain_messages):
                if chunk.content:
                    await callback(chunk.content)
        else:
            # Hugging Face streaming is more complex, fall back to non-streaming
            response = await self.generate_response(messages)
            await callback(response)


# Global instance
llm_service = LLMService()
