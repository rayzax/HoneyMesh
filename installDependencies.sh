#!/bin/bash
################################################################################
# HoneyMesh Dependency Installation Script
# Automatically installs and configures all required dependencies
#
# This script installs:
# - Docker & Docker Compose
# - Python 3.7+ and pip
# - curl
# - Python packages (docker, PyYAML, requests)
# - Configures Docker permissions
#
# Usage: sudo ./install-dependencies.sh
################################################################################

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[+]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[-]${NC} $1"
}

log_error() {
    echo -e "${RED}[x]${NC} $1"
}

log_header() {
    echo -e "\n${CYAN}${BOLD}===========================================================================${NC}"
    echo -e "${CYAN}${BOLD}$1${NC}"
    echo -e "${CYAN}${BOLD}===========================================================================${NC}\n"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        echo -e "${YELLOW}Usage: sudo $0${NC}"
        exit 1
    fi
}

# Get the actual user (not root when using sudo)
get_actual_user() {
    if [[ -n "$SUDO_USER" ]]; then
        echo "$SUDO_USER"
    else
        echo "$USER"
    fi
}

# Detect Linux distribution
detect_distro() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        DISTRO=$ID
        VERSION=$VERSION_ID
    elif [[ -f /etc/debian_version ]]; then
        DISTRO="debian"
    elif [[ -f /etc/redhat-release ]]; then
        DISTRO="rhel"
    else
        DISTRO="unknown"
    fi

    log_info "Detected distribution: $DISTRO"
}

# Check Python version
check_python_version() {
    log_header "Checking Python Version"

    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
        PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

        if [[ $PYTHON_MAJOR -eq 3 ]] && [[ $PYTHON_MINOR -ge 7 ]]; then
            log_success "Python $PYTHON_VERSION detected (requirement: 3.7+)"
            return 0
        else
            log_warning "Python $PYTHON_VERSION detected (requirement: 3.7+)"
            return 1
        fi
    else
        log_warning "Python3 not found"
        return 1
    fi
}

# Check system resources
check_system_resources() {
    log_header "Checking System Resources"

    # Check disk space
    DISK_FREE_GB=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
    if [[ $DISK_FREE_GB -ge 10 ]]; then
        log_success "Disk space: ${DISK_FREE_GB}GB available (recommended: 10GB+)"
    elif [[ $DISK_FREE_GB -ge 5 ]]; then
        log_warning "Disk space: ${DISK_FREE_GB}GB available (minimum: 5GB, recommended: 10GB)"
    else
        log_error "Disk space: ${DISK_FREE_GB}GB available (need at least 5GB)"
        return 1
    fi

    # Check memory
    if [[ -f /proc/meminfo ]]; then
        MEM_FREE_MB=$(grep MemAvailable /proc/meminfo | awk '{print int($2/1024)}')
        MEM_FREE_GB=$(echo "scale=1; $MEM_FREE_MB/1024" | bc)

        if [[ $MEM_FREE_MB -ge 4096 ]]; then
            log_success "Available memory: ${MEM_FREE_GB}GB (recommended: 4GB+)"
        elif [[ $MEM_FREE_MB -ge 2048 ]]; then
            log_warning "Available memory: ${MEM_FREE_GB}GB (minimum: 2GB, recommended: 4GB)"
        else
            log_error "Available memory: ${MEM_FREE_GB}GB (need at least 2GB)"
            return 1
        fi
    fi
}

