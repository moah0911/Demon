"""
Package manager for the Demon programming language.
This module handles downloading, installing, and managing packages.
"""

import os
import sys
import json
import shutil
import zipfile
import tempfile
import hashlib
import urllib.request
import urllib.error
from typing import Dict, List, Optional, Any, Tuple

class PackageManager:
    """Package manager for the Demon language."""
    
    def __init__(self, demon):
        self.demon = demon
        self.registry_url = "https://demon-lang.org/registry"  # Placeholder URL
        self.packages_dir = os.path.join(os.path.expanduser("~"), ".demon", "packages")
        self.config_file = os.path.join(os.path.expanduser("~"), ".demon", "config.json")
        
        # Create necessary directories
        os.makedirs(self.packages_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        # Load or create config
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Error: Invalid config file format. Using defaults.")
        
        # Default configuration
        config = {
            "registry_url": self.registry_url,
            "installed_packages": {}
        }
        
        # Save default config
        self._save_config(config)
        return config
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def install(self, package_name: str, version: Optional[str] = None) -> bool:
        """Install a package."""
        print(f"Installing package: {package_name}" + (f" (version {version})" if version else ""))
        
        try:
            # Get package info from registry
            package_info = self._fetch_package_info(package_name)
            
            if not package_info:
                print(f"Error: Package '{package_name}' not found in registry.")
                return False
            
            # Determine version to install
            if version:
                if version not in package_info["versions"]:
                    print(f"Error: Version '{version}' not found for package '{package_name}'.")
                    return False
                target_version = version
            else:
                # Use latest version
                target_version = package_info["latest_version"]
            
            # Check if already installed
            installed_packages = self.config.get("installed_packages", {})
            if package_name in installed_packages and installed_packages[package_name]["version"] == target_version:
                print(f"Package '{package_name}' version {target_version} is already installed.")
                return True
            
            # Download package
            package_url = package_info["versions"][target_version]["url"]
            package_hash = package_info["versions"][target_version]["hash"]
            
            # Create package directory
            package_dir = os.path.join(self.packages_dir, f"{package_name}-{target_version}")
            if os.path.exists(package_dir):
                shutil.rmtree(package_dir)
            os.makedirs(package_dir)
            
            # Download and extract package
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                self._download_file(package_url, temp_file.name)
                
                # Verify hash
                if not self._verify_hash(temp_file.name, package_hash):
                    print(f"Error: Package hash verification failed.")
                    return False
                
                # Extract package
                with zipfile.ZipFile(temp_file.name, 'r') as zip_ref:
                    zip_ref.extractall(package_dir)
            
            # Install dependencies
            dependencies = package_info["versions"][target_version].get("dependencies", {})
            for dep_name, dep_version in dependencies.items():
                if not self.install(dep_name, dep_version):
                    print(f"Error: Failed to install dependency '{dep_name}'.")
                    return False
            
            # Update config
            installed_packages[package_name] = {
                "version": target_version,
                "path": package_dir
            }
            self.config["installed_packages"] = installed_packages
            self._save_config(self.config)
            
            print(f"Successfully installed '{package_name}' version {target_version}.")
            return True
            
        except Exception as e:
            print(f"Error installing package: {e}")
            return False
    
    def uninstall(self, package_name: str) -> bool:
        """Uninstall a package."""
        print(f"Uninstalling package: {package_name}")
        
        installed_packages = self.config.get("installed_packages", {})
        if package_name not in installed_packages:
            print(f"Package '{package_name}' is not installed.")
            return False
        
        # Check for dependent packages
        for pkg, info in installed_packages.items():
            if pkg == package_name:
                continue
            
            # Get package info
            pkg_info = self._fetch_package_info(pkg)
            if not pkg_info:
                continue
            
            # Check dependencies
            dependencies = pkg_info["versions"][info["version"]].get("dependencies", {})
            if package_name in dependencies:
                print(f"Error: Package '{pkg}' depends on '{package_name}'.")
                return False
        
        # Remove package directory
        package_dir = installed_packages[package_name]["path"]
        if os.path.exists(package_dir):
            shutil.rmtree(package_dir)
        
        # Update config
        del installed_packages[package_name]
        self.config["installed_packages"] = installed_packages
        self._save_config(self.config)
        
        print(f"Successfully uninstalled '{package_name}'.")
        return True
    
    def update(self, package_name: Optional[str] = None) -> bool:
        """Update a package or all packages."""
        if package_name:
            print(f"Updating package: {package_name}")
            
            installed_packages = self.config.get("installed_packages", {})
            if package_name not in installed_packages:
                print(f"Package '{package_name}' is not installed.")
                return False
            
            # Get package info
            package_info = self._fetch_package_info(package_name)
            if not package_info:
                print(f"Error: Package '{package_name}' not found in registry.")
                return False
            
            # Check if update is needed
            current_version = installed_packages[package_name]["version"]
            latest_version = package_info["latest_version"]
            
            if current_version == latest_version:
                print(f"Package '{package_name}' is already up to date (version {current_version}).")
                return True
            
            # Install latest version
            return self.install(package_name, latest_version)
        else:
            # Update all packages
            print("Updating all packages...")
            
            installed_packages = self.config.get("installed_packages", {})
            success = True
            
            for pkg in installed_packages:
                if not self.update(pkg):
                    success = False
            
            return success
    
    def list_packages(self) -> List[Dict[str, str]]:
        """List installed packages."""
        installed_packages = self.config.get("installed_packages", {})
        result = []
        
        for pkg_name, pkg_info in installed_packages.items():
            result.append({
                "name": pkg_name,
                "version": pkg_info["version"],
                "path": pkg_info["path"]
            })
        
        return result
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search for packages in the registry."""
        try:
            url = f"{self.config['registry_url']}/search?q={query}"
            with urllib.request.urlopen(url) as response:
                search_results = json.loads(response.read().decode())
                return search_results
        except Exception as e:
            print(f"Error searching for packages: {e}")
            return []
    
    def get_package_path(self, package_name: str) -> Optional[str]:
        """Get the path to an installed package."""
        installed_packages = self.config.get("installed_packages", {})
        if package_name in installed_packages:
            return installed_packages[package_name]["path"]
        return None
    
    def _fetch_package_info(self, package_name: str) -> Optional[Dict[str, Any]]:
        """Fetch package information from the registry."""
        try:
            url = f"{self.config['registry_url']}/packages/{package_name}"
            with urllib.request.urlopen(url) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            raise
        except Exception as e:
            print(f"Error fetching package info: {e}")
            return None
    
    def _download_file(self, url: str, dest_path: str) -> None:
        """Download a file from URL to destination path."""
        try:
            urllib.request.urlretrieve(url, dest_path)
        except Exception as e:
            raise Exception(f"Failed to download file: {e}")
    
    def _verify_hash(self, file_path: str, expected_hash: str) -> bool:
        """Verify file hash."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest() == expected_hash

class PackageLoader:
    """Loader for Demon packages."""
    
    def __init__(self, demon, package_manager):
        self.demon = demon
        self.package_manager = package_manager
        self.loaded_packages = {}
    
    def import_package(self, package_name: str) -> bool:
        """Import a package into the Demon runtime."""
        if package_name in self.loaded_packages:
            return True
        
        # Get package path
        package_path = self.package_manager.get_package_path(package_name)
        if not package_path:
            print(f"Error: Package '{package_name}' is not installed.")
            return False
        
        # Check for package manifest
        manifest_path = os.path.join(package_path, "package.json")
        if not os.path.exists(manifest_path):
            print(f"Error: Invalid package format. Missing package.json.")
            return False
        
        # Load manifest
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
        except json.JSONDecodeError:
            print(f"Error: Invalid package.json format.")
            return False
        
        # Get main file
        main_file = manifest.get("main", "index.demon")
        main_path = os.path.join(package_path, main_file)
        
        if not os.path.exists(main_path):
            print(f"Error: Main file '{main_file}' not found in package.")
            return False
        
        # Load and execute main file
        try:
            with open(main_path, 'r') as f:
                source = f.read()
            
            # Create a new environment for the package
            from interpreter import Environment
            package_env = Environment(self.demon.interpreter.globals)
            
            # Execute the package code
            previous_env = self.demon.interpreter.environment
            self.demon.interpreter.environment = package_env
            
            # Parse and execute
            from scanner import Scanner
            from parser import Parser
            
            scanner = Scanner(source, main_path)
            tokens = scanner.scan_tokens()
            
            parser = Parser(tokens, self.demon)
            statements = parser.parse()
            
            if statements:
                self.demon.interpreter.interpret(statements)
            
            # Restore environment
            self.demon.interpreter.environment = previous_env
            
            # Mark package as loaded
            self.loaded_packages[package_name] = package_env
            
            return True
        except Exception as e:
            print(f"Error loading package: {e}")
            return False
    
    def get_package_exports(self, package_name: str) -> Optional[Dict[str, Any]]:
        """Get exported values from a package."""
        if package_name not in self.loaded_packages:
            if not self.import_package(package_name):
                return None
        
        # Return the package environment
        return self.loaded_packages[package_name]