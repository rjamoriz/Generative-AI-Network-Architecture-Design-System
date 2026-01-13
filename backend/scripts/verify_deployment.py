"""
Deployment Verification Script
Comprehensive checks before deployment
"""
import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple
import importlib.util

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class DeploymentVerifier:
    """Verify deployment readiness"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed: List[str] = []
    
    def check_python_version(self) -> bool:
        """Check Python version"""
        version = sys.version_info
        if version.major == 3 and version.minor >= 11:
            self.passed.append(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
            return True
        else:
            self.errors.append(f"✗ Python version {version.major}.{version.minor} < 3.11")
            return False
    
    def check_required_files(self) -> bool:
        """Check required files exist"""
        backend_dir = Path(__file__).parent.parent
        required_files = [
            "app/main.py",
            "app/core/config.py",
            "app/core/database.py",
            "requirements.txt",
            "Dockerfile",
            ".env.example",
        ]
        
        all_exist = True
        for file_path in required_files:
            full_path = backend_dir / file_path
            if full_path.exists():
                self.passed.append(f"✓ Found: {file_path}")
            else:
                self.errors.append(f"✗ Missing: {file_path}")
                all_exist = False
        
        return all_exist
    
    def check_imports(self) -> bool:
        """Check critical imports"""
        critical_modules = [
            "fastapi",
            "pydantic",
            "sqlalchemy",
            "motor",
            "redis",
            "openai",
            "anthropic",
            "sentence_transformers",
        ]
        
        all_imported = True
        for module_name in critical_modules:
            try:
                importlib.import_module(module_name)
                self.passed.append(f"✓ Import: {module_name}")
            except ImportError as e:
                self.errors.append(f"✗ Cannot import {module_name}: {e}")
                all_imported = False
        
        return all_imported
    
    def check_environment_template(self) -> bool:
        """Check .env.example has required variables"""
        backend_dir = Path(__file__).parent.parent
        env_file = backend_dir / ".env.example"
        
        required_vars = [
            "DATABASE_URL",
            "MONGODB_URL",
            "REDIS_URL",
            "OPENAI_API_KEY",
            "SECRET_KEY",
        ]
        
        if not env_file.exists():
            self.errors.append("✗ .env.example not found")
            return False
        
        content = env_file.read_text()
        all_present = True
        
        for var in required_vars:
            if var in content:
                self.passed.append(f"✓ Env var template: {var}")
            else:
                self.warnings.append(f"⚠ Missing env var template: {var}")
                all_present = False
        
        return all_present
    
    def check_app_structure(self) -> bool:
        """Check application structure"""
        backend_dir = Path(__file__).parent.parent / "app"
        
        required_dirs = [
            "api/routes",
            "core",
            "models",
            "agents",
            "services",
            "validation",
            "db",
        ]
        
        all_exist = True
        for dir_path in required_dirs:
            full_path = backend_dir / dir_path
            if full_path.exists() and full_path.is_dir():
                self.passed.append(f"✓ Directory: app/{dir_path}")
            else:
                self.errors.append(f"✗ Missing directory: app/{dir_path}")
                all_exist = False
        
        return all_exist
    
    def check_docker_files(self) -> bool:
        """Check Docker configuration"""
        backend_dir = Path(__file__).parent.parent.parent
        
        docker_files = [
            "backend/Dockerfile",
            "docker-compose.yml",
            "backend/.dockerignore",
        ]
        
        all_exist = True
        for file_path in docker_files:
            full_path = backend_dir / file_path
            if full_path.exists():
                self.passed.append(f"✓ Docker file: {file_path}")
            else:
                self.errors.append(f"✗ Missing Docker file: {file_path}")
                all_exist = False
        
        return all_exist
    
    async def check_app_imports(self) -> bool:
        """Check main app can be imported"""
        try:
            from app.main import app
            self.passed.append("✓ Main app imports successfully")
            return True
        except Exception as e:
            self.errors.append(f"✗ Cannot import main app: {e}")
            return False
    
    async def check_database_models(self) -> bool:
        """Check database models"""
        try:
            from app.models import (
                NetworkDesign,
                DesignRequirements,
                ValidationResult,
            )
            self.passed.append("✓ Database models import successfully")
            return True
        except Exception as e:
            self.errors.append(f"✗ Cannot import models: {e}")
            return False
    
    async def check_agents(self) -> bool:
        """Check AI agents"""
        try:
            from app.agents import (
                RequirementAnalyzer,
                DesignSynthesizer,
                ValidationAgent,
            )
            self.passed.append("✓ AI agents import successfully")
            return True
        except Exception as e:
            self.errors.append(f"✗ Cannot import agents: {e}")
            return False
    
    async def check_validation_rules(self) -> bool:
        """Check validation rules"""
        try:
            from app.validation.rule_registry import RuleRegistry
            registry = RuleRegistry()
            rule_count = len(registry.get_all_rules())
            
            if rule_count >= 50:
                self.passed.append(f"✓ Validation rules loaded: {rule_count} rules")
                return True
            else:
                self.warnings.append(f"⚠ Only {rule_count} validation rules loaded (expected 50+)")
                return True
        except Exception as e:
            self.errors.append(f"✗ Cannot load validation rules: {e}")
            return False
    
    def check_documentation(self) -> bool:
        """Check documentation exists"""
        root_dir = Path(__file__).parent.parent.parent
        
        docs = [
            "README.md",
            "DEPLOYMENT_GUIDE.md",
            "PROJECT_COMPLETION_REPORT.md",
            "backend/README.md",
        ]
        
        all_exist = True
        for doc in docs:
            full_path = root_dir / doc
            if full_path.exists():
                self.passed.append(f"✓ Documentation: {doc}")
            else:
                self.warnings.append(f"⚠ Missing documentation: {doc}")
        
        return True
    
    async def run_all_checks(self) -> Tuple[bool, Dict]:
        """Run all verification checks"""
        print("\n" + "=" * 80)
        print("DEPLOYMENT VERIFICATION")
        print("=" * 80 + "\n")
        
        checks = [
            ("Python Version", self.check_python_version),
            ("Required Files", self.check_required_files),
            ("Python Imports", self.check_imports),
            ("Environment Template", self.check_environment_template),
            ("App Structure", self.check_app_structure),
            ("Docker Files", self.check_docker_files),
            ("App Imports", self.check_app_imports),
            ("Database Models", self.check_database_models),
            ("AI Agents", self.check_agents),
            ("Validation Rules", self.check_validation_rules),
            ("Documentation", self.check_documentation),
        ]
        
        results = {}
        for check_name, check_func in checks:
            print(f"\nChecking: {check_name}...")
            try:
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()
                results[check_name] = result
            except Exception as e:
                self.errors.append(f"✗ {check_name} check failed: {e}")
                results[check_name] = False
        
        # Print summary
        print("\n" + "=" * 80)
        print("VERIFICATION SUMMARY")
        print("=" * 80 + "\n")
        
        if self.passed:
            print(f"✓ PASSED ({len(self.passed)}):")
            for msg in self.passed[:10]:  # Show first 10
                print(f"  {msg}")
            if len(self.passed) > 10:
                print(f"  ... and {len(self.passed) - 10} more")
        
        if self.warnings:
            print(f"\n⚠ WARNINGS ({len(self.warnings)}):")
            for msg in self.warnings:
                print(f"  {msg}")
        
        if self.errors:
            print(f"\n✗ ERRORS ({len(self.errors)}):")
            for msg in self.errors:
                print(f"  {msg}")
        
        print("\n" + "=" * 80)
        
        all_passed = len(self.errors) == 0
        
        if all_passed:
            print("✓ ALL CHECKS PASSED - Ready for deployment!")
        else:
            print("✗ DEPLOYMENT BLOCKED - Fix errors before deploying")
        
        print("=" * 80 + "\n")
        
        return all_passed, {
            "passed": len(self.passed),
            "warnings": len(self.warnings),
            "errors": len(self.errors),
            "results": results,
        }


async def main():
    """Main verification function"""
    verifier = DeploymentVerifier()
    success, summary = await verifier.run_all_checks()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
