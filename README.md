# QuickGrocery - Grocery Delivery App

A modern Flask-based grocery delivery application with REST API backend and MySQL database.

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
- ✅ Check and start Docker/MySQL container
- ✅ Install dependencies automatically
- ✅ Start backend API server (port 5001)
- ✅ Start frontend application (port 5000)
- ✅ Provide colored output and status updates
- ✅ Handle cleanup on exit (Ctrl+C)

## 📋 Prerequisites

- **Docker** - For MySQL database
- **Python 3.9+** - For the applications
- **Git** - For cloning the repository

## 🏗️ Architecture

### Backend API (Port 5001)
- **Framework**: Flask with Flask-RESTFUL
- **Database**: MySQL 8.0 (Docker container)
- **API Endpoints**: REST API for all operations
- **Authentication**: Session-based with password hashing

### Frontend (Port 5000)
- **Framework**: Flask with Jinja2 templates
- **UI**: Bootstrap 5 with custom CSS
- **API Client**: Communicates with backend via REST API
- **Features**: Responsive design, real-time cart updates

### Database
- **MySQL Container**: `grocery_mysql` on port 3306
- **Database**: `grocery_db`
- **User**: `grocery_user` / Password: `grocery_password`

## 🔧 Manual Setup (Alternative)

If you prefer to run components manually:

### 1. Start MySQL Container
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

## 🎨 Features

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
│   └── requirements.txt    # Backend dependencies
├── frontend_app.py         # Frontend application
├── templates/              # HTML templates
├── static/                 # CSS, JS, images
├── docker-compose.yml      # MySQL container
├── init.sql               # Database initialization
├── run_app.py             # Python startup script
├── run_app.sh             # Shell startup script
└── README.md              # This file
```

### Adding New Features

1. **Backend**: Add new API endpoints in `backend/app.py`
2. **Frontend**: Add new routes in `frontend_app.py`
3. **Database**: Update models in both files
4. **Templates**: Add/modify HTML templates
5. **Styling**: Update `static/css/style.css`

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**
   - Kill existing processes: `pkill -f python`
   - Check ports: `lsof -i :5000` or `lsof -i :5001`

2. **MySQL connection issues**
   - Restart container: `docker-compose restart`
   - Check container: `docker ps`

3. **Dependencies missing**
   - The startup scripts handle this automatically
   - Manual install: `pip install -r requirements.txt`

### Log Files
- **Backend logs**: `backend.log`
- **Frontend logs**: `frontend.log`

View logs in real-time:
```bash
tail -f backend.log
tail -f frontend.log
```

## 📝 License

This project is for educational purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Happy Coding!** 🛒✨ 