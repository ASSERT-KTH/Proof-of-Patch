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
    
    def get_main_contract_path(self) -> str:
        """Get main contract path from user input"""
        self.log_verbose("Prompting user for main contract path")
        main_contract = input(f"{Colors.BOLD}Enter main contract path (e.g., 'src/Size.sol' or 'contracts/Token.sol'): {Colors.ENDC}").strip()
        if not main_contract:
            self.log_warning("Main contract path cannot be empty")
            return self.get_main_contract_path()  # Ask again
        self.log_verbose(f"Main contract path: {main_contract}")
        return main_contract
    
    def calculate_target_directory(self, finding_id: int, repo_name: str) -> str:
        """Calculate target directory using dataset/findings/id/project structure"""
        target_dir = f"dataset/findings/{finding_id}/{repo_name}"
        self.log_verbose(f"Calculated target directory: {target_dir}")
        return target_dir
    
    def add_submodule(self, finding_id: int, repo_url: str, repo_name: str) -> bool:
        """Add repository as git submodule"""
        # New directory structure: dataset/findings/{finding_id}/{repo-name}/
        findings_dir = self.dataset_dir / "findings"
        finding_dir = findings_dir / str(finding_id)
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
    def manage_nested_submodules(self, finding_id: int, repo_name: str) -> bool:
        """ run git submodule update --init --recursive in the target directory """
        findings_dir = self.dataset_dir / "findings"
        finding_dir = findings_dir / str(finding_id)
        target_dir = finding_dir / repo_name
        self.log_verbose(f"Initializing nested submodules in: {target_dir}")
        try:
            result = subprocess.run([
                'git', 'submodule', 'update', '--init', '--recursive'
            ], cwd=target_dir, capture_output=True, text=True, check=True, timeout=300)
            self.log_success("Nested submodules initialized successfully")
            self.log_verbose(f"Git output: {result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            self.log_error(f"Failed to initialize nested submodules: {e}")
            self.log_verbose(f"stdout: {e.stdout}")
            self.log_verbose(f"stderr: {e.stderr}")
            return False
        except Exception as e:
            self.log_error(f"Unexpected error during nested submodule initialization: {e}")
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
    
    def compile_project(self, finding_id: int, repo_name: str) -> Tuple[bool, str]:
        """Compile the project using forge"""
        findings_dir = self.dataset_dir / "findings"
        finding_dir = findings_dir / str(finding_id)
        target_dir = finding_dir / repo_name
        
        self.log_verbose(f"Target directory for compilation: {target_dir}")
        
        if not target_dir.exists():
            error_msg = f"Target directory {target_dir} does not exist"
            self.log_error(error_msg)
            return False, error_msg
        
        try:
            self.log_verbose(f"Starting compilation in {target_dir}")
            self.log_verbose("Executing: forge build")
            start_time = time.time()
            
            result = subprocess.run([
                'forge', 'build'
            ], cwd=target_dir, capture_output=True, text=True, check=True, timeout=300)
            
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
    
    def test_project(self, finding_id: int, repo_name: str) -> Tuple[bool, str, bool]:
        """Run tests for the project using forge with timeout and fallback strategies
        
        Returns: (test_success, output, can_list_tests)
        """
        findings_dir = self.dataset_dir / "findings"
        finding_dir = findings_dir / str(finding_id)
        target_dir = finding_dir / repo_name
        
        self.log_verbose(f"Target directory for testing: {target_dir}")
        
        if not target_dir.exists():
            error_msg = f"Target directory {target_dir} does not exist"
            self.log_error(error_msg)
            return False, error_msg, False
        
        # Strategy 1: Try regular forge test with 3-minute timeout
        try:
            self.log_verbose("Starting tests (timeout: 180s)")
            self.log_verbose("Executing: forge test")
            start_time = time.time()
            
            result = subprocess.run([
                'forge', 'test'
            ], cwd=target_dir, capture_output=True, text=True, check=True, timeout=180)
            
            elapsed = time.time() - start_time
            self.log_success(f"Tests passed in {elapsed:.2f}s")
            
            # Show test output summary
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                self.log_verbose(f"Test output ({len(lines)} lines):")
                for line in lines[-15:]:  # Show last 15 lines
                    self.log_verbose(f"  {line}")
            
            return True, result.stdout, False
            
        except subprocess.TimeoutExpired:
            self.log_warning("Tests timed out after 3 minutes, trying alternative strategies...")
            
            # Strategy 2: Try listing tests
            can_list = False
            try:
                self.log_verbose("Executing: forge test --list")
                list_result = subprocess.run([
                    'forge', 'test', '--list'
                ], cwd=target_dir, capture_output=True, text=True, timeout=60)
                
                self.log_verbose("Test list output:")
                self.log_verbose(list_result.stdout)
                can_list = True  # Tests can be listed
                
            except Exception as e:
                self.log_warning(f"Could not list tests: {e}")
            
            # Strategy 3: Try fail-fast mode
            try:
                self.log_verbose("Executing: forge test --fail-fast (timeout: 180s)")
                start_time = time.time()
                
                result = subprocess.run([
                    'forge', 'test', '--fail-fast'
                ], cwd=target_dir, capture_output=True, text=True, check=True, timeout=180)
                
                elapsed = time.time() - start_time
                self.log_success(f"Tests passed with --fail-fast in {elapsed:.2f}s")
                return True, f"[FAIL-FAST MODE]\n{result.stdout}", can_list
                
            except subprocess.TimeoutExpired:
                self.log_error("Tests timed out even with --fail-fast")
                return False, "Test timeout (fail-fast mode, 180s)", can_list
            except subprocess.CalledProcessError as e:
                self.log_error("Tests failed in fail-fast mode")
                return False, f"[FAIL-FAST MODE]\n{e.stderr}", can_list
            
        except subprocess.CalledProcessError as e:
            self.log_error("Tests failed")
            self.log_verbose(f"Error output:\n{e.stderr}")
            
            # Try listing tests to see if manual review is possible
            can_list = False
            try:
                self.log_verbose("Checking if tests can be listed...")
                list_result = subprocess.run([
                    'forge', 'test', '--list'
                ], cwd=target_dir, capture_output=True, text=True, timeout=60)
                can_list = True
                self.log_verbose("Tests can be listed - manual review possible")
            except:
                self.log_verbose("Cannot list tests")
            
            # Try fail-fast as fallback
            try:
                self.log_verbose("Trying with --fail-fast after failure...")
                result = subprocess.run([
                    'forge', 'test', '--fail-fast'
                ], cwd=full_project_path, capture_output=True, text=True, timeout=180)
                
                self.log_verbose(f"Fail-fast output:\n{result.stdout}")
                return False, f"[ORIGINAL FAILED]\n{e.stderr}\n\n[FAIL-FAST OUTPUT]\n{result.stdout}", can_list
            except:
                pass
            
            return False, e.stderr, can_list
            
        except Exception as e:
            self.log_error(f"Unexpected error during testing: {e}")
            return False, str(e), False
    
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
        
        # Main contract is now collected earlier in the process
        
        # Get audit text for annotations
        print(f"{Colors.BOLD}Enter audit text for annotations (optional, press Enter twice when done):{Colors.ENDC}")
        print(f"{Colors.OKCYAN}(Paste the audit finding/vulnerability description){Colors.ENDC}")
        audit_lines = []
        while True:
            line = input()
            if line == "" and len(audit_lines) > 0 and audit_lines[-1] == "":
                audit_lines.pop()  # Remove the last empty line
                break
            audit_lines.append(line)
        
        if audit_lines:
            audit_text = '\n'.join(audit_lines).strip()
            if audit_text:
                info['audit_text'] = audit_text
                self.log_verbose(f"Audit text captured ({len(audit_text)} characters)")
        
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
        
        # Note: patch_ref is now collected in verify_patch_exists() step
        
        self.log_verbose(f"Collected {len(info)} additional fields")
        return info
    
    def manual_review_tests(self, finding_id: int, repo_name: str) -> Tuple[bool, Optional[str]]:
        """Interactive manual review of tests
        
        Returns: (tests_pass, fix_commands)
        """
        findings_dir = self.dataset_dir / "findings"
        finding_dir = findings_dir / str(finding_id)
        target_dir = finding_dir / repo_name
        
        print("\n" + "="*70)
        print(f"{Colors.WARNING}{Colors.BOLD}⚠️  TIME FOR MANUAL REVIEW{Colors.ENDC}")
        print("="*70)
        print(f"\n{Colors.BOLD}Automated tests failed, but the project can be tested manually.{Colors.ENDC}")
        print(f"\n{Colors.OKCYAN}Project location:{Colors.ENDC} {target_dir.absolute()}")
        print(f"\n{Colors.BOLD}Instructions:{Colors.ENDC}")
        print("  1. Open another terminal")
        print(f"  2. Navigate to: cd {target_dir.absolute()}")
        print("  3. Try running: forge test --list")
        print("  4. Run specific tests or all tests as needed")
        print("  5. Come back here when done")
        print("\n" + "-"*70)
        
        # Ask if tests pass
        while True:
            response = input(f"\n{Colors.BOLD}Do the tests pass after manual review? (yes/no): {Colors.ENDC}").strip().lower()
            
            if response in ['yes', 'y']:
                self.log_success("User confirmed tests pass")
                
                # Ask for fix commands
                print(f"\n{Colors.BOLD}If you needed to run any specific commands to make tests pass, enter them below.{Colors.ENDC}")
                print(f"{Colors.OKCYAN}(e.g., 'forge test --match-contract MyTest', or press Enter if none needed){Colors.ENDC}")
                
                fix_commands = input(f"{Colors.BOLD}Fix commands (optional): {Colors.ENDC}").strip()
                
                if fix_commands:
                    self.log_verbose(f"Fix commands provided: {fix_commands}")
                    return True, fix_commands
                else:
                    self.log_verbose("No fix commands needed")
                    return True, None
            
            elif response in ['no', 'n']:
                self.log_warning("User confirmed tests do NOT pass")
                confirm_remove = input(f"\n{Colors.WARNING}Remove this project from the dataset? (yes/no): {Colors.ENDC}").strip().lower()
                
                if confirm_remove in ['yes', 'y']:
                    return False, None
                else:
                    # Give another chance
                    print(f"\n{Colors.OKCYAN}Please review the tests again.{Colors.ENDC}")
                    continue
            
            else:
                print(f"{Colors.FAIL}Please answer 'yes' or 'no'{Colors.ENDC}")
    
    def remove_failed_project(self, finding_id: int, repo_name: str) -> bool:
        """Remove a failed project's submodule"""
        findings_dir = self.dataset_dir / "findings"
        finding_dir = findings_dir / str(finding_id)
        target_dir = finding_dir / repo_name
        
        self.log_warning(f"Removing failed project: {target_dir}")
        
        try:
            # Deinitialize the submodule
            self.log_verbose("Deinitializing submodule...")
            subprocess.run([
                'git', 'submodule', 'deinit', '-f', str(target_dir)
            ], capture_output=True, text=True, check=True)
            
            # Remove from git
            self.log_verbose("Removing from git index...")
            subprocess.run([
                'git', 'rm', '-f', str(target_dir)
            ], capture_output=True, text=True, check=True)
            
            # Remove submodule from .git/modules
            git_modules_path = Path('.git/modules') / target_dir
            if git_modules_path.exists():
                self.log_verbose(f"Removing .git/modules/{target_dir}...")
                shutil.rmtree(git_modules_path)
            
            # Remove the actual directory if it still exists
            if target_dir.exists():
                self.log_verbose(f"Removing directory {target_dir}...")
                shutil.rmtree(target_dir)
            
            # Remove finding directory if empty
            if finding_dir.exists() and not any(finding_dir.iterdir()):
                self.log_verbose(f"Removing empty finding directory {finding_dir}...")
                finding_dir.rmdir()
            
            self.log_success("Failed project removed successfully")
            return True
            
        except Exception as e:
            self.log_error(f"Error removing project: {e}")
            # Try to force remove the directory anyway
            if target_dir.exists():
                try:
                    shutil.rmtree(target_dir)
                    self.log_warning("Directory force-removed")
                except:
                    pass
            return False
    
    def add_patch_directory(self, finding_id: int) -> Tuple[bool, str]:
        """Add patch directory for the project
        
        Returns: (success, patch_path)
        """
        patch_dir = self.dataset_dir / "patches" / str(finding_id)
        
        self.log_verbose(f"Creating patch directory: {patch_dir}")
        
        try:
            # Create the patch directory
            patch_dir.mkdir(parents=True, exist_ok=True)
            
            # Check if directory was created successfully
            if patch_dir.exists():
                self.log_success(f"Patch directory created: {patch_dir}")
                return True, f"patches/{finding_id}"
            else:
                self.log_error("Failed to create patch directory")
                return False, ""
                
        except Exception as e:
            self.log_error(f"Error creating patch directory: {e}")
            return False, ""
    
    def verify_patch_exists(self, finding_id: int, repo_name: str) -> Tuple[bool, Optional[str]]:
        """Interactive patch verification
        
        Returns: (has_patch, patch_reference)
        """
        print("\n" + "="*70)
        print(f"{Colors.OKCYAN}{Colors.BOLD}🔍 PATCH VERIFICATION{Colors.ENDC}")
        print("="*70)
        print(f"\n{Colors.BOLD}Please search for the patch for this vulnerability.{Colors.ENDC}")
        print(f"\n{Colors.OKCYAN}Instructions:{Colors.ENDC}")
        print("  1. Search for patch/fix commits in the repository")
        print("  2. Check if the audit report mentions a patch")
        print("  3. Look for mitigation PRs or fix references")
        print("  4. Verify the patch can be included in the dataset")
        print("\n" + "-"*70)
        
        while True:
            response = input(f"\n{Colors.BOLD}Does a patch exist for this vulnerability? (yes/no): {Colors.ENDC}").strip().lower()
            
            if response in ['yes', 'y']:
                self.log_success("User confirmed patch exists")
                
                # Create patch directory
                success, patch_path = self.add_patch_directory(finding_id)
                
                if not success:
                    self.log_error("Failed to create patch directory")
                    return False, None
                
                # Ask for patch reference
                print(f"\n{Colors.BOLD}Please provide the patch reference:{Colors.ENDC}")
                print(f"{Colors.OKCYAN}Options:{Colors.ENDC}")
                print("  - Enter a GitHub PR/commit URL")
                print("  - Enter 'from_audit' if patch is described in the audit")
                print("  - Enter any other reference link")
                
                patch_ref = input(f"\n{Colors.BOLD}Patch reference: {Colors.ENDC}").strip()
                
                if patch_ref:
                    self.log_verbose(f"Patch reference provided: {patch_ref}")
                    return True, patch_ref
                else:
                    self.log_warning("No patch reference provided, asking again...")
                    continue
            
            elif response in ['no', 'n']:
                self.log_warning("User confirmed NO patch exists")
                confirm_remove = input(f"\n{Colors.WARNING}This vulnerability has no patch. Remove project from dataset? (yes/no): {Colors.ENDC}").strip().lower()
                
                if confirm_remove in ['yes', 'y']:
                    self.log_error("Removing project - no patch available")
                    return False, None
                else:
                    # Give another chance to search
                    print(f"\n{Colors.OKCYAN}Please search again for the patch.{Colors.ENDC}")
                    continue
            
            else:
                print(f"{Colors.FAIL}Please answer 'yes' or 'no'{Colors.ENDC}")
    
    def add_poc_directory(self, finding_id: int) -> Tuple[bool, str]:
        """Add POC directory for the project
        
        Returns: (success, poc_path)
        """
        poc_dir = self.dataset_dir / "pocs" / str(finding_id)
        
        self.log_verbose(f"Creating POC directory: {poc_dir}")
        
        try:
            # Create the POC directory
            poc_dir.mkdir(parents=True, exist_ok=True)
            
            # Check if directory was created successfully
            if poc_dir.exists():
                self.log_success(f"POC directory created: {poc_dir}")
                return True, f"pocs/{finding_id}"
            else:
                self.log_error("Failed to create POC directory")
                return False, ""
                
        except Exception as e:
            self.log_error(f"Error creating POC directory: {e}")
            return False, ""
    
    def verify_poc_exists(self, finding_id: int) -> Tuple[bool, Optional[str]]:
        """Interactive POC verification
        
        Returns: (wants_poc, poc_reference)
        """
        print("\n" + "="*70)
        print(f"{Colors.OKCYAN}{Colors.BOLD}📋 POC (PROOF OF CONCEPT) VERIFICATION{Colors.ENDC}")
        print("="*70)
        print(f"\n{Colors.BOLD}Would you like to add a POC for this vulnerability?{Colors.ENDC}")
        print(f"\n{Colors.OKCYAN}Instructions:{Colors.ENDC}")
        print("  - POC directory will be created at: dataset/pocs/{finding_id}/")
        print("  - You can add POC files later to this directory")
        print("  - Provide a reference URL for the POC")
        print("\n" + "-"*70)
        
        while True:
            response = input(f"\n{Colors.BOLD}Add POC for this vulnerability? (yes/no): {Colors.ENDC}").strip().lower()
            
            if response in ['yes', 'y']:
                self.log_success("User wants to add POC")
                
                # Create POC directory
                success, poc_path = self.add_poc_directory(finding_id)
                
                if not success:
                    self.log_error("Failed to create POC directory")
                    return False, None
                
                # Ask for POC reference
                print(f"\n{Colors.BOLD}Please provide the POC reference:{Colors.ENDC}")
                print(f"{Colors.OKCYAN}Options:{Colors.ENDC}")
                print("  - Enter a GitHub URL with POC code")
                print("  - Enter a link to exploit/attack code")
                print("  - Enter any other POC reference")
                
                poc_ref = input(f"\n{Colors.BOLD}POC reference URL: {Colors.ENDC}").strip()
                
                if poc_ref:
                    self.log_verbose(f"POC reference provided: {poc_ref}")
                    return True, poc_ref
                else:
                    self.log_warning("No POC reference provided, asking again...")
                    continue
            
            elif response in ['no', 'n']:
                self.log_verbose("User chose not to add POC")
                return False, None
            
            else:
                print(f"{Colors.FAIL}Please answer 'yes' or 'no'{Colors.ENDC}")
    
    def save_audit_text(self, finding_id: int, audit_text: str) -> str:
        """Save audit text to annotations file"""
        # Create annotations directory if it doesn't exist
        annotations_dir = self.dataset_dir / "annotations"
        annotations_dir.mkdir(exist_ok=True)
        
        # Save to annotations/{finding_id}.txt
        annotations_file = annotations_dir / f"{finding_id}.txt"
        
        self.log_verbose(f"Saving audit text to {annotations_file}")
        try:
            with open(annotations_file, 'w') as f:
                f.write(audit_text)
            self.log_success(f"Audit text saved to annotations/{finding_id}.txt")
            return f"annotations/{finding_id}.txt"
        except Exception as e:
            self.log_error(f"Failed to save audit text: {e}")
            return ""
    
    def process_project(self):
        """Main interactive process for adding a project"""
        print("\n" + "="*70)
        print(f"{Colors.HEADER}{Colors.BOLD}DATASET PROJECT MANAGER{Colors.ENDC}")
        print("="*70)
        
        total_steps = 9
        
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
        main_contract_path = self.get_main_contract_path()
        target_directory = self.calculate_target_directory(finding_id, repo_name)
        
        print(f"\n{Colors.OKCYAN}Project Summary:{Colors.ENDC}")
        print(f"  Finding ID:     {finding_id}")
        print(f"  Repository:     {repo_url}")
        print(f"  Repo Name:      {repo_name}")
        print(f"  Main Contract:  {main_contract_path}")
        print(f"  Target Dir:     {target_directory}/")
        
        confirm = input(f"\n{Colors.BOLD}Proceed with adding this project? (Y/n): {Colors.ENDC}").strip().lower()
        if confirm == 'n':
            self.log_warning("Operation cancelled by user")
            return
        
        # Step 3: Add submodule
        self.log_step(3, total_steps, "Adding Git submodule")
        if not self.add_submodule(finding_id, repo_url, repo_name):
            self.log_error("Failed to add submodule. Aborting.")
            return
        
        # and include recursive command 
        if not self.manage_nested_submodules(finding_id, repo_name):
            self.log_warning("Failed to initialize nested submodules. Continuing anyway.")
            
        
        
        # Step 4: Compile project
        self.log_step(4, total_steps, "Compiling project")
        compile_success = False
        compile_output = ""
        if forge_available:
            compile_success, compile_output = self.compile_project(finding_id, repo_name)
        else:
            self.log_warning("Skipping compilation (forge not available)")
        
        # Step 5: Run tests
        self.log_step(5, total_steps, "Running tests")
        test_success = False
        test_output = ""
        fix_commands = None
        
        if forge_available:
            test_success, test_output, can_list = self.test_project(finding_id, repo_name)
            
            # If tests failed but can be listed, offer manual review
            if not test_success and can_list:
                manual_pass, fix_cmds = self.manual_review_tests(finding_id, repo_name)
                
                if manual_pass:
                    test_success = True
                    fix_commands = fix_cmds
                    self.log_success("Tests pass after manual review")
                else:
                    # User confirmed tests don't pass - remove project
                    self.log_error("Tests failed manual review - removing project")
                    self.remove_failed_project(finding_id, repo_name)
                    print(f"\n{Colors.FAIL}Project removed due to failed tests{Colors.ENDC}\n")
                    return
        else:
            self.log_warning("Skipping tests (forge not available)")
        
        # Step 5.5: Verify patch exists
        self.log_step(6, total_steps, "Verifying patch availability")
        has_patch, patch_reference = self.verify_patch_exists(finding_id, repo_name)
        
        if not has_patch:
            # User confirmed no patch exists - remove project
            self.log_error("No patch available - removing project")
            self.remove_failed_project(finding_id, repo_name)
            print(f"\n{Colors.FAIL}Project removed - no patch available{Colors.ENDC}\n")
            return
        
        # Step 6: Verify POC (optional)
        self.log_step(7, total_steps, "Verifying POC availability")
        wants_poc, poc_reference = self.verify_poc_exists(finding_id)
        
        # Step 7: Get additional information
        self.log_step(8, total_steps, "Collecting additional metadata")
        print("-"*70)
        print("Additional Information (press Enter to skip)")
        print("-"*70)
        additional_info = self.get_additional_info()
        
        # Save audit text if provided
        annotations_path = ""
        if 'audit_text' in additional_info:
            audit_text = additional_info.pop('audit_text')  # Remove from dict to save separately
            annotations_path = self.save_audit_text(finding_id, audit_text)
        
        # Create metadata entry
        metadata_entry = {
            "finding_id": finding_id,
            "code_repo": repo_url,
            "repo_name": repo_name,
            "main_contract": main_contract_path,
            "target_directory": target_directory,
            "patch": f"patches/{finding_id}",  # Always include patch path
            "patch_ref": patch_reference,  # Always include patch reference
            "added_timestamp": datetime.now().isoformat(),
            **additional_info
        }
        
        # Add annotations path if audit text was saved
        if annotations_path:
            metadata_entry['annotations'] = annotations_path
        
        # Add fix commands if provided during manual review
        if fix_commands:
            metadata_entry['test_fix_commands'] = fix_commands
        
        # Add POC information if provided
        if wants_poc and poc_reference:
            metadata_entry['poc_path'] = f"pocs/{finding_id}"
            metadata_entry['poc_ref'] = poc_reference
        
        # Step 9: Save metadata
        self.log_step(9, total_steps, "Saving metadata")
        self.metadata[str(finding_id)] = metadata_entry
        self.save_metadata()
        
        # Final Summary
        print("\n" + "="*70)
        print(f"{Colors.OKGREEN}{Colors.BOLD}PROJECT ADDED SUCCESSFULLY{Colors.ENDC}")
        print("="*70)
        print(f"Finding ID:      {finding_id}")
        print(f"Repository:      {repo_url}")
        print(f"Repo Name:       {repo_name}")
        print(f"Main Contract:   {main_contract_path}")
        print(f"Target Dir:      {target_directory}/")
        print(f"Compilation:     {'✅ Success' if compile_success else '❌ Failed'}")
        print(f"Tests:           {'✅ Passed' if test_success else '❌ Failed'}")
        print(f"Patch Path:      patches/{finding_id}")
        print(f"Patch Reference: {patch_reference}")
        if wants_poc and poc_reference:
            print(f"POC Path:        pocs/{finding_id}")
            print(f"POC Reference:   {poc_reference}")
        if annotations_path:
            print(f"Annotations:     {annotations_path}")
        if fix_commands:
            print(f"Fix Commands:    {fix_commands}")
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
            print(f"  Main Contract: {data.get('main_contract', 'N/A')}")
            print(f"  Target Dir:    {data.get('target_directory', 'N/A')}")
            if data.get('patch'):
                print(f"  Patch Path:    {data['patch']}")
            if data.get('patch_ref'):
                print(f"  Patch Ref:     {data['patch_ref']}")
            if data.get('poc_path'):
                print(f"  POC Path:      {data['poc_path']}")
            if data.get('poc_ref'):
                print(f"  POC Ref:       {data['poc_ref']}")
            if data.get('name'):
                print(f"  Name:          {data['name']}")
            if data.get('annotations'):
                print(f"  Annotations:   {data['annotations']}")
            if data.get('test_fix_commands'):
                print(f"  Fix Commands:  {data['test_fix_commands']}")
            if data.get('added_timestamp'):
                print(f"  Added:         {data['added_timestamp']}")
        
        print("\n" + "="*70 + "\n")
    
    def edit_project(self, finding_id: int):
        """Edit an existing project to add missing information"""
        finding_id_str = str(finding_id)
        
        if finding_id_str not in self.metadata:
            self.log_error(f"Finding ID {finding_id} not found in metadata")
            return
        
        project_data = self.metadata[finding_id_str]
        
        print("\n" + "="*70)
        print(f"{Colors.HEADER}{Colors.BOLD}EDIT PROJECT - FINDING ID {finding_id}{Colors.ENDC}")
        print("="*70)
        
        # Show current project info
        print(f"\n{Colors.OKCYAN}Current Project Information:{Colors.ENDC}")
        print(f"  Repository:    {project_data.get('code_repo', 'N/A')}")
        print(f"  Repo Name:     {project_data.get('repo_name', 'N/A')}")
        print(f"  Main Contract: {project_data.get('main_contract', 'N/A')}")
        print(f"  Target Dir:    {project_data.get('target_directory', 'N/A')}")
        print(f"  Patch Path:    {project_data.get('patch', 'N/A')}")
        print(f"  Patch Ref:     {project_data.get('patch_ref', 'N/A')}")
        print(f"  POC Path:      {project_data.get('poc_path', 'N/A')}")
        print(f"  POC Ref:       {project_data.get('poc_ref', 'N/A')}")
        print(f"  Annotations:   {project_data.get('annotations', 'N/A')}")
        print(f"  Fix Commands:  {project_data.get('test_fix_commands', 'N/A')}")
        
        print(f"\n{Colors.BOLD}What would you like to update?{Colors.ENDC}")
        print(f"{Colors.OKCYAN}1.{Colors.ENDC} Re-run tests (manual review)")
        print(f"{Colors.OKCYAN}2.{Colors.ENDC} Update patch information")
        print(f"{Colors.OKCYAN}3.{Colors.ENDC} Add/update POC information")
        print(f"{Colors.OKCYAN}4.{Colors.ENDC} Update audit text/annotations")
        print(f"{Colors.OKCYAN}5.{Colors.ENDC} Update other metadata")
        print(f"{Colors.OKCYAN}6.{Colors.ENDC} Cancel")
        
        choice = input(f"\n{Colors.BOLD}Select option (1-6): {Colors.ENDC}").strip()
        
        if choice == '1':
            self.edit_project_tests(finding_id, project_data)
        elif choice == '2':
            self.edit_project_patch(finding_id, project_data)
        elif choice == '3':
            self.edit_project_poc(finding_id, project_data)
        elif choice == '4':
            self.edit_project_annotations(finding_id, project_data)
        elif choice == '5':
            self.edit_project_metadata(finding_id, project_data)
        elif choice == '6':
            self.log_warning("Edit cancelled")
            return
        else:
            self.log_error("Invalid option")
            return
    
    def edit_project_tests(self, finding_id: int, project_data: Dict[str, Any]):
        """Re-run tests for an existing project"""
        repo_name = project_data.get('repo_name', '')
        
        if not repo_name:
            self.log_error("Cannot re-run tests: repo_name not found")
            return
        
        print(f"\n{Colors.WARNING}Re-running tests for finding ID {finding_id}...{Colors.ENDC}")
        
        # Check if forge is available
        if not self.check_forge_available():
            self.log_error("Forge not available - cannot run tests")
            return
        
        # Run tests
        test_success, test_output, can_list = self.test_project(finding_id, repo_name)
        
        if not test_success and can_list:
            # Offer manual review
            manual_pass, fix_cmds = self.manual_review_tests(finding_id, repo_name)
            
            if manual_pass:
                test_success = True
                if fix_cmds:
                    project_data['test_fix_commands'] = fix_cmds
                    self.log_success("Test fix commands updated")
            else:
                self.log_error("Tests failed manual review")
                return
        
        if test_success:
            self.log_success("Tests now pass")
            # Remove old test_fix_commands if tests now pass without them
            if 'test_fix_commands' in project_data and not fix_cmds:
                del project_data['test_fix_commands']
        else:
            self.log_error("Tests still fail")
            return
        
        # Save updated metadata
        self.metadata[str(finding_id)] = project_data
        self.save_metadata()
        self.log_success("Project updated successfully")
    
    def edit_project_patch(self, finding_id: int, project_data: Dict[str, Any]):
        """Update patch information for an existing project"""
        print(f"\n{Colors.WARNING}Updating patch information for finding ID {finding_id}...{Colors.ENDC}")
        
        # Create patch directory if it doesn't exist
        success, patch_path = self.add_patch_directory(finding_id)
        if not success:
            self.log_error("Failed to create patch directory")
            return
        
        # Ask for patch reference
        print(f"\n{Colors.BOLD}Please provide the patch reference:{Colors.ENDC}")
        print(f"{Colors.OKCYAN}Options:{Colors.ENDC}")
        print("  - Enter a GitHub PR/commit URL")
        print("  - Enter 'from_audit' if patch is described in the audit")
        print("  - Enter any other reference link")
        
        patch_ref = input(f"\n{Colors.BOLD}Patch reference: {Colors.ENDC}").strip()
        
        if patch_ref:
            project_data['patch'] = patch_path
            project_data['patch_ref'] = patch_ref
            self.log_success(f"Patch information updated: {patch_ref}")
            
            # Save updated metadata
            self.metadata[str(finding_id)] = project_data
            self.save_metadata()
        else:
            self.log_warning("No patch reference provided - update cancelled")
    
    def edit_project_poc(self, finding_id: int, project_data: Dict[str, Any]):
        """Add/update POC information for an existing project"""
        print(f"\n{Colors.WARNING}Updating POC information for finding ID {finding_id}...{Colors.ENDC}")
        
        # Ask if user wants to add/update POC
        response = input(f"\n{Colors.BOLD}Add/update POC for this vulnerability? (yes/no): {Colors.ENDC}").strip().lower()
        
        if response in ['yes', 'y']:
            # Create POC directory
            success, poc_path = self.add_poc_directory(finding_id)
            if not success:
                self.log_error("Failed to create POC directory")
                return
            
            # Ask for POC reference
            print(f"\n{Colors.BOLD}Please provide the POC reference:{Colors.ENDC}")
            print(f"{Colors.OKCYAN}Options:{Colors.ENDC}")
            print("  - Enter a GitHub URL with POC code")
            print("  - Enter a link to exploit/attack code")
            print("  - Enter any other POC reference")
            
            poc_ref = input(f"\n{Colors.BOLD}POC reference URL: {Colors.ENDC}").strip()
            
            if poc_ref:
                project_data['poc_path'] = poc_path
                project_data['poc_ref'] = poc_ref
                self.log_success(f"POC information updated: {poc_ref}")
            else:
                self.log_warning("No POC reference provided - update cancelled")
                return
        else:
            # Remove POC information if user says no
            if 'poc_path' in project_data:
                del project_data['poc_path']
            if 'poc_ref' in project_data:
                del project_data['poc_ref']
            self.log_success("POC information removed")
        
        # Save updated metadata
        self.metadata[str(finding_id)] = project_data
        self.save_metadata()
    
    def edit_project_annotations(self, finding_id: int, project_data: Dict[str, Any]):
        """Update audit text/annotations for an existing project"""
        print(f"\n{Colors.WARNING}Updating annotations for finding ID {finding_id}...{Colors.ENDC}")
        
        # Ask for new audit text
        print(f"\n{Colors.BOLD}Enter new audit text (press Enter twice when done):{Colors.ENDC}")
        print(f"{Colors.OKCYAN}(This will replace existing annotations){Colors.ENDC}")
        
        audit_lines = []
        while True:
            line = input()
            if line == "" and len(audit_lines) > 0 and audit_lines[-1] == "":
                audit_lines.pop()  # Remove the last empty line
                break
            audit_lines.append(line)
        
        if audit_lines:
            audit_text = '\n'.join(audit_lines).strip()
            if audit_text:
                # Save new audit text
                annotations_path = self.save_audit_text(finding_id, audit_text)
                if annotations_path:
                    project_data['annotations'] = annotations_path
                    self.log_success("Annotations updated successfully")
                    
                    # Save updated metadata
                    self.metadata[str(finding_id)] = project_data
                    self.save_metadata()
                else:
                    self.log_error("Failed to save annotations")
            else:
                self.log_warning("No audit text provided - update cancelled")
        else:
            self.log_warning("No audit text provided - update cancelled")
    
    def edit_project_metadata(self, finding_id: int, project_data: Dict[str, Any]):
        """Update other metadata for an existing project"""
        print(f"\n{Colors.WARNING}Updating metadata for finding ID {finding_id}...{Colors.ENDC}")
        
        # Get additional information (reuse existing function)
        print("-"*70)
        print("Enter new values (press Enter to keep current value)")
        print("-"*70)
        
        # Show current values and ask for updates
        current_name = project_data.get('name', '')
        new_name = input(f"{Colors.BOLD}Project name (current: '{current_name}'): {Colors.ENDC}").strip()
        if new_name:
            project_data['name'] = new_name
            self.log_verbose(f"Name updated: {new_name}")
        
        current_main_contract = project_data.get('main_contract', '')
        new_main_contract = input(f"{Colors.BOLD}Main contract (current: '{current_main_contract}'): {Colors.ENDC}").strip()
        if new_main_contract:
            project_data['main_contract'] = new_main_contract
            self.log_verbose(f"Main contract updated: {new_main_contract}")
        
        current_expected_vuln = project_data.get('expected_vulnerability', '')
        new_expected_vuln = input(f"{Colors.BOLD}Expected vulnerability (current: '{current_expected_vuln}'): {Colors.ENDC}").strip()
        if new_expected_vuln:
            project_data['expected_vulnerability'] = new_expected_vuln
            self.log_verbose(f"Expected vulnerability updated: {new_expected_vuln}")
        
        current_difficulty = project_data.get('difficulty', '')
        new_difficulty = input(f"{Colors.BOLD}Difficulty (current: '{current_difficulty}'): {Colors.ENDC}").strip()
        if new_difficulty:
            project_data['difficulty'] = new_difficulty
            self.log_verbose(f"Difficulty updated: {new_difficulty}")
        
        current_audit_ref = project_data.get('audit_ref', '')
        new_audit_ref = input(f"{Colors.BOLD}Audit reference (current: '{current_audit_ref}'): {Colors.ENDC}").strip()
        if new_audit_ref:
            project_data['audit_ref'] = new_audit_ref
            self.log_verbose(f"Audit reference updated: {new_audit_ref}")
        
        # Save updated metadata
        self.metadata[str(finding_id)] = project_data
        self.save_metadata()
        self.log_success("Metadata updated successfully")
    
    def interactive_menu(self):
        """Main interactive menu"""
        while True:
            print("\n" + "="*70)
            print(f"{Colors.HEADER}{Colors.BOLD}DATASET MANAGEMENT MENU{Colors.ENDC}")
            print("="*70)
            print(f"{Colors.OKCYAN}1.{Colors.ENDC} Add new project")
            print(f"{Colors.OKCYAN}2.{Colors.ENDC} Edit existing project")
            print(f"{Colors.OKCYAN}3.{Colors.ENDC} List all projects")
            print(f"{Colors.OKCYAN}4.{Colors.ENDC} Exit")
            
            choice = input(f"\n{Colors.BOLD}Select an option (1-4): {Colors.ENDC}").strip()
            
            if choice == '1':
                self.process_project()
            elif choice == '2':
                self.edit_project_menu()
            elif choice == '3':
                self.list_projects()
            elif choice == '4':
                self.log_success("Goodbye!")
                break
            else:
                self.log_error("Invalid option. Please select 1, 2, 3, or 4.")
    
    def edit_project_menu(self):
        """Menu for selecting which project to edit"""
        if not self.metadata:
            self.log_warning("No projects in dataset")
            return
        
        # Show available projects
        self.list_projects()
        
        # Get finding ID to edit
        while True:
            try:
                finding_id = input(f"\n{Colors.BOLD}Enter finding ID to edit (or 'cancel' to abort): {Colors.ENDC}").strip()
                if finding_id.lower() == 'cancel':
                    self.log_warning("Edit cancelled")
                    return
                finding_id = int(finding_id)
                break
            except ValueError:
                self.log_error("Please enter a valid number")
            except KeyboardInterrupt:
                print("\nOperation cancelled")
                return
        
        # Edit the project
        self.edit_project(finding_id)

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
