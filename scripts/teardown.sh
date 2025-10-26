#!/bin/bash
#
# HoneyMesh Complete Teardown Script
# This script removes all HoneyMesh containers, networks, volumes, and data directories
#
# Usage: ./teardown_honeymesh.sh [OPTIONS]
# Options:
#   --keep-logs    Keep log files (don't delete honeypot-data/logs)
#   --keep-data    Keep all data directories (only remove containers)
#   --force        Skip confirmation prompts
#

set -e

# Color codes
RED='\033[91m'
GREEN='\033[92m'
YELLOW='\033[93m'
BLUE='\033[94m'
BOLD='\033[1m'
END='\033[0m'

# Default options
KEEP_LOGS=false
KEEP_DATA=false
FORCE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --keep-logs)
            KEEP_LOGS=true
            shift
            ;;
        --keep-data)
            KEEP_DATA=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --help)
            echo "HoneyMesh Teardown Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --keep-logs    Keep log files (don't delete honeypot-data/logs)"
            echo "  --keep-data    Keep all data directories (only remove containers)"
            echo "  --force        Skip confirmation prompts"
            echo "  --help         Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${END}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Function to print status messages
print_status() {
    local message=$1
    local status=${2:-"info"}
    
    case $status in
        "success")
            echo -e "${GREEN}[+]${END} $message"
            ;;
        "error")
            echo -e "${RED}[x]${END} $message"
            ;;
        "warning")
            echo -e "${YELLOW}[-]${END} $message"
            ;;
        *)
            echo -e "${BLUE}[i]${END} $message"
            ;;
    esac
}

# Function to check if running as root
check_root() {
    if [ "$EUID" -eq 0 ]; then
        print_status "Running as root - proceeding with elevated privileges" "warning"
        return 0
    else
        return 1
    fi
}

# Banner
echo -e "${BOLD}${RED}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           HoneyMesh Complete Teardown Script                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${END}"

# Show what will be removed
echo -e "${BOLD}This script will remove:${END}"
echo "  • All HoneyMesh Docker containers (honeymesh-*)"
echo "  • HoneyMesh Docker network"
echo "  • Docker volumes"

if [ "$KEEP_DATA" = false ]; then
    echo "  • honeypot-data directory (including configs and logs)"
    if [ "$KEEP_LOGS" = true ]; then
        echo "    ${GREEN}(logs will be preserved)${END}"
    fi
else
    echo "  ${GREEN}• Data directories will be preserved${END}"
fi

echo "  • honeymesh-logs directory"
echo ""

# Confirmation prompt unless --force is used
if [ "$FORCE" = false ]; then
    echo -e "${YELLOW}${BOLD}WARNING: This action cannot be undone!${END}"
    read -p "Are you sure you want to continue? (yes/no): " -r
    echo
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        print_status "Teardown cancelled by user" "warning"
        exit 0
    fi
fi

echo ""
print_status "Starting HoneyMesh teardown..." "info"
echo ""

# Step 1: Stop and remove containers
print_status "Stopping HoneyMesh containers..." "info"

# Check if honeypot-data directory exists with docker-compose.yml
if [ -d "./honeypot-data" ] && [ -f "./honeypot-data/docker-compose.yml" ]; then
    cd ./honeypot-data
    
    if command -v docker-compose &> /dev/null; then
        docker-compose down --volumes --remove-orphans 2>/dev/null || true
        print_status "Docker Compose services stopped" "success"
    else
        print_status "docker-compose not found, skipping compose down" "warning"
    fi
    
    cd ..
fi

# Stop individual containers by name pattern
CONTAINERS=$(docker ps -a --filter "name=honeymesh-" --format "{{.Names}}" 2>/dev/null || true)

if [ -n "$CONTAINERS" ]; then
    print_status "Found HoneyMesh containers:" "info"
    echo "$CONTAINERS" | while read -r container; do
        echo "  - $container"
    done
    
    echo "$CONTAINERS" | while read -r container; do
        docker stop "$container" 2>/dev/null || true
        docker rm "$container" 2>/dev/null || true
    done
    print_status "All HoneyMesh containers removed" "success"
else
    print_status "No HoneyMesh containers found" "info"
fi

# Step 2: Remove Docker network
print_status "Removing Docker network..." "info"

