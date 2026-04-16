"""
Docker sandbox for isolated test execution.

Executes generated tests in an isolated, resource-constrained Docker container.
"""

import os
import subprocess
from typing import Dict


def run_test_in_sandbox(
    repo_path: str,
    test_file_content: str,
    test_filename: str,
    language: str,
    buggy_commit: str,
) -> Dict:
    """
    Execute a test in an isolated Docker sandbox.
    
    Args:
        repo_path: Absolute path to repository on host
        test_file_content: Raw test file content as string
        test_filename: Filename where test should be written
        language: "python" or "java"
        buggy_commit: Git commit SHA to checkout
        
    Returns:
        Dictionary with keys:
        - "stdout": str - combined stdout and stderr
        - "stderr": str - stderr only
        - "exit_code": int - process exit code
    """
    
    # Create a temporary directory for test file
    test_dir = os.path.join(repo_path, "_asqa_tests")
    os.makedirs(test_dir, exist_ok=True)
    test_path = os.path.join(test_dir, test_filename)
    
    try:
        with open(test_path, "w") as f:
            f.write(test_file_content)
    except Exception as e:
        return {
            "stdout": "",
            "stderr": f"Failed to write test file: {str(e)}",
            "exit_code": 1,
        }
    
    # Get configuration
    timeout = int(os.getenv("ASQA_DOCKER_TIMEOUT", "120"))
    mem_limit = os.getenv("ASQA_DOCKER_MEM_LIMIT", "512m")
    
    # Select image and command based on language
    if language == "python":
        image_name = "python:3.11-slim"
        # Install pytest and checkout code, then run test
        setup_commands = [
            "pip install --no-cache-dir pytest pytest-timeout git",
            f"git checkout {buggy_commit} 2>/dev/null || echo 'Checkout skipped'",
            f"pytest _asqa_tests/{test_filename} -v --tb=short",
        ]
        command = " && ".join(setup_commands)
    elif language == "java":
        image_name = "maven:3.8-openjdk-11"
        # Checkout code and run Maven
        setup_commands = [
            "apt-get update && apt-get install -y git",
            f"git checkout {buggy_commit} 2>/dev/null || echo 'Checkout skipped'",
            "mvn -f _asqa_tests/pom.xml test",
        ]
        command = " && ".join(setup_commands)
    else:
        return {
            "stdout": "",
            "stderr": f"Unsupported language: {language}",
            "exit_code": 1,
        }
    
    try:
        # Run docker container using CLI with timeout
        docker_cmd = [
            "docker", "run", "--rm",
            "-v", f"{repo_path}:/repo",
            "-w", "/repo",
            f"--memory={mem_limit}",
            "--network=none",
            f"--entrypoint=bash",
            image_name,
            "-c", command,
        ]
        
        # Use subprocess with timeout
        result = subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
        }
        
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": f"Test execution timed out after {timeout} seconds",
            "exit_code": 124,  # Standard timeout exit code
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": f"Docker execution failed: {str(e)}",
            "exit_code": 127,
        }
