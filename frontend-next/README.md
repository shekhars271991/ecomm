# QuickGrocery Next.js Frontend

A modern, professional grocery delivery web application built with Next.js, TypeScript, and Tailwind CSS. Inspired by popular grocery delivery apps like BlinkIt and Zepto.

## 🌟 Features

### ✨ Modern UI/UX
- **Professional Design**: Clean, modern interface inspired by leading grocery delivery apps
- **Responsive Layout**: Mobile-first design that works perfectly on all devices
- **Smooth Animations**: Framer Motion animations for delightful user interactions
- **Glassmorphism Effects**: Modern glass-like UI elements with backdrop blur
- **Custom Color Scheme**: Vibrant orange/yellow primary colors with professional styling

### 🛒 Core Functionality
- **Product Browsing**: Browse thousands of products by categories
- **Smart Search**: Real-time search with suggestions and filters
- **Shopping Cart**: Advanced cart with quantity management and discount calculations
- **User Authentication**: Secure login/registration system
- **Order Management**: Complete order tracking and history
- **Database Switching**: Toggle between MySQL and Aerospike databases

### 📱 User Experience
- **10-Minute Delivery Promise**: Prominent delivery time messaging
- **Category Navigation**: Visual category cards with icons
- **Quick Add to Cart**: Smooth quantity selection with plus/minus buttons
- **Real-time Updates**: Live cart count and instant feedback
- **Mobile Menu**: Slide-out navigation for mobile devices

### 🎨 Design Elements
- **Custom Icons**: Lucide React icons throughout the interface
- **Product Cards**: Beautiful product cards with hover effects
- **Loading States**: Skeleton loaders for smooth loading experience
- **Toast Notifications**: Beautiful toast messages for user feedback
- **Gradient Backgrounds**: Eye-catching gradients and color combinations

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+ (for backend)
- Docker (for MySQL database)

### Installation

1. **Install Dependencies**
   ```bash
   # Navigate to the frontend directory
   cd frontend-next
   
   # Install Node.js dependencies
   npm install
   ```

2. **Start the Application**
   ```bash
   # From the project root directory
   
   # Option 1: Using the shell script (recommended)
   ./run_app.sh -f next
   
   # Option 2: Using the Python runner
   python run_app.py -f next
   
   # Option 3: Start manually
   # Terminal 1: Start backend
   cd backend && python app.py
   
   # Terminal 2: Start Next.js frontend
   cd frontend-next && npm run dev
   ```

3. **Access the Application**
   - Frontend: http://localhost:4000
   - Backend API: http://localhost:5001
   - MySQL Database: localhost:3306

## 🛠️ Technology Stack

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Animation library for smooth interactions
- **React Query**: Data fetching and caching
- **React Hot Toast**: Beautiful notification system
- **Lucide React**: Modern icon library
- **Axios**: HTTP client for API requests

### Backend Integration
- **Flask REST API**: Python backend with comprehensive endpoints
- **MySQL + Aerospike**: Dual database support
- **Session Management**: Cart persistence across sessions
- **Real-time Updates**: Live cart and product updates

## 📁 Project Structure

```
frontend-next/
├── src/
│   ├── app/                 # Next.js App Router pages
│   │   ├── globals.css     # Global styles and Tailwind
│   │   ├── layout.tsx      # Root layout component
│   │   ├── page.tsx        # Homepage component
│   │   └── providers.tsx   # App-wide providers
│   ├── components/         # Reusable UI components
│   ├── lib/               # Utility functions and API
│   │   └── api.ts         # API service functions
│   ├── types/             # TypeScript type definitions
│   │   └── index.ts       # Application types
│   ├── hooks/             # Custom React hooks
│   └── utils/             # Helper utilities
├── package.json           # Dependencies and scripts
├── tailwind.config.js     # Tailwind CSS configuration
├── tsconfig.json          # TypeScript configuration
└── next.config.js         # Next.js configuration
```

