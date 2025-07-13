'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Heart, Plus, Minus, ShoppingCart, Star, Info, Package, Truck, ArrowLeft, ArrowRight } from 'lucide-react'
import Image from 'next/image'
import { Product, Category } from '@/types'
import { formatPrice } from '@/lib/api'
import { renderIcon } from '@/lib/iconMapping'

interface ProductDetailModalProps {
  product: Product | null
  isOpen: boolean
  onClose: () => void
  onAddToCart: (productId: number, quantity: number) => void
  categories?: Category[]
  relatedProducts?: Product[]
}

export default function ProductDetailModal({ 
  product, 
  isOpen, 
  onClose, 
  onAddToCart,
  categories = [],
  relatedProducts = []
}: ProductDetailModalProps) {
  const [quantity, setQuantity] = useState(1)
  const [selectedImageIndex, setSelectedImageIndex] = useState(0)
  const [isInWishlist, setIsInWishlist] = useState(false)

  // Reset state when product changes
  useEffect(() => {
    if (product) {
      setQuantity(1)
      setSelectedImageIndex(0)
    }
  }, [product])

  // Handle escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose()
      }
    }
    
    if (isOpen) {
      document.addEventListener('keydown', handleEscape)
      document.body.style.overflow = 'hidden'
    }
    
    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.body.style.overflow = 'unset'
    }
  }, [isOpen, onClose])

  if (!product) return null

  const handleAddToCart = () => {
    onAddToCart(product.id, quantity)
    onClose()
  }

  const updateQuantity = (delta: number) => {
    setQuantity(prev => Math.max(1, Math.min(99, prev + delta)))
  }

  const productCategory = product.category || categories.find(cat => cat.id === product.category_id)

  // Mock additional product details (in a real app, these would come from the API)
  const productDetails = {
    nutritionalInfo: {
      calories: '150 per serving',
      protein: '12g',
      carbs: '25g',
      fat: '3g'
    },
    ingredients: 'Premium quality ingredients sourced from trusted suppliers',
    origin: 'Locally sourced',
    shelfLife: '7 days',
    storage: 'Store in refrigerator',
    brand: 'QuickGrocery Fresh'
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="sticky top-0 bg-white border-b border-neutral-200 px-6 py-4 flex items-center justify-between z-10">
              <div className="flex items-center space-x-3">
                {productCategory && (
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
                      {renderIcon(productCategory.icon, { className: "w-4 h-4 text-primary-600" })}
                    </div>
                    <span className="text-sm font-medium text-primary-600">{productCategory.name}</span>
                  </div>
                )}
                <div className="flex items-center space-x-2">
                  <div className="flex items-center space-x-1">
                    {Array.from({ length: 5 }).map((_, i) => (
                      <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    ))}
                  </div>
                  <span className="text-sm text-neutral-600">(4.8) · 234 reviews</span>
                </div>
              </div>
              <button
                onClick={onClose}
                className="w-10 h-10 bg-neutral-100 rounded-full flex items-center justify-center hover:bg-neutral-200 transition-colors"
              >
                <X className="w-5 h-5 text-neutral-600" />
              </button>
            </div>

            {/* Content */}
            <div className="p-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Product Image */}
                <div className="space-y-4">
                  <div className="aspect-square relative overflow-hidden rounded-xl bg-neutral-100">
                    <Image
                      src={product.image_url && (product.image_url.startsWith('/') || product.image_url.startsWith('http')) ? product.image_url : '/placeholder-product.svg'}
                      alt={product.name}
                      fill
                      className="object-cover"
                    />
                    <button
                      onClick={() => setIsInWishlist(!isInWishlist)}
                      className="absolute top-4 right-4 w-10 h-10 bg-white/90 rounded-full flex items-center justify-center hover:bg-white transition-colors"
                    >
                      <Heart className={`w-5 h-5 ${isInWishlist ? 'fill-red-500 text-red-500' : 'text-neutral-600'}`} />
                    </button>
                  </div>
                  
                  {/* Quick Facts */}
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="flex items-center space-x-2 p-3 bg-green-50 rounded-lg">
                      <Package className="w-4 h-4 text-green-600" />
                      <span className="text-green-700">
                        {product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2 p-3 bg-blue-50 rounded-lg">
                      <Truck className="w-4 h-4 text-blue-600" />
                      <span className="text-blue-700">10 min delivery</span>
                    </div>
                  </div>
                </div>

                {/* Product Info */}
                <div className="space-y-6">
                  <div>
                    <h1 className="text-2xl font-bold text-neutral-800 mb-2">{product.name}</h1>
                    <p className="text-neutral-600 leading-relaxed">{product.description}</p>
                  </div>

                  {/* Price */}
                  <div className="flex items-center space-x-4">
                    <div className="text-3xl font-bold text-neutral-800">
                      {formatPrice(product.price)}
                    </div>
                    <div className="text-sm text-neutral-500">
                      <span className="bg-neutral-100 px-2 py-1 rounded">per unit</span>
                    </div>
                  </div>

                  {/* Quantity & Add to Cart */}
                  <div className="space-y-4">
                    <div className="flex items-center space-x-4">
                      <span className="text-sm font-medium text-neutral-700">Quantity:</span>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => updateQuantity(-1)}
                          className="w-10 h-10 bg-neutral-100 rounded-full flex items-center justify-center hover:bg-neutral-200 transition-colors"
                        >
                          <Minus className="w-4 h-4 text-neutral-600" />
                        </button>
                        <span className="font-medium text-neutral-800 w-12 text-center">{quantity}</span>
                        <button
                          onClick={() => updateQuantity(1)}
                          className="w-10 h-10 bg-neutral-100 rounded-full flex items-center justify-center hover:bg-neutral-200 transition-colors"
                        >
                          <Plus className="w-4 h-4 text-neutral-600" />
                        </button>
                      </div>
                    </div>

                    <div className="flex space-x-3">
                      <button
                        onClick={handleAddToCart}
                        disabled={product.stock <= 0}
                        className="flex-1 bg-primary-500 text-white py-3 px-6 rounded-xl font-medium hover:bg-primary-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                      >
                        <ShoppingCart className="w-5 h-5" />
                        <span>Add to Cart · {formatPrice(product.price * quantity)}</span>
                      </button>
                      <button
                        onClick={() => setIsInWishlist(!isInWishlist)}
                        className="w-12 h-12 bg-neutral-100 rounded-xl flex items-center justify-center hover:bg-neutral-200 transition-colors"
                      >
                        <Heart className={`w-5 h-5 ${isInWishlist ? 'fill-red-500 text-red-500' : 'text-neutral-600'}`} />
                      </button>
                    </div>
                  </div>

                  {/* Product Details */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-neutral-800">Product Details</h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="font-medium text-neutral-700">Brand:</span>
                        <span className="ml-2 text-neutral-600">{productDetails.brand}</span>
                      </div>
                      <div>
                        <span className="font-medium text-neutral-700">Origin:</span>
                        <span className="ml-2 text-neutral-600">{productDetails.origin}</span>
                      </div>
                      <div>
                        <span className="font-medium text-neutral-700">Shelf Life:</span>
                        <span className="ml-2 text-neutral-600">{productDetails.shelfLife}</span>
                      </div>
                      <div>
                        <span className="font-medium text-neutral-700">Storage:</span>
                        <span className="ml-2 text-neutral-600">{productDetails.storage}</span>
                      </div>
                    </div>
                  </div>

                  {/* Nutritional Information */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-neutral-800">Nutritional Information</h3>
                    <div className="bg-neutral-50 rounded-xl p-4">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="font-medium text-neutral-700">Calories:</span>
                          <span className="ml-2 text-neutral-600">{productDetails.nutritionalInfo.calories}</span>
                        </div>
                        <div>
                          <span className="font-medium text-neutral-700">Protein:</span>
                          <span className="ml-2 text-neutral-600">{productDetails.nutritionalInfo.protein}</span>
                        </div>
                        <div>
                          <span className="font-medium text-neutral-700">Carbs:</span>
                          <span className="ml-2 text-neutral-600">{productDetails.nutritionalInfo.carbs}</span>
                        </div>
                        <div>
                          <span className="font-medium text-neutral-700">Fat:</span>
                          <span className="ml-2 text-neutral-600">{productDetails.nutritionalInfo.fat}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Ingredients */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-neutral-800">Ingredients</h3>
                    <p className="text-sm text-neutral-600 leading-relaxed">
                      {productDetails.ingredients}
                    </p>
                  </div>
                </div>
              </div>

              {/* Related Products */}
              {relatedProducts.length > 0 && (
                <div className="mt-8 pt-8 border-t border-neutral-200">
                  <h3 className="text-xl font-semibold text-neutral-800 mb-4">Related Products</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                    {relatedProducts.slice(0, 4).map((relatedProduct) => (
                      <div key={relatedProduct.id} className="card card-hover">
                        <div className="aspect-square relative overflow-hidden">
                          <Image
                            src={relatedProduct.image_url && (relatedProduct.image_url.startsWith('/') || relatedProduct.image_url.startsWith('http')) ? relatedProduct.image_url : '/placeholder-product.svg'}
                            alt={relatedProduct.name}
                            fill
                            className="object-cover"
                          />
                        </div>
                        <div className="p-3">
                          <h4 className="font-medium text-neutral-800 text-sm line-clamp-2 mb-1">{relatedProduct.name}</h4>
                          <div className="text-sm font-semibold text-neutral-800">
                            {formatPrice(relatedProduct.price)}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
} 