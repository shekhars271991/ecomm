'use client'

import { 
  Database, Table, FileText, Zap, Network, ArrowRight, Clock, 
  MapPin, Users, ShoppingCart, TrendingUp, Globe, Target,
  BarChart3, Layers, Timer, Lightbulb, Star, Wifi, Shield
} from 'lucide-react'
import { motion } from 'framer-motion'
import Image from 'next/image'

export default function WhyAerospikePage() {
  const useCases = [
    {
      title: "Live Inventory Tracking",
      icon: ShoppingCart,
      mysql: "Complex UPDATE queries with locking",
      aerospike: "Atomic operations with sub-ms latency",
      advantage: "Real-time stock updates across thousands of stores",
      example: "Stock: 50 → 49 (instant update for all users)"
    },
    {
      title: "Flash Sales with TTL",
      icon: Timer,
      mysql: "Scheduled jobs to expire offers",
      aerospike: "Built-in TTL expiration",
      advantage: "Automatic price reversion without cleanup jobs",
      example: "50% off expires in 10 minutes (auto-cleanup)"
    },
    {
      title: "Real-time Analytics",
      icon: BarChart3,
      mysql: "Aggregate queries slow down app",
      aerospike: "Real-time counters and metrics",
      advantage: "Live dashboards without performance impact",
      example: "Revenue: $125,432 (updating every second)"
    },
    {
      title: "Geospatial Delivery",
      icon: MapPin,
      mysql: "Complex spatial queries",
      aerospike: "Native geospatial indexes",
      advantage: "Find nearest stores/drivers instantly",
      example: "3 stores within 2km (0.1ms response)"
    },
    {
      title: "Session Management",
      icon: Users,
      mysql: "Database sessions with expiry logic",
      aerospike: "Native session storage with TTL",
      advantage: "Millions of concurrent sessions",
      example: "Cart expires in 30 min (automatic cleanup)"
    },
    {
      title: "Smart Recommendations",
      icon: Lightbulb,
      mysql: "Complex ML queries impact performance",
      aerospike: "Real-time model serving",
      advantage: "Personalized results without latency",
      example: "\"Customers like you bought...\" (instant)"
    }
  ]

  const performanceMetrics = [
    { metric: "Read Latency", mysql: "5-50ms", aerospike: "<1ms", improvement: "50x faster" },
    { metric: "Write Latency", mysql: "10-100ms", aerospike: "<1ms", improvement: "100x faster" },
    { metric: "Concurrent Users", mysql: "1,000s", aerospike: "100,000s", improvement: "100x scale" },
    { metric: "Data Durability", mysql: "99.9%", aerospike: "99.999%", improvement: "100x reliable" }
  ]

  const dataStructures = [
    {
      name: "Lists",
      mysql: "JSON columns or separate tables",
      aerospike: "Native LIST data type",
      useCase: "Shopping cart items, wish lists"
    },
    {
      name: "Maps",
      mysql: "Serialized JSON or key-value tables",
      aerospike: "Native MAP data type", 
      useCase: "User preferences, product attributes"
    },
    {
      name: "Sets",
      mysql: "Junction tables with unique constraints",
      aerospike: "Native mathematical sets",
      useCase: "Product categories, user tags"
    },
    {
      name: "Geospatial",
      mysql: "PostGIS extension required",
      aerospike: "Built-in GeoJSON support",
      useCase: "Store locations, delivery zones"
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-50 to-neutral-100">
      {/* Header */}
      <header className="bg-white border-b border-neutral-200 sticky top-0 z-10">
        <div className="container mx-auto px-4 py-6">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-4 mb-4">
              <div className="w-16 h-16 relative">
                <Image
                  src="/logos/aerospike-logo-yellow.webp"
                  alt="Aerospike Logo"
                  fill
                  className="object-contain"
                />
              </div>
              <div>
                <h1 className="text-4xl font-bold text-neutral-800 mb-2">
                  Why Choose Aerospike Over MySQL?
                </h1>
                <p className="text-lg text-neutral-600">
                  Real-world use cases where NoSQL delivers superior performance
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        
        {/* Hero Section */}
        <div className="max-w-6xl mx-auto mb-16">
          <div className="bg-gradient-to-r from-red-500 to-orange-500 rounded-3xl shadow-xl text-white p-8 md:p-12">
            <div className="grid md:grid-cols-2 gap-8 items-center">
              <div>
                <h2 className="text-3xl font-bold mb-4">Built for Speed & Scale</h2>
                <p className="text-lg opacity-90 mb-6">
                  Modern applications demand real-time performance. See how Aerospike's 
                  hybrid memory architecture delivers sub-millisecond responses at massive scale.
                </p>
                <div className="flex items-center space-x-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold">{'<1ms'}</div>
                    <div className="text-sm opacity-80">Response Time</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">100x</div>
                    <div className="text-sm opacity-80">Faster Than Disk</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">PB</div>
                    <div className="text-sm opacity-80">Scale Capacity</div>
                  </div>
                </div>
              </div>
              <div className="text-center">
                <div className="bg-white/20 rounded-2xl p-8 backdrop-blur">
                  <div className="w-20 h-20 relative mx-auto mb-4">
                    <Image
                      src="/logos/aerospike-logo-yellow.webp"
                      alt="Aerospike Logo"
                      fill
                      className="object-contain"
                    />
                  </div>
                  <div className="text-xl font-semibold">Hybrid Memory Architecture</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Use Cases Showcase */}
        <div className="mb-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-neutral-800 mb-4">Game-Changing Use Cases</h2>
            <p className="text-lg text-neutral-600 max-w-3xl mx-auto">
              Discover how leading companies use Aerospike to power real-time applications 
              that simply wouldn't be possible with traditional databases.
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-8">
            {useCases.map((useCase, index) => (
              <motion.div
                key={useCase.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="bg-white rounded-2xl shadow-soft border border-neutral-200 overflow-hidden"
              >
                <div className="p-6">
                  <div className="flex items-start space-x-4 mb-4">
                    <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center flex-shrink-0">
                      <useCase.icon className="w-6 h-6 text-red-600" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-neutral-800 mb-2">{useCase.title}</h3>
                      <p className="text-red-600 font-medium text-sm mb-2">{useCase.advantage}</p>
                      <div className="bg-neutral-50 rounded-lg p-3 font-mono text-sm text-neutral-700">
                        {useCase.example}
                      </div>
                    </div>
                  </div>
                  
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="border border-blue-200 rounded-lg p-3 bg-blue-50">
                      <div className="flex items-center space-x-2 mb-2">
                        <Database className="w-4 h-4 text-blue-600" />
                        <span className="font-medium text-blue-800 text-sm">MySQL</span>
                      </div>
                      <p className="text-xs text-blue-700">{useCase.mysql}</p>
                    </div>
                    
                    <div className="border border-red-200 rounded-lg p-3 bg-red-50">
                      <div className="flex items-center space-x-2 mb-2">
                        <Zap className="w-4 h-4 text-red-600" />
                        <span className="font-medium text-red-800 text-sm">Aerospike</span>
                      </div>
                      <p className="text-xs text-red-700">{useCase.aerospike}</p>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Performance Comparison */}
        <div className="mb-16">
          <div className="bg-white rounded-2xl shadow-soft border border-neutral-200 p-8">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-neutral-800 mb-4">Performance at Scale</h2>
              <p className="text-lg text-neutral-600">
                Real-world performance metrics from production environments
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {performanceMetrics.map((metric, index) => (
                <motion.div
                  key={metric.metric}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className="text-center p-6 bg-gradient-to-br from-neutral-50 to-neutral-100 rounded-xl"
                >
                  <h4 className="font-semibold text-neutral-800 mb-4">{metric.metric}</h4>
                  <div className="space-y-2 mb-4">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-blue-600">MySQL</span>
                      <span className="font-mono text-neutral-700">{metric.mysql}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-red-600">Aerospike</span>
                      <span className="font-mono text-neutral-700">{metric.aerospike}</span>
                    </div>
                  </div>
                  <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-xs font-medium">
                    {metric.improvement}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>

        {/* Advanced Data Structures */}
        <div className="mb-16">
          <div className="bg-white rounded-2xl shadow-soft border border-neutral-200 p-8">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-neutral-800 mb-4">Rich Data Types</h2>
              <p className="text-lg text-neutral-600">
                Native support for complex data structures without the overhead
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              {dataStructures.map((structure, index) => (
                <motion.div
                  key={structure.name}
                  initial={{ opacity: 0, x: index % 2 === 0 ? -20 : 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className="border border-neutral-200 rounded-xl p-6"
                >
                  <div className="flex items-center space-x-3 mb-4">
                    <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                      <Layers className="w-5 h-5 text-purple-600" />
                    </div>
                    <h3 className="text-lg font-bold text-neutral-800">{structure.name}</h3>
                  </div>
                  
                  <div className="space-y-3 mb-4">
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                      <div className="text-sm font-medium text-blue-800 mb-1">MySQL</div>
                      <div className="text-xs text-blue-700">{structure.mysql}</div>
                    </div>
                    
                    <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                      <div className="text-sm font-medium text-red-800 mb-1">Aerospike</div>
                      <div className="text-xs text-red-700">{structure.aerospike}</div>
                    </div>
                  </div>
                  
                  <div className="bg-neutral-50 rounded-lg p-3">
                    <div className="text-sm font-medium text-neutral-800 mb-1">Use Case</div>
                    <div className="text-xs text-neutral-600">{structure.useCase}</div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>

        {/* Real-World Scenarios */}
        <div className="mb-16">
          <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl shadow-xl text-white p-8">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold mb-4">Enterprise Success Stories</h2>
              <p className="text-lg opacity-90">
                See how industry leaders leverage Aerospike for mission-critical applications
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-6">
              <div className="bg-white/10 backdrop-blur rounded-xl p-6">
                <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center mb-4">
                  <Globe className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-bold mb-3">Global E-commerce</h3>
                <p className="text-sm opacity-90 mb-4">
                  Handle Black Friday traffic spikes with consistent sub-millisecond performance 
                  across millions of concurrent users.
                </p>
                <div className="text-xs opacity-75">
                  "99.999% uptime during peak traffic"
                </div>
              </div>

              <div className="bg-white/10 backdrop-blur rounded-xl p-6">
                <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center mb-4">
                  <Target className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-bold mb-3">Ad Tech Platforms</h3>
                <p className="text-sm opacity-90 mb-4">
                  Real-time bidding and audience targeting with microsecond decision making 
                  for programmatic advertising.
                </p>
                <div className="text-xs opacity-75">
                  "100M+ bid requests per second"
                </div>
              </div>

              <div className="bg-white/10 backdrop-blur rounded-xl p-6">
                <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center mb-4">
                  <Shield className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-bold mb-3">Financial Services</h3>
                <p className="text-sm opacity-90 mb-4">
                  Fraud detection and risk scoring with real-time transaction processing 
                  and compliance monitoring.
                </p>
                <div className="text-xs opacity-75">
                  "Real-time fraud detection at scale"
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Architecture Comparison */}
        <div className="mb-16">
          <div className="bg-white rounded-2xl shadow-soft border border-neutral-200 p-8">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-neutral-800 mb-4">Architecture Deep Dive</h2>
              <p className="text-lg text-neutral-600">
                Understanding the fundamental differences that drive performance
              </p>
            </div>

            <div className="grid lg:grid-cols-2 gap-8">
              {/* MySQL Architecture */}
              <div className="border border-blue-200 rounded-xl p-6 bg-blue-50">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="w-10 h-10 bg-blue-500 rounded-xl flex items-center justify-center">
                    <Database className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-blue-800">MySQL Traditional Approach</h3>
                </div>

                <div className="space-y-4">
                  <div className="bg-white rounded-lg p-4">
                    <h4 className="font-medium text-blue-800 mb-2">Storage</h4>
                    <p className="text-sm text-blue-700">Disk-based with memory caching layer</p>
                  </div>
                  <div className="bg-white rounded-lg p-4">
                    <h4 className="font-medium text-blue-800 mb-2">Query Processing</h4>
                    <p className="text-sm text-blue-700">SQL parsing, optimization, and execution</p>
                  </div>
                  <div className="bg-white rounded-lg p-4">
                    <h4 className="font-medium text-blue-800 mb-2">Scaling</h4>
                    <p className="text-sm text-blue-700">Vertical scaling with replication</p>
                  </div>
                </div>

                <div className="mt-4 p-3 bg-blue-100 rounded-lg">
                  <div className="text-xs text-blue-800 font-medium">Best for: Complex queries, reporting, ACID compliance</div>
                </div>
              </div>

              {/* Aerospike Architecture */}
              <div className="border border-red-200 rounded-xl p-6 bg-red-50">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="w-10 h-10 bg-red-500 rounded-xl flex items-center justify-center">
                    <div className="w-5 h-5 relative">
                      <Image
                        src="/logos/aerospike-logo-yellow.webp"
                        alt="Aerospike Logo"
                        fill
                        className="object-contain"
                      />
                    </div>
                  </div>
                  <h3 className="text-xl font-bold text-red-800">Aerospike Hybrid Memory</h3>
                </div>

                <div className="space-y-4">
                  <div className="bg-white rounded-lg p-4">
                    <h4 className="font-medium text-red-800 mb-2">Storage</h4>
                    <p className="text-sm text-red-700">Hybrid memory architecture (RAM + Flash)</p>
                  </div>
                  <div className="bg-white rounded-lg p-4">
                    <h4 className="font-medium text-red-800 mb-2">Query Processing</h4>
                    <p className="text-sm text-red-700">Direct key-based access, no query planning</p>
                  </div>
                  <div className="bg-white rounded-lg p-4">
                    <h4 className="font-medium text-red-800 mb-2">Scaling</h4>
                    <p className="text-sm text-red-700">Horizontal scaling with automatic sharding</p>
                  </div>
                </div>

                <div className="mt-4 p-3 bg-red-100 rounded-lg">
                  <div className="text-xs text-red-800 font-medium">Best for: Real-time apps, high throughput, low latency</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Implementation Examples */}
        <div className="mb-16">
          <div className="bg-white rounded-2xl shadow-soft border border-neutral-200 p-8">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-neutral-800 mb-4">Code Examples</h2>
              <p className="text-lg text-neutral-600">
                See the difference in implementation complexity and performance
              </p>
            </div>

            <div className="space-y-8">
              {/* Real-time Inventory Example */}
              <div className="border border-neutral-200 rounded-xl overflow-hidden">
                <div className="bg-neutral-50 p-4 border-b border-neutral-200">
                  <h3 className="font-bold text-neutral-800">Real-time Inventory Update</h3>
                </div>
                
                <div className="grid md:grid-cols-2 gap-0">
                  <div className="p-6 border-r border-neutral-200">
                    <h4 className="font-medium text-blue-800 mb-3 flex items-center">
                      <Database className="w-4 h-4 mr-2" />
                      MySQL Approach
                    </h4>
                    <div className="bg-blue-50 rounded-lg p-4 font-mono text-sm">
                      <div className="text-blue-900">
                        {'BEGIN TRANSACTION;'}<br/>
                        {'UPDATE products'}<br/>
                        {'SET stock = stock - 1'}<br/>
                        {'WHERE id = ? AND stock > 0;'}<br/>
                        {'-- Check affected rows'}<br/>
                        {'IF affected_rows = 0 THEN'}<br/>
                        {'  ROLLBACK;'}<br/>
                        {'ELSE'}<br/>
                        {'  COMMIT;'}<br/>
                        {'END IF;'}
                      </div>
                    </div>
                    <div className="mt-3 text-xs text-blue-700">
                      ⚠️ Potential for deadlocks and slow performance
                    </div>
                  </div>
                  
                  <div className="p-6">
                    <h4 className="font-medium text-red-800 mb-3 flex items-center">
                      <div className="w-4 h-4 mr-2 relative">
                        <Image
                          src="/logos/aerospike-logo-yellow.webp"
                          alt="Aerospike Logo"
                          fill
                          className="object-contain"
                        />
                      </div>
                      Aerospike Approach
                    </h4>
                    <div className="bg-red-50 rounded-lg p-4 font-mono text-sm">
                      <div className="text-red-900">
                        {'client.operate('}<br/>
                        {'  key=Key("grocery", "products", id),'}<br/>
                        {'  ops=['}<br/>
                        {'    operations.add("stock", -1),'}<br/>
                        {'    operations.read("stock")'}<br/>
                        {'  ]'}<br/>
                        {')'}
                      </div>
                    </div>
                    <div className="mt-3 text-xs text-red-700">
                      ✅ Atomic operation, no locks, sub-ms performance
                    </div>
                  </div>
                </div>
              </div>

              {/* Session Storage Example */}
              <div className="border border-neutral-200 rounded-xl overflow-hidden">
                <div className="bg-neutral-50 p-4 border-b border-neutral-200">
                  <h3 className="font-bold text-neutral-800">Session Storage with TTL</h3>
                </div>
                
                <div className="grid md:grid-cols-2 gap-0">
                  <div className="p-6 border-r border-neutral-200">
                    <h4 className="font-medium text-blue-800 mb-3 flex items-center">
                      <Database className="w-4 h-4 mr-2" />
                      MySQL Approach
                    </h4>
                    <div className="bg-blue-50 rounded-lg p-4 font-mono text-sm">
                      <div className="text-blue-900">
                        {'INSERT INTO user_sessions'}<br/>
                        {'(session_id, data, expires_at)'}<br/>
                        {'VALUES (?, ?, NOW() + INTERVAL 30 MINUTE)'}<br/>
                        {'ON DUPLICATE KEY UPDATE'}<br/>
                        {'  data = VALUES(data),'}<br/>
                        {'  expires_at = VALUES(expires_at);'}<br/><br/>
                        {'-- Cleanup job needed:'}<br/>
                        {'DELETE FROM user_sessions'}<br/>
                        {'WHERE expires_at < NOW();'}
                      </div>
                    </div>
                  </div>
                  
                  <div className="p-6">
                    <h4 className="font-medium text-red-800 mb-3 flex items-center">
                      <div className="w-4 h-4 mr-2 relative">
                        <Image
                          src="/logos/aerospike-logo-yellow.webp"
                          alt="Aerospike Logo"
                          fill
                          className="object-contain"
                        />
                      </div>
                      Aerospike Approach
                    </h4>
                    <div className="bg-red-50 rounded-lg p-4 font-mono text-sm">
                      <div className="text-red-900">
                        {'client.put('}<br/>
                        {'  key=Key("grocery", "sessions", session_id),'}<br/>
                        {'  bins={"data": session_data},'}<br/>
                        {'  ttl=1800  # 30 minutes'}<br/>
                        {')'}
                      </div>
                    </div>
                    <div className="mt-3 text-xs text-red-700">
                      ✅ Automatic expiration, no cleanup jobs needed
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Call to Action */}
        <div className="text-center">
          <div className="bg-gradient-to-r from-orange-400 to-red-500 rounded-2xl shadow-xl text-white p-8 max-w-4xl mx-auto">
            <div className="w-16 h-16 relative mx-auto mb-4">
              <Image
                src="/logos/aerospike-logo-yellow.webp"
                alt="Aerospike Logo"
                fill
                className="object-contain"
              />
            </div>
            <h2 className="text-3xl font-bold mb-4">Ready to Experience the Difference?</h2>
            <p className="text-lg opacity-90 mb-6">
              Switch between MySQL and Aerospike in real-time using the database selector 
              in the header to see the performance difference firsthand.
            </p>
            <div className="flex justify-center items-center space-x-6">
              <div className="flex items-center space-x-2 bg-white/20 rounded-lg px-4 py-2">
                <Database className="w-5 h-5" />
                <span>Try MySQL Mode</span>
              </div>
              <ArrowRight className="w-6 h-6" />
              <div className="flex items-center space-x-2 bg-white/20 rounded-lg px-4 py-2">
                <div className="w-5 h-5 relative">
                  <Image
                    src="/logos/aerospike-logo-yellow.webp"
                    alt="Aerospike Logo"
                    fill
                    className="object-contain"
                  />
                </div>
                <span>Switch to Aerospike</span>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  )
} 