#!/usr/bin/env python3
"""
RCCM Quiz App Startup Script
Handles port conflicts and ensures clean startup
"""

import os
import subprocess
import time
import socket
import sys

def check_port_available(port):
    """Check if a port is available"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def find_and_kill_process_on_port(port):
    """Find and kill process using specified port"""
    try:
        # Use ss to find process using the port
        result = subprocess.run(['ss', '-tlnp'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        for line in lines:
            if f':{port}' in line and 'users:' in line:
                # Extract PID from ss output
                import re
                pid_match = re.search(r'pid=(\d+)', line)
                if pid_match:
                    pid = int(pid_match.group(1))
                    print(f"Found process {pid} using port {port}")
                    
                    # Kill the process
                    subprocess.run(['kill', str(pid)], check=False)
                    time.sleep(2)
                    
                    # Verify it's dead
                    if check_port_available(port):
                        print(f"Successfully freed port {port}")
                        return True
                    else:
                        print(f"Port {port} still in use, trying force kill...")
                        subprocess.run(['kill', '-9', str(pid)], check=False)
                        time.sleep(2)
                        return check_port_available(port)
        return True
    except Exception as e:
        print(f"Error checking/killing process: {e}")
        return False

def start_flask_app():
    """Start the Flask application with proper error handling"""
    print("🚀 Starting RCCM Quiz Application...")
    
    # Default port
    port = int(os.environ.get('PORT', 5005))
    
    # Check if port is available
    if not check_port_available(port):
        print(f"⚠️ Port {port} is in use, attempting to free it...")
        if not find_and_kill_process_on_port(port):
            print(f"❌ Failed to free port {port}")
            # Try alternative ports
            for alt_port in [5006, 5007, 5008, 5009]:
                if check_port_available(alt_port):
                    print(f"✅ Using alternative port {alt_port}")
                    os.environ['PORT'] = str(alt_port)
                    port = alt_port
                    break
            else:
                print("❌ No available ports found")
                sys.exit(1)
    
    print(f"✅ Port {port} is available")
    
    # Start the Flask app
    try:
        print("Starting Flask application...")
        subprocess.run([sys.executable, 'app.py'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Flask app failed to start: {e}")
        sys.exit(1)

if __name__ == '__main__':
    start_flask_app()