#!/bin/bash

# Simple Assistant Setup Script
# Streamlined health data collection system setup

set -e  # Exit on any error

echo "🏥 Simple Assistant Setup - Streamlined Health Data Collection"
echo "============================================================"

# Color codes for output
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

# Function to check Python version
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python 3 found: $PYTHON_VERSION"
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version | cut -d' ' -f2)
        if [[ $PYTHON_VERSION == 3.* ]]; then
            print_success "Python found: $PYTHON_VERSION"
            PYTHON_CMD="python"
        else
            print_error "Python 3.8+ required. Found Python $PYTHON_VERSION"
            print_status "Please install Python 3.8+ from https://python.org"
            exit 1
        fi
    else
        print_error "Python not found. Please install Python 3.8+ from https://python.org"
        exit 1
    fi
}

# Function to check pip
check_pip() {
    if command -v pip3 &> /dev/null; then
        print_success "pip3 found"
        PIP_CMD="pip3"
    elif command -v pip &> /dev/null; then
        print_success "pip found"
        PIP_CMD="pip"
    else
        print_error "pip not found. Please install pip"
        exit 1
    fi
}

# Function to create project directory
setup_directory() {
    print_status "Setting up project directory..."
    
    # Create heltia directory if it doesn't exist
    mkdir -p ~/heltia
    cd ~/heltia
    
    # Check if directory already exists
    if [ -d "simple_assistant" ]; then
        print_warning "Directory 'simple_assistant' already exists. Pulling latest changes..."
        cd simple_assistant
        git pull origin main || git pull origin master
        cd ..
    else
        print_status "Cloning Simple Assistant repository..."
        git clone https://github.com/PoyrazTahan/simple_assistant.git
        print_success "Repository cloned successfully!"
    fi
    
    cd simple_assistant
    print_success "Project directory setup complete: $(pwd)"
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    # Install required packages
    $PIP_CMD install openai python-dotenv
    
    print_success "Dependencies installed successfully!"
}

# Function to setup environment file
setup_env_file() {
    print_status "Creating .env file..."
    
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# OpenAI API Key - Get from https://platform.openai.com/api-keys
OPENAI_API_KEY=put-your-key-here
EOF
        print_success ".env file created!"
    else
        print_warning ".env file already exists"
    fi
}

# Function to test the installation
test_installation() {
    print_status "Testing installation..."
    
    # Test if we can import required modules
    if $PYTHON_CMD -c "import openai; print('✅ OpenAI module available')"; then
        print_success "Installation test passed!"
        return 0
    else
        print_error "Installation test failed. Please check dependencies."
        return 1
    fi
}

# Function to open .env file for editing
open_env_file() {
    print_status "Opening .env file for API key setup..."
    
    # Open .env file in TextEdit on macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open -a TextEdit .env
        print_warning "📝 TextEdit opened with .env file"
        print_warning "Replace 'put-your-key-here' with your actual OpenAI API key"
    else
        print_warning "Please edit the .env file and add your OpenAI API key:"
        print_status "File location: $(pwd)/.env"
    fi
}

# Function to show next steps
show_next_steps() {
    echo ""
    echo "🎉 Setup Complete!"
    echo "=================="
    echo ""
    echo -e "${GREEN}Next steps:${NC}"
    echo ""
    echo "1. Add your OpenAI API key to the .env file (should be open in TextEdit)"
    echo -e "   ${YELLOW}Get your key from: https://platform.openai.com/api-keys${NC}"
    echo ""
    echo "2. Navigate to the project directory:"
    echo -e "   ${BLUE}cd ~/heltia/simple_assistant${NC}"
    echo ""
    echo "3. Run the Simple Assistant system:"
    echo -e "   ${BLUE}$PYTHON_CMD app.py${NC}                    # Interactive mode"
    echo -e "   ${BLUE}$PYTHON_CMD app.py --debug${NC}            # Debug mode"
    echo -e "   ${BLUE}$PYTHON_CMD app.py --full-prompt${NC}      # Full prompt mode"
    echo ""
    echo "4. Run automated tests:"
    echo -e "   ${BLUE}$PYTHON_CMD test.py${NC}                   # Run all tests"
    echo -e "   ${BLUE}$PYTHON_CMD test.py list${NC}              # List available tests"
    echo -e "   ${BLUE}$PYTHON_CMD test.py run 1${NC}             # Run specific test"
    echo ""
    echo -e "${YELLOW}📖 For more information, see the README.md file${NC}"
}

# Main installation flow
main() {
    print_status "Starting Simple Assistant setup..."
    
    # Step 1: Check Python and pip
    check_python
    check_pip
    
    # Step 2: Setup project directory
    setup_directory
    
    # Step 3: Install dependencies
    install_dependencies
    
    # Step 4: Setup environment file
    setup_env_file
    
    # Step 5: Test installation
    if test_installation; then
        # Step 6: Open .env file for editing
        open_env_file
        show_next_steps
    else
        print_error "Setup completed with errors. Please check the output above."
        exit 1
    fi
}

# Handle script interruption
trap 'echo -e "\n${RED}[ERROR]${NC} Setup interrupted. Please run the script again."; exit 1' INT

# Run main function
main

print_success "🏥 Simple Assistant setup completed successfully!"
echo -e "${YELLOW}Remember to add your OpenAI API key to the .env file before running the application!${NC}"