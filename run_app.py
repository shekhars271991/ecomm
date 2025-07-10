#!/usr/bin/env python3
"""
Cross-platform script to run both backend and frontend applications
"""

import subprocess
import sys
import os
import time
import signal
import requests
import threading
from pathlib import Path

# Colors for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

# Global variables to track processes
backend_process = None
frontend_process = None

def print_colored(message, color=Colors.NC):
    """Print colored message to terminal"""
    print(f"{color}{message}{Colors.NC}")

def cleanup_processes():
    """Clean up background processes"""
    global backend_process, frontend_process
    
    print_colored("\n⏹️  Shutting down applications...", Colors.YELLOW)
    
    # Terminate backend process
    if backend_process and backend_process.poll() is None:
        print_colored("Stopping backend...", Colors.BLUE)
        backend_process.terminate()
        try:
            backend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_process.kill()
    
    # Terminate frontend process
    if frontend_process and frontend_process.poll() is None:
        print_colored("Stopping frontend...", Colors.BLUE)
        frontend_process.terminate()
        try:
            frontend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            frontend_process.kill()
    
    # Kill any remaining processes
    try:
        subprocess.run(["pkill", "-f", "python.*backend/app.py"], stderr=subprocess.DEVNULL)
        subprocess.run(["pkill", "-f", "python.*frontend/frontend_app.py"], stderr=subprocess.DEVNULL)
    except:
        pass
    
    print_colored("✅ Applications stopped successfully!", Colors.GREEN)

def signal_handler(signum, frame):
    """Handle interrupt signals"""
    cleanup_processes()
    sys.exit(0)