# Install Docker
install_docker() {
    log_header "Installing Docker"

    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version)
        log_success "Docker already installed: $DOCKER_VERSION"
        return 0
    fi

    log_info "Installing Docker..."

    case $DISTRO in
        ubuntu|debian)
            # Update package index
            apt-get update

            # Install prerequisites
            apt-get install -y \
                ca-certificates \
                curl \
                gnupg \
                lsb-release

            # Add Docker's official GPG key
            mkdir -p /etc/apt/keyrings
            curl -fsSL https://download.docker.com/linux/$DISTRO/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

            # Set up repository
            echo \
                "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$DISTRO \
                $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

            # Install Docker Engine
            apt-get update
            apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

            log_success "Docker installed successfully"
            ;;

        fedora|rhel|centos)
            # Install dependencies
            dnf -y install dnf-plugins-core

            # Add Docker repository
            dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo

            # Install Docker
            dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

            log_success "Docker installed successfully"
            ;;

        *)
            log_error "Unsupported distribution: $DISTRO"
            log_info "Please install Docker manually from https://docs.docker.com/engine/install/"
            return 1
            ;;
    esac
}

# Install Docker Compose (standalone)
install_docker_compose() {
    log_header "Installing Docker Compose"

    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version)
        log_success "Docker Compose already installed: $COMPOSE_VERSION"
        return 0
    fi

    log_info "Installing Docker Compose..."

    case $DISTRO in
        ubuntu|debian)
            apt-get install -y docker-compose
            log_success "Docker Compose installed successfully"
            ;;

        fedora|rhel|centos)
            dnf install -y docker-compose
            log_success "Docker Compose installed successfully"
            ;;

        *)
            log_warning "Installing Docker Compose via pip as fallback..."
            pip3 install docker-compose
            ;;
    esac
}

# Install system packages
install_system_packages() {
    log_header "Installing System Packages"

    case $DISTRO in
        ubuntu|debian)
            log_info "Updating package lists..."
            apt-get update

            log_info "Installing required packages..."
            apt-get install -y \
                python3 \
                python3-pip \
                curl \
                git \
                bc

            log_success "System packages installed"
            ;;

        fedora|rhel|centos)
            log_info "Installing required packages..."
            dnf install -y \
                python3 \
                python3-pip \
                curl \
                git \
                bc

            log_success "System packages installed"
            ;;

        *)
            log_error "Unsupported distribution for automatic package installation"
            return 1
            ;;
    esac
}

# Install Python packages
install_python_packages() {
    log_header "Installing Python Packages"

    ACTUAL_USER=$(get_actual_user)

    # Check if requirements.txt exists
    if [[ -f "requirements.txt" ]]; then
        log_info "Installing packages from requirements.txt..."

        # Install as the actual user (not root)
        if [[ -n "$SUDO_USER" ]]; then
            sudo -u "$ACTUAL_USER" pip3 install --user -r requirements.txt
        else
            pip3 install -r requirements.txt
        fi

        log_success "Python packages installed from requirements.txt"
    else
        log_warning "requirements.txt not found, installing packages manually..."

        # Install packages manually
        PACKAGES="docker>=6.0.0 PyYAML>=6.0 requests>=2.28.0"

        if [[ -n "$SUDO_USER" ]]; then
            sudo -u "$ACTUAL_USER" pip3 install --user $PACKAGES
        else
            pip3 install $PACKAGES
        fi

        log_success "Python packages installed manually"
    fi
}

# Configure Docker
configure_docker() {
    log_header "Configuring Docker"

    ACTUAL_USER=$(get_actual_user)

    # Start Docker service
    log_info "Starting Docker service..."
    systemctl start docker
    systemctl enable docker
    log_success "Docker service started and enabled"

    # Add user to docker group
    if id -nG "$ACTUAL_USER" | grep -qw docker; then
        log_success "User '$ACTUAL_USER' is already in docker group"
    else
        log_info "Adding user '$ACTUAL_USER' to docker group..."
        usermod -aG docker "$ACTUAL_USER"
        log_success "User '$ACTUAL_USER' added to docker group"
        log_warning "User must logout and login again for group changes to take effect"
    fi
}

