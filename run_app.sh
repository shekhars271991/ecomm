#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse command line arguments
REFRESH_DATA=false
FRONTEND_TYPE="next"  # Default to Next.js
DATALOADER_TYPE="file"  # Default to CSV file loading
HELP=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--refresh)
            REFRESH_DATA=true
            shift
            ;;
        -f|--frontend)
            FRONTEND_TYPE="$2"
            shift 2
            ;;
        -d|--dataloader)
            DATALOADER_TYPE="$2"
            shift 2
            ;;
        -h|--help)
            HELP=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            HELP=true
            shift
            ;;
    esac
done

# Show help if requested
if [[ "$HELP" == true ]]; then
    echo -e "${BLUE}🍎 Grocery Delivery App Launcher${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -r, --refresh           Force refresh all data (truncates existing data)"
    echo "  -f, --frontend TYPE     Choose frontend type: 'next' (default) or 'python'"
    echo "  -d, --dataloader TYPE   Choose dataloader type: 'file' (default) or 'default'"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Dataloader Types:"
    echo "  file                    Load data from CSV file (GroceryDataset.csv) - 19 categories"
    echo "  default                 Load sample data (hardcoded) - 6 categories"
    echo ""
    echo "Examples:"
    echo "  $0                      # Normal startup with Next.js frontend and CSV data"
    echo "  $0 -f python            # Use Python Flask frontend with CSV data"
    echo "  $0 -d default           # Use sample data (6 categories)"
    echo "  $0 -d file              # Use CSV data (19 categories) - default"
    echo "  $0 -r                   # Force refresh CSV data"
    echo "  $0 -r -d default        # Force refresh with sample data"
    echo "  $0 -r -f next -d file   # Refresh CSV data with Next.js frontend"
    echo ""
    exit 0
fi

# Validate frontend type
if [[ "$FRONTEND_TYPE" != "next" && "$FRONTEND_TYPE" != "python" ]]; then
    echo -e "${RED}❌ Invalid frontend type: $FRONTEND_TYPE${NC}"
    echo -e "${YELLOW}Valid options: 'next' or 'python'${NC}"
    exit 1
fi

# Validate dataloader type
if [[ "$DATALOADER_TYPE" != "file" && "$DATALOADER_TYPE" != "default" ]]; then
    echo -e "${RED}❌ Invalid dataloader type: $DATALOADER_TYPE${NC}"
    echo -e "${YELLOW}Valid options: 'file' or 'default'${NC}"
    exit 1
fi

# Function to cleanup processes on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down applications...${NC}"
    
    # Kill backend process
    if [[ ! -z "$BACKEND_PID" ]]; then
        echo -e "${BLUE}Stopping backend (PID: $BACKEND_PID)...${NC}"
        kill $BACKEND_PID 2>/dev/null
    fi
    
    # Kill frontend process
    if [[ ! -z "$FRONTEND_PID" ]]; then
        echo -e "${BLUE}Stopping frontend (PID: $FRONTEND_PID)...${NC}"
        kill $FRONTEND_PID 2>/dev/null
    fi
    
    # Kill any remaining python/node processes related to our apps
    pkill -f "python.*backend/app.py" 2>/dev/null
    pkill -f "python.*frontend/frontend_app.py" 2>/dev/null
    pkill -f "node.*next.*dev" 2>/dev/null
    
    echo -e "${GREEN}Applications stopped successfully!${NC}"
    exit 0
}

# Set up trap to cleanup on exit
trap cleanup SIGINT SIGTERM EXIT

echo -e "${GREEN}🚀 Starting Grocery Delivery App...${NC}"

if [[ "$REFRESH_DATA" == true ]]; then
    echo -e "${YELLOW}🔄 Data refresh mode enabled - will reload all data from CSV${NC}"
fi

