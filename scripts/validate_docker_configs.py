#!/usr/bin/env python3
"""
Validate Docker configurations script for pre-commit hooks.

Validates that all Dockerfiles and docker-compose configurations are valid.
"""

import os
import sys
import subprocess
from pathlib import Path


def validate_docker_configs() -> bool:
    """Validate all Docker configurations."""
    root_dir = Path(__file__).parent.parent
    errors = []
    
    # Check docker-compose.yml
    compose_file = root_dir / "docker-compose.yml"
    if compose_file.exists():
        print("Validating docker-compose.yml...")
        try:
            result = subprocess.run(
                ["docker-compose", "config"],
                cwd=root_dir,
                capture_output=True,
                text=True,
                check=True
            )
            print("✅ docker-compose.yml is valid")
        except subprocess.CalledProcessError as e:
            errors.append(f"docker-compose.yml validation failed: {e.stderr}")
        except FileNotFoundError:
            print("⚠️  docker-compose not found, skipping validation")
    
    # Check individual Dockerfiles
    servers_dir = root_dir / "servers"
    for server_dir in servers_dir.iterdir():
        if not server_dir.is_dir() or server_dir.name == "template":
            continue
        
        dockerfile = server_dir / "Dockerfile"
        if dockerfile.exists():
            print(f"Validating {server_dir.name}/Dockerfile...")
            try:
                result = subprocess.run(
                    ["docker", "build", "--dry-run", "-f", str(dockerfile), "."],
                    cwd=root_dir,
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"✅ {server_dir.name}/Dockerfile is valid")
            except subprocess.CalledProcessError as e:
                errors.append(f"{server_dir.name}/Dockerfile validation failed: {e.stderr}")
            except FileNotFoundError:
                print("⚠️  docker not found, skipping validation")
    
    if errors:
        print("Docker validation failed:")
        for error in errors:
            print(f"  ❌ {error}")
        return False
    
    print("✅ All Docker configurations are valid")
    return True


if __name__ == "__main__":
    success = validate_docker_configs()
    sys.exit(0 if success else 1)
