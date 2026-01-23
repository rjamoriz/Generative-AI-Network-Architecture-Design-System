"""
Configuration Management System
Handles all environment variables and secrets without hardcoding credentials
"""
from typing import Optional, List
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Never hardcode credentials - always use environment variables or secrets management.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )
    
    # Application Settings
    app_name: str = "Network Architecture Design System"
    environment: str = Field(default="development", description="Environment: development, staging, production")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    api_version: str = Field(default="v1", description="API version")
    
    # API Server Configuration
    host: str = Field(default="0.0.0.0", description="API host")
    port: int = Field(default=8000, description="API port")
    reload: bool = Field(default=False, description="Auto-reload on code changes")
    workers: int = Field(default=4, description="Number of worker processes")
    
    # Security Settings
    jwt_secret_key: Optional[str] = Field(default=None, description="JWT secret key - MUST be set via environment")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expiration_minutes: int = Field(default=60, description="JWT token expiration in minutes")
    api_key_salt: Optional[str] = Field(default=None, description="API key salt - MUST be set via environment")
    cors_origins: List[str] = Field(default=["http://localhost:3000"], description="CORS allowed origins")
    
    # LLM Provider Settings - OpenAI
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key - injected at runtime")
    openai_model: str = Field(default="gpt-4", description="OpenAI model to use")
    openai_temperature: float = Field(default=0.7, description="OpenAI temperature")
    openai_max_tokens: int = Field(default=4096, description="OpenAI max tokens")
    openai_timeout: int = Field(default=60, description="OpenAI API timeout in seconds")
    openai_max_retries: int = Field(default=3, description="OpenAI API max retries")
    
    # LLM Provider Settings - Anthropic Claude
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key - injected at runtime")
    anthropic_model: str = Field(default="claude-3-5-sonnet-20241022", description="Claude model to use")
    anthropic_temperature: float = Field(default=0.7, description="Claude temperature")
    anthropic_max_tokens: int = Field(default=4096, description="Claude max tokens")
    anthropic_timeout: int = Field(default=60, description="Claude API timeout in seconds")
    
    # PostgreSQL Database Settings
    postgres_host: Optional[str] = Field(default=None, description="PostgreSQL host")
    postgres_port: int = Field(default=5432, description="PostgreSQL port")
    postgres_db: Optional[str] = Field(default=None, description="PostgreSQL database name")
    postgres_user: Optional[str] = Field(default=None, description="PostgreSQL user - injected at runtime")
    postgres_password: Optional[str] = Field(default=None, description="PostgreSQL password - injected at runtime")
    postgres_pool_size: int = Field(default=10, description="PostgreSQL connection pool size")
    postgres_max_overflow: int = Field(default=20, description="PostgreSQL max overflow connections")
    
    # MongoDB Atlas Vector Search Settings
    mongodb_uri: Optional[str] = Field(default=None, description="MongoDB connection URI - injected at runtime")
    mongodb_database: str = Field(default="network_vectors", description="MongoDB database name")
    mongodb_collection: str = Field(default="design_embeddings", description="MongoDB collection for embeddings")
    mongodb_timeout: int = Field(default=10000, description="MongoDB timeout in milliseconds")
    
    # Vector Store Provider
    vector_store_provider: str = Field(default="mongodb", description="Vector store provider: mongodb or astra")
    
    # DataStax Astra DB Settings (Alternative to MongoDB)
    astra_db_id: Optional[str] = Field(default=None, description="Astra DB ID")
    astra_db_region: Optional[str] = Field(default=None, description="Astra DB region")
    astra_db_token: Optional[str] = Field(default=None, description="Astra DB token - injected at runtime")
    astra_db_keyspace: str = Field(default="network_designs", description="Astra DB keyspace")
    astra_db_collection: str = Field(default="design_embeddings", description="Astra DB collection for embeddings")
    
    # Redis Settings
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_password: Optional[str] = Field(default=None, description="Redis password - injected at runtime")
    redis_db: int = Field(default=0, description="Redis database number")
    redis_pool_size: int = Field(default=10, description="Redis connection pool size")
    redis_timeout: int = Field(default=5, description="Redis timeout in seconds")
    
    # Embedding Settings
    embedding_model: str = Field(default="text-embedding-3-large", description="Embedding model")
    embedding_dimensions: int = Field(default=1536, description="Embedding dimensions")
    embedding_batch_size: int = Field(default=100, description="Batch size for embedding generation")
    
    # RAG Settings
    rag_top_k: int = Field(default=5, description="Number of similar designs to retrieve")
    rag_similarity_threshold: float = Field(default=0.75, description="Minimum similarity threshold")
    rag_max_context_tokens: int = Field(default=8000, description="Maximum tokens for RAG context")
    
    # Validation Settings
    validation_threshold: float = Field(default=0.85, description="Minimum validation score for approval")
    max_design_iterations: int = Field(default=10, description="Maximum design refinement iterations")
    
    # MCP Server Settings (External API Connections)
    mcp_legacy_db_url: Optional[str] = Field(default=None, description="Legacy database API URL")
    mcp_legacy_db_api_key: Optional[str] = Field(default=None, description="Legacy DB API key - injected at runtime")
    mcp_web_app_url: Optional[str] = Field(default=None, description="Web application API URL")
    mcp_web_app_api_key: Optional[str] = Field(default=None, description="Web app API key - injected at runtime")
    mcp_timeout: int = Field(default=30, description="MCP server timeout in seconds")
    mcp_max_retries: int = Field(default=3, description="MCP server max retries")
    
    # Salesforce Settings (Technical Validation Source)
    salesforce_enabled: bool = Field(default=False, description="Enable Salesforce integration")
    salesforce_login_url: str = Field(default="https://login.salesforce.com", description="Salesforce OAuth login URL")
    salesforce_instance_url: Optional[str] = Field(default=None, description="Salesforce instance URL")
    salesforce_client_id: Optional[str] = Field(default=None, description="Salesforce Connected App client ID")
    salesforce_client_secret: Optional[str] = Field(default=None, description="Salesforce Connected App client secret")
    salesforce_username: Optional[str] = Field(default=None, description="Salesforce username")
    salesforce_password: Optional[str] = Field(default=None, description="Salesforce password")
    salesforce_security_token: Optional[str] = Field(default=None, description="Salesforce security token")
    salesforce_access_token: Optional[str] = Field(default=None, description="Salesforce access token (if pre-generated)")
    salesforce_api_version: str = Field(default="v60.0", description="Salesforce API version")
    salesforce_validation_soql: str = Field(
        default="SELECT Id, Name FROM Technical_Validation__c LIMIT 100",
        description="SOQL query for validation records"
    )
    
    # Celery Task Queue Settings
    celery_broker_url: Optional[str] = Field(default=None, description="Celery broker URL (Redis)")
    celery_result_backend: Optional[str] = Field(default=None, description="Celery result backend")
    
    # Monitoring and Observability
    langsmith_api_key: Optional[str] = Field(default=None, description="LangSmith API key - injected at runtime")
    langsmith_project: str = Field(default="network-design-ai", description="LangSmith project name")
    enable_tracing: bool = Field(default=False, description="Enable distributed tracing")
    
    # Secrets Management (Optional - for production)
    use_vault: bool = Field(default=False, description="Use HashiCorp Vault for secrets")
    vault_url: Optional[str] = Field(default=None, description="Vault server URL")
    vault_token: Optional[str] = Field(default=None, description="Vault token")
    vault_mount_point: str = Field(default="secret", description="Vault mount point")
    
    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment value"""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    @validator("jwt_secret_key")
    def validate_jwt_secret(cls, v, values):
        """Ensure JWT secret is set in production"""
        if values.get("environment") == "production" and not v:
            raise ValueError("JWT_SECRET_KEY must be set in production environment")
        return v
    
    @property
    def postgres_url(self) -> Optional[str]:
        """Generate PostgreSQL connection URL"""
        if not all([self.postgres_host, self.postgres_user, self.postgres_password, self.postgres_db]):
            return None
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def postgres_url_async(self) -> Optional[str]:
        """Generate async PostgreSQL connection URL"""
        if not all([self.postgres_host, self.postgres_user, self.postgres_password, self.postgres_db]):
            return None
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def redis_url(self) -> str:
        """Generate Redis connection URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == "development"
    
    def get_llm_config(self, provider: str = "openai") -> dict:
        """Get LLM configuration for specified provider"""
        if provider == "openai":
            return {
                "api_key": self.openai_api_key,
                "model": self.openai_model,
                "temperature": self.openai_temperature,
                "max_tokens": self.openai_max_tokens,
                "timeout": self.openai_timeout,
                "max_retries": self.openai_max_retries
            }
        elif provider == "anthropic":
            return {
                "api_key": self.anthropic_api_key,
                "model": self.anthropic_model,
                "temperature": self.anthropic_temperature,
                "max_tokens": self.anthropic_max_tokens,
                "timeout": self.anthropic_timeout
            }
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
    
    def validate_required_credentials(self) -> List[str]:
        """Validate that required credentials are set"""
        missing = []
        
        # Check LLM credentials (at least one provider required)
        if not self.openai_api_key and not self.anthropic_api_key:
            missing.append("At least one LLM provider API key (OPENAI_API_KEY or ANTHROPIC_API_KEY)")
        
        # Check database credentials
        if not self.postgres_host or not self.postgres_user or not self.postgres_password:
            missing.append("PostgreSQL credentials (POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD)")
        
        # Check vector database (at least one required)
        if self.vector_store_provider.lower() == "mongodb" and not self.mongodb_uri:
            missing.append("MongoDB vector store credentials (MONGODB_URI)")
        if self.vector_store_provider.lower() == "astra" and not self.astra_db_token:
            missing.append("DataStax Astra credentials (ASTRA_DB_TOKEN)")
        
        # Check security settings in production
        if self.is_production:
            if not self.jwt_secret_key:
                missing.append("JWT_SECRET_KEY (required in production)")
            if not self.api_key_salt:
                missing.append("API_KEY_SALT (required in production)")
        
        return missing


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    This ensures settings are loaded only once and reused across the application.
    """
    return Settings()


def validate_configuration():
    """
    Validate configuration on application startup.
    Raises exception if required credentials are missing.
    """
    settings = get_settings()
    missing = settings.validate_required_credentials()
    
    if missing:
        error_msg = "Missing required configuration:\n" + "\n".join(f"  - {item}" for item in missing)
        raise ValueError(error_msg)
    
    return settings
