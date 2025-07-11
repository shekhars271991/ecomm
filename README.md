# QuickGrocery - Multi-Database Grocery Delivery App

A modern grocery delivery application with Flask REST API backend supporting both MySQL and Aerospike Enterprise databases, featuring **dual frontend options**: a professional Next.js frontend (default) and a Flask frontend with real-time database switching capabilities.

## 🚀 Quick Start

### Option 1: Using the Python Script (Recommended)
```bash
# Start with Next.js frontend (default)
python run_app.py

# Or explicitly specify frontend
python run_app.py -f next      # Next.js frontend (modern, professional)
python run_app.py -f python    # Flask frontend (original)
```

### Option 2: Using the Shell Script (macOS/Linux)
```bash
# Start with Next.js frontend (default)
./run_app.sh

# Or explicitly specify frontend
./run_app.sh -f next           # Next.js frontend (modern, professional)
./run_app.sh -f python         # Flask frontend (original)
```

### Refresh Data Option
```bash
# Force refresh all data from CSV
./run_app.sh -r
./run_app.sh -r -f next        # Refresh with Next.js frontend
./run_app.sh -r -f python      # Refresh with Flask frontend

python run_app.py -r           # Python script version
python run_app.py -r -f next   # Refresh with Next.js frontend
```

Both scripts will:
- ✅ Check and start Docker containers (MySQL + Aerospike Enterprise)
- ✅ Install dependencies automatically (Node.js for Next.js, Python packages)
- ✅ Start backend API server (port 5001)
- ✅ Start your chosen frontend (Next.js on port 4000 or Flask on port 5000)
- ✅ Provide colored output and status updates
- ✅ Handle cleanup on exit (Ctrl+C)

## 📋 Prerequisites

### Required
- **Docker** - For MySQL and Aerospike Enterprise containers
- **Python 3.9+** - For the backend API and Flask frontend

### For Next.js Frontend (Default)
- **Node.js 18+** - For the modern frontend
- **npm** - Node package manager

## 🏗️ Architecture

### Backend API (Port 5001)
- **Framework**: Flask with Flask-RESTFUL
- **Database**: MySQL 8.0 + Aerospike Enterprise (Docker containers)
- **Database Abstraction**: `DatabaseManager` class supporting dual databases
- **API Endpoints**: REST API for all operations
- **Authentication**: Session-based with password hashing
- **Query Logging**: Database operations logged with execution times
- **Data Loading**: Smart CSV loading with skip logic and refresh option

### Frontend Options

#### Next.js Frontend (Port 4000) - **Default & Recommended**
- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS with custom design system
- **UI/UX**: Modern, professional design inspired by BlinkIt/Zepto
- **Features**: 
  - Responsive mobile-first design
  - Smooth animations with Framer Motion
  - Real-time cart updates with React Query
  - Beautiful toast notifications
  - Glassmorphism UI effects
  - Advanced search with suggestions
  - Professional product cards with hover effects

#### Flask Frontend (Port 5000) - **Original**
- **Framework**: Flask with Jinja2 templates
- **UI**: Bootstrap 5 with custom CSS
- **API Client**: Communicates with backend via REST API
- **Features**: Responsive design, real-time cart updates, database selection UI

### Database Options
- **MySQL Container**: `grocery_mysql` on port 3306
  - Database: `grocery_db`
  - User: `grocery_user` / Password: `grocery_password`
  - Full dataset with 1740+ products and 30+ categories

- **Aerospike Enterprise Container**: `aerospike` on port 3000
  - Namespace: `grocery`
  - Version: 6.4.0.0
  - Same dataset mirrored from MySQL

## 🎨 Frontend Comparison

| Feature | Next.js Frontend | Flask Frontend |
|---------|------------------|----------------|
| **Technology** | Next.js 14 + TypeScript | Flask + Jinja2 |
| **Styling** | Tailwind CSS + Custom | Bootstrap 5 |
| **Performance** | ⭐⭐⭐⭐⭐ Server-side rendering | ⭐⭐⭐ Traditional server rendering |
| **Design** | ⭐⭐⭐⭐⭐ Modern, professional | ⭐⭐⭐ Clean, functional |
| **Mobile Experience** | ⭐⭐⭐⭐⭐ Touch-optimized | ⭐⭐⭐ Responsive |
| **Animations** | ⭐⭐⭐⭐⭐ Smooth Framer Motion | ⭐⭐ Basic CSS transitions |
| **Load Time** | ⭐⭐⭐⭐⭐ Optimized bundles | ⭐⭐⭐ Standard loading |
| **Development** | ⭐⭐⭐⭐⭐ Hot reload, TypeScript | ⭐⭐⭐ Flask dev server |

## 🔄 Database Switching

### Real-time Database Switching
- Switch between MySQL and Aerospike Enterprise via the UI
- No application restart required
- Automatic data initialization for Aerospike
- Query logging with database type prefixes (MYSQL/AEROSPIKE)
- Available in both frontend options

## 🔧 Manual Setup (Alternative)

If you prefer to run components manually:

### 1. Start Database Containers
```bash
docker-compose up -d
```