echo -e "${BLUE}📱 Frontend: $(echo $FRONTEND_TYPE | tr '[:lower:]' '[:upper:]')${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check if MySQL container is running
if ! docker ps | grep -q "grocery_mysql"; then
    echo -e "${YELLOW}📦 Starting MySQL container...${NC}"
    docker-compose up -d
    echo -e "${GREEN}✅ MySQL container started${NC}"
    echo -e "${YELLOW}⏳ Waiting for MySQL to be ready...${NC}"
    sleep 10
else
    echo -e "${GREEN}✅ MySQL container is already running${NC}"
fi

# Check if backend dependencies are installed
if [[ ! -d "backend/venv" ]] && [[ ! -f "backend/.venv_created" ]]; then
    echo -e "${YELLOW}📦 Installing backend dependencies...${NC}"
    cd backend
    pip install -r requirements.txt
    touch .venv_created
    cd ..
    echo -e "${GREEN}✅ Backend dependencies installed${NC}"
fi

# Frontend-specific dependency checks and setup
if [[ "$FRONTEND_TYPE" == "next" ]]; then
    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js is not installed. Please install Node.js first.${NC}"
        echo -e "${YELLOW}Visit: https://nodejs.org/en/download/${NC}"
        exit 1
    fi
    
    # Check if npm is installed
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}❌ npm is not installed. Please install npm first.${NC}"
        exit 1
    fi
    
    # Check if Next.js dependencies are installed
    if [[ ! -d "frontend-next/node_modules" ]]; then
        echo -e "${YELLOW}📦 Installing Next.js dependencies...${NC}"
        cd frontend-next
        npm install
        cd ..
        echo -e "${GREEN}✅ Next.js dependencies installed${NC}"
    fi
else
    # Check if Python frontend dependencies are installed
    if ! python -c "import requests" 2>/dev/null; then
        echo -e "${YELLOW}📦 Installing Python frontend dependencies...${NC}"
        pip install requests
        echo -e "${GREEN}✅ Python frontend dependencies installed${NC}"
    fi
fi

echo -e "${BLUE}🔧 Starting backend API server...${NC}"
cd backend

# Set up environment and build backend command with flags
export PYTHONPATH=.
if [[ "$REFRESH_DATA" == true ]]; then
    if [[ "$DATALOADER_TYPE" == "default" ]]; then
        echo -e "${YELLOW}🔄 Backend will refresh with sample data (6 categories)${NC}"
    else
        echo -e "${YELLOW}🔄 Backend will refresh with CSV data (19 categories)${NC}"
    fi
    python app.py --refresh --dataloader "$DATALOADER_TYPE" > ../backend.log 2>&1 &
else
    if [[ "$DATALOADER_TYPE" == "default" ]]; then
        echo -e "${BLUE}🔧 Backend starting with sample data (6 categories)${NC}"
    else
        echo -e "${BLUE}🔧 Backend starting with CSV data (19 categories)${NC}"
    fi
    python app.py --dataloader "$DATALOADER_TYPE" > ../backend.log 2>&1 &
fi

BACKEND_PID=$!
cd ..

# Wait for backend to start with appropriate messaging
if [[ "$REFRESH_DATA" == true ]]; then
    echo -e "${YELLOW}⏳ Waiting for backend to start (refreshing data from CSV...)${NC}"
    sleep 8
else
    echo -e "${YELLOW}⏳ Waiting for backend to start...${NC}"
    sleep 5
fi

# Check if backend is responding with retries
MAX_RETRIES=12
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:5001/api/categories > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend API started successfully on http://localhost:5001${NC}"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
            if [[ "$REFRESH_DATA" == true ]]; then
                echo -e "${YELLOW}⏳ Backend still loading data... (attempt $RETRY_COUNT/$MAX_RETRIES)${NC}"
                sleep 8
            else
                echo -e "${YELLOW}⏳ Backend still starting... (attempt $RETRY_COUNT/$MAX_RETRIES)${NC}"
                sleep 5
            fi
        fi
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}❌ Backend failed to start after $MAX_RETRIES attempts.${NC}"
    echo -e "${RED}📄 Check backend.log for details:${NC}"
    echo -e "${YELLOW}   tail -f backend.log${NC}"
    exit 1
