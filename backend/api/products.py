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
    
    return CategoriesResource, ProductsResource, ProductResource 