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
import argparse
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
refresh_data = False
frontend_type = 'next'  # Default to Next.js

def print_colored(message, color=Colors.NC):
    """Print colored message to terminal"""
    print(f"{color}{message}{Colors.NC}")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="🍎 Grocery Delivery App Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_app.py                    # Normal startup with Next.js frontend
  python run_app.py -f python         # Use Python Flask frontend
  python run_app.py -f next           # Use Next.js frontend (default)
  python run_app.py -r                # Force refresh all data with Next.js frontend
  python run_app.py -r -f python      # Force refresh data with Python frontend
  python run_app.py --refresh --frontend next  # Force refresh with Next.js frontend
        """
    )
    
    parser.add_argument(
        '-r', '--refresh',
        action='store_true',
        help='Force refresh all data from CSV (truncates existing data)'
    )
    
    parser.add_argument(
        '-f', '--frontend',
        choices=['next', 'python'],
        default='next',
        help='Choose frontend type: "next" (default) or "python"'
    )
    
    return parser.parse_args()

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
        subprocess.run(["pkill", "-f", "node.*next.*dev"], stderr=subprocess.DEVNULL)
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

def check_containers():
    """Check if all required containers are running"""
    try:
        result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
        containers = {
            'mysql': "grocery_mysql" in result.stdout,
            'aerospike': "grocery_aerospike" in result.stdout,
            'aerospike_tools': "grocery_aerospike_tools" in result.stdout
        }
        return containers
    except:
        return {'mysql': False, 'aerospike': False, 'aerospike_tools': False}

def start_containers():
    """Start all containers using docker-compose"""
    print_colored("📦 Starting database containers...", Colors.YELLOW)
    result = subprocess.run(["docker-compose", "up", "-d"], capture_output=True, text=True)
    if result.returncode == 0:
        print_colored("✅ All containers started", Colors.GREEN)
        print_colored("⏳ Waiting for containers to be ready...", Colors.YELLOW)
        
        # Wait longer for Aerospike to initialize
        time.sleep(15)
        
        # Check container status
        containers = check_containers()
        for name, running in containers.items():
            if running:
                print_colored(f"✅ {name.replace('_', ' ').title()} container is running", Colors.GREEN)
            else:
                print_colored(f"⚠️  {name.replace('_', ' ').title()} container may not be ready", Colors.YELLOW)
        
        return True
    else:
        print_colored(f"❌ Failed to start containers: {result.stderr}", Colors.RED)
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

def install_frontend_dependencies(frontend_type):
    """Install frontend dependencies based on type"""
    if frontend_type == 'next':
        # Check if Node.js is installed
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                print_colored("❌ Node.js is not installed. Please install Node.js first.", Colors.RED)
                print_colored("Visit: https://nodejs.org/en/download/", Colors.YELLOW)
                return False
        except FileNotFoundError:
            print_colored("❌ Node.js is not installed. Please install Node.js first.", Colors.RED)
            print_colored("Visit: https://nodejs.org/en/download/", Colors.YELLOW)
            return False
        
        # Check if npm is installed
        try:
            result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                print_colored("❌ npm is not installed. Please install npm first.", Colors.RED)
                return False
        except FileNotFoundError:
            print_colored("❌ npm is not installed. Please install npm first.", Colors.RED)
            return False
        
        # Check if Next.js dependencies are installed
        frontend_dir = Path("frontend-next")
        node_modules = frontend_dir / "node_modules"
        
        if not node_modules.exists():
            print_colored("📦 Installing Next.js dependencies...", Colors.YELLOW)
            result = subprocess.run(['npm', 'install'], cwd=frontend_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                print_colored("✅ Next.js dependencies installed", Colors.GREEN)
                return True
            else:
                print_colored(f"❌ Failed to install Next.js dependencies: {result.stderr}", Colors.RED)
                return False
        return True
    else:
        # Python frontend dependencies
        try:
            import requests
            return True
        except ImportError:
            print_colored("📦 Installing Python frontend dependencies...", Colors.YELLOW)
            result = subprocess.run([sys.executable, "-m", "pip", "install", "requests"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print_colored("✅ Python frontend dependencies installed", Colors.GREEN)
                return True
            else:
                print_colored(f"❌ Failed to install Python frontend dependencies: {result.stderr}", Colors.RED)
                return False

def start_backend():
    """Start backend application"""
    global backend_process
    
    print_colored("🔧 Starting backend API server...", Colors.BLUE)
    
    # Change to backend directory and start the app
    backend_dir = Path("backend")
    backend_log = Path("backend.log")
    
    # Build command with refresh flag if needed
    cmd = [sys.executable, "app.py"]
    if refresh_data:
        cmd.append("--refresh")
        print_colored("🔄 Backend will refresh all data from CSV", Colors.YELLOW)
    
    with open(backend_log, 'w') as log_file:
        backend_process = subprocess.Popen(
            cmd,
            cwd=backend_dir,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True,
            env={**os.environ, 'PYTHONPATH': '.'}
        )
    
    # Wait for backend to start with appropriate messaging
    if refresh_data:
        print_colored("⏳ Waiting for backend to start (refreshing data from CSV...)...", Colors.YELLOW)
        time.sleep(8)
    else:
        print_colored("⏳ Waiting for backend to start...", Colors.YELLOW)
        time.sleep(5)
    
    # Check if backend is responding
    max_retries = 12
    for retry in range(max_retries):
        try:
            response = requests.get("http://localhost:5001/api/categories", timeout=2)
            if response.status_code == 200:
                print_colored("✅ Backend API started successfully on http://localhost:5001", Colors.GREEN)
                return True
        except requests.RequestException:
            if retry < max_retries - 1:
                if refresh_data:
                    print_colored(f"⏳ Backend still loading data... (attempt {retry + 1}/{max_retries})", Colors.YELLOW)
                    time.sleep(8)
                else:
                    print_colored(f"⏳ Backend still starting... (attempt {retry + 1}/{max_retries})", Colors.YELLOW)
                    time.sleep(5)
    
    print_colored("❌ Backend failed to start. Check backend.log for details.", Colors.RED)
    print_colored("📄 Check backend.log for details:", Colors.RED)
    print_colored("   tail -f backend.log", Colors.YELLOW)
    return False

def start_frontend(frontend_type):
    """Start frontend application based on type"""
    global frontend_process
    
    if frontend_type == 'next':
        print_colored("🌐 Starting Next.js frontend application...", Colors.BLUE)
        
        frontend_log = Path("frontend.log")
        frontend_dir = Path("frontend-next")
        
        with open(frontend_log, 'w') as log_file:
            frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=frontend_dir,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                text=True
            )
        
        # Wait for Next.js to start
        print_colored("⏳ Waiting for Next.js to start...", Colors.YELLOW)
        time.sleep(8)
        
        # Check if Next.js is responding
        frontend_url = "http://localhost:4000"
        max_retries = 10
        for retry in range(max_retries):
            try:
                response = requests.get(frontend_url, timeout=2)
                if response.status_code == 200:
                    print_colored(f"✅ Next.js frontend started successfully on {frontend_url}", Colors.GREEN)
                    return True
            except requests.RequestException:
                if retry < max_retries - 1:
                    print_colored(f"⏳ Next.js still starting... (attempt {retry + 1}/{max_retries})", Colors.YELLOW)
                    time.sleep(3)
        
        print_colored("❌ Next.js frontend failed to start. Check frontend.log for details.", Colors.RED)
        return False
    else:
        print_colored("🌐 Starting Python Flask frontend application...", Colors.BLUE)
        
        frontend_log = Path("frontend.log")
        
        with open(frontend_log, 'w') as log_file:
            frontend_process = subprocess.Popen(
                [sys.executable, "frontend_app.py"],
                cwd="frontend",
                stdout=log_file,
                stderr=subprocess.STDOUT,
                text=True
            )
        
        # Wait for Flask to start
        print_colored("⏳ Waiting for Flask frontend to start...", Colors.YELLOW)
        time.sleep(3)
        
        # Check if Flask is responding
        frontend_url = "http://localhost:5000"
        for _ in range(10):  # Try for 10 seconds
            try:
                response = requests.get(frontend_url, timeout=1)
                if response.status_code == 200:
                    print_colored(f"✅ Flask frontend started successfully on {frontend_url}", Colors.GREEN)
                    return True
            except requests.RequestException:
                time.sleep(1)
        
        print_colored("❌ Flask frontend failed to start. Check frontend.log for details.", Colors.RED)
        return False

def main():
    """Main function to orchestrate application startup"""
    global refresh_data, frontend_type
    
    # Parse arguments
    args = parse_arguments()
    refresh_data = args.refresh
    frontend_type = args.frontend
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print_colored("🚀 Starting Grocery Delivery App...", Colors.GREEN)
    
    if refresh_data:
        print_colored("🔄 Data refresh mode enabled - will reload all data from CSV", Colors.YELLOW)
    
    print_colored(f"📱 Frontend: {frontend_type.upper()}", Colors.BLUE)
    
    # Check Docker
    if not check_docker():
        print_colored("❌ Docker is not running. Please start Docker first.", Colors.RED)
        sys.exit(1)
    
    # Check/Start all containers
    containers = check_containers()
    if not all(containers.values()):
        if not start_containers():
            sys.exit(1)
    else:
        print_colored("✅ All containers are already running", Colors.GREEN)
        for name, running in containers.items():
            if running:
                print_colored(f"✅ {name.replace('_', ' ').title()} container is running", Colors.GREEN)
    
    # Install dependencies
    if not install_backend_dependencies():
        sys.exit(1)
    
    if not install_frontend_dependencies(frontend_type):
        sys.exit(1)
    
    # Start backend
    if not start_backend():
        cleanup_processes()
        sys.exit(1)
    
    # Start frontend
    if not start_frontend(frontend_type):
        cleanup_processes()
        sys.exit(1)
    
    # Success message
    print_colored("🎉 All applications are running successfully!", Colors.GREEN)
    print_colored("┌─────────────────────────────────────────────────────┐", Colors.BLUE)
    print_colored("│                                                     │", Colors.BLUE)
    
    if frontend_type == 'next':
        print_colored("│  🌐 Frontend:  http://localhost:4000 (Next.js)     │", Colors.BLUE)
    else:
        print_colored("│  🌐 Frontend:  http://localhost:5000 (Flask)       │", Colors.BLUE)
    
    print_colored("│  🔧 Backend:   http://localhost:5001               │", Colors.BLUE)
    print_colored("│  🐳 MySQL:     localhost:3306                      │", Colors.BLUE)
    print_colored("│  🚀 Aerospike: localhost:3000                      │", Colors.BLUE)
    print_colored("│                                                     │", Colors.BLUE)
    print_colored("│  📄 Backend logs: tail -f backend.log              │", Colors.BLUE)
    print_colored("│  📄 Frontend logs: tail -f frontend.log            │", Colors.BLUE)
    print_colored("│                                                     │", Colors.BLUE)
    
    if refresh_data:
        print_colored("│  🔄 Data was refreshed from CSV                     │", Colors.BLUE)
        print_colored("│                                                     │", Colors.BLUE)
    
    print_colored(f"│  Frontend Type: {frontend_type.upper():<31}│", Colors.BLUE)
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