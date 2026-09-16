from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from app.core.database import get_async_db
from app.models.memory import LLMConfiguration, LLMProvider
from app.models.user import User
from typing import Optional, List
from datetime import datetime
import json

router = APIRouter()


@router.get("/llm/config")
async def get_llm_configurations(user_id: int = 1):
    """Get all LLM configurations for a user."""
    async for db in get_async_db():
        result = await db.execute(
            select(LLMConfiguration)
            .where(LLMConfiguration.user_id == user_id)
            .order_by(LLMConfiguration.created_at.desc())
        )
        configurations = result.scalars().all()
        
        # If no local configuration exists, create default local configuration
        local_configs = [c for c in configurations if c.provider == LLMProvider.LOCAL]
        if len(local_configs) == 0:
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
            configurations = [default_config] + list(configurations)
        
        return {
            "configurations": [
                {
                    "id": config.id,
                    "provider": config.provider.value,
                    "model_name": config.model_name,
                    "endpoint": config.endpoint,
                    "api_key": "***" if config.api_key else None,  # Mask API key
                    "temperature": config.temperature,
                    "max_tokens": config.max_tokens,
                    "is_active": config.is_active,
                    "created_at": config.created_at.isoformat(),
                    "updated_at": config.updated_at.isoformat() if config.updated_at else None
                }
                for config in configurations
            ],
            "count": len(configurations)
        }


@router.get("/llm/config/{config_id}")
async def get_llm_configuration(config_id: int, user_id: int = 1):
    """Get a specific LLM configuration."""
    async for db in get_async_db():
        result = await db.execute(
            select(LLMConfiguration)
            .where(LLMConfiguration.id == config_id)
            .where(LLMConfiguration.user_id == user_id)
        )
        config = result.scalar_one_or_none()
        
        if not config:
            raise HTTPException(status_code=404, detail="Configuration not found")
        
        return {
            "id": config.id,
            "provider": config.provider.value,
            "model_name": config.model_name,
            "endpoint": config.endpoint,
            "api_key": "***" if config.api_key else None,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "is_active": config.is_active,
            "created_at": config.created_at.isoformat(),
            "updated_at": config.updated_at.isoformat() if config.updated_at else None
        }


@router.get("/llm/config/active")
async def get_active_llm_configuration(user_id: int = 1):
    """Get the active LLM configuration for a user."""
    async for db in get_async_db():
        result = await db.execute(
            select(LLMConfiguration)
            .where(LLMConfiguration.user_id == user_id)
            .where(LLMConfiguration.is_active == True)
        )
        config = result.scalar_one_or_none()
        
        if not config:
            # Create default local configuration
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
            
            return {
                "id": default_config.id,
                "provider": default_config.provider.value,
                "model_name": default_config.model_name,
                "endpoint": default_config.endpoint,
                "api_key": default_config.api_key,
                "temperature": default_config.temperature,
                "max_tokens": default_config.max_tokens,
                "is_active": default_config.is_active
            }
        
        return {
            "id": config.id,
            "provider": config.provider.value,
            "model_name": config.model_name,
            "endpoint": config.endpoint,
            "api_key": config.api_key,  # Return actual API key for use
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "is_active": config.is_active
        }


@router.post("/llm/config")
async def create_llm_configuration(
    provider: str,
    model_name: str,
    endpoint: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1000,
    user_id: int = 1
):
    """Create a new LLM configuration."""
    async for db in get_async_db():
        # Validate provider
        try:
            provider_enum = LLMProvider(provider.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid provider. Must be one of: {[p.value for p in LLMProvider]}"
            )
        
        # If this is the first configuration, make it active
        result = await db.execute(
            select(LLMConfiguration)
            .where(LLMConfiguration.user_id == user_id)
        )
        existing_count = len(result.scalars().all())
        is_active = existing_count == 0
        
        # Deactivate all other configurations if this one is active
        if is_active:
            await db.execute(
                select(LLMConfiguration)
                .where(LLMConfiguration.user_id == user_id)
                .where(LLMConfiguration.is_active == True)
            )
            configs = result.scalars().all()
            for config in configs:
                config.is_active = False
        
        # Create new configuration
        config = LLMConfiguration(
            user_id=user_id,
            provider=provider_enum,
            model_name=model_name,
            endpoint=endpoint,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            is_active=is_active
        )
        
        db.add(config)
        await db.commit()
        await db.refresh(config)
        
        return {
            "id": config.id,
            "provider": config.provider.value,
            "model_name": config.model_name,
            "endpoint": config.endpoint,
            "api_key": "***" if config.api_key else None,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "is_active": config.is_active,
            "created_at": config.created_at.isoformat()
        }


