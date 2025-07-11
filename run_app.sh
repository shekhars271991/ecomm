#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse command line arguments
REFRESH_DATA=false
HELP=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--refresh)
            REFRESH_DATA=true
            shift
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
    echo "  -r, --refresh    Force refresh all data from CSV (truncates existing data)"
    echo "  -h, --help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0               # Normal startup (skip data load if data exists)"
    echo "  $0 -r            # Force refresh all data"
    echo "  $0 --refresh     # Force refresh all data (long form)"
    echo ""
    exit 0
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
    
    # Kill any remaining python processes related to our apps
    pkill -f "python.*backend/app.py" 2>/dev/null
    pkill -f "python.*frontend/frontend_app.py" 2>/dev/null
    
    echo -e "${GREEN}Applications stopped successfully!${NC}"
    exit 0
}

# Set up trap to cleanup on exit
trap cleanup SIGINT SIGTERM EXIT

echo -e "${GREEN}🚀 Starting Grocery Delivery App...${NC}"

if [[ "$REFRESH_DATA" == true ]]; then
    echo -e "${YELLOW}🔄 Data refresh mode enabled - will reload all data from CSV${NC}"
fi

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

# Check if frontend dependencies are installed
if ! python -c "import requests" 2>/dev/null; then
    echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
    pip install requests
    echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
fi

echo -e "${BLUE}🔧 Starting backend API server...${NC}"
cd backend

# Set up environment and build backend command with refresh flag if needed
export PYTHONPATH=.
if [[ "$REFRESH_DATA" == true ]]; then
    echo -e "${YELLOW}🔄 Backend will refresh all data from CSV${NC}"
    python app.py --refresh > ../backend.log 2>&1 &
else
    python app.py > ../backend.log 2>&1 &
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

echo -e "${BLUE}🌐 Starting frontend application...${NC}"
cd frontend && python frontend_app.py > ../frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start
echo -e "${YELLOW}⏳ Waiting for frontend to start...${NC}"
sleep 3

# Check if frontend is responding
if curl -s http://localhost:5000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend started successfully on http://localhost:5000${NC}"
else
    echo -e "${RED}❌ Frontend failed to start. Check frontend.log for details.${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 All applications are running successfully!${NC}"
echo -e "${BLUE}┌─────────────────────────────────────────────────────┐${NC}"
echo -e "${BLUE}│                                                     │${NC}"
echo -e "${BLUE}│  🌐 Frontend:  http://localhost:5000               │${NC}"
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
echo -e "${BLUE}│  Press Ctrl+C to stop all applications             │${NC}"
echo -e "${BLUE}│                                                     │${NC}"
echo -e "${BLUE}└─────────────────────────────────────────────────────┘${NC}"

# Wait for processes to complete
wait $BACKEND_PID $FRONTEND_PID 