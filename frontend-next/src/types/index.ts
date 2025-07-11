// User types
export interface User {
  id: number
  email: string
  name: string
  address?: string
  phone?: string
  created_at: string
}

// Product types
export interface Product {
  id: number
  name: string
  description: string
  price: number
  image_url: string
  stock: number
  category_id: number
  is_available: boolean
  created_at: string
  category?: Category
}

// Category types
export interface Category {
  id: number
  name: string
  icon: string
}

// Cart types
export interface CartItem {
  id: number
  user_session: string
  product_id: number
  quantity: number
  created_at: string
  updated_at: string
  product: Product
  total: number
}

export interface Cart {
  cart_items: CartItem[]
  total: number
  subtotal: number
  total_quantity: number
  discount_percentage: number
  discount_amount: number
}

// Order types
export interface OrderItem {
  id: number
  order_id: number
  product_id: number
  quantity: number
  price: number
  product: Product
}

export interface Order {
  id: number
  user_id: number
  total_amount: number
  status: string
  delivery_address: string
  created_at: string
  items: OrderItem[]
}

// API Response types
export interface ApiResponse<T> {
  success: boolean
  message: string
  data: T
  debug?: {
    recent_queries: any[]
    demo_mode: boolean
  }
}

// Form types
export interface LoginForm {
  email: string
  password: string
}

export interface RegisterForm {
  name: string
  email: string
  password: string
  address?: string
  phone?: string
}

export interface CheckoutForm {
  address: string
  phone?: string
}

// Database types
export type DatabaseType = 'mysql' | 'aerospike'

export interface DatabaseInfo {
  current_database: DatabaseType
  available_databases: DatabaseType[]
}

// Search and Filter types
export interface ProductFilters {
  category?: number
  search?: string
  min_price?: number
  max_price?: number
  in_stock?: boolean
}

// UI State types
export interface LoadingState {
  isLoading: boolean
  error: string | null
}

export interface NotificationState {
  type: 'success' | 'error' | 'info' | 'warning'
  message: string
  id: string
}

// Hook types
export interface UseApiOptions {
  enabled?: boolean
  refetchInterval?: number
  onSuccess?: (data: any) => void
  onError?: (error: any) => void
}

// Component prop types
export interface ProductCardProps {
  product: Product
  onAddToCart: (productId: number, quantity: number) => void
  showQuickAdd?: boolean
  className?: string
}

export interface CategoryCardProps {
  category: Category
  onClick: (categoryId: number) => void
  className?: string
}

export interface CartItemProps {
  item: CartItem
  onUpdateQuantity: (itemId: number, quantity: number) => void
  onRemove: (itemId: number) => void
  className?: string
}

// Layout types
export interface LayoutProps {
  children: React.ReactNode
  showHeader?: boolean
  showFooter?: boolean
  className?: string
}

// Navigation types
export interface NavItem {
  label: string
  href: string
  icon?: React.ReactNode
  isActive?: boolean
}

// Modal types
export interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  children: React.ReactNode
  size?: 'sm' | 'md' | 'lg' | 'xl'
  className?: string
}

// Form validation types
export interface FormErrors {
  [key: string]: string | string[]
}

// Pagination types
export interface PaginationMeta {
  current_page: number
  per_page: number
  total: number
  total_pages: number
  has_next_page: boolean
  has_prev_page: boolean
}

export interface PaginatedResponse<T> {
  data: T[]
  meta: PaginationMeta
}

// Theme types
export type Theme = 'light' | 'dark' | 'system'

// Device types
export type DeviceType = 'mobile' | 'tablet' | 'desktop'

// Animation types
export interface AnimationVariants {
  initial: object
  animate: object
  exit?: object
  transition?: object
}

// Utility types
export type Nullable<T> = T | null
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>
export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>> 