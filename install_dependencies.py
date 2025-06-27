#!/usr/bin/env python3
"""
Script to check and install missing dependencies
"""

import subprocess
import sys

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_and_install_dependencies():
    """Check and install required dependencies"""
    required_packages = [
        'pandas>=1.3.0',
        'requests>=2.25.0',
        'beautifulsoup4>=4.9.0',
        'retry>=0.9.2',
        'mojimoji>=0.0.11',
        'tqdm>=4.61.0',
        'numpy>=1.21.0',
        'scikit-learn>=1.0.0',
        'urllib3>=1.26.0',
        'lxml>=4.6.0'
    ]
    
    print("🔧 Checking dependencies...")
    
    for package in required_packages:
        package_name = package.split('>=')[0]
        try:
            __import__(package_name.replace('-', '_'))
            print(f"✅ {package_name} is already installed")
        except ImportError:
            print(f"❌ {package_name} is missing. Installing...")
            if install_package(package):
                print(f"✅ Successfully installed {package}")
            else:
                print(f"❌ Failed to install {package}")
    
    print("\n🚀 All dependencies checked!")

if __name__ == "__main__":
    check_and_install_dependencies() 