@router.put("/llm/config/{config_id}")
async def update_llm_configuration(
    config_id: int,
    provider: Optional[str] = None,
    model_name: Optional[str] = None,
    endpoint: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    is_active: Optional[bool] = None,
    user_id: int = 1
):
    """Update an existing LLM configuration."""
    async for db in get_async_db():
        result = await db.execute(
            select(LLMConfiguration)
            .where(LLMConfiguration.id == config_id)
            .where(LLMConfiguration.user_id == user_id)
        )
        config = result.scalar_one_or_none()
        
        if not config:
            raise HTTPException(status_code=404, detail="Configuration not found")
        
        # Update fields if provided
        if provider is not None:
            try:
                config.provider = LLMProvider(provider.lower())
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid provider. Must be one of: {[p.value for p in LLMProvider]}"
                )
        
        if model_name is not None:
            config.model_name = model_name
        
        if endpoint is not None:
            config.endpoint = endpoint
        
        if api_key is not None:
            config.api_key = api_key
        
        if temperature is not None:
            config.temperature = temperature
        
        if max_tokens is not None:
            config.max_tokens = max_tokens
        
        if is_active is not None:
            # If setting to active, deactivate all others
            if is_active:
                result = await db.execute(
                    select(LLMConfiguration)
                    .where(LLMConfiguration.user_id == user_id)
                    .where(LLMConfiguration.id != config_id)
                )
                other_configs = result.scalars().all()
                for other_config in other_configs:
                    other_config.is_active = False
            
            config.is_active = is_active
        
        config.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(config)
        
        return {
            "id": config.id,
            "provider": config.provider.value,
            "model_name": config.model_name,
            "endpoint": config.endpoint,
            "api_key": "***" if config.api_key else None,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "is_active": config.is_active,
            "updated_at": config.updated_at.isoformat()
        }


@router.delete("/llm/config/{config_id}")
async def delete_llm_configuration(config_id: int, user_id: int = 1):
    """Delete an LLM configuration."""
    async for db in get_async_db():
        result = await db.execute(
            select(LLMConfiguration)
            .where(LLMConfiguration.id == config_id)
            .where(LLMConfiguration.user_id == user_id)
        )
        config = result.scalar_one_or_none()
        
        if not config:
            raise HTTPException(status_code=404, detail="Configuration not found")
        
        # Prevent deletion of active configuration
        if config.is_active:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete active configuration. Please activate another configuration first."
            )
        
        await db.delete(config)
        await db.commit()
        
        return {"message": "Configuration deleted successfully"}


@router.post("/llm/config/{config_id}/activate")
async def activate_llm_configuration(config_id: int, user_id: int = 1):
    """Activate a specific LLM configuration."""
    async for db in get_async_db():
        result = await db.execute(
            select(LLMConfiguration)
            .where(LLMConfiguration.id == config_id)
            .where(LLMConfiguration.user_id == user_id)
        )
        config = result.scalar_one_or_none()
        
        if not config:
            raise HTTPException(status_code=404, detail="Configuration not found")
        
        # Deactivate all configurations
        result = await db.execute(
            select(LLMConfiguration)
            .where(LLMConfiguration.user_id == user_id)
        )
        all_configs = result.scalars().all()
        for c in all_configs:
            c.is_active = False
        
        # Activate selected configuration
        config.is_active = True
        config.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(config)
        
        return {
            "message": "Configuration activated successfully",
            "configuration": {
                "id": config.id,
                "provider": config.provider.value,
                "model_name": config.model_name,
                "is_active": True
            }
        }


@router.get("/llm/providers")
async def get_available_providers():
    """Get list of available LLM providers with their details."""
    providers = [
        {
            "value": "local",
            "name": "Local",
            "description": "Local GPT-2 model (free, limited quality)",
            "requires_endpoint": False,
            "requires_api_key": False,
            "default_model": "gpt2"
        },
        {
            "value": "groq",
            "name": "Groq",
            "description": "Groq Cloud (free, fast, high quality)",
            "requires_endpoint": False,
            "requires_api_key": True,
            "default_model": "llama2-70b-4096"
        },
        {
            "value": "runpod",
            "name": "RunPod",
            "description": "RunPod Cloud (paid, flexible)",
            "requires_endpoint": True,
            "requires_api_key": True,
            "default_model": "custom"
        },
        {
            "value": "openai",
            "name": "OpenAI",
            "description": "OpenAI GPT models (paid, high quality)",
            "requires_endpoint": False,
            "requires_api_key": True,
            "default_model": "gpt-4"
        },
        {
            "value": "anthropic",
            "name": "Anthropic",
            "description": "Anthropic Claude models (paid, high quality)",
            "requires_endpoint": False,
            "requires_api_key": True,
            "default_model": "claude-3-opus-20240229"
        },
        {
            "value": "azure",
            "name": "Azure OpenAI",
            "description": "Azure OpenAI Service (paid, enterprise)",
            "requires_endpoint": True,
            "requires_api_key": True,
            "default_model": "gpt-4"
        },
        {
            "value": "custom",
            "name": "Custom",
            "description": "Custom LLM endpoint",
            "requires_endpoint": True,
            "requires_api_key": True,
            "default_model": "custom"
        }
    ]
    
    return {"providers": providers}


@router.post("/llm/config/test")
async def test_llm_configuration(
    provider: str,
    model_name: str,
    endpoint: Optional[str] = None,
    api_key: Optional[str] = None
):
    """Test a LLM configuration without saving it."""
    # This is a placeholder - actual implementation would test the connection
    # For now, we'll just validate the configuration
    
    try:
        provider_enum = LLMProvider(provider.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider. Must be one of: {[p.value for p in LLMProvider]}"
        )
    
    # Validate required fields based on provider
    if provider_enum != LLMProvider.LOCAL:
        if not api_key:
            raise HTTPException(
                status_code=400,
                detail="API key is required for this provider"
            )
        
        if provider_enum in [LLMProvider.RUNPOD, LLMProvider.AZURE, LLMProvider.CUSTOM]:
            if not endpoint:
                raise HTTPException(
                    status_code=400,
                    detail="Endpoint is required for this provider"
                )
    
    # Return success (actual implementation would test the connection)
    return {
        "success": True,
        "message": "Configuration is valid",
        "note": "Connection test not implemented yet"
    }
