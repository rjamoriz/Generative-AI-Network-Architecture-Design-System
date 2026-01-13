"""
Secrets Management Module
Provides abstraction for retrieving secrets from various sources
Supports: Environment Variables, HashiCorp Vault, AWS Secrets Manager
"""
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
import os
import logging

logger = logging.getLogger(__name__)


class SecretsProvider(ABC):
    """Abstract base class for secrets providers"""
    
    @abstractmethod
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieve a secret by key"""
        pass
    
    @abstractmethod
    def get_secrets(self, keys: list[str]) -> Dict[str, Optional[str]]:
        """Retrieve multiple secrets"""
        pass


class EnvironmentSecretsProvider(SecretsProvider):
    """
    Retrieve secrets from environment variables.
    This is the default and simplest approach.
    """
    
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret from environment variable"""
        value = os.getenv(key, default)
        if value:
            logger.debug(f"Retrieved secret '{key}' from environment")
        return value
    
    def get_secrets(self, keys: list[str]) -> Dict[str, Optional[str]]:
        """Get multiple secrets from environment"""
        return {key: self.get_secret(key) for key in keys}


class VaultSecretsProvider(SecretsProvider):
    """
    Retrieve secrets from HashiCorp Vault.
    Requires hvac library: pip install hvac
    """
    
    def __init__(self, vault_url: str, vault_token: str, mount_point: str = "secret"):
        """
        Initialize Vault client
        
        Args:
            vault_url: Vault server URL (e.g., https://vault.example.com:8200)
            vault_token: Vault authentication token
            mount_point: Vault mount point for secrets
        """
        try:
            import hvac
            self.client = hvac.Client(url=vault_url, token=vault_token)
            self.mount_point = mount_point
            
            if not self.client.is_authenticated():
                raise ValueError("Failed to authenticate with Vault")
            
            logger.info(f"Successfully connected to Vault at {vault_url}")
        except ImportError:
            raise ImportError("hvac library required for Vault integration. Install: pip install hvac")
        except Exception as e:
            logger.error(f"Failed to initialize Vault client: {e}")
            raise
    
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get secret from Vault
        
        Args:
            key: Secret path in format 'path/to/secret:field'
            default: Default value if secret not found
        """
        try:
            # Parse key format: path/to/secret:field
            if ':' in key:
                path, field = key.rsplit(':', 1)
            else:
                path = key
                field = 'value'
            
            # Read secret from Vault
            secret = self.client.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point=self.mount_point
            )
            
            value = secret['data']['data'].get(field)
            if value:
                logger.debug(f"Retrieved secret '{key}' from Vault")
            return value or default
            
        except Exception as e:
            logger.warning(f"Failed to retrieve secret '{key}' from Vault: {e}")
            return default
    
    def get_secrets(self, keys: list[str]) -> Dict[str, Optional[str]]:
        """Get multiple secrets from Vault"""
        return {key: self.get_secret(key) for key in keys}


class AWSSecretsProvider(SecretsProvider):
    """
    Retrieve secrets from AWS Secrets Manager.
    Requires boto3 library: pip install boto3
    """
    
    def __init__(self, region_name: str = "us-east-1"):
        """
        Initialize AWS Secrets Manager client
        
        Args:
            region_name: AWS region
        """
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            self.client = boto3.client('secretsmanager', region_name=region_name)
            self.ClientError = ClientError
            logger.info(f"Successfully connected to AWS Secrets Manager in {region_name}")
        except ImportError:
            raise ImportError("boto3 library required for AWS Secrets Manager. Install: pip install boto3")
        except Exception as e:
            logger.error(f"Failed to initialize AWS Secrets Manager client: {e}")
            raise
    
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get secret from AWS Secrets Manager
        
        Args:
            key: Secret name in AWS Secrets Manager
            default: Default value if secret not found
        """
        try:
            response = self.client.get_secret_value(SecretId=key)
            
            # Handle both string and binary secrets
            if 'SecretString' in response:
                value = response['SecretString']
                logger.debug(f"Retrieved secret '{key}' from AWS Secrets Manager")
                return value
            else:
                logger.warning(f"Secret '{key}' is binary, returning default")
                return default
                
        except self.ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.warning(f"Secret '{key}' not found in AWS Secrets Manager")
            else:
                logger.error(f"Error retrieving secret '{key}': {e}")
            return default
        except Exception as e:
            logger.error(f"Unexpected error retrieving secret '{key}': {e}")
            return default
    
    def get_secrets(self, keys: list[str]) -> Dict[str, Optional[str]]:
        """Get multiple secrets from AWS Secrets Manager"""
        return {key: self.get_secret(key) for key in keys}


