# QuickGrocery - Multi-Database Grocery Delivery App

A modern Flask-based grocery delivery application with REST API backend supporting both MySQL and Aerospike Enterprise databases with real-time switching capabilities.

## 🚀 Quick Start

### Option 1: Using the Python Script (Recommended)
```bash
python run_app.py
```

### Option 2: Using the Shell Script (macOS/Linux)
```bash
./run_app.sh
```

Both scripts will:
- ✅ Check and start Docker containers (MySQL + Aerospike Enterprise)
- ✅ Install dependencies automatically
- ✅ Start backend API server (port 5001)
- ✅ Start frontend application (port 5000)
- ✅ Provide colored output and status updates
- ✅ Handle cleanup on exit (Ctrl+C)

## 📋 Prerequisites

- **Docker** - For MySQL and Aerospike Enterprise containers
- **Python 3.9+** - For the applications
- **Git** - For cloning the repository

## 🏗️ Architecture

### Backend API (Port 5001)
- **Framework**: Flask with Flask-RESTFUL
- **Database**: MySQL 8.0 + Aerospike Enterprise (Docker containers)
- **Database Abstraction**: `DatabaseManager` class supporting dual databases
- **API Endpoints**: REST API for all operations
- **Authentication**: Session-based with password hashing
- **Query Logging**: Database operations logged with execution times

### Frontend (Port 5000)
- **Framework**: Flask with Jinja2 templates
- **UI**: Bootstrap 5 with custom CSS
- **API Client**: Communicates with backend via REST API
- **Features**: Responsive design, real-time cart updates, database selection UI

### Database Options
- **MySQL Container**: `grocery_mysql` on port 3306
  - Database: `grocery_db`
  - User: `grocery_user` / Password: `grocery_password`
  - Full dataset with 30+ products and 6 categories

- **Aerospike Enterprise Container**: `aerospike` on port 3000
  - Namespace: `grocery`
  - Version: 6.4.0.0
  - Sample dataset with 6 products and 6 categories

## 🔄 Database Switching

### Real-time Database Switching
- Switch between MySQL and Aerospike Enterprise via the UI dropdown
- No application restart required
- Automatic data initialization for Aerospike
- Query logging with database type prefixes (MYSQL/AEROSPIKE)

### Database Selection UI
- Dropdown menu in the navigation bar
- Shows current active database
- Instant switching with loading indicators
- Success/error notifications

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
python app.py
```

### 3. Start Frontend
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
- `POST /api/cart` - Add item to cart
- `PUT /api/cart` - Update cart item
- `DELETE /api/cart` - Remove from cart

### Orders
- `POST /api/orders` - Create order
- `GET /api/orders?user_id=<id>` - Get user orders

### Database Management
- `GET /api/database-switch` - Get current database type
- `POST /api/database-switch` - Switch database type
- `GET /api/db-logs` - Get database query logs
- `DELETE /api/db-logs` - Clear database query logs

## 🎨 Features

### Database Management
- **Dual Database Support**: MySQL (relational) and Aerospike (NoSQL)
- **Real-time Switching**: Switch databases without restart
- **Query Logging**: Track all database operations with execution times
- **Automatic Initialization**: Aerospike auto-populated with sample data
- **Database Abstraction**: Unified API regardless of backend database

### User Management
- User registration and login
- Secure password hashing
- Session management
- Profile management

### Product Catalog
- Category-based organization
- Search functionality
- Product details with images
- Stock management
- Availability tracking

### Shopping Cart
- Add/remove/update items
- Real-time quantity updates
- Persistent cart (session-based)
- Cart total calculations

### Order Management
- Complete checkout process
- Order confirmation
- Order history
- Status tracking
- Delivery address management

## 🛠️ Development

### Project Structure
```
rampup/
├── backend/
│   ├── app.py              # Backend API server
│   ├── database_manager.py # Database abstraction layer
│   └── requirements.txt    # Backend dependencies
├── frontend/
│   ├── frontend_app.py     # Frontend application
│   ├── templates/          # HTML templates
│   └── static/             # CSS, JS, images
├── docker-compose.yml      # MySQL + Aerospike containers
├── aerospike.conf          # Aerospike configuration
├── init.sql               # MySQL database initialization
├── run_app.py             # Python startup script
├── run_app.sh             # Shell startup script
└── README.md              # This file
```

### Database Architecture

#### MySQL Mode
- Full relational database with normalized tables
- Complete dataset with 30+ products
- Traditional SQL queries
- Foreign key relationships

#### Aerospike Mode
- NoSQL document store
- Sample dataset with 6 products and 6 categories
- Key-value operations
- Bins (fields) with JSON-like structure

### Adding New Features

1. **Backend**: Add new API endpoints in `backend/app.py`
2. **Database**: Update both MySQL and Aerospike methods in `database_manager.py`
3. **Frontend**: Add new routes in `frontend/frontend_app.py`
4. **Templates**: Add/modify HTML templates
5. **Styling**: Update `frontend/static/css/style.css`

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**
   - Kill existing processes: `pkill -f python`
   - Check ports: `lsof -i :5000` or `lsof -i :5001`

2. **Database connection issues**
   - Restart containers: `docker-compose restart`
   - Check containers: `docker ps`

3. **Aerospike connection issues**
   - Verify Aerospike container is running on port 3000
   - Check Aerospike logs: `docker logs aerospike`

4. **Dependencies missing**
   - The startup scripts handle this automatically
   - Manual install: `pip install -r requirements.txt`

5. **Database switching errors**
   - Check both database containers are running
   - Verify database initialization completed successfully

### Log Files
- **Backend logs**: `backend.log`
- **Frontend logs**: `frontend.log`
- **Database Query logs**: Available via `/api/db-logs` endpoint

View logs in real-time:
```bash
tail -f backend.log
tail -f frontend.log
```

### Docker Containers
```bash
# Check all containers
docker ps

# View container logs
docker logs grocery_mysql
docker logs aerospike

# Restart containers
docker-compose restart
```

## 📝 License

This project is for educational purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with both MySQL and Aerospike databases
5. Submit a pull request

---

**Happy Coding!** 🛒✨ Database switching made simple! 