# Verify installation
verify_installation() {
    log_header "Verifying Installation"

    local errors=0

    # Check Docker
    if command -v docker &> /dev/null; then
        log_success "Docker: $(docker --version)"
    else
        log_error "Docker: Not found"
        ((errors++))
    fi

    # Check Docker Compose
    if command -v docker-compose &> /dev/null; then
        log_success "Docker Compose: $(docker-compose --version)"
    else
        log_error "Docker Compose: Not found"
        ((errors++))
    fi

    # Check curl
    if command -v curl &> /dev/null; then
        log_success "curl: $(curl --version | head -n1)"
    else
        log_error "curl: Not found"
        ((errors++))
    fi

    # Check Python
    if command -v python3 &> /dev/null; then
        log_success "Python3: $(python3 --version)"
    else
        log_error "Python3: Not found"
        ((errors++))
    fi

    # Check Python packages
    ACTUAL_USER=$(get_actual_user)
    for package in docker yaml requests; do
        if sudo -u "$ACTUAL_USER" python3 -c "import $package" 2>/dev/null; then
            log_success "Python package '$package': Installed"
        else
            log_error "Python package '$package': Not found"
            ((errors++))
        fi
    done

    # Check Docker service
    if systemctl is-active --quiet docker; then
        log_success "Docker service: Running"
    else
        log_error "Docker service: Not running"
        ((errors++))
    fi

    return $errors
}

# Print next steps
print_next_steps() {
    log_header "Installation Complete!"

    ACTUAL_USER=$(get_actual_user)

    echo -e "${GREEN}${BOLD}All dependencies have been installed successfully!${NC}\n"

    echo -e "${YELLOW}${BOLD}IMPORTANT NEXT STEPS:${NC}"
    echo -e "${YELLOW}1. Logout and login again for Docker group changes to take effect${NC}"
    echo -e "${YELLOW}2. Verify installation by running:${NC}"
    echo -e "   ${CYAN}python3 scripts/DependencyCheck.py${NC}"
    echo -e "${YELLOW}3. Start HoneyMesh:${NC}"
    echo -e "   ${CYAN}python3 honeymesh.py${NC}\n"

    echo -e "${BLUE}${BOLD}Optional:${NC}"
    echo -e "• Check Docker status: ${CYAN}docker ps${NC}"
    echo -e "• Test Docker access: ${CYAN}docker run hello-world${NC}"
    echo -e "• View Docker info: ${CYAN}docker info${NC}\n"

}

# Main installation flow
main() {
    log_header "HoneyMesh Dependency Installer"

    echo -e "${CYAN}This script will install all required dependencies for HoneyMesh:${NC}"
    echo -e "  • Docker & Docker Compose"
    echo -e "  • Python 3.7+ and pip"
    echo -e "  • curl"
    echo -e "  • Python packages (docker, PyYAML, requests)"
    echo -e "  • Docker group configuration\n"

    # Check if running as root
    check_root

    # Detect distribution
    detect_distro

    # Check system resources
    if ! check_system_resources; then
        log_error "System does not meet minimum requirements"
        read -p "Continue anyway? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Installation cancelled"
            exit 1
        fi
    fi

    # Install system packages
    if ! install_system_packages; then
        log_error "Failed to install system packages"
        exit 1
    fi

    # Check Python version
    if ! check_python_version; then
        log_warning "Python version check failed, but continuing..."
    fi

    # Install Docker
    if ! install_docker; then
        log_error "Failed to install Docker"
        exit 1
    fi

    # Install Docker Compose
    if ! install_docker_compose; then
        log_error "Failed to install Docker Compose"
        exit 1
    fi

    # Configure Docker
    if ! configure_docker; then
        log_error "Failed to configure Docker"
        exit 1
    fi

    # Install Python packages
    if ! install_python_packages; then
        log_error "Failed to install Python packages"
        exit 1
    fi

    # Verify installation
    if verify_installation; then
        print_next_steps
        exit 0
    else
        log_error "Installation verification failed"
        log_info "Please check the errors above and try again"
        exit 1
    fi
}

# Run main function
main "$@"
