# Database Filter Operations

This document describes the filter operations implemented across all three databases (MySQL, Aerospike, and MongoDB) in the grocery store application.

## Overview

The application now supports comprehensive filtering capabilities that demonstrate the different approaches each database uses for filtering operations:

- **Aerospike**: Uses scan operations with callback filters
- **MySQL**: Uses SQL WHERE clauses with SQLAlchemy ORM
- **MongoDB**: Uses find operations and aggregation pipelines

## Available Filter Operations

### 1. Price Range Filter
**Endpoint**: `GET /api/products/filter/price`

**Parameters**:
- `min_price` (float): Minimum price
- `max_price` (float): Maximum price

**Example**:
```bash
curl -H "X-Database: aerospike" "http://localhost:5001/api/products/filter/price?min_price=10&max_price=50"
```

**Supported by**: All databases (MySQL, Aerospike, MongoDB)

### 2. Rating Filter
**Endpoint**: `GET /api/products/filter/rating`

**Parameters**:
- `min_rating` (float): Minimum rating (0-5, default: 4.0)

**Example**:
```bash
curl -H "X-Database: aerospike" "http://localhost:5001/api/products/filter/rating?min_rating=4.5"
```

**Supported by**: Aerospike, MongoDB (MySQL doesn't have rating data)

### 3. Discount Status Filter
**Endpoint**: `GET /api/products/filter/discount`

**Parameters**:
- `has_discount` (boolean): Whether to show products with discounts (default: true)

**Example**:
```bash
curl -H "X-Database: mongodb" "http://localhost:5001/api/products/filter/discount?has_discount=true"
```

**Supported by**: Aerospike, MongoDB (MySQL doesn't have discount data)

### 4. Feature Filter
**Endpoint**: `GET /api/products/filter/feature`

**Parameters**:
- `feature` (string): Feature keyword to search for

**Example**:
```bash
curl -H "X-Database: aerospike" "http://localhost:5001/api/products/filter/feature?feature=Kosher"
```

**Supported by**: Aerospike, MongoDB (MySQL doesn't have feature data)

### 5. Stock Level Filter
**Endpoint**: `GET /api/products/filter/stock`

**Parameters**:
- `min_stock` (int): Minimum stock level (default: 0)

**Example**:
```bash
curl -H "X-Database: mysql" "http://localhost:5001/api/products/filter/stock?min_stock=50"
```

**Supported by**: MySQL only (Aerospike/MongoDB don't track stock levels)

### 6. Availability Filter
**Endpoint**: `GET /api/products/filter/availability`

**Parameters**:
- `is_available` (boolean): Whether to show available products (default: true)

**Example**:
```bash
curl -H "X-Database: mysql" "http://localhost:5001/api/products/filter/availability?is_available=true"
```

**Supported by**: MySQL only (Aerospike/MongoDB don't track availability)

### 7. Advanced Multi-Criteria Filter
**Endpoint**: `GET /api/products/filter/advanced`

**Parameters** (all optional):
- `min_price` (float): Minimum price
- `max_price` (float): Maximum price
- `min_rating` (float): Minimum rating (Aerospike/MongoDB only)
- `category_id` (int): Category ID
- `has_discount` (boolean): Has discount (Aerospike/MongoDB only)
- `feature_keyword` (string): Feature keyword (Aerospike/MongoDB only)
- `min_stock` (int): Minimum stock (MySQL only)
- `is_available` (boolean): Is available (MySQL only)
- `search_term` (string): Search in product names

**Example**:
```bash
curl -H "X-Database: aerospike" "http://localhost:5001/api/products/filter/advanced?min_price=20&max_price=100&min_rating=4.0&has_discount=true"
```

**Supported by**: All databases (with database-specific parameters)

## Database-Specific Implementations

### Aerospike Implementation
- Uses `scan()` operations with callback functions
- Filters are applied in memory during scan
- Supports all CSV fields (rating, discount, feature, etc.)
- Example query: `SCAN grocery.products WHERE price BETWEEN 10 AND 50`

### MySQL Implementation
- Uses SQLAlchemy ORM with `filter()` methods
- Leverages SQL WHERE clauses for efficient filtering
- Limited to basic product fields (no rating, discount, feature)
- Example query: `SELECT * FROM products WHERE price BETWEEN 10 AND 50`

### MongoDB Implementation
- Uses `find()` operations and aggregation pipelines
- Supports complex text search with regex
- Rating filtering uses aggregation pipeline to extract numeric values
- Example query: `db.products.find({price: {$gte: 10, $lte: 50}})`

## Performance Characteristics

### Aerospike
- **Pros**: Fast scan operations, supports all data fields
- **Cons**: Scan operations read all records, filtering done in memory

### MySQL
- **Pros**: Efficient SQL queries with indexes, familiar SQL syntax
- **Cons**: Limited to basic product fields, requires proper indexing

### MongoDB
- **Pros**: Flexible querying, powerful aggregation pipelines
- **Cons**: Complex queries can be slower, requires proper indexing

## Testing

Run the test suite to verify all filter operations:

```bash
cd tests/backend
python test_filters.py
```

This will test all filter operations across all three databases and verify that the API endpoints are working correctly.

## Usage Examples

### Frontend Integration
```javascript
// Switch to Aerospike and get products with rating >= 4.0
fetch('/api/products/filter/rating?min_rating=4.0', {
  headers: { 'X-Database': 'aerospike' }
})

// Switch to MySQL and get products with stock >= 50
fetch('/api/products/filter/stock?min_stock=50', {
  headers: { 'X-Database': 'mysql' }
})

// Advanced filtering with MongoDB
fetch('/api/products/filter/advanced?min_price=20&max_price=100&has_discount=true', {
  headers: { 'X-Database': 'mongodb' }
})
```

### Performance Comparison
The filter operations are logged with timing information, allowing you to compare performance across databases. Check the database logs in the application to see query execution times.

## Notes

1. **Database Switching**: Use the `X-Database` header to switch between databases
2. **Data Availability**: Not all fields are available in all databases due to different data models
3. **Error Handling**: All endpoints return appropriate HTTP status codes and error messages
4. **Validation**: Parameters are validated before processing (e.g., rating must be 0-5)
5. **Logging**: All operations are logged with timing information for performance analysis 