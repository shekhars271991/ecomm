'use client'

import { Database, Table, FileText, Zap, Network, ArrowRight } from 'lucide-react'
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
              <p className="text-neutral-600">MySQL vs Aerospike Data Models</p>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Introduction */}
        <div className="max-w-4xl mx-auto mb-12">
          <div className="bg-white rounded-2xl shadow-soft border border-neutral-200 p-8">
            <div className="text-center mb-6">
              <div className="flex justify-center items-center space-x-4 mb-4">
                <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                  <Database className="w-6 h-6 text-blue-600" />
                </div>
                <ArrowRight className="w-6 h-6 text-neutral-400" />
                <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center">
                  <Zap className="w-6 h-6 text-red-600" />
                </div>
              </div>
              <h2 className="text-2xl font-bold text-neutral-800 mb-4">Relational vs NoSQL Architecture</h2>
              <p className="text-neutral-600 leading-relaxed">
                This demo showcases how the same grocery application data is structured and accessed 
                in two fundamentally different database paradigms: MySQL (relational) and Aerospike (NoSQL).
              </p>
            </div>
          </div>
        </div>

        {/* Database Comparison */}
        <div className="grid lg:grid-cols-2 gap-8 mb-12">
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

              <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                <h5 className="font-medium text-blue-800 mb-2">Characteristics:</h5>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>• Structured tables with relationships</li>
                  <li>• FOREIGN KEY constraints</li>
                  <li>• JOIN operations for data retrieval</li>
                  <li>• ACID transactions</li>
                  <li>• Schema must be defined upfront</li>
                </ul>
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
                <span className="bg-red-100 text-red-700 px-2 py-1 rounded-full text-xs font-medium">Key-Value</span>
                <span className="bg-red-100 text-red-700 px-2 py-1 rounded-full text-xs font-medium">In-Memory</span>
                <span className="bg-red-100 text-red-700 px-2 py-1 rounded-full text-xs font-medium">Schema-less</span>
              </div>
            </div>
            
            <div className="p-6">
              <h4 className="font-semibold text-neutral-800 mb-4 flex items-center">
                <Network className="w-4 h-4 mr-2" />
                Namespace Structure
              </h4>
              
              <div className="space-y-4">
                {/* Namespace */}
                <div className="border border-neutral-200 rounded-lg overflow-hidden">
                  <div className="bg-neutral-50 px-3 py-2 border-b border-neutral-200">
                    <span className="font-mono text-sm font-medium text-neutral-700">grocery (namespace)</span>
                  </div>
                </div>

                {/* Categories Set */}
                <div className="border border-neutral-200 rounded-lg overflow-hidden ml-4">
                  <div className="bg-red-50 px-3 py-2 border-b border-red-200">
                    <span className="font-mono text-sm font-medium text-red-700">categories (set)</span>
                  </div>
                  <div className="p-3 text-sm font-mono">
                    <div className="space-y-1 text-xs">
                      <div className="text-neutral-600">Key: category_1, category_2, ...</div>
                      <div className="bg-neutral-100 p-2 rounded">
                        <div className="text-red-600 font-medium">Record Bins:</div>
                        <div className="ml-2 space-y-1">
                          <div>id: 1</div>
                          <div>name: "Fruits"</div>
                          <div>icon: "apple"</div>
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
                      <div className="text-neutral-600">Key: product_1, product_2, ...</div>
                      <div className="bg-neutral-100 p-2 rounded">
                        <div className="text-red-600 font-medium">Record Bins:</div>
                        <div className="ml-2 space-y-1">
                          <div>id: 1</div>
                          <div>name: "Fresh Apples"</div>
                          <div>price: 2.99</div>
                          <div>category_id: 1</div>
                          <div>stock: 50</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Cart Set */}
                <div className="border border-neutral-200 rounded-lg overflow-hidden ml-4">
                  <div className="bg-red-50 px-3 py-2 border-b border-red-200">
                    <span className="font-mono text-sm font-medium text-red-700">cart (set)</span>
                  </div>
                  <div className="p-3 text-sm font-mono">
                    <div className="space-y-1 text-xs">
                      <div className="text-neutral-600">Key: session_123_product_1</div>
                      <div className="bg-neutral-100 p-2 rounded">
                        <div className="text-red-600 font-medium">Record Bins:</div>
                        <div className="ml-2 space-y-1">
                          <div>user_session: "session_123"</div>
                          <div>product_id: 1</div>
                          <div>quantity: 2</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-6 p-4 bg-red-50 rounded-lg">
                <h5 className="font-medium text-red-800 mb-2">Characteristics:</h5>
                <ul className="text-sm text-red-700 space-y-1">
                  <li>• Key-value pairs with bins (fields)</li>
                  <li>• No schema constraints</li>
                  <li>• Single record operations</li>
                  <li>• In-memory performance</li>
                  <li>• Horizontal scaling</li>
                </ul>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Key Differences */}
        <div className="max-w-6xl mx-auto">
          <div className="bg-white rounded-2xl shadow-soft border border-neutral-200 p-8">
            <h2 className="text-2xl font-bold text-neutral-800 mb-6 text-center">Key Differences in Practice</h2>
            
            <div className="grid md:grid-cols-2 gap-8">
              {/* Query Patterns */}
              <div>
                <h3 className="text-lg font-semibold text-neutral-800 mb-4">Query Patterns</h3>
                
                <div className="space-y-4">
                  <div className="border border-blue-200 rounded-lg p-4 bg-blue-50">
                    <h4 className="font-medium text-blue-800 mb-2">MySQL - Complex Queries</h4>
                    <div className="bg-white p-3 rounded font-mono text-sm text-blue-900">
                      SELECT p.*, c.name as category_name<br/>
                      FROM products p<br/>
                      JOIN categories c ON p.category_id = c.id<br/>
                      WHERE c.name = 'Fruits'
                    </div>
                  </div>
                  
                  <div className="border border-red-200 rounded-lg p-4 bg-red-50">
                    <h4 className="font-medium text-red-800 mb-2">Aerospike - Key-Based</h4>
                    <div className="bg-white p-3 rounded font-mono text-sm text-red-900">
                      // Direct key access<br/>
                      get(namespace="grocery",<br/>
                          set="products",<br/>
                          key="product_1")
                    </div>
                  </div>
                </div>
              </div>

              {/* Performance Characteristics */}
              <div>
                <h3 className="text-lg font-semibold text-neutral-800 mb-4">Performance Characteristics</h3>
                
                <div className="space-y-4">
                  <div className="border border-blue-200 rounded-lg p-4 bg-blue-50">
                    <h4 className="font-medium text-blue-800 mb-2">MySQL</h4>
                    <ul className="text-sm text-blue-700 space-y-1">
                      <li>• Disk-based storage</li>
                      <li>• Query optimization needed</li>
                      <li>• JOIN operations can be costly</li>
                      <li>• ACID compliance overhead</li>
                    </ul>
                  </div>
                  
                  <div className="border border-red-200 rounded-lg p-4 bg-red-50">
                    <h4 className="font-medium text-red-800 mb-2">Aerospike</h4>
                    <ul className="text-sm text-red-700 space-y-1">
                      <li>• In-memory performance</li>
                      <li>• Sub-millisecond response</li>
                      <li>• Linear scalability</li>
                      <li>• No complex query planning</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            {/* Use Case Scenarios */}
            <div className="mt-8 pt-8 border-t border-neutral-200">
              <h3 className="text-lg font-semibold text-neutral-800 mb-4 text-center">Best Use Cases</h3>
              
              <div className="grid md:grid-cols-2 gap-6">
                <div className="text-center">
                  <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mx-auto mb-3">
                    <Database className="w-6 h-6 text-blue-600" />
                  </div>
                  <h4 className="font-medium text-blue-800 mb-2">MySQL - Best For</h4>
                  <ul className="text-sm text-blue-700 space-y-1 text-left">
                    <li>• Complex reporting and analytics</li>
                    <li>• Multi-table transactions</li>
                    <li>• Regulatory compliance (ACID)</li>
                    <li>• Ad-hoc queries and exploration</li>
                  </ul>
                </div>
                
                <div className="text-center">
                  <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center mx-auto mb-3">
                    <Zap className="w-6 h-6 text-red-600" />
                  </div>
                  <h4 className="font-medium text-red-800 mb-2">Aerospike - Best For</h4>
                  <ul className="text-sm text-red-700 space-y-1 text-left">
                    <li>• High-speed applications</li>
                    <li>• Real-time recommendations</li>
                    <li>• Session storage and caching</li>
                    <li>• Massive scale operations</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Note */}
        <div className="text-center mt-12">
          <div className="inline-flex items-center space-x-2 bg-white px-6 py-3 rounded-full shadow-soft border border-neutral-200">
            <FileText className="w-4 h-4 text-neutral-600" />
            <span className="text-sm text-neutral-600">
              This demo switches between both databases in real-time to showcase performance differences
            </span>
          </div>
        </div>
      </div>
    </div>
  )
} 