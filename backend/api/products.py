from flask import request
from flask_restful import Resource


def create_product_resources(db_manager, time_api_call, create_api_response):
    """Factory function to create product-related resources with initialized dependencies"""
    
    class CategoriesResource(Resource):
        @time_api_call
        def get(self):
            categories_data = db_manager.get_all_categories()
            return create_api_response(categories_data)

    class ProductsResource(Resource):
        @time_api_call
        def get(self):
            # Get query parameters
            category_id = request.args.get('category')
            search_term = request.args.get('search')
            
            # Convert category_id to int if provided
            if category_id:
                try:
                    category_id = int(category_id)
                except ValueError:
                    category_id = None
            else:
                category_id = None
            
            products_data = db_manager.get_all_products(category_id, search_term)
            return create_api_response(products_data)

    class ProductResource(Resource):
        def get(self, product_id):
            product_data = db_manager.get_product_by_id(product_id)
            
            if not product_data:
                return create_api_response(None, False, "Product not found"), 404
            
            return create_api_response({'product': product_data})
    
    # Filter endpoints
    class ProductsByPriceRangeResource(Resource):
        @time_api_call
        def get(self):
            min_price = request.args.get('min_price', type=float)
            max_price = request.args.get('max_price', type=float)
            
            if min_price is None and max_price is None:
                return create_api_response(None, False, "At least one price parameter required"), 400
            
            products_data = db_manager.get_products_by_price_range(
                min_price or 0, 
                max_price or float('inf')
            )
            return create_api_response(products_data)
    
    class ProductsByRatingResource(Resource):
        @time_api_call
        def get(self):
            min_rating = request.args.get('min_rating', type=float, default=4.0)
            
            if min_rating < 0 or min_rating > 5:
                return create_api_response(None, False, "Rating must be between 0 and 5"), 400
            
            products_data = db_manager.get_products_by_rating(min_rating)
            return create_api_response(products_data)
    
    class ProductsByDiscountStatusResource(Resource):
        @time_api_call
        def get(self):
            has_discount = request.args.get('has_discount', type=lambda v: v.lower() == 'true', default=True)
            
            products_data = db_manager.get_products_by_discount_status(has_discount)
            return create_api_response(products_data)
    
    class ProductsByFeatureResource(Resource):
        @time_api_call
        def get(self):
            feature_keyword = request.args.get('feature', type=str)
            
            if not feature_keyword:
                return create_api_response(None, False, "Feature keyword is required"), 400
            
            products_data = db_manager.get_products_by_feature(feature_keyword)
            return create_api_response(products_data)
    
    class ProductsByStockLevelResource(Resource):
        @time_api_call
        def get(self):
            min_stock = request.args.get('min_stock', type=int, default=0)
            
            if min_stock < 0:
                return create_api_response(None, False, "Minimum stock must be non-negative"), 400
            
            products_data = db_manager.get_products_by_stock_level(min_stock)
            return create_api_response(products_data)
    
    class ProductsByAvailabilityResource(Resource):
        @time_api_call
        def get(self):
            is_available = request.args.get('is_available', type=lambda v: v.lower() == 'true', default=True)
            
            products_data = db_manager.get_products_by_availability(is_available)
            return create_api_response(products_data)
    
    class ProductsAdvancedFilterResource(Resource):
        @time_api_call
        def get(self):
            # Get all possible filter parameters
            min_price = request.args.get('min_price', type=float)
            max_price = request.args.get('max_price', type=float)
            min_rating = request.args.get('min_rating', type=float)
            category_id = request.args.get('category_id', type=int)
            has_discount = request.args.get('has_discount', type=lambda v: v.lower() == 'true')
            feature_keyword = request.args.get('feature', type=str)
            min_stock = request.args.get('min_stock', type=int)
            is_available = request.args.get('is_available', type=lambda v: v.lower() == 'true')
            search_term = request.args.get('search', type=str)
            
            # Validate rating if provided
            if min_rating is not None and (min_rating < 0 or min_rating > 5):
                return create_api_response(None, False, "Rating must be between 0 and 5"), 400
            
            # Validate stock if provided
            if min_stock is not None and min_stock < 0:
                return create_api_response(None, False, "Minimum stock must be non-negative"), 400
            
            products_data = db_manager.get_products_advanced_filter(
                min_price=min_price,
                max_price=max_price,
                min_rating=min_rating,
                category_id=category_id,
                has_discount=has_discount,
                feature_keyword=feature_keyword,
                min_stock=min_stock,
                is_available=is_available,
                search_term=search_term
            )
            return create_api_response(products_data)
    
    return (CategoriesResource, ProductsResource, ProductResource, 
            ProductsByPriceRangeResource, ProductsByRatingResource, 
            ProductsByDiscountStatusResource, ProductsByFeatureResource,
            ProductsByStockLevelResource, ProductsByAvailabilityResource,
            ProductsAdvancedFilterResource) 