if docker network ls | grep -q "honeymesh"; then
    docker network rm honeymesh 2>/dev/null || true
    print_status "HoneyMesh network removed" "success"
else
    print_status "HoneyMesh network not found" "info"
fi

# Step 3: Clean up Docker volumes
print_status "Cleaning up Docker volumes..." "info"

VOLUMES=$(docker volume ls --filter "name=honeypot-data" --format "{{.Name}}" 2>/dev/null || true)

if [ -n "$VOLUMES" ]; then
    echo "$VOLUMES" | while read -r volume; do
        docker volume rm "$volume" 2>/dev/null || true
    done
    print_status "Docker volumes removed" "success"
else
    print_status "No related Docker volumes found" "info"
fi

# Step 4: Remove data directories
if [ "$KEEP_DATA" = false ]; then
    print_status "Removing data directories..." "info"
    
    if [ -d "./honeypot-data" ]; then
        if [ "$KEEP_LOGS" = true ]; then
            # Backup logs
            if [ -d "./honeypot-data/logs" ]; then
                BACKUP_DIR="./honeymesh-logs-backup-$(date +%Y%m%d_%H%M%S)"
                mkdir -p "$BACKUP_DIR"
                cp -r ./honeypot-data/logs/* "$BACKUP_DIR/" 2>/dev/null || true
                print_status "Logs backed up to: $BACKUP_DIR" "success"
            fi
        fi
        
        # Remove the directory
        if check_root; then
            rm -rf ./honeypot-data
        else
            # Try without sudo first
            rm -rf ./honeypot-data 2>/dev/null || sudo rm -rf ./honeypot-data
        fi
        
        print_status "honeypot-data directory removed" "success"
    else
        print_status "honeypot-data directory not found" "info"
    fi
else
    print_status "Keeping honeypot-data directory as requested" "info"
fi

# Step 5: Remove honeymesh-logs directory
print_status "Removing honeymesh-logs directory..." "info"

if [ -d "./honeymesh-logs" ]; then
    if check_root; then
        rm -rf ./honeymesh-logs
    else
        rm -rf ./honeymesh-logs 2>/dev/null || sudo rm -rf ./honeymesh-logs
    fi
    print_status "honeymesh-logs directory removed" "success"
else
    print_status "honeymesh-logs directory not found" "info"
fi

# Step 6: Clean up any backup directories (optional)
BACKUPS=$(ls -d ./honeymesh-backup-* 2>/dev/null || true)

if [ -n "$BACKUPS" ]; then
    echo ""
    print_status "Found backup directories:" "info"
    echo "$BACKUPS"
    
    if [ "$FORCE" = false ]; then
        read -p "Do you want to remove backup directories too? (yes/no): " -r
        echo
        if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            echo "$BACKUPS" | while read -r backup; do
                if check_root; then
                    rm -rf "$backup"
                else
                    rm -rf "$backup" 2>/dev/null || sudo rm -rf "$backup"
                fi
            done
            print_status "Backup directories removed" "success"
        else
            print_status "Keeping backup directories" "info"
        fi
    fi
fi

# Step 7: Prune Docker system (optional)
echo ""
print_status "Docker system cleanup..." "info"

if [ "$FORCE" = false ]; then
    read -p "Run 'docker system prune' to clean up unused Docker resources? (yes/no): " -r
    echo
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        docker system prune -f
        print_status "Docker system pruned" "success"
    fi
else
    docker system prune -f
    print_status "Docker system pruned" "success"
fi

# Final summary
echo ""
echo -e "${GREEN}${BOLD}════════════════════════════════════════════════════════${END}"
echo -e "${GREEN}${BOLD}  HoneyMesh Teardown Complete!${END}"
echo -e "${GREEN}${BOLD}════════════════════════════════════════════════════════${END}"
echo ""

print_status "Summary of actions:" "info"
echo "  ✓ Docker containers stopped and removed"
echo "  ✓ Docker networks removed"
echo "  ✓ Docker volumes cleaned up"

if [ "$KEEP_DATA" = false ]; then
    echo "  ✓ Data directories removed"
else
    echo "  • Data directories preserved"
fi

if [ "$KEEP_LOGS" = true ] && [ -d "./honeymesh-logs-backup-"* ]; then
    echo "  ✓ Logs backed up"
fi

echo ""
print_status "Your system is now clean of HoneyMesh components" "success"
echo ""

exit 0