### 2. Start Backend API
```bash
cd backend
pip install -r requirements.txt
python app.py                    # Normal startup
python app.py --refresh          # Force refresh data
```

### 3. Start Frontend (Choose One)

#### Next.js Frontend (Recommended)
```bash
cd frontend-next
npm install                      # First time only
npm run dev                      # Development server
```

#### Flask Frontend
```bash
pip install requests
cd frontend
python frontend_app.py
```

## 📊 API Endpoints

### Categories
- `GET /api/categories` - Get all categories

### Products
- `GET /api/products` - Get all products
- `GET /api/products/<id>` - Get specific product
- `GET /api/products?category=<id>` - Get products by category
- `GET /api/products?search=<term>` - Search products

### Users
- `POST /api/user` - Register/login user

### Cart
- `GET /api/cart` - Get cart items with discount calculation
- `POST /api/cart` - Add item to cart
- `PUT /api/cart/<id>` - Update cart item quantity
- `DELETE /api/cart/<id>` - Remove item from cart
- `DELETE /api/cart` - Clear entire cart

### Orders
- `POST /api/orders` - Create order
- `GET /api/orders` - Get user orders

### Database Management
- `GET /api/database-switch` - Get current database type
- `POST /api/database-switch` - Switch database type
- `GET /api/db-logs` - Get database query logs
- `DELETE /api/db-logs` - Clear database query logs

## 🎯 Key Features

### Smart Data Loading
- **Intelligent Startup**: Skips data loading if database already contains data
- **Force Refresh**: Use `-r` flag to reload all data from CSV
- **Graceful Errors**: Better error handling for database connection issues
- **Progress Tracking**: Clear status messages during data loading

### Database Management
- **Dual Database Support**: MySQL (relational) and Aerospike (NoSQL)
- **Real-time Switching**: Switch databases without restart
- **Query Logging**: Track all database operations with execution times
- **Automatic Initialization**: Data auto-populated in both databases
- **Database Abstraction**: Unified API regardless of backend database

### User Experience
- **Modern Design**: Professional UI inspired by leading grocery delivery apps
- **Responsive**: Mobile-first design that works on all devices
- **Fast Performance**: Optimized loading and smooth interactions
- **Real-time Updates**: Live cart updates and instant feedback
- **Discount System**: 10% discount when total items > 5

### Shopping Features
- **Advanced Search**: Real-time search with suggestions
- **Category Navigation**: Visual category cards with icons
- **Smart Cart**: Quantity management with discount calculations
- **Quick Actions**: One-click add to cart with quantity selectors
- **Order Management**: Complete checkout and order tracking

## 🛠️ Development

### Project Structure
```
rampup/
├── backend/
│   ├── app.py                     # Backend API server
│   ├── mysql_manager.py           # MySQL database operations
│   ├── aerospike_manager.py       # Aerospike database operations
│   ├── unified_database_manager.py # Database abstraction layer
│   ├── csv_data_loader.py         # Smart data loading from CSV
│   └── requirements.txt           # Backend dependencies
├── frontend-next/                 # Next.js Frontend (Default)
│   ├── src/
│   │   ├── app/                   # Next.js App Router pages
│   │   ├── components/            # Reusable UI components
│   │   ├── lib/                   # API client and utilities
│   │   └── types/                 # TypeScript definitions
│   ├── package.json               # Node.js dependencies
│   ├── tailwind.config.js         # Tailwind CSS configuration
│   └── README.md                  # Next.js frontend documentation
├── frontend/                      # Flask Frontend (Original)
│   ├── frontend_app.py            # Flask frontend application
│   ├── templates/                 # HTML templates
│   └── static/                    # CSS, JS, images
├── docker-compose.yml             # MySQL + Aerospike containers
├── aerospike.conf                 # Aerospike configuration
├── init.sql                       # MySQL database initialization
├── run_app.py                     # Python startup script with frontend selection
├── run_app.sh                     # Shell startup script with frontend selection
└── README.md                      # This file
```

### Frontend Development

#### Next.js Frontend
```bash
cd frontend-next
npm run dev          # Development server with hot reload
npm run build        # Production build
npm run start        # Production server
npm run lint         # Code linting
```

#### Flask Frontend
```bash
cd frontend
python frontend_app.py  # Development server
```

### Adding New Features

1. **Backend**: Add new API endpoints in `backend/app.py`
2. **Database**: Update both MySQL and Aerospike methods in respective managers
3. **Next.js Frontend**: Add components in `frontend-next/src/components/`
4. **Flask Frontend**: Add routes in `frontend/frontend_app.py`

## 🌟 Getting the Best Experience

**For the best user experience, we recommend:**
1. ✅ Use the **Next.js frontend** (default) for modern, professional UI
2. ✅ Use the **Python startup script** for cross-platform compatibility
3. ✅ Run with **Docker** for easy database management
4. ✅ Use **MySQL database** for full dataset (1740+ products)

```bash
# Recommended startup command
python run_app.py -f next
```

Access the application at:
- **Next.js Frontend**: http://localhost:4000 (Recommended)
- **Flask Frontend**: http://localhost:5000 (Alternative)
- **Backend API**: http://localhost:5001

Enjoy your modern grocery delivery app! 🛒✨ 