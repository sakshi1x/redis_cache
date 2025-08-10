#!/usr/bin/env python3
"""
Redis Setup Script for FastAPI Session Management

This script helps set up Redis for the session management functionality.
"""

import subprocess
import sys
import os
from pathlib import Path


def check_redis_installed():
    """Check if Redis is installed"""
    try:
        result = subprocess.run(['redis-server', '--version'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def install_redis_macos():
    """Install Redis on macOS using Homebrew"""
    print("Installing Redis on macOS...")
    try:
        subprocess.run(['brew', 'install', 'redis'], check=True)
        print("✅ Redis installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Redis. Please install manually:")
        print("   brew install redis")
        return False
    except FileNotFoundError:
        print("❌ Homebrew not found. Please install Homebrew first:")
        print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        return False


def install_redis_ubuntu():
    """Install Redis on Ubuntu/Debian"""
    print("Installing Redis on Ubuntu/Debian...")
    try:
        subprocess.run(['sudo', 'apt-get', 'update'], check=True)
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'redis-server'], check=True)
        print("✅ Redis installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Redis. Please install manually:")
        print("   sudo apt-get install redis-server")
        return False


def start_redis():
    """Start Redis server"""
    print("Starting Redis server...")
    try:
        # Check if Redis is already running
        result = subprocess.run(['redis-cli', 'ping'], 
                              capture_output=True, text=True)
        if result.returncode == 0 and 'PONG' in result.stdout:
            print("✅ Redis is already running!")
            return True
        
        # Start Redis server
        subprocess.run(['redis-server', '--daemonize', 'yes'], check=True)
        print("✅ Redis server started!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to start Redis server")
        return False


def test_redis_connection():
    """Test Redis connection"""
    print("Testing Redis connection...")
    try:
        result = subprocess.run(['redis-cli', 'ping'], 
                              capture_output=True, text=True)
        if result.returncode == 0 and 'PONG' in result.stdout:
            print("✅ Redis connection successful!")
            return True
        else:
            print("❌ Redis connection failed")
            return False
    except subprocess.CalledProcessError:
        print("❌ Redis connection failed")
        return False


def main():
    """Main setup function"""
    print("🚀 Redis Setup for FastAPI Session Management")
    print("=" * 50)
    
    # Check if Redis is installed
    if not check_redis_installed():
        print("Redis is not installed. Installing...")
        
        # Detect OS and install Redis
        if sys.platform == "darwin":  # macOS
            if not install_redis_macos():
                sys.exit(1)
        elif sys.platform.startswith("linux"):  # Linux
            if not install_redis_ubuntu():
                sys.exit(1)
        else:
            print("❌ Unsupported operating system. Please install Redis manually.")
            print("   Visit: https://redis.io/download")
            sys.exit(1)
    else:
        print("✅ Redis is already installed!")
    
    # Start Redis server
    if not start_redis():
        sys.exit(1)
    
    # Test connection
    if not test_redis_connection():
        sys.exit(1)
    
    print("\n🎉 Redis setup completed successfully!")
    print("\nNext steps:")
    print("1. Install Python dependencies: uv sync")
    print("2. Run the FastAPI application: uv run python main.py")
    print("3. Access the API documentation: http://localhost:8000/docs")
    print("\nSession endpoints available:")
    print("- POST /api/v1/login - Create a new session")
    print("- POST /api/v1/logout - Destroy current session")
    print("- GET /api/v1/session/info - Get session information")
    print("- POST /api/v1/ask - Ask questions (now session-aware)")


if __name__ == "__main__":
    main()
