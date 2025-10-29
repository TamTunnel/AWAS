
# Create example files and implementation code
import json

# 5. Example ai-actions.json
example_manifest = {
    "$schema": "https://awas.dev/schema/v1/manifest.json",
    "version": "1.0",
    "name": "E-Commerce Example Store",
    "description": "AI-readable actions for product browsing and shopping",
    "actions": [
        {
            "id": "search_products",
            "type": "search",
            "name": "Search Products",
            "description": "Search for products by keyword, category, or filters",
            "method": "GET",
            "endpoint": "/api/search",
            "selector": "form[role='search']",
            "inputs": [
                {
                    "name": "q",
                    "type": "string",
                    "required": True,
                    "description": "Search query",
                    "selector": "input[name='q']"
                },
                {
                    "name": "category",
                    "type": "string",
                    "required": False,
                    "description": "Filter by category",
                    "selector": "select[name='category']",
                    "validation": {
                        "enum": ["electronics", "clothing", "home", "sports"]
                    }
                },
                {
                    "name": "page",
                    "type": "integer",
                    "required": False,
                    "default": 1,
                    "description": "Page number for pagination"
                }
            ],
            "outputs": {
                "type": "object",
                "schema": {
                    "success": "boolean",
                    "results": "array",
                    "total_results": "integer",
                    "page": "integer",
                    "per_page": "integer"
                },
                "success_codes": [200],
                "error_codes": {
                    "400": "Invalid search parameters",
                    "429": "Rate limit exceeded"
                }
            }
        },
        {
            "id": "apply_filters",
            "type": "filter",
            "name": "Apply Product Filters",
            "description": "Filter products by price range, brand, rating, etc.",
            "method": "GET",
            "endpoint": "/products/filter",
            "selector": "form[data-action='filter']",
            "inputs": [
                {
                    "name": "category",
                    "type": "array",
                    "required": False,
                    "selector": "input[name='category[]']:checked"
                },
                {
                    "name": "price_min",
                    "type": "number",
                    "required": False,
                    "selector": "input[name='price_min']",
                    "validation": {
                        "min": 0
                    }
                },
                {
                    "name": "price_max",
                    "type": "number",
                    "required": False,
                    "selector": "input[name='price_max']",
                    "validation": {
                        "min": 0
                    }
                },
                {
                    "name": "brand",
                    "type": "array",
                    "required": False,
                    "selector": "input[name='brand[]']:checked"
                },
                {
                    "name": "rating",
                    "type": "integer",
                    "required": False,
                    "selector": "select[name='rating']",
                    "validation": {
                        "min": 1,
                        "max": 5
                    }
                }
            ]
        },
        {
            "id": "add_to_cart",
            "type": "form_submission",
            "name": "Add Product to Cart",
            "description": "Add a product to the shopping cart",
            "method": "POST",
            "endpoint": "/api/cart/add",
            "selector": "button[data-action='add-to-cart']",
            "authentication_required": False,
            "inputs": [
                {
                    "name": "product_id",
                    "type": "string",
                    "required": True,
                    "selector": "input[name='product_id']",
                    "validation": {
                        "pattern": "^PROD-[A-Z0-9]+$"
                    }
                },
                {
                    "name": "quantity",
                    "type": "integer",
                    "required": False,
                    "default": 1,
                    "selector": "input[name='quantity']",
                    "validation": {
                        "min": 1,
                        "max": 100
                    }
                },
                {
                    "name": "variant_id",
                    "type": "string",
                    "required": False,
                    "selector": "select[name='variant']"
                }
            ],
            "outputs": {
                "type": "object",
                "schema": {
                    "success": "boolean",
                    "cart_id": "string",
                    "product_id": "string",
                    "quantity": "integer",
                    "total_items": "integer",
                    "cart_total": "number"
                }
            }
        },
        {
            "id": "view_product",
            "type": "navigation",
            "name": "View Product Details",
            "description": "Navigate to product detail page",
            "method": "GET",
            "endpoint": "/product/{product_id}",
            "inputs": [
                {
                    "name": "product_id",
                    "type": "string",
                    "required": True
                }
            ]
        },
        {
            "id": "add_to_wishlist",
            "type": "navigation",
            "name": "Add to Wishlist",
            "description": "Add product to user's wishlist",
            "method": "GET",
            "endpoint": "/wishlist/add",
            "authentication_required": True,
            "inputs": [
                {
                    "name": "id",
                    "type": "string",
                    "required": True,
                    "description": "Product ID"
                }
            ]
        },
        {
            "id": "compare_products",
            "type": "navigation",
            "name": "Compare Products",
            "description": "Add product to comparison list",
            "method": "GET",
            "endpoint": "/compare",
            "inputs": [
                {
                    "name": "add",
                    "type": "string",
                    "required": True,
                    "description": "Product ID to add to comparison"
                }
            ]
        }
    ],
    "workflows": [
        {
            "id": "purchase_flow",
            "name": "Complete Purchase",
            "description": "Full workflow from search to checkout",
            "steps": [
                "search_products",
                "view_product",
                "add_to_cart",
                "view_cart",
                "proceed_to_checkout"
            ]
        },
        {
            "id": "product_discovery",
            "name": "Product Discovery",
            "description": "Find and compare products",
            "steps": [
                "search_products",
                "apply_filters",
                "view_product",
                "compare_products"
            ]
        }
    ],
    "rate_limits": {
        "requests_per_minute": 60,
        "requests_per_hour": 1000,
        "burst_limit": 10,
        "concurrent_requests": 3
    },
    "authentication": {
        "required": False,
        "optional_for": ["add_to_cart", "view_cart", "add_to_wishlist"],
        "methods": ["session", "api_key", "oauth"],
        "endpoints": {
            "login": "/auth/login",
            "token": "/auth/token",
            "refresh": "/auth/refresh"
        }
    }
}

files['examples/ai-actions.json'] = json.dumps(example_manifest, indent=2)
print("Created examples/ai-actions.json")
print(f"Length: {len(files['examples/ai-actions.json'])} characters")
