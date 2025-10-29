
# 8. Python/Flask Implementation
files['examples/implementations/python/awas_middleware.py'] = '''"""
AWAS Middleware for Python/Flask
Version 1.0.0

Provides server-side support for AWAS (AI Web Action Standard)
"""

from flask import Flask, request, jsonify, g, send_from_directory
from functools import wraps
import json
import time
import logging
from typing import Dict, List, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class AWASMiddleware:
    """Middleware to handle AWAS requests in Flask applications"""
    
    def __init__(self, app: Flask, manifest_path: str = '.well-known/ai-actions.json',
                 enable_rate_limiting: bool = True, enable_logging: bool = True):
        """
        Initialize AWAS middleware
        
        Args:
            app: Flask application instance
            manifest_path: Path to AI actions manifest
            enable_rate_limiting: Enable rate limiting for AI agents
            enable_logging: Enable audit logging
        """
        self.app = app
        self.manifest_path = manifest_path
        self.enable_rate_limiting = enable_rate_limiting
        self.enable_logging = enable_logging
        self.manifest = self._load_manifest()
        self.rate_limit_store = {}
        
        # Register well-known routes
        self._register_routes()
        
        # Register before_request handler
        if enable_rate_limiting:
            app.before_request(self._check_rate_limit)
        
        logger.info("AWAS Middleware initialized")
    
    def _load_manifest(self) -> Dict:
        """Load the AI action manifest"""
        try:
            with open(self.manifest_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Manifest file not found: {self.manifest_path}")
            return {"version": "1.0", "actions": []}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in manifest: {e}")
            return {"version": "1.0", "actions": []}
    
    def _register_routes(self):
        """Register well-known routes for AI discovery"""
        
        @self.app.route('/.well-known/ai-actions.json')
        def ai_actions_manifest():
            """Serve the AI action manifest"""
            return jsonify(self.manifest)
        
        @self.app.route('/.well-known/ai-sitemap.json')
        def ai_sitemap():
            """Serve AI sitemap (optional, customize as needed)"""
            return jsonify({
                "version": "1.0",
                "pages": self._generate_sitemap()
            })
        
        @self.app.route('/.well-known/ai-capabilities')
        def ai_capabilities():
            """Expose AI capabilities"""
            return jsonify({
                "version": "1.0",
                "supported_protocols": ["HTTP/1.1", "HTTP/2"],
                "auth_methods": self.manifest.get("authentication", {}).get("methods", []),
                "rate_limits": self.manifest.get("rate_limits", {}),
                "features": [
                    "structured_actions",
                    "workflow_support",
                    "audit_logging" if self.enable_logging else None
                ]
            })
    
    def _generate_sitemap(self) -> List[Dict]:
        """Generate AI sitemap from routes (override this method)"""
        return []
    
    def _is_ai_agent(self, req=None) -> bool:
        """Check if request is from an AI agent"""
        req = req or request
        return req.headers.get('X-AI-Agent') == 'true'
    
    def _get_client_id(self, req=None) -> str:
        """Get client identifier for rate limiting"""
        req = req or request
        return req.headers.get('X-AI-Agent-Name', req.remote_addr)
    
    def _check_rate_limit(self):
        """Check rate limits before request"""
        if not self._is_ai_agent():
            return  # Rate limiting only for AI agents
        
        client_id = self._get_client_id()
        current_time = time.time()
        
        # Initialize client store
        if client_id not in self.rate_limit_store:
            self.rate_limit_store[client_id] = {
                'requests': [],
                'burst_count': 0
            }
        
        client_store = self.rate_limit_store[client_id]
        
        # Remove old requests (older than 1 minute)
        client_store['requests'] = [
            t for t in client_store['requests'] 
            if current_time - t < 60
        ]
        
        # Get rate limits from manifest
        rate_limits = self.manifest.get('rate_limits', {})
        requests_per_minute = rate_limits.get('requests_per_minute', 60)
        burst_limit = rate_limits.get('burst_limit', 10)
        
        # Check per-minute rate limit
        if len(client_store['requests']) >= requests_per_minute:
            return jsonify({
                "error": "Rate limit exceeded",
                "retry_after": 60
            }), 429
        
        # Check burst limit
        recent_requests = [
            t for t in client_store['requests']
            if current_time - t < 10
        ]
        if len(recent_requests) >= burst_limit:
            return jsonify({
                "error": "Burst limit exceeded",
                "retry_after": 10
            }), 429
        
        # Add current request
        client_store['requests'].append(current_time)
    
    def validate_action(self, action_id: str) -> Callable:
        """
        Decorator to validate action requests
        
        Usage:
            @app.route('/api/cart/add', methods=['POST'])
            @awas.validate_action('add_to_cart')
            def add_to_cart():
                # Your logic here
                pass
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Find action in manifest
                action = self._get_action(action_id)
                if not action:
                    return jsonify({
                        "error": f"Unknown action: {action_id}"
                    }), 400
                
                # Check authentication
                if action.get('authentication_required', False):
                    if not self._check_authentication():
                        return jsonify({
                            "error": "Authentication required"
                        }), 401
                
                # Validate inputs
                if request.method in ['POST', 'PUT', 'PATCH']:
                    data = request.get_json() or {}
                else:
                    data = request.args.to_dict()
                
                validation_result = self._validate_inputs(action, data)
                if not validation_result['valid']:
                    return jsonify({
                        "error": "Validation failed",
                        "details": validation_result['errors']
                    }), 400
                
                # Log action
                if self.enable_logging:
                    self._log_action(action_id, data)
                
                # Execute original function
                result = f(*args, **kwargs)
                
                # Add AWAS headers to response
                if isinstance(result, tuple):
                    response, status_code = result
                    if hasattr(response, 'headers'):
                        response.headers['X-AI-Action-Success'] = 'true'
                        response.headers['X-AI-Action-ID'] = action_id
                    return response, status_code
                
                return result
            
            return decorated_function
        return decorator
    
    def _get_action(self, action_id: str) -> Optional[Dict]:
        """Get action from manifest by ID"""
        for action in self.manifest.get('actions', []):
            if action.get('id') == action_id:
                return action
        return None
    
    def _check_authentication(self) -> bool:
        """Check if request is authenticated (override this method)"""
        # Implement your authentication logic
        return 'Authorization' in request.headers or 'user_id' in g
    
    def _validate_inputs(self, action: Dict, data: Dict) -> Dict:
        """Validate input parameters"""
        errors = []
        inputs = action.get('inputs', [])
        
        for input_def in inputs:
            name = input_def.get('name')
            required = input_def.get('required', False)
            param_type = input_def.get('type', 'string')
            validation = input_def.get('validation', {})
            
            value = data.get(name)
            
            # Check required
            if required and value is None:
                errors.append(f"Parameter '{name}' is required")
                continue
            
            if value is None:
                continue
            
            # Type validation
            type_validators = {
                'string': str,
                'integer': int,
                'number': (int, float),
                'boolean': bool,
                'array': list,
                'object': dict
            }
            
            expected_type = type_validators.get(param_type)
            if expected_type and not isinstance(value, expected_type):
                errors.append(f"Parameter '{name}' should be {param_type}")
                continue
            
            # Validation rules
            if validation:
                # Pattern validation
                if 'pattern' in validation and isinstance(value, str):
                    import re
                    if not re.match(validation['pattern'], value):
                        errors.append(f"Parameter '{name}' does not match required pattern")
                
                # Range validation
                if isinstance(value, (int, float)):
                    if 'min' in validation and value < validation['min']:
                        errors.append(f"Parameter '{name}' must be >= {validation['min']}")
                    if 'max' in validation and value > validation['max']:
                        errors.append(f"Parameter '{name}' must be <= {validation['max']}")
                
                # Length validation
                if isinstance(value, (str, list)):
                    if 'minLength' in validation and len(value) < validation['minLength']:
                        errors.append(f"Parameter '{name}' must have length >= {validation['minLength']}")
                    if 'maxLength' in validation and len(value) > validation['maxLength']:
                        errors.append(f"Parameter '{name}' must have length <= {validation['maxLength']}")
                
                # Enum validation
                if 'enum' in validation and value not in validation['enum']:
                    errors.append(f"Parameter '{name}' must be one of: {', '.join(map(str, validation['enum']))}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _log_action(self, action_id: str, params: Dict):
        """Log AI action for audit trail"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'action_id': action_id,
            'ai_agent': request.headers.get('X-AI-Agent-Name', 'Unknown'),
            'ip_address': request.remote_addr,
            'params': params,
            'user_id': g.get('user_id', 'anonymous')
        }
        
        logger.info(f"AI_ACTION: {json.dumps(log_entry)}")


# Example Usage
if __name__ == '__main__':
    app = Flask(__name__)
    
    # Initialize AWAS middleware
    awas = AWASMiddleware(
        app,
        manifest_path='.well-known/ai-actions.json',
        enable_rate_limiting=True,
        enable_logging=True
    )
    
    # Example endpoint with AWAS validation
    @app.route('/api/cart/add', methods=['POST'])
    @awas.validate_action('add_to_cart')
    def add_to_cart():
        data = request.get_json()
        
        # Your cart logic here
        result = {
            "success": True,
            "cart_id": "cart_123456",
            "product_id": data.get('product_id'),
            "quantity": data.get('quantity', 1),
            "total_items": 3,
            "cart_total": 899.97
        }
        
        return jsonify(result), 200
    
    @app.route('/api/search', methods=['GET'])
    @awas.validate_action('search_products')
    def search_products():
        query = request.args.get('q', '')
        category = request.args.get('category', 'all')
        
        # Your search logic here
        results = {
            "success": True,
            "query": query,
            "category": category,
            "results": [
                {
                    "product_id": "PROD-001",
                    "name": "Sample Product",
                    "price": 29.99
                }
            ],
            "total_results": 1
        }
        
        return jsonify(results), 200
    
    app.run(debug=True, port=5000)
'''

print("Created examples/implementations/python/awas_middleware.py")
print(f"Length: {len(files['examples/implementations/python/awas_middleware.py'])} characters")
