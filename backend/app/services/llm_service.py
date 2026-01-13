"""
LLM Service - Abstraction layer for LLM providers
Handles API connections to OpenAI and Anthropic without hardcoding credentials
"""
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
import logging
from enum import Enum

from app.core.config import get_settings
from app.core.secrets import get_secrets_manager

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients"""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize LLM client
        
        Args:
            api_key: API key (injected at runtime, never hardcoded)
            **kwargs: Additional provider-specific configuration
        """
        if not api_key:
            raise ValueError("API key must be provided (injected from environment or secrets manager)")
        
        self.api_key = api_key
        self.config = kwargs
        logger.info(f"Initialized {self.__class__.__name__}")
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text completion"""
        pass
    
    @abstractmethod
    async def generate_structured(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate structured output conforming to schema"""
        pass
    
    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """Generate embeddings for text"""
        pass


class OpenAIClient(BaseLLMClient):
    """
    OpenAI API client with credential injection
    Requires: pip install openai
    """
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize OpenAI client"""
        super().__init__(api_key, **kwargs)
        
        try:
            from openai import AsyncOpenAI
            
            # Initialize client with injected API key
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                timeout=kwargs.get('timeout', 60),
                max_retries=kwargs.get('max_retries', 3)
            )
            
            self.model = kwargs.get('model', 'gpt-4')
            self.temperature = kwargs.get('temperature', 0.7)
            self.max_tokens = kwargs.get('max_tokens', 4096)
            
            logger.info(f"OpenAI client initialized with model: {self.model}")
            
        except ImportError:
            raise ImportError("openai library required. Install: pip install openai")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text completion using OpenAI
        
        Args:
            prompt: Input prompt
            **kwargs: Override default parameters
        
        Returns:
            Generated text
        """
        try:
            response = await self.client.chat.completions.create(
                model=kwargs.get('model', self.model),
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get('temperature', self.temperature),
                max_tokens=kwargs.get('max_tokens', self.max_tokens)
            )
            
            content = response.choices[0].message.content
            logger.debug(f"Generated {len(content)} characters from OpenAI")
            return content
            
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            raise
    
    async def generate_structured(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Generate structured output using OpenAI function calling
        
        Args:
            prompt: Input prompt
            schema: JSON schema for structured output
            **kwargs: Override default parameters
        
        Returns:
            Structured output as dictionary
        """
        try:
            response = await self.client.chat.completions.create(
                model=kwargs.get('model', self.model),
                messages=[{"role": "user", "content": prompt}],
                functions=[{
                    "name": "structured_output",
                    "description": "Generate structured output",
                    "parameters": schema
                }],
                function_call={"name": "structured_output"},
                temperature=kwargs.get('temperature', self.temperature)
            )
            
            import json
            result = json.loads(response.choices[0].message.function_call.arguments)
            logger.debug(f"Generated structured output from OpenAI")
            return result
            
        except Exception as e:
            logger.error(f"OpenAI structured generation error: {e}")
            raise
    
    async def embed(self, text: str, model: str = "text-embedding-3-large") -> List[float]:
        """
        Generate embeddings using OpenAI
        
        Args:
            text: Text to embed
            model: Embedding model to use
        
        Returns:
            Embedding vector
        """
        try:
            response = await self.client.embeddings.create(
                model=model,
                input=text
            )
            
            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding of dimension {len(embedding)}")
            return embedding
            
        except Exception as e:
            logger.error(f"OpenAI embedding error: {e}")
            raise


class AnthropicClient(BaseLLMClient):
    """
    Anthropic Claude API client with credential injection
    Requires: pip install anthropic
    """
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize Anthropic client"""
        super().__init__(api_key, **kwargs)
        
        try:
            from anthropic import AsyncAnthropic
            
            # Initialize client with injected API key
            self.client = AsyncAnthropic(
                api_key=self.api_key,
                timeout=kwargs.get('timeout', 60)
            )
            
            self.model = kwargs.get('model', 'claude-3-5-sonnet-20241022')
            self.temperature = kwargs.get('temperature', 0.7)
            self.max_tokens = kwargs.get('max_tokens', 4096)
            
            logger.info(f"Anthropic client initialized with model: {self.model}")
            
        except ImportError:
            raise ImportError("anthropic library required. Install: pip install anthropic")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text completion using Claude
        
        Args:
            prompt: Input prompt
            **kwargs: Override default parameters
        
        Returns:
            Generated text
        """
        try:
            response = await self.client.messages.create(
                model=kwargs.get('model', self.model),
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                temperature=kwargs.get('temperature', self.temperature),
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text
            logger.debug(f"Generated {len(content)} characters from Claude")
            return content
            
        except Exception as e:
            logger.error(f"Anthropic generation error: {e}")
            raise
    
    async def generate_structured(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Generate structured output using Claude
        Note: Claude doesn't have native function calling, so we use prompt engineering
        
        Args:
            prompt: Input prompt
            schema: JSON schema for structured output
            **kwargs: Override default parameters
        
        Returns:
            Structured output as dictionary
        """
        try:
            import json
            
            # Enhance prompt with schema instructions
            structured_prompt = f"""{prompt}

Please respond with a valid JSON object that conforms to this schema:
{json.dumps(schema, indent=2)}

Return ONLY the JSON object, no additional text."""
            
            response = await self.client.messages.create(
                model=kwargs.get('model', self.model),
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                temperature=kwargs.get('temperature', self.temperature),
                messages=[{"role": "user", "content": structured_prompt}]
            )
            
            content = response.content[0].text
            result = json.loads(content)
            logger.debug(f"Generated structured output from Claude")
            return result
            
        except Exception as e:
            logger.error(f"Anthropic structured generation error: {e}")
            raise
    
    async def embed(self, text: str) -> List[float]:
        """
        Claude doesn't provide embeddings API
        This method raises NotImplementedError
        """
        raise NotImplementedError("Anthropic Claude does not provide embeddings API. Use OpenAI or sentence-transformers.")


class LLMService:
    """
    Unified LLM service that manages multiple providers
    Handles credential injection and provider fallback
    """
    
    def __init__(self, 
                 primary_provider: LLMProvider = LLMProvider.OPENAI,
                 fallback_provider: Optional[LLMProvider] = LLMProvider.ANTHROPIC):
        """
        Initialize LLM service with providers
        
        Args:
            primary_provider: Primary LLM provider to use
            fallback_provider: Fallback provider if primary fails
        """
        self.settings = get_settings()
        self.secrets_manager = get_secrets_manager()
        
        self.primary_provider = primary_provider
        self.fallback_provider = fallback_provider
        
        # Initialize clients with injected credentials
        self.clients: Dict[LLMProvider, BaseLLMClient] = {}
        self._initialize_clients()
        
        logger.info(f"LLM Service initialized with primary: {primary_provider}, fallback: {fallback_provider}")
    
    def _initialize_clients(self):
        """Initialize LLM clients with credentials from config/secrets"""
        
        # Initialize OpenAI client if API key available
        if self.settings.openai_api_key:
            try:
                self.clients[LLMProvider.OPENAI] = OpenAIClient(
                    api_key=self.settings.openai_api_key,
                    model=self.settings.openai_model,
                    temperature=self.settings.openai_temperature,
                    max_tokens=self.settings.openai_max_tokens,
                    timeout=self.settings.openai_timeout,
                    max_retries=self.settings.openai_max_retries
                )
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        
        # Initialize Anthropic client if API key available
        if self.settings.anthropic_api_key:
            try:
                self.clients[LLMProvider.ANTHROPIC] = AnthropicClient(
                    api_key=self.settings.anthropic_api_key,
                    model=self.settings.anthropic_model,
                    temperature=self.settings.anthropic_temperature,
                    max_tokens=self.settings.anthropic_max_tokens,
                    timeout=self.settings.anthropic_timeout
                )
                logger.info("Anthropic client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")
        
        if not self.clients:
            raise ValueError("No LLM providers configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY")
    
    def _get_client(self, provider: Optional[LLMProvider] = None) -> BaseLLMClient:
        """Get LLM client for specified provider"""
        provider = provider or self.primary_provider
        
        if provider not in self.clients:
            raise ValueError(f"Provider {provider} not configured")
        
        return self.clients[provider]
    
    async def generate(self, 
                      prompt: str, 
                      provider: Optional[LLMProvider] = None,
                      use_fallback: bool = True,
                      **kwargs) -> str:
        """
        Generate text completion with automatic fallback
        
        Args:
            prompt: Input prompt
            provider: Specific provider to use (defaults to primary)
            use_fallback: Use fallback provider if primary fails
            **kwargs: Additional generation parameters
        
        Returns:
            Generated text
        """
        provider = provider or self.primary_provider
        
        try:
            client = self._get_client(provider)
            return await client.generate(prompt, **kwargs)
            
        except Exception as e:
            logger.error(f"Generation failed with {provider}: {e}")
            
            # Try fallback if enabled
            if use_fallback and self.fallback_provider and self.fallback_provider != provider:
                logger.info(f"Attempting fallback to {self.fallback_provider}")
                try:
                    fallback_client = self._get_client(self.fallback_provider)
                    return await fallback_client.generate(prompt, **kwargs)
                except Exception as fallback_error:
                    logger.error(f"Fallback generation failed: {fallback_error}")
            
            raise
    
    async def generate_structured(self,
                                 prompt: str,
                                 schema: Dict[str, Any],
                                 provider: Optional[LLMProvider] = None,
                                 use_fallback: bool = True,
                                 **kwargs) -> Dict[str, Any]:
        """
        Generate structured output with automatic fallback
        
        Args:
            prompt: Input prompt
            schema: JSON schema for output
            provider: Specific provider to use
            use_fallback: Use fallback provider if primary fails
            **kwargs: Additional generation parameters
        
        Returns:
            Structured output dictionary
        """
        provider = provider or self.primary_provider
        
        try:
            client = self._get_client(provider)
            return await client.generate_structured(prompt, schema, **kwargs)
            
        except Exception as e:
            logger.error(f"Structured generation failed with {provider}: {e}")
            
            # Try fallback if enabled
            if use_fallback and self.fallback_provider and self.fallback_provider != provider:
                logger.info(f"Attempting fallback to {self.fallback_provider}")
                try:
                    fallback_client = self._get_client(self.fallback_provider)
                    return await fallback_client.generate_structured(prompt, schema, **kwargs)
                except Exception as fallback_error:
                    logger.error(f"Fallback structured generation failed: {fallback_error}")
            
            raise
    
    async def embed(self, text: str) -> List[float]:
        """
        Generate embeddings (uses OpenAI only)
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector
        """
        if LLMProvider.OPENAI not in self.clients:
            raise ValueError("OpenAI client required for embeddings")
        
        client = self._get_client(LLMProvider.OPENAI)
        return await client.embed(text)


# Dependency injection function for FastAPI
def get_llm_service() -> LLMService:
    """Get LLM service instance for dependency injection"""
    return LLMService()
