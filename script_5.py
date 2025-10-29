
# 6. HTML Example
files['examples/html-example.html'] = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AWAS Example - E-Commerce Product Page</title>
    
    <!-- AWAS Discovery -->
    <link rel="ai-actions" href="/.well-known/ai-actions.json" type="application/json">
    <link rel="ai-sitemap" href="/.well-known/ai-sitemap.json" type="application/json">
    <link rel="ai-capabilities" href="/.well-known/ai-capabilities" type="application/json">
    
    <!-- Standard Schema.org Structured Data -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org/",
      "@type": "Product",
      "name": "Premium Wireless Headphones",
      "description": "High-quality noise-canceling wireless headphones with 30-hour battery life",
      "sku": "PROD-HEADPHONE-001",
      "brand": {
        "@type": "Brand",
        "name": "AudioTech"
      },
      "offers": {
        "@type": "Offer",
        "price": "299.99",
        "priceCurrency": "USD",
        "availability": "https://schema.org/InStock"
      },
      "aggregateRating": {
        "@type": "AggregateRating",
        "ratingValue": "4.8",
        "reviewCount": "247"
      }
    }
    </script>
    
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        .product { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; }
        .product-image { background: #f0f0f0; aspect-ratio: 1; display: flex; align-items: center; justify-content: center; }
        button { background: #007bff; color: white; border: none; padding: 12px 24px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
        input, select { padding: 8px; margin: 8px 0; }
        .search-bar { margin: 20px 0; }
        .filters { background: #f9f9f9; padding: 20px; margin: 20px 0; }
    </style>
</head>
<body>
    <!-- AI Rate Limiting Hints -->
    <meta name="ai-rate-limit" content="60/minute">
    <meta name="ai-auth-required" content="false">
    <meta name="ai-session-required" content="false">
    
    <!-- Header with Search -->
    <header>
        <h1>AudioTech Store</h1>
        
        <!-- AI-Enhanced Search -->
        <div class="search-bar">
            <form 
                role="search"
                data-ai-action="search_products"
                data-ai-action-type="search"
                data-ai-endpoint="/api/search"
                data-ai-method="GET"
                aria-label="Product search">
                
                <input 
                    type="search" 
                    name="q" 
                    placeholder="Search products..."
                    data-ai-param="q"
                    data-ai-param-type="string"
                    data-ai-param-required="true"
                    aria-label="Search query"
                    size="40">
                
                <select 
                    name="category"
                    data-ai-param="category"
                    data-ai-param-type="string"
                    data-ai-param-required="false"
                    aria-label="Product category">
                    <option value="">All Categories</option>
                    <option value="electronics">Electronics</option>
                    <option value="clothing">Clothing</option>
                    <option value="home">Home</option>
                    <option value="sports">Sports</option>
                </select>
                
                <button 
                    type="submit"
                    data-ai-action-trigger="search_products"
                    aria-label="Submit search">
                    Search
                </button>
            </form>
        </div>
    </header>
    
    <!-- Product Filters -->
    <aside class="filters" data-ai-widget="filters">
        <h3>Filters</h3>
        <form 
            data-ai-action="apply_filters"
            data-ai-action-type="filter"
            data-ai-endpoint="/products/filter"
            data-ai-method="GET"
            aria-label="Product filters">
            
            <div>
                <label>Price Range:</label><br>
                <input 
                    type="number" 
                    name="price_min" 
                    placeholder="Min"
                    data-ai-param="price_min"
                    data-ai-param-type="number"
                    data-ai-param-required="false"
                    min="0">
                <input 
                    type="number" 
                    name="price_max" 
                    placeholder="Max"
                    data-ai-param="price_max"
                    data-ai-param-type="number"
                    data-ai-param-required="false"
                    min="0">
            </div>
            
            <div>
                <label>Minimum Rating:</label><br>
                <select 
                    name="rating"
                    data-ai-param="rating"
                    data-ai-param-type="integer"
                    data-ai-param-required="false">
                    <option value="">Any</option>
                    <option value="5">5 Stars</option>
                    <option value="4">4+ Stars</option>
                    <option value="3">3+ Stars</option>
                </select>
            </div>
            
            <button 
                type="submit"
                data-ai-action-trigger="apply_filters">
                Apply Filters
            </button>
        </form>
    </aside>
    
    <!-- Main Product Content -->
    <main data-ai-content="primary" data-ai-intent="product-detail">
        <article 
            class="product"
            itemscope 
            itemtype="https://schema.org/Product"
            data-ai-entity="product"
            data-ai-id="PROD-HEADPHONE-001">
            
            <div class="product-image">
                <p>[Product Image]</p>
            </div>
            
            <div class="product-info">
                <h2 
                    itemprop="name" 
                    data-ai-field="product-name">
                    Premium Wireless Headphones
                </h2>
                
                <div 
                    data-ai-field="product-rating"
                    itemprop="aggregateRating"
                    itemscope
                    itemtype="https://schema.org/AggregateRating">
                    <span itemprop="ratingValue">4.8</span> stars 
                    (<span itemprop="reviewCount">247</span> reviews)
                </div>
                
                <div 
                    data-ai-field="product-price" 
                    itemprop="offers" 
                    itemscope 
                    itemtype="https://schema.org/Offer">
                    <strong>Price:</strong> 
                    <span itemprop="price" content="299.99">$299.99</span>
                    <meta itemprop="priceCurrency" content="USD">
                    <link itemprop="availability" href="https://schema.org/InStock">
                </div>
                
                <div 
                    data-ai-field="product-description"
                    itemprop="description">
                    <p>High-quality noise-canceling wireless headphones with 30-hour battery life. 
                    Features premium audio drivers, comfortable ear cushions, and intuitive touch controls.</p>
                </div>
                
                <div 
                    data-ai-field="product-features">
                    <strong>Features:</strong>
                    <ul>
                        <li>Active Noise Cancellation</li>
                        <li>30-hour battery life</li>
                        <li>Bluetooth 5.2</li>
                        <li>Premium audio drivers</li>
                        <li>Comfortable design</li>
                    </ul>
                </div>
                
                <!-- AI-Enhanced Add to Cart Form -->
                <form 
                    id="add-to-cart-form"
                    data-ai-action="add_to_cart"
                    data-ai-action-type="form_submission"
                    data-ai-endpoint="/api/cart/add"
                    data-ai-method="POST"
                    aria-label="Add product to shopping cart">
                    
                    <input 
                        type="hidden" 
                        name="product_id" 
                        value="PROD-HEADPHONE-001"
                        data-ai-param="product_id"
                        data-ai-param-type="string"
                        data-ai-param-required="true">
                    
                    <label for="quantity">
                        Quantity:
                        <input 
                            type="number" 
                            id="quantity"
                            name="quantity" 
                            value="1" 
                            min="1" 
                            max="10"
                            data-ai-param="quantity"
                            data-ai-param-type="integer"
                            data-ai-param-required="false"
                            data-ai-param-default="1"
                            aria-label="Product quantity">
                    </label>
                    
                    <label for="color-variant">
                        Color:
                        <select 
                            id="color-variant"
                            name="variant_id"
                            data-ai-param="variant_id"
                            data-ai-param-type="string"
                            data-ai-param-required="false"
                            aria-label="Product color selection">
                            <option value="black">Black</option>
                            <option value="silver">Silver</option>
                            <option value="white">White</option>
                        </select>
                    </label>
                    
                    <br><br>
                    
                    <button 
                        type="submit"
                        data-ai-action-trigger="add_to_cart"
                        aria-label="Add to cart button">
                        Add to Cart
                    </button>
                </form>
                
                <!-- Additional Actions -->
                <nav data-ai-navigation="product-actions" aria-label="Product actions" style="margin-top: 20px;">
                    <a 
                        href="/wishlist/add?id=PROD-HEADPHONE-001"
                        data-ai-action="add_to_wishlist"
                        data-ai-action-type="navigation"
                        data-ai-method="GET"
                        aria-label="Add to wishlist"
                        style="margin-right: 10px;">
                        ❤️ Add to Wishlist
                    </a>
                    
                    <a 
                        href="/compare?add=PROD-HEADPHONE-001"
                        data-ai-action="compare_products"
                        data-ai-action-type="navigation"
                        data-ai-method="GET"
                        aria-label="Compare this product">
                        📊 Compare
                    </a>
                </nav>
            </div>
        </article>
    </main>
    
    <!-- Footer -->
    <footer data-ai-content="footer" style="margin-top: 40px; border-top: 1px solid #ccc; padding-top: 20px;">
        <p>&copy; 2025 AudioTech Store. Powered by AWAS.</p>
    </footer>
    
    <!-- Optional: JavaScript to handle AI agent interactions -->
    <script>
        // Check if being accessed by AI agent
        if (navigator.userAgent.includes('AI-Browser') || 
            document.querySelector('[data-ai-action]')) {
            console.log('AWAS-enhanced page ready for AI interaction');
        }
    </script>
</body>
</html>
'''

print("Created examples/html-example.html")
print(f"Length: {len(files['examples/html-example.html'])} characters")
