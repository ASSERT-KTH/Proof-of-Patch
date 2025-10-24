#!/bin/bash

# Proof-of-Patch Dataset Configuration Script
# This script initializes and configures the dataset for use after cloning

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if we're in the right directory
check_directory() {
    if [ ! -f "dataset/dataset_metadata.json" ] || [ ! -d "dataset" ]; then
        print_error "Please run this script from the root of the Proof-of-Patch repository"
        exit 1
    fi
}

# Function to initialize submodules
init_submodules() {
    print_status "Initializing Git submodules..."
    
    if ! command_exists git; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    # Initialize and update submodules recursively
    git submodule update --init --recursive
    
    print_success "Submodules initialized successfully"
}

# Function to setup specific findings based on metadata
setup_findings() {
    print_status "Setting up specific findings configurations..."
    
    # Check if jq is available for JSON processing
    if ! command_exists jq; then
        print_warning "jq is not installed. Some automated setup features will be skipped."
        print_warning "Install jq with: sudo apt-get install jq (Ubuntu/Debian) or brew install jq (macOS)"
        return
    fi
    
    # Store the metadata file path (absolute path to avoid issues when changing directories)
    metadata_file="$(pwd)/dataset/dataset_metadata.json"
    
    # Process each finding from metadata
    print_status "Processing findings from dataset_metadata.json..."
    
    # Get all finding IDs from metadata
    finding_ids=$(jq -r 'keys[]' "$metadata_file")
    
    for finding_key in $finding_ids; do
        # finding_key is expected to already be zero-padded (e.g. 001, 015, 077)
        padded_id="$finding_key"
        finding_id=$(jq -r ".[\"$finding_key\"].finding_id" "$metadata_file" 2>/dev/null)
        display_id=${finding_id:-$padded_id}
        
        print_status "Setting up finding $display_id..."
        
        # Get finding data
        repo_name=$(jq -r ".[\"$finding_key\"].repo_name" "$metadata_file")
        target_directory=$(jq -r ".[\"$finding_key\"].target_directory" "$metadata_file" | tr -d '\n')
        test_commands=$(jq -r ".[\"$finding_key\"].test_fix_commands" "$metadata_file")
        
        # Convert relative paths to absolute paths if needed
        if [[ "$target_directory" == dataset/* ]]; then
            target_directory="$(pwd)/$target_directory"
        fi
        
        # Try the target directory from metadata first, then fall back to zero-padded format
        if [ "$target_directory" != "null" ] && [ -d "$target_directory" ]; then
            working_directory="$target_directory"
            print_status "Using target directory: $working_directory"
        elif [ -d "dataset/findings/$padded_id" ]; then
            # Find the actual repo directory inside (look for directories that are not the parent)
            repo_dir=$(find "dataset/findings/$padded_id" -maxdepth 1 -mindepth 1 -type d | head -1)
            if [ -n "$repo_dir" ]; then
                working_directory="$repo_dir"
                print_status "Using found repo directory: $working_directory"
            else
                working_directory="dataset/findings/$padded_id"
                print_status "Using base finding directory: $working_directory"
            fi
        else
            working_directory=""
            print_warning "No directory found for finding $display_id (tried: $target_directory and dataset/findings/$padded_id)"
        fi
        
        if [ -n "$working_directory" ] && [ -d "$working_directory" ]; then
            # Store the original directory
            original_dir=$(pwd)
            cd "$working_directory"
            
            # Apply specific configurations based on finding ID
            case $padded_id in
                "001")
                    print_status "Setting up finding 1 (2024-06-size)..."
                    # No special setup needed for this one
                    ;;
                "003")
                    print_status "Setting up finding 3 (2023-07-pooltogether)..."
                    # This has 3 submodules, needs special setup
                    if [ -d "accounts-v2" ]; then
                        cd accounts-v2
                        git submodule update --init --recursive
                        # Update foundry.toml to comment line 10 --no-match-path
                        if [ -f "foundry.toml" ]; then
                            sed -i 's/^--no-match-path/#--no-match-path/' foundry.toml
                        fi
                        cd ..
                    fi
                    ;;
                "008"|"051")
                    print_status "Setting up finding $display_id (2023-09-centrifuge)..."
                    # No special setup needed
                    ;;
                "009"|"018"|"033"|"048")
                    print_status "Setting up finding $display_id (2023-04-caviar)..."
                    # No special setup needed
                    ;;
                "015")
                    print_status "Setting up finding 15 (2023-07-pooltogether)..."
                    # Must be worked from vault/ directory
                    if [ -d "vault" ]; then
                        cd vault
                        print_warning "Note: This finding should be worked from the vault/ directory"
                    fi
                    ;;
                "020")
                    print_status "Setting up finding 20 (2023-12-dodo-gsp)..."
                    if [ -d "dodo-gassaving-pool" ]; then
                        cd dodo-gassaving-pool
                        if [ -f "package.json" ]; then
                            npm install
                        fi
                        cd ..
                    fi
                    ;;
                "032"|"058")
                    print_status "Setting up finding $display_id (2022-06-putty)..."
                    if [ -d "contracts" ]; then
                        cd contracts
                        if [ -f "package.json" ]; then
                            npm install
                        fi
                        cd ..
                    fi
                    ;;
                "039"|"041")
                    print_status "Setting up finding $display_id (2024-03-axis-finance)..."
                    if [ -d "moonraker" ]; then
                        cd moonraker
                        print_warning "Note: Tests should be run from moonraker/ directory"
                        cd ..
                    fi
                    ;;
                "042")
                    print_status "Setting up finding 42 (2025-07-cap)..."
                    if [ -d "cap-contracts" ]; then
                        cd cap-contracts
                        # No special setup needed
                        cd ..
                    fi
                    ;;
                "046")
                    print_status "Setting up finding 46 (2023-05-xeth)..."
                    # Needs MAINNET_RPC_URL in .env file
                    if [ ! -f ".env" ]; then
                        echo "MAINNET_RPC_URL=your_mainnet_rpc_url_here" > .env
                        print_warning "Created .env file. Please add your MAINNET_RPC_URL"
                    fi
                    # Check if foundry.toml exists, if not create a basic one
                    if [ ! -f "foundry.toml" ]; then
                        cat > foundry.toml << EOF
[profile.default]
src = "src"
out = "out"
libs = ["lib"]
solc = "0.8.19"
optimizer = true
optimizer_runs = 200
EOF
                        print_warning "Created basic foundry.toml file"
                    fi
                    ;;
                "049")
                    print_status "Setting up finding 49 (2023-08-cooler)..."
                    if [ -d "Cooler" ]; then
                        cd Cooler
                        # Add test configuration to foundry.toml
                        if [ -f "foundry.toml" ]; then
                            if ! grep -q "test = 'src/tests'" foundry.toml; then
                                echo "test = 'src/tests'" >> foundry.toml
                            fi
                        fi
                        cd ..
                    fi
                    ;;
                "054"|"098")
                    print_status "Setting up finding $display_id (2022-05-cally)..."
                    if [ -d "contracts" ]; then
                        cd contracts
                        if [ -f "package.json" ]; then
                            npm install
                        fi
                        cd ..
                    fi
                    ;;
                "066")
                    print_status "Setting up finding 66 (2023-11-kelp)..."
                    # No special setup needed
                    ;;
                "070")
                    print_status "Setting up finding 70 (2024-08-phi)..."
                    if [ -f "package.json" ]; then
                        npm install
                    fi
                    ;;
                "077")
                    print_status "Setting up finding 77 (2024-02-ai-arena)..."
                    # No special setup needed
                    ;;
                "091")
                    print_status "Setting up finding 91 (2023-07-basin)..."
                    # No special setup needed
                    ;;
                *)
                    print_warning "No specific setup defined for finding $display_id"
                    ;;
            esac
            
            # Return to original directory
            cd "$original_dir"
        else
            print_warning "Target directory not found for finding $display_id (tried: $target_directory and dataset/findings/$padded_id)"
        fi
    done
    
    print_success "Findings setup completed"
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing common dependencies..."
    
    # Check for Node.js projects
    if command_exists npm; then
        print_status "Installing Node.js dependencies where needed..."
        find dataset/findings -name "package.json" -execdir npm install \; 2>/dev/null || true
    else
        print_warning "npm not found. Node.js dependencies will not be installed."
    fi
    
    # Check for Foundry projects
    if command_exists forge; then
        print_status "Installing Foundry dependencies..."
        find dataset/findings -name "foundry.toml" -execdir forge install \; 2>/dev/null || true
    else
        print_warning "forge not found. Foundry dependencies will not be installed."
        print_warning "Install Foundry from: https://book.getfoundry.sh/getting-started/installation"
    fi
    
    print_success "Dependencies installation completed"
}

# Function to run basic tests
run_basic_tests() {
    print_status "Running basic tests to verify setup..."
    
    # Test a few key findings
    test_findings=("001" "003" "008" "015" "020" "032" "046" "054" "070" "077")
    
    for finding_key in "${test_findings[@]}"; do
        target_directory=$(jq -r ".[\"$finding_key\"].target_directory" "$metadata_file" 2>/dev/null)
        test_commands=$(jq -r ".[\"$finding_key\"].test_fix_commands" "$metadata_file" 2>/dev/null)
        finding_id=$(jq -r ".[\"$finding_key\"].finding_id" "$metadata_file" 2>/dev/null)
        display_id=${finding_id:-$finding_key}
        
        # Convert relative paths to absolute paths if needed
        if [[ "$target_directory" == dataset/* ]]; then
            target_directory="$(pwd)/$target_directory"
        fi
        
        # Try the target directory from metadata first, then fall back to zero-padded format
        if [ "$target_directory" != "null" ] && [ -d "$target_directory" ]; then
            working_directory="$target_directory"
        elif [ -d "dataset/findings/$finding_key" ]; then
            # Find the actual repo directory inside (look for directories that are not the parent)
            repo_dir=$(find "dataset/findings/$finding_key" -maxdepth 1 -mindepth 1 -type d | head -1)
            if [ -n "$repo_dir" ]; then
                working_directory="$repo_dir"
            else
                working_directory="dataset/findings/$finding_key"
            fi
        else
            working_directory=""
        fi
        
        if [ -n "$working_directory" ] && [ -d "$working_directory" ] && [ "$test_commands" != "null" ]; then
            print_status "Testing finding $display_id..."
            # Store the original directory
            original_dir=$(pwd)
            cd "$working_directory"
            
            # Run basic compilation test
            if command_exists forge && [ -f "foundry.toml" ]; then
                if forge build >/dev/null 2>&1; then
                    print_success "Finding $display_id compiles successfully"
                else
                    print_warning "Finding $display_id failed to compile"
                fi
            fi
            
            # Return to original directory
            cd "$original_dir"
        fi
    done
    
    print_success "Basic tests completed"
}

# Function to display usage information
show_usage() {
    echo "Proof-of-Patch Dataset Configuration Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --skip-submodules    Skip submodule initialization"
    echo "  --skip-deps          Skip dependency installation"
    echo "  --skip-tests         Skip basic tests"
    echo "  --help               Show this help message"
    echo ""
    echo "This script will:"
    echo "  1. Initialize Git submodules"
    echo "  2. Set up specific configurations for each finding"
    echo "  3. Install dependencies (npm, forge)"
    echo "  4. Run basic compilation tests"
    echo ""
}

# Main function
main() {
    echo "=========================================="
    echo "Proof-of-Patch Dataset Configuration"
    echo "=========================================="
    echo ""
    
    # Parse command line arguments
    SKIP_SUBMODULES=false
    SKIP_DEPS=false
    SKIP_TESTS=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-submodules)
                SKIP_SUBMODULES=true
                shift
                ;;
            --skip-deps)
                SKIP_DEPS=true
                shift
                ;;
            --skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Check if we're in the right directory
    check_directory
    
    # Initialize submodules
    if [ "$SKIP_SUBMODULES" = false ]; then
        init_submodules
    else
        print_warning "Skipping submodule initialization"
    fi
    
    # Setup specific findings
    setup_findings
    
    # Install dependencies
    if [ "$SKIP_DEPS" = false ]; then
        install_dependencies
    else
        print_warning "Skipping dependency installation"
    fi
    
    # Run basic tests
    if [ "$SKIP_TESTS" = false ]; then
        run_basic_tests
    else
        print_warning "Skipping basic tests"
    fi
    
    echo ""
    print_success "Dataset configuration completed successfully!"
    echo ""
    echo "Next steps:"
    echo "  1. Review the dataset_metadata.json for detailed information about each finding"
    echo "  2. Check individual finding directories for specific setup requirements"
    echo "  3. Run tests using the commands specified in the metadata"
    echo ""
    echo "For more information, see the README.md file."
}

# Run main function with all arguments
main "$@"