fi

# Start the appropriate frontend
if [[ "$FRONTEND_TYPE" == "next" ]]; then
    echo -e "${BLUE}🌐 Starting Next.js frontend application...${NC}"
    cd frontend-next && npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    
    # Wait for Next.js to start
    echo -e "${YELLOW}⏳ Waiting for Next.js to start...${NC}"
    sleep 8
    
    # Check if Next.js is responding
    FRONTEND_URL="http://localhost:4000"
    MAX_FRONTEND_RETRIES=10
    FRONTEND_RETRY_COUNT=0
    
    while [ $FRONTEND_RETRY_COUNT -lt $MAX_FRONTEND_RETRIES ]; do
        if curl -s $FRONTEND_URL > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Next.js frontend started successfully on $FRONTEND_URL${NC}"
            break
        else
            FRONTEND_RETRY_COUNT=$((FRONTEND_RETRY_COUNT + 1))
            if [ $FRONTEND_RETRY_COUNT -lt $MAX_FRONTEND_RETRIES ]; then
                echo -e "${YELLOW}⏳ Next.js still starting... (attempt $FRONTEND_RETRY_COUNT/$MAX_FRONTEND_RETRIES)${NC}"
                sleep 3
            fi
        fi
    done
    
    if [ $FRONTEND_RETRY_COUNT -eq $MAX_FRONTEND_RETRIES ]; then
        echo -e "${RED}❌ Next.js frontend failed to start. Check frontend.log for details.${NC}"
        exit 1
    fi
else
    echo -e "${BLUE}🌐 Starting Python Flask frontend application...${NC}"
    cd frontend && python frontend_app.py > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    
    # Wait for Flask to start
    echo -e "${YELLOW}⏳ Waiting for Flask frontend to start...${NC}"
    sleep 3
    
    # Check if Flask is responding
    FRONTEND_URL="http://localhost:5000"
    if curl -s $FRONTEND_URL > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Flask frontend started successfully on $FRONTEND_URL${NC}"
    else
        echo -e "${RED}❌ Flask frontend failed to start. Check frontend.log for details.${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}🎉 All applications are running successfully!${NC}"
echo -e "${BLUE}┌─────────────────────────────────────────────────────┐${NC}"
echo -e "${BLUE}│                                                     │${NC}"
if [[ "$FRONTEND_TYPE" == "next" ]]; then
echo -e "${BLUE}│  🌐 Frontend:  http://localhost:4000 (Next.js)     │${NC}"
else
echo -e "${BLUE}│  🌐 Frontend:  http://localhost:5000 (Flask)       │${NC}"
fi
echo -e "${BLUE}│  🔧 Backend:   http://localhost:5001               │${NC}"
echo -e "${BLUE}│  🐳 MySQL:     localhost:3306                      │${NC}"
echo -e "${BLUE}│                                                     │${NC}"
echo -e "${BLUE}│  📄 Backend logs: tail -f backend.log              │${NC}"
echo -e "${BLUE}│  📄 Frontend logs: tail -f frontend.log            │${NC}"
echo -e "${BLUE}│                                                     │${NC}"
if [[ "$REFRESH_DATA" == true ]]; then
echo -e "${BLUE}│  🔄 Data was refreshed from CSV                     │${NC}"
echo -e "${BLUE}│                                                     │${NC}"
fi
echo -e "${BLUE}│  Frontend Type: $(printf "%-31s" "$(echo $FRONTEND_TYPE | tr '[:lower:]' '[:upper:]')")│${NC}"
echo -e "${BLUE}│                                                     │${NC}"
echo -e "${BLUE}│  Press Ctrl+C to stop all applications             │${NC}"
echo -e "${BLUE}│                                                     │${NC}"
echo -e "${BLUE}└─────────────────────────────────────────────────────┘${NC}"

# Wait for processes to complete
wait $BACKEND_PID $FRONTEND_PID 