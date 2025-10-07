#!/usr/bin/env python3
"""
Interactive Dataset Management Script
====================================

This script helps manage dataset projects by:
1. Adding GitHub repositories as submodules
2. Compiling projects with forge
3. Running tests with forge test
4. Storing metadata in JSON format

Usage: python manage_dataset.py
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import shutil
import time
from datetime import datetime
import re

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class DatasetManager:
    def __init__(self, dataset_dir: str = "dataset", metadata_file: str = "dataset_metadata.json"):
        self.dataset_dir = Path(dataset_dir)
        self.metadata_file = Path(metadata_file)
        self.metadata = self.load_metadata()
        
        # Ensure dataset directory exists
        self.dataset_dir.mkdir(exist_ok=True)
        self.log_verbose("Initialized DatasetManager")
        self.log_verbose(f"Dataset directory: {self.dataset_dir.absolute()}")
        self.log_verbose(f"Metadata file: {self.metadata_file.absolute()}")
    
    def log_verbose(self, message: str, color: str = ""):
        """Print verbose log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if color:
            print(f"{color}[{timestamp}] {message}{Colors.ENDC}")
        else:
            print(f"[{timestamp}] {message}")
    
    def log_step(self, step_num: int, total_steps: int, message: str):
        """Log a step in the process"""
        self.log_verbose(f"[Step {step_num}/{total_steps}] {message}", Colors.OKCYAN)
    
    def log_success(self, message: str):
        """Log success message"""
        self.log_verbose(f"✅ {message}", Colors.OKGREEN)
    
    def log_error(self, message: str):
        """Log error message"""
        self.log_verbose(f"❌ {message}", Colors.FAIL)
    
    def log_warning(self, message: str):
        """Log warning message"""
        self.log_verbose(f"⚠️  {message}", Colors.WARNING)
    
    def extract_repo_name(self, repo_url: str) -> str:
        """Extract repository name from GitHub URL"""
        self.log_verbose(f"Extracting repository name from: {repo_url}")
        
        # Handle HTTPS URLs
        if repo_url.startswith('https://github.com/'):
            # Remove .git suffix if present
            repo_url = repo_url.rstrip('.git')
            # Extract the last part (repo name)
            parts = repo_url.split('/')
            repo_name = parts[-1]
        # Handle SSH URLs
        elif repo_url.startswith('git@github.com:'):
            repo_url = repo_url.rstrip('.git')
            parts = repo_url.split('/')
            repo_name = parts[-1]
        else:
            repo_name = "unknown-repo"
        
        self.log_verbose(f"Extracted repository name: {repo_name}")
        return repo_name
    
    def load_metadata(self) -> Dict[str, Any]:
        """Load existing metadata from JSON file"""
        if self.metadata_file.exists():
            try:
                self.log_verbose(f"Loading metadata from {self.metadata_file}")
                with open(self.metadata_file, 'r') as f:
                    metadata = json.load(f)
                self.log_verbose(f"Loaded {len(metadata)} existing entries")
                return metadata
            except (json.JSONDecodeError, FileNotFoundError) as e:
                self.log_warning(f"Could not load {self.metadata_file}: {e}")
                self.log_warning("Starting with empty metadata")
                return {}
        self.log_verbose("No existing metadata file found, starting fresh")
        return {}
    
    def save_metadata(self):
        """Save metadata to JSON file"""
        self.log_verbose(f"Saving metadata to {self.metadata_file}...")
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            self.log_success(f"Metadata saved successfully ({len(self.metadata)} entries)")
        except Exception as e:
            self.log_error(f"Failed to save metadata: {e}")
    
    def get_finding_id(self) -> int:
        """Get finding ID from user input"""
        self.log_verbose("Prompting user for finding ID")
        while True:
            try:
                finding_id = input(f"{Colors.BOLD}Enter finding ID (number): {Colors.ENDC}").strip()
                if not finding_id:
                    self.log_warning("Finding ID cannot be empty")
                    continue
                finding_id = int(finding_id)
                self.log_verbose(f"User entered finding ID: {finding_id}")
                
                # Check if this ID already exists
                if str(finding_id) in self.metadata:
                    self.log_warning(f"Finding ID {finding_id} already exists in metadata")
                    overwrite = input(f"{Colors.WARNING}Finding ID {finding_id} already exists. Overwrite? (y/N): {Colors.ENDC}").strip().lower()
                    if overwrite != 'y':
                        self.log_verbose("User chose not to overwrite, asking for new ID")
                        continue
                    self.log_verbose("User confirmed overwrite")
                
                return finding_id
            except ValueError:
                self.log_error("Invalid input - please enter a valid number")
            except KeyboardInterrupt:
                print("\nOperation cancelled by user")
                sys.exit(0)
    
    def get_github_repo(self) -> str:
        """Get GitHub repository URL from user input"""
        self.log_verbose("Prompting user for GitHub repository URL")
        while True:
            repo_url = input(f"{Colors.BOLD}Enter GitHub repository URL: {Colors.ENDC}").strip()
            if not repo_url:
                self.log_warning("Repository URL cannot be empty")
                continue
            
            # Basic validation
            if not (repo_url.startswith('https://github.com/') or repo_url.startswith('git@github.com:')):
                self.log_error("Invalid GitHub URL format")
                print("Please enter a valid GitHub repository URL (https://github.com/... or git@github.com:...)")
                continue
            
            self.log_verbose(f"Valid GitHub URL received: {repo_url}")
            return repo_url
    
    def get_project_path(self) -> str:
        """Get project path within the repository"""
        self.log_verbose("Prompting user for project path")
        project_path = input(f"{Colors.BOLD}Enter project path within repository (e.g., 'contracts' or '.' for root): {Colors.ENDC}").strip()
        if not project_path:
            project_path = "."
            self.log_verbose("No path specified, using root directory")
        else:
            self.log_verbose(f"Project path set to: {project_path}")
        return project_path
    
    def add_submodule(self, finding_id: int, repo_url: str, repo_name: str) -> bool:
        """Add repository as git submodule"""
        # New directory structure: dataset/{finding_id}/{repo-name}/
        finding_dir = self.dataset_dir / str(finding_id)
        target_dir = finding_dir / repo_name
        
        self.log_verbose(f"Target directory will be: {target_dir}")
        
        try:
            # Create finding directory if it doesn't exist
            if not finding_dir.exists():
                self.log_verbose(f"Creating finding directory: {finding_dir}")
                finding_dir.mkdir(parents=True, exist_ok=True)
            
            # Remove existing repository directory if it exists
            if target_dir.exists():
                self.log_warning(f"Removing existing directory: {target_dir}")
                shutil.rmtree(target_dir)
            
            # Add as submodule
            self.log_verbose(f"Executing: git submodule add {repo_url} {target_dir}")
            start_time = time.time()
            
            result = subprocess.run([
                'git', 'submodule', 'add', repo_url, str(target_dir)
            ], capture_output=True, text=True, check=True)
            
            elapsed = time.time() - start_time
            self.log_success(f"Submodule added successfully in {elapsed:.2f}s")
            self.log_verbose(f"Git output: {result.stdout}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.log_error(f"Failed to add submodule: {e}")
            self.log_verbose(f"stdout: {e.stdout}")
            self.log_verbose(f"stderr: {e.stderr}")
            return False
        except Exception as e:
            self.log_error(f"Unexpected error: {e}")
            return False
    
    def check_forge_available(self) -> bool:
        """Check if forge is available in the system"""
        self.log_verbose("Checking if forge is available...")
        try:
            result = subprocess.run(['forge', '--version'], capture_output=True, check=True, text=True)
            version = result.stdout.strip()
            self.log_success(f"Forge is available: {version}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log_warning("Forge not found in system PATH")
            return False
    
    def compile_project(self, finding_id: int, repo_name: str, project_path: str) -> Tuple[bool, str]:
        """Compile the project using forge"""
        finding_dir = self.dataset_dir / str(finding_id)
        target_dir = finding_dir / repo_name
        full_project_path = target_dir / project_path
        
        self.log_verbose(f"Full project path for compilation: {full_project_path}")
        
        if not full_project_path.exists():
            error_msg = f"Project path {full_project_path} does not exist"
            self.log_error(error_msg)
            return False, error_msg
        
        try:
            self.log_verbose(f"Starting compilation in {full_project_path}")
            self.log_verbose("Executing: forge build")
            start_time = time.time()
            
            result = subprocess.run([
                'forge', 'build'
            ], cwd=full_project_path, capture_output=True, text=True, check=True, timeout=300)
            
            elapsed = time.time() - start_time
            self.log_success(f"Compilation successful in {elapsed:.2f}s")
            
            # Show compilation output summary
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                self.log_verbose(f"Compilation output ({len(lines)} lines):")
                for line in lines[-10:]:  # Show last 10 lines
                    self.log_verbose(f"  {line}")
            
            return True, result.stdout
            
        except subprocess.TimeoutExpired:
            self.log_error("Compilation timed out after 5 minutes")
            return False, "Compilation timeout (300s)"
        except subprocess.CalledProcessError as e:
            self.log_error("Compilation failed")
            self.log_verbose(f"Error output:\n{e.stderr}")
            return False, e.stderr
        except Exception as e:
            self.log_error(f"Unexpected error during compilation: {e}")
            return False, str(e)
    
    def test_project(self, finding_id: int, repo_name: str, project_path: str) -> Tuple[bool, str]:
        """Run tests for the project using forge with timeout and fallback strategies"""
        finding_dir = self.dataset_dir / str(finding_id)
        target_dir = finding_dir / repo_name
        full_project_path = target_dir / project_path
        
        self.log_verbose(f"Full project path for testing: {full_project_path}")
        
        if not full_project_path.exists():
            error_msg = f"Project path {full_project_path} does not exist"
            self.log_error(error_msg)
            return False, error_msg
        
        # Strategy 1: Try regular forge test with 3-minute timeout
        try:
            self.log_verbose("Starting tests (timeout: 180s)")
            self.log_verbose("Executing: forge test")
            start_time = time.time()
            
            result = subprocess.run([
                'forge', 'test'
            ], cwd=full_project_path, capture_output=True, text=True, check=True, timeout=180)
            
            elapsed = time.time() - start_time
            self.log_success(f"Tests passed in {elapsed:.2f}s")
            
            # Show test output summary
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                self.log_verbose(f"Test output ({len(lines)} lines):")
                for line in lines[-15:]:  # Show last 15 lines
                    self.log_verbose(f"  {line}")
            
            return True, result.stdout
            
        except subprocess.TimeoutExpired:
            self.log_warning("Tests timed out after 3 minutes, trying alternative strategies...")
            
            # Strategy 2: Try listing tests
            try:
                self.log_verbose("Executing: forge test --list")
                list_result = subprocess.run([
                    'forge', 'test', '--list'
                ], cwd=full_project_path, capture_output=True, text=True, timeout=60)
                
                self.log_verbose("Test list output:")
                self.log_verbose(list_result.stdout)
                
            except Exception as e:
                self.log_warning(f"Could not list tests: {e}")
            
            # Strategy 3: Try fail-fast mode
            try:
                self.log_verbose("Executing: forge test --fail-fast (timeout: 180s)")
                start_time = time.time()
                
                result = subprocess.run([
                    'forge', 'test', '--fail-fast'
                ], cwd=full_project_path, capture_output=True, text=True, check=True, timeout=180)
                
                elapsed = time.time() - start_time
                self.log_success(f"Tests passed with --fail-fast in {elapsed:.2f}s")
                return True, f"[FAIL-FAST MODE]\n{result.stdout}"
                
            except subprocess.TimeoutExpired:
                self.log_error("Tests timed out even with --fail-fast")
                return False, "Test timeout (fail-fast mode, 180s)"
            except subprocess.CalledProcessError as e:
                self.log_error("Tests failed in fail-fast mode")
                return False, f"[FAIL-FAST MODE]\n{e.stderr}"
            
        except subprocess.CalledProcessError as e:
            self.log_error("Tests failed")
            self.log_verbose(f"Error output:\n{e.stderr}")
            
            # Try fail-fast as fallback
            try:
                self.log_verbose("Trying with --fail-fast after failure...")
                result = subprocess.run([
                    'forge', 'test', '--fail-fast'
                ], cwd=full_project_path, capture_output=True, text=True, timeout=180)
                
                self.log_verbose(f"Fail-fast output:\n{result.stdout}")
                return False, f"[ORIGINAL FAILED]\n{e.stderr}\n\n[FAIL-FAST OUTPUT]\n{result.stdout}"
            except:
                pass
            
            return False, e.stderr
            
        except Exception as e:
            self.log_error(f"Unexpected error during testing: {e}")
            return False, str(e)
    
    def get_additional_info(self) -> Dict[str, str]:
        """Get additional project information from user"""
        self.log_verbose("Collecting additional project information")
        info = {}
        
        # Get finding link
        finding_link = input(f"{Colors.BOLD}Enter finding link (optional): {Colors.ENDC}").strip()
        if finding_link:
            info['finding_link'] = finding_link
            self.log_verbose(f"Finding link: {finding_link}")
        
        # Get project name
        name = input(f"{Colors.BOLD}Enter project name (optional): {Colors.ENDC}").strip()
        if name:
            info['name'] = name
            self.log_verbose(f"Project name: {name}")
        
        # Get main contract
        main_contract = input(f"{Colors.BOLD}Enter main contract path (optional, e.g., 'src/MergingPool.sol'): {Colors.ENDC}").strip()
        if main_contract:
            info['main_contract'] = main_contract
            self.log_verbose(f"Main contract: {main_contract}")
        
        # Get annotations
        annotations = input(f"{Colors.BOLD}Enter annotations file path (optional): {Colors.ENDC}").strip()
        if annotations:
            info['annotations'] = annotations
            self.log_verbose(f"Annotations: {annotations}")
        
        # Get expected vulnerability
        expected_vuln = input(f"{Colors.BOLD}Enter expected vulnerability type (optional): {Colors.ENDC}").strip()
        if expected_vuln:
            info['expected_vulnerability'] = expected_vuln
            self.log_verbose(f"Expected vulnerability: {expected_vuln}")
        
        # Get difficulty
        difficulty = input(f"{Colors.BOLD}Enter difficulty level (optional): {Colors.ENDC}").strip()
        if difficulty:
            info['difficulty'] = difficulty
            self.log_verbose(f"Difficulty: {difficulty}")
        
        # Get patch path
        patch_path = input(f"{Colors.BOLD}Enter patch directory path (optional): {Colors.ENDC}").strip()
        if patch_path:
            info['patch'] = patch_path
            self.log_verbose(f"Patch path: {patch_path}")
        
        # Get audit reference
        audit_ref = input(f"{Colors.BOLD}Enter audit reference URL (optional): {Colors.ENDC}").strip()
        if audit_ref:
            info['audit_ref'] = audit_ref
            self.log_verbose(f"Audit reference: {audit_ref}")
        
        # Get patch reference
        patch_ref = input(f"{Colors.BOLD}Enter patch reference URL (optional): {Colors.ENDC}").strip()
        if patch_ref:
            info['patch_ref'] = patch_ref
            self.log_verbose(f"Patch reference: {patch_ref}")
        
        self.log_verbose(f"Collected {len(info)} additional fields")
        return info
    
    def process_project(self):
        """Main interactive process for adding a project"""
        print("\n" + "="*70)
        print(f"{Colors.HEADER}{Colors.BOLD}DATASET PROJECT MANAGER{Colors.ENDC}")
        print("="*70)
        
        total_steps = 7
        
        # Step 1: Check forge
        self.log_step(1, total_steps, "Checking Forge availability")
        forge_available = self.check_forge_available()
        if not forge_available:
            self.log_warning("Forge not found - compilation and testing will be skipped")
            print("Make sure Foundry is installed: https://book.getfoundry.sh/getting-started/installation")
        
        # Step 2: Get basic information
        self.log_step(2, total_steps, "Collecting project information")
        finding_id = self.get_finding_id()
        repo_url = self.get_github_repo()
        repo_name = self.extract_repo_name(repo_url)
        project_path = self.get_project_path()
        
        print(f"\n{Colors.OKCYAN}Project Summary:{Colors.ENDC}")
        print(f"  Finding ID:     {finding_id}")
        print(f"  Repository:     {repo_url}")
        print(f"  Repo Name:      {repo_name}")
        print(f"  Project Path:   {project_path}")
        print(f"  Target Dir:     dataset/{finding_id}/{repo_name}/")
        
        confirm = input(f"\n{Colors.BOLD}Proceed with adding this project? (Y/n): {Colors.ENDC}").strip().lower()
        if confirm == 'n':
            self.log_warning("Operation cancelled by user")
            return
        
        # Step 3: Add submodule
        self.log_step(3, total_steps, "Adding Git submodule")
        if not self.add_submodule(finding_id, repo_url, repo_name):
            self.log_error("Failed to add submodule. Aborting.")
            return
        
        # Step 4: Compile project
        self.log_step(4, total_steps, "Compiling project")
        compile_success = False
        compile_output = ""
        if forge_available:
            compile_success, compile_output = self.compile_project(finding_id, repo_name, project_path)
        else:
            self.log_warning("Skipping compilation (forge not available)")
        
        # Step 5: Run tests
        self.log_step(5, total_steps, "Running tests")
        test_success = False
        test_output = ""
        if forge_available:
            test_success, test_output = self.test_project(finding_id, repo_name, project_path)
        else:
            self.log_warning("Skipping tests (forge not available)")
        
        # Step 6: Get additional information
        self.log_step(6, total_steps, "Collecting additional metadata")
        print("-"*70)
        print("Additional Information (press Enter to skip)")
        print("-"*70)
        additional_info = self.get_additional_info()
        
        # Create metadata entry
        metadata_entry = {
            "finding_id": finding_id,
            "code_repo": repo_url,
            "repo_name": repo_name,
            "project_path": project_path,
            "target_directory": f"dataset/{finding_id}/{repo_name}",
            "compilation_success": compile_success,
            "test_success": test_success,
            "compile_output": compile_output,
            "test_output": test_output,
            "added_timestamp": datetime.now().isoformat(),
            **additional_info
        }
        
        # Step 7: Save metadata
        self.log_step(7, total_steps, "Saving metadata")
        self.metadata[str(finding_id)] = metadata_entry
        self.save_metadata()
        
        # Final Summary
        print("\n" + "="*70)
        print(f"{Colors.OKGREEN}{Colors.BOLD}PROJECT ADDED SUCCESSFULLY{Colors.ENDC}")
        print("="*70)
        print(f"Finding ID:      {finding_id}")
        print(f"Repository:      {repo_url}")
        print(f"Repo Name:       {repo_name}")
        print(f"Project Path:    {project_path}")
        print(f"Target Dir:      dataset/{finding_id}/{repo_name}/")
        print(f"Compilation:     {'✅ Success' if compile_success else '❌ Failed'}")
        print(f"Tests:           {'✅ Passed' if test_success else '❌ Failed'}")
        print(f"Metadata saved:  {self.metadata_file}")
        print("="*70 + "\n")
    
    def list_projects(self):
        """List all projects in the dataset"""
        if not self.metadata:
            self.log_warning("No projects in dataset")
            return
        
        print("\n" + "="*70)
        print(f"{Colors.HEADER}{Colors.BOLD}DATASET PROJECTS{Colors.ENDC}")
        print("="*70)
        
        for finding_id, data in sorted(self.metadata.items(), key=lambda x: int(x[0])):
            print(f"\n{Colors.BOLD}Finding ID: {finding_id}{Colors.ENDC}")
            print(f"  Repository:    {data.get('code_repo', 'N/A')}")
            print(f"  Repo Name:     {data.get('repo_name', 'N/A')}")
            print(f"  Project Path:  {data.get('project_path', 'N/A')}")
            print(f"  Target Dir:    {data.get('target_directory', 'N/A')}")
            print(f"  Compilation:   {'✅ Success' if data.get('compilation_success') else '❌ Failed'}")
            print(f"  Tests:         {'✅ Passed' if data.get('test_success') else '❌ Failed'}")
            if data.get('name'):
                print(f"  Name:          {data['name']}")
            if data.get('added_timestamp'):
                print(f"  Added:         {data['added_timestamp']}")
        
        print("\n" + "="*70 + "\n")
    
    def interactive_menu(self):
        """Main interactive menu"""
        while True:
            print("\n" + "="*70)
            print(f"{Colors.HEADER}{Colors.BOLD}DATASET MANAGEMENT MENU{Colors.ENDC}")
            print("="*70)
            print(f"{Colors.OKCYAN}1.{Colors.ENDC} Add new project")
            print(f"{Colors.OKCYAN}2.{Colors.ENDC} List all projects")
            print(f"{Colors.OKCYAN}3.{Colors.ENDC} Exit")
            
            choice = input(f"\n{Colors.BOLD}Select an option (1-3): {Colors.ENDC}").strip()
            
            if choice == '1':
                self.process_project()
            elif choice == '2':
                self.list_projects()
            elif choice == '3':
                self.log_success("Goodbye!")
                break
            else:
                self.log_error("Invalid option. Please select 1, 2, or 3.")

def main():
    """Main function"""
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║         DATASET PROJECT MANAGEMENT TOOL (VERBOSE MODE)           ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(Colors.ENDC)
    
    manager = DatasetManager()
    
    # Check if we're in a git repository
    if not Path('.git').exists():
        manager.log_warning("Not in a git repository. Submodule operations may not work properly.")
        confirm = input(f"{Colors.WARNING}Continue anyway? (y/N): {Colors.ENDC}").strip().lower()
        if confirm != 'y':
            manager.log_error("Please run this script from within a git repository.")
            sys.exit(1)
    
    manager.interactive_menu()

if __name__ == "__main__":
    main()