def check_docker():
    """Check if Docker is running"""
    try:
        result = subprocess.run(["docker", "info"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def check_mysql_container():
    """Check if MySQL container is running"""
    try:
        result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
        return "grocery_mysql" in result.stdout
    except:
        return False

def start_mysql_container():
    """Start MySQL container using docker-compose"""
    print_colored("📦 Starting MySQL container...", Colors.YELLOW)
    result = subprocess.run(["docker-compose", "up", "-d"], capture_output=True, text=True)
    if result.returncode == 0:
        print_colored("✅ MySQL container started", Colors.GREEN)
        time.sleep(5)
        return True
    else:
        print_colored(f"❌ Failed to start MySQL container: {result.stderr}", Colors.RED)
        return False

def install_backend_dependencies():
    """Install backend dependencies"""
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print_colored("❌ Backend directory not found", Colors.RED)
        return False
    
    requirements_file = backend_dir / "requirements.txt"
    if not requirements_file.exists():
        print_colored("❌ Backend requirements.txt not found", Colors.RED)
        return False
    
    venv_marker = backend_dir / ".venv_created"
    if venv_marker.exists():
        return True
    
    print_colored("📦 Installing backend dependencies...", Colors.YELLOW)
    result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        venv_marker.touch()
        print_colored("✅ Backend dependencies installed", Colors.GREEN)
        return True
    else:
        print_colored(f"❌ Failed to install backend dependencies: {result.stderr}", Colors.RED)
        return False

def install_frontend_dependencies():
    """Install frontend dependencies"""
    try:
        import requests
        return True
    except ImportError:
        print_colored("📦 Installing frontend dependencies...", Colors.YELLOW)
        result = subprocess.run([sys.executable, "-m", "pip", "install", "requests"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print_colored("✅ Frontend dependencies installed", Colors.GREEN)
            return True
        else:
            print_colored(f"❌ Failed to install frontend dependencies: {result.stderr}", Colors.RED)
            return False

def start_backend():
    """Start backend application"""
    global backend_process
    
    print_colored("🔧 Starting backend API server...", Colors.BLUE)
    
    # Change to backend directory and start the app
    backend_dir = Path("backend")
    backend_log = Path("backend.log")
    
    with open(backend_log, 'w') as log_file:
        backend_process = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd=backend_dir,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True
        )
    
    # Wait for backend to start
    print_colored("⏳ Waiting for backend to start...", Colors.YELLOW)
    time.sleep(3)
    
    # Check if backend is responding
    for _ in range(10):  # Try for 10 seconds
        try:
            response = requests.get("http://localhost:5001/api/categories", timeout=1)
            if response.status_code == 200:
                print_colored("✅ Backend API started successfully on http://localhost:5001", Colors.GREEN)
                return True
        except requests.RequestException:
            time.sleep(1)
    
    print_colored("❌ Backend failed to start. Check backend.log for details.", Colors.RED)
    return False

def start_frontend():
    """Start frontend application"""
    global frontend_process
    
    print_colored("🌐 Starting frontend application...", Colors.BLUE)
    
    frontend_log = Path("frontend.log")
    
    with open(frontend_log, 'w') as log_file:
        frontend_process = subprocess.Popen(
            [sys.executable, "frontend_app.py"],
            cwd="frontend",
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True
        )
    
    # Wait for frontend to start
    print_colored("⏳ Waiting for frontend to start...", Colors.YELLOW)
    time.sleep(3)
    
    # Check if frontend is responding
    for _ in range(10):  # Try for 10 seconds
        try:
            response = requests.get("http://localhost:5000", timeout=1)
            if response.status_code == 200:
                print_colored("✅ Frontend started successfully on http://localhost:5000", Colors.GREEN)
                return True
        except requests.RequestException:
            time.sleep(1)
    
    print_colored("❌ Frontend failed to start. Check frontend.log for details.", Colors.RED)
    return False

def main():
    """Main function to orchestrate application startup"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print_colored("🚀 Starting Grocery Delivery App...", Colors.GREEN)
    
    # Check Docker
    if not check_docker():
        print_colored("❌ Docker is not running. Please start Docker first.", Colors.RED)
        sys.exit(1)
    
    # Check/Start MySQL container
    if not check_mysql_container():
        if not start_mysql_container():
            sys.exit(1)
    else:
        print_colored("✅ MySQL container is already running", Colors.GREEN)
    
    # Install dependencies
    if not install_backend_dependencies():
        sys.exit(1)
    
    if not install_frontend_dependencies():
        sys.exit(1)
    
    # Start backend
    if not start_backend():
        cleanup_processes()
        sys.exit(1)
    
    # Start frontend
    if not start_frontend():
        cleanup_processes()
        sys.exit(1)
    
    # Success message
    print_colored("🎉 All applications are running successfully!", Colors.GREEN)
    print_colored("┌─────────────────────────────────────────────────────┐", Colors.BLUE)
    print_colored("│                                                     │", Colors.BLUE)
    print_colored("│  🌐 Frontend:  http://localhost:5000               │", Colors.BLUE)
    print_colored("│  🔧 Backend:   http://localhost:5001               │", Colors.BLUE)
    print_colored("│  🐳 MySQL:     localhost:3306                      │", Colors.BLUE)
    print_colored("│                                                     │", Colors.BLUE)
    print_colored("│  📄 Backend logs: tail -f backend.log              │", Colors.BLUE)
    print_colored("│  📄 Frontend logs: tail -f frontend.log            │", Colors.BLUE)
    print_colored("│                                                     │", Colors.BLUE)
    print_colored("│  Press Ctrl+C to stop all applications             │", Colors.BLUE)
    print_colored("│                                                     │", Colors.BLUE)
    print_colored("└─────────────────────────────────────────────────────┘", Colors.BLUE)
    
    try:
        # Wait for processes to complete
        while True:
            if backend_process and backend_process.poll() is not None:
                print_colored("❌ Backend process has stopped!", Colors.RED)
                break
            if frontend_process and frontend_process.poll() is not None:
                print_colored("❌ Frontend process has stopped!", Colors.RED)
                break
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup_processes()

if __name__ == "__main__":
    main() 