## 🎨 Styling & Theming

### Color Palette
- **Primary**: Orange shades (#f1730c - #782c10)
- **Secondary**: Green shades (#22c55e - #14532d)
- **Accent**: Orange/yellow gradients
- **Neutral**: Gray scale for text and backgrounds

### Custom CSS Classes
```css
/* Buttons */
.btn-primary        /* Primary orange button */
.btn-secondary      /* Green button */
.btn-outline        /* Outlined button */
.btn-ghost          /* Transparent button */

/* Cards */
.card              /* Base card styling */
.card-hover        /* Card with hover effects */

/* Layout */
.category-grid     /* Responsive category grid */
.product-grid      /* Responsive product grid */

/* Animations */
.animate-float     /* Floating animation */
.animate-bounce-in /* Bounce entrance */
.animate-fade-in   /* Fade entrance */
```

## 🔧 Configuration

### Environment Variables
Create a `.env.local` file in the `frontend-next` directory:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:5001/api

# Application Settings
NEXT_PUBLIC_APP_NAME=QuickGrocery
NEXT_PUBLIC_DELIVERY_TIME=10
```

### Tailwind Configuration
The `tailwind.config.js` includes custom:
- Color scheme
- Font families (Inter & Poppins)
- Custom animations
- Responsive breakpoints
- Custom shadows and effects

## 📱 Responsive Design

### Breakpoints
- **Mobile**: < 640px (sm)
- **Tablet**: 640px - 1024px (md)
- **Desktop**: > 1024px (lg)

### Mobile Features
- Touch-friendly interface
- Slide-out navigation menu
- Optimized product grid
- Large tap targets
- Smooth scrolling

## 🔄 API Integration

### Key Endpoints
```typescript
// Products
GET /api/products               // Get all products
GET /api/products?category=1    // Filter by category
GET /api/products?search=apple  // Search products

// Cart
GET /api/cart                   // Get cart items
POST /api/cart                  // Add to cart
PUT /api/cart/:id              // Update quantity
DELETE /api/cart/:id           // Remove item

// Categories
GET /api/categories            // Get all categories

// Orders
GET /api/orders                // Get user orders
POST /api/orders               // Create order
```

### Error Handling
- Graceful error boundaries
- User-friendly error messages
- Automatic retry mechanisms
- Loading states and fallbacks

## 🚀 Deployment

### Development
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
```

### Production Build
1. Build the application: `npm run build`
2. Start production server: `npm run start`
3. Configure reverse proxy (nginx/Apache)
4. Set up environment variables
5. Enable HTTPS for production

## 🎯 Performance Optimizations

### Next.js Features
- **Server-Side Rendering**: Fast initial page loads
- **Image Optimization**: Automatic image optimization
- **Code Splitting**: Automatic bundle splitting
- **Static Generation**: Pre-rendered pages where possible

### Custom Optimizations
- **React Query**: Intelligent data caching
- **Debounced Search**: Reduced API calls
- **Lazy Loading**: Progressive image loading
- **Optimized Animations**: Hardware-accelerated CSS

## 🔮 Future Enhancements

### Planned Features
- **Progressive Web App**: Offline support and installability
- **Push Notifications**: Order updates and promotions
- **Dark Mode**: Theme switching capability
- **Advanced Filters**: Price range, ratings, availability
- **User Profiles**: Account management and preferences
- **Wishlist**: Save favorite products
- **Reviews & Ratings**: User feedback system

### Technical Improvements
- **Unit Testing**: Jest and React Testing Library
- **E2E Testing**: Playwright or Cypress
- **Bundle Analysis**: Webpack bundle analyzer
- **Performance Monitoring**: Web Vitals tracking
- **Accessibility**: WCAG compliance improvements

## 📄 License

This project is part of the QuickGrocery application suite.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For questions or support, please refer to the main project documentation or create an issue in the repository. 