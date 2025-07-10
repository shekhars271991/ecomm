#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
    sleep 5
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
python app.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo -e "${YELLOW}⏳ Waiting for backend to start...${NC}"
sleep 3

# Check if backend is responding
if curl -s http://localhost:5001/api/categories > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend API started successfully on http://localhost:5001${NC}"
else
    echo -e "${RED}❌ Backend failed to start. Check backend.log for details.${NC}"
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
echo -e "${BLUE}│  Press Ctrl+C to stop all applications             │${NC}"
echo -e "${BLUE}│                                                     │${NC}"
echo -e "${BLUE}└─────────────────────────────────────────────────────┘${NC}"

# Wait for processes to complete
wait $BACKEND_PID $FRONTEND_PID 