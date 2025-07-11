'use client'

import { useState, useEffect } from 'react'
import { ShoppingCart, Search, Clock, Truck, Star, Plus, Minus, Filter, MapPin, User, Heart, Menu, X, ArrowRight, Database, ChevronDown } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useQuery } from 'react-query'
import toast from 'react-hot-toast'
import { apiService, formatPrice, handleApiError } from '@/lib/api'
import { renderIcon } from '@/lib/iconMapping'
import type { Product, Category, Cart } from '@/types'
import Image from 'next/image'

export default function HomePage() {
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [cartItems, setCartItems] = useState<Cart | null>(null)
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [quantities, setQuantities] = useState<Record<number, number>>({})
  const [currentDatabase, setCurrentDatabase] = useState<string>('mysql')
  const [showDatabaseDropdown, setShowDatabaseDropdown] = useState(false)
  const [showQueryLog, setShowQueryLog] = useState(false)
  const [queryLog, setQueryLog] = useState<any[]>([])
  const [queryFilter, setQueryFilter] = useState<string>('all') // 'all', 'mysql', 'aerospike'

  // Fetch categories
  const { data: categories = [], isLoading: categoriesLoading } = useQuery('categories', async () => {
    try {
      const response = await fetch('/api/categories')
      const data = await response.json()
      
      // Extract query log from debug info if available
      if (data?.debug?.recent_queries) {
        setQueryLog(data.debug.recent_queries)
      }
      
      return data.data || []
    } catch (error) {
      return apiService.getCategories()
    }
  })

  // Fetch products
  const { data: products = [], isLoading: productsLoading } = useQuery(
    ['products', selectedCategory, searchQuery],
    () => apiService.getProducts({ category: selectedCategory || undefined, search: searchQuery || undefined }),
    { enabled: true }
  )

  // Fetch cart
  const { data: cart, refetch: refetchCart } = useQuery('cart', apiService.getCart)

  // Fetch current database
  const { data: dbInfo } = useQuery('database-info', apiService.getCurrentDatabase, {
    onSuccess: (data) => {
      setCurrentDatabase(data.current_database)
    }
  })

  const handleAddToCart = async (productId: number, quantity: number = 1) => {
    try {
      await apiService.addToCart(productId, quantity)
      toast.success('Added to cart!')
      refetchCart()
      setQuantities(prev => ({ ...prev, [productId]: 0 }))
    } catch (error) {
      toast.error(handleApiError(error))
    }
  }

  const handleDatabaseSwitch = async (database: 'mysql' | 'aerospike') => {
    try {
      await apiService.switchDatabase(database)
      setCurrentDatabase(database)
      toast.success(`Switched to ${database.toUpperCase()} database`)
      // Refetch data after switching
      window.location.reload()
    } catch (error) {
      toast.error(handleApiError(error))
    }
  }

  const updateQuantity = (productId: number, delta: number) => {
    setQuantities(prev => ({
      ...prev,
      [productId]: Math.max(0, (prev[productId] || 0) + delta)
    }))
  }

  const featuredProducts = products.slice(0, 8)
  const cartItemCount = cart?.total_quantity || 0

  // Fetch query logs
  const fetchQueryLogs = async () => {
    try {
      const filterParam = queryFilter !== 'all' ? `?database_type=${queryFilter}` : ''
      const response = await fetch(`http://localhost:5001/api/db-logs${filterParam}`)
      const data = await response.json()
      
      if (data.success && data.data) {
        setQueryLog(data.data.logs || [])
      }
    } catch (error) {
      console.error('Failed to fetch query logs:', error)
    }
  }

  // Clear query logs
  const clearQueryLogs = async () => {
    try {
      const filterParam = queryFilter !== 'all' ? `?database_type=${queryFilter}` : ''
      const response = await fetch(`http://localhost:5001/api/db-logs${filterParam}`, {
        method: 'DELETE'
      })
      const data = await response.json()
      
      if (data.success) {
        setQueryLog([])
        toast.success(data.message || 'Logs cleared successfully')
      } else {
        toast.error(data.message || 'Failed to clear logs')
      }
    } catch (error) {
      console.error('Failed to clear query logs:', error)
      toast.error('Failed to clear logs')
    }
  }

  // Calculate average query time
  const calculateAverageQueryTime = () => {
    if (queryLog.length === 0) return 0
    const total = queryLog.reduce((sum, query) => sum + (query.time_taken_ms || 0), 0)
    return Math.round(total / queryLog.length * 100) / 100
  }

  // Filter queries based on selected filter
  const filteredQueries = queryLog.filter(query => {
    if (queryFilter === 'all') return true
    return query.database_type === queryFilter
  })

  // Fetch logs when filter changes or modal opens
  useEffect(() => {
    if (showQueryLog) {
      fetchQueryLogs()
    }
  }, [showQueryLog, queryFilter])

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (showDatabaseDropdown) {
        setShowDatabaseDropdown(false)
      }
    }

    document.addEventListener('click', handleClickOutside)
    return () => document.removeEventListener('click', handleClickOutside)
  }, [showDatabaseDropdown])

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-50 to-neutral-100">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-neutral-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-primary-500 rounded-xl flex items-center justify-center">
                <ShoppingCart className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-neutral-800">QuickGrocery</h1>
                <p className="text-xs text-neutral-500">Delivery in 10 minutes</p>
              </div>
            </div>

            {/* Location */}
            <div className="hidden md:flex items-center space-x-2 text-sm text-neutral-600">
              <MapPin className="w-4 h-4" />
              <span>Deliver to Home</span>
            </div>

            {/* Database Selection & Actions */}
            <div className="flex items-center space-x-4">
              {/* Database Selector - Simple Dropdown */}
              <div className="relative">
                <button
                  className="flex items-center space-x-2 bg-neutral-100 hover:bg-neutral-200 px-3 py-2 rounded-lg text-sm font-medium transition-colors"
                  onClick={(e) => {
                    e.stopPropagation()
                    setShowDatabaseDropdown(!showDatabaseDropdown)
                  }}
                >
                  <Database className="w-4 h-4" />
                  <span className="hidden sm:inline">{currentDatabase.toUpperCase()}</span>
                  <ChevronDown className="w-3 h-3" />
                </button>
                
                {showDatabaseDropdown && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg border border-neutral-200 p-2 z-50"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <button
                      onClick={() => {
                        handleDatabaseSwitch('mysql')
                        setShowDatabaseDropdown(false)
                      }}
                      className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                        currentDatabase === 'mysql' ? 'bg-primary-100 text-primary-700' : 'hover:bg-neutral-100'
                      }`}
                    >
                      <div className="flex items-center space-x-2">
                        <Database className="w-4 h-4" />
                        <div>
                          <span className="font-medium block">MySQL</span>
                          <span className="text-xs text-neutral-500">Relational Database</span>
                        </div>
                      </div>
                    </button>
                    <button
                      onClick={() => {
                        handleDatabaseSwitch('aerospike')
                        setShowDatabaseDropdown(false)
                      }}
                      className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                        currentDatabase === 'aerospike' ? 'bg-primary-100 text-primary-700' : 'hover:bg-neutral-100'
                      }`}
                    >
                      <div className="flex items-center space-x-2">
                        <Database className="w-4 h-4" />
                        <div>
                          <span className="font-medium block">Aerospike</span>
                          <span className="text-xs text-neutral-500">NoSQL Database</span>
                        </div>
                      </div>
                    </button>
                  </motion.div>
                )}
              </div>

              {/* Query Log Button */}
              <button
                onClick={() => setShowQueryLog(!showQueryLog)}
                className="flex items-center space-x-2 text-neutral-600 hover:text-primary-500 text-sm font-medium"
                title="View Database Queries"
              >
                <span className="hidden sm:inline">DB Logs</span>
                <span className="text-xs bg-neutral-200 text-neutral-700 px-2 py-1 rounded-full">
                  {queryLog.length}
                </span>
              </button>

              <button className="hidden md:flex items-center space-x-2 text-neutral-600 hover:text-primary-500">
                <User className="w-5 h-5" />
                <span>Login</span>
              </button>
              
              <button className="relative">
                <div className="w-10 h-10 bg-secondary-500 rounded-full flex items-center justify-center">
                  <ShoppingCart className="w-5 h-5 text-white" />
                </div>
                {cartItemCount > 0 && (
                  <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    {cartItemCount}
                  </span>
                )}
              </button>

              <button 
                className="md:hidden"
                onClick={() => setIsMenuOpen(!isMenuOpen)}
              >
                {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>

          {/* Search Bar */}
          <div className="mt-4 relative">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-neutral-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search for products..."
                className="w-full pl-12 pr-16 py-4 bg-neutral-100 rounded-2xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:bg-white transition-all duration-200"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <button className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-primary-500 text-white px-4 py-2 rounded-xl hover:bg-primary-600 transition-colors">
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="bg-gradient-to-r from-primary-500 to-accent-500 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row items-center">
            <div className="md:w-1/2 mb-8 md:mb-0">
              <h2 className="text-4xl md:text-5xl font-bold mb-4">
                Groceries delivered in 
                <span className="block text-yellow-300">10 minutes</span>
              </h2>
              <p className="text-xl mb-6 opacity-90">
                Get fresh groceries & essentials delivered to your doorstep
              </p>
              <div className="flex flex-wrap gap-4 text-sm">
                <div className="flex items-center space-x-2">
                  <Clock className="w-4 h-4" />
                  <span>10 min delivery</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Truck className="w-4 h-4" />
                  <span>Free delivery</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Star className="w-4 h-4" />
                  <span>Best quality</span>
                </div>
              </div>
            </div>
            <div className="md:w-1/2">
              <div className="relative">
                <div className="w-80 h-80 bg-white/20 rounded-full flex items-center justify-center animate-float">
                  <div className="w-60 h-60 bg-white/30 rounded-full flex items-center justify-center">
                    <ShoppingCart className="w-20 h-20 text-white" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Categories */}
      <section className="py-8 bg-white">
        <div className="container mx-auto px-4">
          <h3 className="text-2xl font-bold text-neutral-800 mb-6">Shop by Category</h3>
          <div className="category-grid">
            {categoriesLoading ? (
              Array.from({ length: 8 }).map((_, index) => (
                <div key={index} className="bg-neutral-100 rounded-2xl p-6 animate-pulse">
                  <div className="w-12 h-12 bg-neutral-200 rounded-full mb-3"></div>
                  <div className="h-4 bg-neutral-200 rounded"></div>
                </div>
              ))
            ) : (
              categories.map((category: Category) => (
                <motion.button
                  key={category.id}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className={`card p-6 text-center transition-all duration-200 ${
                    selectedCategory === category.id ? 'ring-2 ring-primary-500 bg-primary-50' : 'hover:shadow-md'
                  }`}
                  onClick={() => setSelectedCategory(selectedCategory === category.id ? null : category.id)}
                >
                  <div className="text-3xl mb-3 flex justify-center">
                    {renderIcon(category.icon, { className: "w-8 h-8 text-primary-600" })}
                  </div>
                  <h4 className="font-medium text-neutral-800">{category.name}</h4>
                </motion.button>
              ))
            )}
          </div>
        </div>
      </section>

      {/* Products */}
      <section className="py-8">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-2xl font-bold text-neutral-800">
              {selectedCategory ? 'Category Products' : 'Featured Products'}
            </h3>
            <button className="text-primary-500 hover:text-primary-600 font-medium">
              View All
            </button>
          </div>

          <div className="product-grid">
            {productsLoading ? (
              Array.from({ length: 8 }).map((_, index) => (
                <div key={index} className="card animate-pulse">
                  <div className="aspect-square bg-neutral-200"></div>
                  <div className="p-4">
                    <div className="h-4 bg-neutral-200 rounded mb-2"></div>
                    <div className="h-6 bg-neutral-200 rounded"></div>
                  </div>
                </div>
              ))
            ) : (
              featuredProducts.map((product) => (
                <motion.div
                  key={product.id}
                  whileHover={{ y: -5 }}
                  className="card card-hover relative overflow-hidden group"
                >
                  <div className="aspect-square relative overflow-hidden">
                    <Image
                      src={product.image_url || '/placeholder-product.jpg'}
                      alt={product.name}
                      fill
                      className="object-cover group-hover:scale-110 transition-transform duration-300"
                    />
                    <button className="absolute top-3 right-3 w-8 h-8 bg-white/80 rounded-full flex items-center justify-center hover:bg-white transition-colors">
                      <Heart className="w-4 h-4 text-neutral-600" />
                    </button>
                  </div>
                  
                  <div className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs text-primary-500 font-medium bg-primary-50 px-2 py-1 rounded-full">
                        {product.category?.name || 'Product'}
                      </span>
                      <span className="text-xs text-green-600 font-medium">
                        {product.stock > 0 ? 'In Stock' : 'Out of Stock'}
                      </span>
                    </div>
                    
                    <h4 className="font-semibold text-neutral-800 mb-1 line-clamp-2">{product.name}</h4>
                    <p className="text-sm text-neutral-600 mb-3 line-clamp-1">{product.description}</p>
                    
                    <div className="flex items-center justify-between">
                      <div className="text-lg font-bold text-neutral-800">
                        {formatPrice(product.price)}
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        {quantities[product.id] > 0 ? (
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => updateQuantity(product.id, -1)}
                              className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center hover:bg-primary-200 transition-colors"
                            >
                              <Minus className="w-4 h-4 text-primary-600" />
                            </button>
                            <span className="font-medium text-neutral-800 w-8 text-center">
                              {quantities[product.id]}
                            </span>
                            <button
                              onClick={() => updateQuantity(product.id, 1)}
                              className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center hover:bg-primary-200 transition-colors"
                            >
                              <Plus className="w-4 h-4 text-primary-600" />
                            </button>
                          </div>
                        ) : (
                          <button
                            onClick={() => updateQuantity(product.id, 1)}
                            className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center hover:bg-primary-600 transition-colors"
                          >
                            <Plus className="w-4 h-4 text-white" />
                          </button>
                        )}
                        
                        {quantities[product.id] > 0 && (
                          <button
                            onClick={() => handleAddToCart(product.id, quantities[product.id])}
                            className="btn btn-primary text-xs px-3 py-1"
                          >
                            Add
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))
            )}
          </div>
        </div>
      </section>

      {/* Query Log Modal */}
      <AnimatePresence>
        {showQueryLog && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={() => setShowQueryLog(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-white rounded-2xl shadow-xl max-w-4xl w-full max-h-[80vh] overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between p-6 border-b border-neutral-200">
                <div>
                  <h2 className="text-2xl font-bold text-neutral-800">Database Query Log</h2>
                  <p className="text-neutral-600">Current Database: <span className="font-medium text-primary-600">{currentDatabase.toUpperCase()}</span></p>
                </div>
                <button
                  onClick={() => setShowQueryLog(false)}
                  className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-neutral-100 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <div className="p-6 overflow-y-auto max-h-[60vh]">
                <div className="mb-4 space-y-3">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-semibold text-neutral-800">Query Log</h3>
                    <div className="flex space-x-2">
                      <button
                        onClick={fetchQueryLogs}
                        className="px-3 py-1 rounded-lg text-sm font-medium text-blue-600 hover:bg-blue-50 hover:text-blue-700 transition-colors"
                      >
                        Refresh
                      </button>
                      <button
                        onClick={clearQueryLogs}
                        className="px-3 py-1 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 hover:text-red-700 transition-colors"
                      >
                        Clear Logs
                      </button>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => setQueryFilter('all')}
                        className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                          queryFilter === 'all' ? 'bg-primary-100 text-primary-700' : 'hover:bg-neutral-100'
                        }`}
                      >
                        All
                      </button>
                      <button
                        onClick={() => setQueryFilter('mysql')}
                        className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                          queryFilter === 'mysql' ? 'bg-primary-100 text-primary-700' : 'hover:bg-neutral-100'
                        }`}
                      >
                        MySQL
                      </button>
                      <button
                        onClick={() => setQueryFilter('aerospike')}
                        className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                          queryFilter === 'aerospike' ? 'bg-primary-100 text-primary-700' : 'hover:bg-neutral-100'
                        }`}
                      >
                        Aerospike
                      </button>
                    </div>
                    
                    <div className="flex items-center space-x-4 text-sm text-neutral-600">
                      <span>
                        Total: <span className="font-medium text-neutral-800">{filteredQueries.length}</span>
                      </span>
                      <span>
                        Avg: <span className="font-medium text-neutral-800">{calculateAverageQueryTime()}ms</span>
                      </span>
                    </div>
                  </div>
                </div>
                <div className="space-y-3">
                  {filteredQueries.length > 0 ? (
                    filteredQueries.map((query, index) => (
                      <div key={index} className="bg-neutral-50 border border-neutral-200 rounded-xl p-4">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              query.database_type === 'mysql' 
                                ? 'bg-blue-100 text-blue-700' 
                                : 'bg-purple-100 text-purple-700'
                            }`}>
                              {query.database_type?.toUpperCase()}
                            </span>
                            <span className="text-xs text-neutral-500">ID: {query.id}</span>
                          </div>
                          <div className="text-right">
                            <div className="text-sm font-medium text-neutral-800">{query.time_taken_ms}ms</div>
                            <div className="text-xs text-neutral-500">{query.timestamp}</div>
                          </div>
                        </div>
                        
                        <div className="bg-neutral-800 text-neutral-100 p-3 rounded-lg font-mono text-sm overflow-x-auto">
                          {query.operation}
                        </div>
                        
                        <div className="flex items-center justify-between mt-2 text-xs text-neutral-600">
                          <span>Response Count: <span className="font-medium">{query.response_count}</span></span>
                          <span className={`font-medium ${
                            query.time_taken_ms < 10 ? 'text-green-600' : 
                            query.time_taken_ms < 50 ? 'text-yellow-600' : 'text-red-600'
                          }`}>
                            {query.time_taken_ms < 10 ? 'Fast' : query.time_taken_ms < 50 ? 'Moderate' : 'Slow'}
                          </span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-12">
                      <Database className="w-16 h-16 text-neutral-300 mx-auto mb-4" />
                      <h3 className="text-lg font-semibold text-neutral-600 mb-2">
                        {queryFilter === 'all' ? 'No Queries Yet' : `No ${queryFilter.toUpperCase()} Queries`}
                      </h3>
                      <p className="text-neutral-500">
                        {queryFilter === 'all' 
                          ? 'Database queries will appear here as you interact with the app.' 
                          : `Switch to "${queryFilter === 'mysql' ? 'Aerospike' : 'MySQL'}" database or clear filters to see more queries.`
                        }
                      </p>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="p-6 border-t border-neutral-200 bg-neutral-50">
                <div className="flex items-center justify-between">
                  <div className="text-sm text-neutral-600">
                    Current Database: <span className="font-medium text-primary-600">{currentDatabase.toUpperCase()}</span>
                  </div>
                  <button
                    onClick={() => setShowQueryLog(false)}
                    className="btn btn-primary"
                  >
                    Close
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: '-100%' }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: '-100%' }}
            className="fixed inset-0 z-50 bg-white md:hidden"
          >
            <div className="p-4">
              <div className="flex items-center justify-between mb-8">
                <h2 className="text-xl font-bold">Menu</h2>
                <button onClick={() => setIsMenuOpen(false)}>
                  <X className="w-6 h-6" />
                </button>
              </div>
              
              <nav className="space-y-6">
                <a href="#" className="flex items-center space-x-3 text-lg">
                  <User className="w-5 h-5" />
                  <span>Login</span>
                </a>
                <a href="#" className="flex items-center space-x-3 text-lg">
                  <ShoppingCart className="w-5 h-5" />
                  <span>Cart ({cartItemCount})</span>
                </a>
                <a href="#" className="flex items-center space-x-3 text-lg">
                  <MapPin className="w-5 h-5" />
                  <span>Change Location</span>
                </a>
                <button
                  onClick={() => setShowDatabaseDropdown(!showDatabaseDropdown)}
                  className="flex items-center space-x-3 text-lg w-full text-left"
                >
                  <Database className="w-5 h-5" />
                  <span>Database: {currentDatabase.toUpperCase()}</span>
                </button>
                <button
                  onClick={() => {
                    setShowQueryLog(!showQueryLog)
                    setIsMenuOpen(false)
                  }}
                  className="flex items-center space-x-3 text-lg w-full text-left"
                >
                  <Database className="w-5 h-5" />
                  <span>DB Logs ({queryLog.length})</span>
                </button>
              </nav>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
} 