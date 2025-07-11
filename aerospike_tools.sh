#!/bin/bash

# Aerospike Tools Helper Script
# This script provides easy access to Aerospike tools

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Aerospike Tools Helper${NC}"
echo -e "${BLUE}Connecting to Aerospike container...${NC}"

# Check if aerospike-tools container is running
if ! docker ps | grep -q "grocery_aerospike_tools"; then
    echo -e "${YELLOW}⚠️  Aerospike tools container is not running. Starting containers...${NC}"
    docker-compose up -d
    sleep 5
fi

# Function to run AQL (Aerospike Query Language)
aql() {
    echo -e "${BLUE}🔍 Connecting to Aerospike via AQL...${NC}"
    echo -e "${YELLOW}Host: aerospike:3000${NC}"
    docker exec -it grocery_aerospike_tools aql -h aerospike -p 3000
}

# Function to run ASADM (Aerospike Admin)
asadm() {
    echo -e "${BLUE}⚙️  Connecting to Aerospike via ASADM...${NC}"
    echo -e "${YELLOW}Host: aerospike:3000${NC}"
    docker exec -it grocery_aerospike_tools asadm -h aerospike -p 3000
}

# Function to show cluster info
info() {
    echo -e "${BLUE}ℹ️  Getting Aerospike cluster info...${NC}"
    docker exec grocery_aerospike_tools asinfo -h aerospike -p 3000
}

# Function to show namespace info
namespace() {
    echo -e "${BLUE}📊 Getting namespace info...${NC}"
    docker exec grocery_aerospike_tools asinfo -h aerospike -p 3000 -v "namespaces"
    echo ""
    echo -e "${BLUE}📋 Namespace 'grocery' details:${NC}"
    docker exec grocery_aerospike_tools asinfo -h aerospike -p 3000 -v "namespace/grocery"
}

# Function to list all sets in grocery namespace
sets() {
    echo -e "${BLUE}📦 Getting sets in 'grocery' namespace...${NC}"
    docker exec grocery_aerospike_tools asinfo -h aerospike -p 3000 -v "sets/grocery"
}

# Function to show help
help() {
    echo -e "${GREEN}Available commands:${NC}"
    echo -e "  ${BLUE}./aerospike_tools.sh aql${NC}       - Connect to AQL (Aerospike Query Language)"
    echo -e "  ${BLUE}./aerospike_tools.sh asadm${NC}     - Connect to ASADM (Aerospike Admin)"
    echo -e "  ${BLUE}./aerospike_tools.sh info${NC}      - Show cluster information"
    echo -e "  ${BLUE}./aerospike_tools.sh namespace${NC} - Show namespace information"
    echo -e "  ${BLUE}./aerospike_tools.sh sets${NC}      - List all sets in grocery namespace"
    echo -e "  ${BLUE}./aerospike_tools.sh help${NC}      - Show this help message"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo -e "  ${BLUE}# Connect to AQL and run queries${NC}"
    echo -e "  ./aerospike_tools.sh aql"
    echo -e "  aql> SELECT * FROM grocery.products"
    echo ""
    echo -e "  ${BLUE}# Get cluster status${NC}"
    echo -e "  ./aerospike_tools.sh info"
    echo ""
    echo -e "  ${BLUE}# Check what data sets exist${NC}"
    echo -e "  ./aerospike_tools.sh sets"
}

# Parse command line arguments
case "$1" in
    "aql")
        aql
        ;;
    "asadm")
        asadm
        ;;
    "info")
        info
        ;;
    "namespace")
        namespace
        ;;
    "sets")
        sets
        ;;
    "help"|"--help"|"-h"|"")
        help
        ;;
    *)
        echo -e "${YELLOW}Unknown command: $1${NC}"
        echo ""
        help
        ;;
esac 