class SecretsManager:
    """
    Unified secrets manager that can use different providers.
    Provides a single interface for retrieving secrets regardless of source.
    """
    
    def __init__(self, provider: Optional[SecretsProvider] = None):
        """
        Initialize secrets manager
        
        Args:
            provider: Secrets provider to use (defaults to EnvironmentSecretsProvider)
        """
        self.provider = provider or EnvironmentSecretsProvider()
        logger.info(f"Initialized SecretsManager with {self.provider.__class__.__name__}")
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a secret by key"""
        return self.provider.get_secret(key, default)
    
    def get_many(self, keys: list[str]) -> Dict[str, Optional[str]]:
        """Get multiple secrets"""
        return self.provider.get_secrets(keys)
    
    def inject_credentials(self, config: Dict[str, Any], mappings: Dict[str, str]) -> Dict[str, Any]:
        """
        Inject credentials into configuration dictionary
        
        Args:
            config: Configuration dictionary to update
            mappings: Dict mapping config keys to secret keys
                     e.g., {'api_key': 'OPENAI_API_KEY'}
        
        Returns:
            Updated configuration dictionary
        """
        for config_key, secret_key in mappings.items():
            secret_value = self.get(secret_key)
            if secret_value:
                config[config_key] = secret_value
                logger.debug(f"Injected credential for '{config_key}'")
        
        return config


def create_secrets_manager(use_vault: bool = False, 
                          use_aws: bool = False,
                          vault_config: Optional[Dict[str, str]] = None,
                          aws_region: str = "us-east-1") -> SecretsManager:
    """
    Factory function to create appropriate secrets manager
    
    Args:
        use_vault: Use HashiCorp Vault
        use_aws: Use AWS Secrets Manager
        vault_config: Vault configuration (url, token, mount_point)
        aws_region: AWS region for Secrets Manager
    
    Returns:
        Configured SecretsManager instance
    """
    if use_vault:
        if not vault_config:
            raise ValueError("vault_config required when use_vault=True")
        
        provider = VaultSecretsProvider(
            vault_url=vault_config['url'],
            vault_token=vault_config['token'],
            mount_point=vault_config.get('mount_point', 'secret')
        )
        return SecretsManager(provider)
    
    elif use_aws:
        provider = AWSSecretsProvider(region_name=aws_region)
        return SecretsManager(provider)
    
    else:
        # Default to environment variables
        return SecretsManager(EnvironmentSecretsProvider())


# Global secrets manager instance
_secrets_manager: Optional[SecretsManager] = None


def get_secrets_manager() -> SecretsManager:
    """Get global secrets manager instance"""
    global _secrets_manager
    
    if _secrets_manager is None:
        # Initialize with environment variables by default
        _secrets_manager = SecretsManager(EnvironmentSecretsProvider())
    
    return _secrets_manager


def initialize_secrets_manager(use_vault: bool = False,
                               use_aws: bool = False,
                               vault_config: Optional[Dict[str, str]] = None,
                               aws_region: str = "us-east-1"):
    """
    Initialize global secrets manager
    Call this during application startup
    """
    global _secrets_manager
    _secrets_manager = create_secrets_manager(use_vault, use_aws, vault_config, aws_region)
    logger.info("Global secrets manager initialized")
