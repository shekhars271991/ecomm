'use client'

import { Database, Table, FileText, Zap, Network } from 'lucide-react'
import { motion } from 'framer-motion'

export default function DataModelsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-50 to-neutral-100">
      {/* Header */}
      <header className="bg-white border-b border-neutral-200 sticky top-0 z-10">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-center">
            <div className="text-center">
              <h1 className="text-3xl font-bold text-neutral-800 mb-2">Database Architecture Comparison</h1>
              <p className="text-neutral-600">MySQL vs Aerospike vs MongoDB Data Models</p>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Introduction removed as per requirement */}

        {/* Database Comparison */}
        <div className="grid lg:grid-cols-3 gap-8 mb-12">
          {/* MySQL Section */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            className="bg-white rounded-2xl shadow-soft border border-neutral-200 overflow-hidden"
          >
            <div className="bg-blue-50 border-b border-blue-100 p-6">
              <div className="flex items-center space-x-3 mb-3">
                <div className="w-10 h-10 bg-blue-500 rounded-xl flex items-center justify-center">
                  <Database className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-blue-800">MySQL</h3>
                  <p className="text-sm text-blue-600">Relational Database</p>
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded-full text-xs font-medium">ACID Compliant</span>
                <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded-full text-xs font-medium">SQL</span>
                <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded-full text-xs font-medium">Normalized</span>
              </div>
            </div>
            
            <div className="p-6">
              <h4 className="font-semibold text-neutral-800 mb-4 flex items-center">
                <Table className="w-4 h-4 mr-2" />
                Table Structure
              </h4>
              
              <div className="space-y-4">
                {/* Categories Table */}
                <div className="border border-neutral-200 rounded-lg overflow-hidden">
                  <div className="bg-neutral-50 px-3 py-2 border-b border-neutral-200">
                    <span className="font-mono text-sm font-medium text-neutral-700">categories</span>
                  </div>
                  <div className="p-3 text-sm font-mono">
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <span className="text-blue-600 font-medium">id</span>
                      <span className="text-neutral-600">INT PRIMARY KEY</span>
                      <span className="text-blue-600 font-medium">name</span>
                      <span className="text-neutral-600">VARCHAR(100)</span>
                      <span className="text-blue-600 font-medium">icon</span>
                      <span className="text-neutral-600">VARCHAR(50)</span>
                    </div>
                  </div>
                </div>

                {/* Products Table */}
                <div className="border border-neutral-200 rounded-lg overflow-hidden">
                  <div className="bg-neutral-50 px-3 py-2 border-b border-neutral-200">
                    <span className="font-mono text-sm font-medium text-neutral-700">products</span>
                  </div>
                  <div className="p-3 text-sm font-mono">
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <span className="text-blue-600 font-medium">id</span>
                      <span className="text-neutral-600">INT PRIMARY KEY</span>
                      <span className="text-blue-600 font-medium">name</span>
                      <span className="text-neutral-600">VARCHAR(200)</span>
                      <span className="text-blue-600 font-medium">price</span>
                      <span className="text-neutral-600">DECIMAL(10,2)</span>
                      <span className="text-blue-600 font-medium">category_id</span>
                      <span className="text-neutral-600">INT FOREIGN KEY</span>
                      <span className="text-blue-600 font-medium">stock</span>
                      <span className="text-neutral-600">INT</span>
                    </div>
                  </div>
                </div>

                {/* Cart Table */}
                <div className="border border-neutral-200 rounded-lg overflow-hidden">
                  <div className="bg-neutral-50 px-3 py-2 border-b border-neutral-200">
                    <span className="font-mono text-sm font-medium text-neutral-700">cart</span>
                  </div>
                  <div className="p-3 text-sm font-mono">
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <span className="text-blue-600 font-medium">id</span>
                      <span className="text-neutral-600">INT PRIMARY KEY</span>
                      <span className="text-blue-600 font-medium">user_session</span>
                      <span className="text-neutral-600">VARCHAR(255)</span>
                      <span className="text-blue-600 font-medium">product_id</span>
                      <span className="text-neutral-600">INT FOREIGN KEY</span>
                      <span className="text-blue-600 font-medium">quantity</span>
                      <span className="text-neutral-600">INT</span>
                    </div>
                  </div>
                </div>
              </div>

              
            </div>
          </motion.div>

          {/* Aerospike Section */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="bg-white rounded-2xl shadow-soft border border-neutral-200 overflow-hidden"
          >
            <div className="bg-red-50 border-b border-red-100 p-6">
              <div className="flex items-center space-x-3 mb-3">
                <div className="w-10 h-10 bg-red-500 rounded-xl flex items-center justify-center">
                  <Zap className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-red-800">Aerospike</h3>
                  <p className="text-sm text-red-600">NoSQL Database</p>
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                <span className="bg-red-100 text-red-700 px-2 py-1 rounded-full text-xs font-medium">ACID Compliant</span>
                <span className="bg-red-100 text-red-700 px-2 py-1 rounded-full text-xs font-medium">Key-Value</span>
                <span className="bg-red-100 text-red-700 px-2 py-1 rounded-full text-xs font-medium">Hybrid Memory</span>
                <span className="bg-red-100 text-red-700 px-2 py-1 rounded-full text-xs font-medium">Dual Storage</span>
              </div>
            </div>
            
            <div className="p-6">
              <h4 className="font-semibold text-neutral-800 mb-4 flex items-center">
                <Network className="w-4 h-4 mr-2" />
                Dual Storage Architecture
              </h4>
              
              <div className="space-y-4">
                {/* Namespace */}
                <div className="border border-neutral-200 rounded-lg overflow-hidden">
                  <div className="bg-neutral-50 px-3 py-2 border-b border-neutral-200">
                    <span className="font-mono text-sm font-medium text-neutral-700">grocery (namespace)</span>
                  </div>
                </div>

                {/* Meta Set */}
                <div className="border border-neutral-200 rounded-lg overflow-hidden ml-4">
                  <div className="bg-red-50 px-3 py-2 border-b border-red-200">
                    <span className="font-mono text-sm font-medium text-red-700">meta (set)</span>
                  </div>
                  <div className="p-3 text-sm font-mono">
                    <div className="space-y-1 text-xs">
                      <div className="text-neutral-600">Key: all_categories</div>
                      <div className="bg-neutral-100 p-2 rounded">
                        <div className="text-red-600 font-medium">Record Bins:</div>
                        <div className="ml-2 space-y-1">
                          <div>categories: [</div>
                          <div className="ml-4">{"{"} id: 1, name: "Bakery", icon: "cake" {"}"},</div>
                          <div className="ml-4">{"{"} id: 2, name: "Fruits", icon: "apple" {"}"}</div>
                          <div>]</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Category Products Set */}
                <div className="border border-neutral-200 rounded-lg overflow-hidden ml-4">
                  <div className="bg-red-50 px-3 py-2 border-b border-red-200">
                    <span className="font-mono text-sm font-medium text-red-700">category_products (set)</span>
                  </div>
                  <div className="p-3 text-sm font-mono">
                    <div className="space-y-1 text-xs">
                      <div className="text-neutral-600">Key: cat:1, cat:2, ...</div>
                      <div className="bg-neutral-100 p-2 rounded">
                        <div className="text-red-600 font-medium">Record Bins:</div>
                        <div className="ml-2 space-y-1">
                          <div>products: [</div>
                          <div className="ml-4">{"{"} id: 1, name: "Bread", price: 2.99 {"}"},</div>
                          <div className="ml-4">{"{"} id: 2, name: "Cake", price: 12.99 {"}"}</div>
                          <div>]</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Products Set */}
                <div className="border border-neutral-200 rounded-lg overflow-hidden ml-4">
                  <div className="bg-red-50 px-3 py-2 border-b border-red-200">
                    <span className="font-mono text-sm font-medium text-red-700">products (set)</span>
                  </div>
                  <div className="p-3 text-sm font-mono">
                    <div className="space-y-1 text-xs">
                      <div className="text-neutral-600">Key: product:1, product:2, ...</div>
                      <div className="bg-neutral-100 p-2 rounded">
                        <div className="text-red-600 font-medium">Record Bins:</div>
                        <div className="ml-2 space-y-1">
                          <div>id: 1</div>
                          <div>name: "Fresh Bread"</div>
                          <div>price: 2.99</div>
                          <div>category_id: 1</div>
                          <div>stock: 50</div>
                          <div>image_url: "bread.jpg"</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Cart Set (updated single-record model) */}
                <div className="border border-neutral-200 rounded-lg overflow-hidden ml-4">
                  <div className="bg-red-50 px-3 py-2 border-b border-red-200">
                    <span className="font-mono text-sm font-medium text-red-700">cart (set)</span>
                  </div>
                  <div className="p-3 text-sm font-mono">
                    <div className="space-y-1 text-xs">
                      <div className="text-neutral-600">Key: session_123</div>
                      <div className="bg-neutral-100 p-2 rounded">
                        <div className="text-red-600 font-medium">Record Bins:</div>
                        <div className="ml-2 space-y-1">
                          <div>session_id: "session_123"</div>
                          <div>
                            items: [ {"{"} product_id: 1, quantity: 2, added_at: "2024-01-01T10:00:00Z", updated_at: "2024-01-01T10:05:00Z" {"}"} ]
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              
            </div>
          </motion.div>

          {/* MongoDB Section */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="bg-white rounded-2xl shadow-soft border border-neutral-200 overflow-hidden"
          >
            <div className="bg-green-50 border-b border-green-100 p-6">
              <div className="flex items-center space-x-3 mb-3">
                <div className="w-10 h-10 bg-green-500 rounded-xl flex items-center justify-center">
                  <FileText className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-green-800">MongoDB</h3>
                  <p className="text-green-600 text-sm">Document Database</p>
                  
                </div>
                
              </div>
              <div className="flex flex-wrap gap-2">
                <span className="bg-green-100 text-green-700 px-2 py-1 rounded-full text-xs font-medium">JSON Documents</span>
                <span className="bg-green-100 text-green-700 px-2 py-1 rounded-full text-xs font-medium">Complex Queries</span>
                <span className="bg-green-100 text-green-700 px-2 py-1 rounded-full text-xs font-medium">Flexible Schema</span>
              </div>
              
            </div>

            <div className="p-6">
              <h4 className="font-semibold text-neutral-800 mb-4">Document Structure</h4>
              
              <div className="space-y-4">
                {/* Categories Collection */}
                <div className="border border-neutral-200 rounded-lg overflow-hidden">
                  <div className="bg-green-50 px-3 py-2 border-b border-green-200">
                    <span className="font-mono text-sm font-medium text-green-700">categories (collection)</span>
                  </div>
                  <div className="p-3 text-sm font-mono">
                    <div className="bg-neutral-100 p-2 rounded">
                      <div className="text-green-600 font-medium">Document:</div>
                      <div className="ml-2 space-y-1">
                        <div>_id: ObjectId("...")</div>
                        <div>id: 1</div>
                        <div>name: "Fruits"</div>
                        <div>icon: "apple"</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Products Collection */}
                <div className="border border-neutral-200 rounded-lg overflow-hidden ml-4">
                  <div className="bg-green-50 px-3 py-2 border-b border-green-200">
                    <span className="font-mono text-sm font-medium text-green-700">products (collection)</span>
                  </div>
                  <div className="p-3 text-sm font-mono">
                    <div className="bg-neutral-100 p-2 rounded">
                      <div className="text-green-600 font-medium">Document:</div>
                      <div className="ml-2 space-y-1">
                        <div>_id: ObjectId("...")</div>
                        <div>id: 1</div>
                        <div>name: "Fresh Apples"</div>
                        <div>price: 2.99</div>
                        <div>category_id: 1</div>
                        <div>stock_quantity: 50</div>
                        <div>image_url: "apple.jpg"</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Cart Collection */}
                <div className="border border-neutral-200 rounded-lg overflow-hidden ml-4">
                  <div className="bg-green-50 px-3 py-2 border-b border-green-200">
                    <span className="font-mono text-sm font-medium text-green-700">cart (collection)</span>
                  </div>
                  <div className="p-3 text-sm font-mono">
                    <div className="bg-neutral-100 p-2 rounded">
                      <div className="text-green-600 font-medium">Document:</div>
                      <div className="ml-2 space-y-1">
                        <div>_id: ObjectId("...")</div>
                        <div>user_session: "session_123"</div>
                        <div>product_id: 1</div>
                        <div>quantity: 2</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

            
            </div>
          </motion.div>
        </div>

        {/* Performance section removed */}
      </div>
    </div>
  )
} 