/**
 * Recommendation System Frontend Integration
 * Tracks user interactions for improving recommendations
 */

class RecommendationTracker {
    constructor() {
        this.apiUrl = '/recommendations/api/record-interaction/';
        this.init();
    }

    init() {
        this.trackProductViews();
        this.trackProductLikes();
        this.trackCartAdditions();
        this.trackWishlistAdditions();
    }

    // Get CSRF token for Django
    getCsrfToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfToken ? csrfToken.value : '';
    }

    // Generic method to record interactions
    async recordInteraction(productId, interactionType, additionalData = {}) {
        try {
            const response = await fetch(this.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken(),
                },
                body: JSON.stringify({
                    product_id: productId,
                    interaction_type: interactionType,
                    ...additionalData
                })
            });

            if (!response.ok) {
                console.warn('Failed to record interaction:', response.statusText);
            }
        } catch (error) {
            console.warn('Error recording interaction:', error);
        }
    }

    // Track when users view product pages
    trackProductViews() {
        // Check if we're on a product detail page
        const productIdElement = document.querySelector('[data-product-id]');
        if (productIdElement) {
            const productId = productIdElement.getAttribute('data-product-id');
            this.recordInteraction(productId, 'view');
        }
    }

    // Track product likes/favorites
    trackProductLikes() {
        document.addEventListener('click', (event) => {
            if (event.target.matches('.like-button, .favorite-button')) {
                const productId = this.getProductIdFromElement(event.target);
                if (productId) {
                    this.recordInteraction(productId, 'like');
                }
            }
        });
    }

    // Track when products are added to cart
    trackCartAdditions() {
        document.addEventListener('click', (event) => {
            if (event.target.matches('.add-to-cart, .btn-add-cart')) {
                const productId = this.getProductIdFromElement(event.target);
                if (productId) {
                    this.recordInteraction(productId, 'cart');
                }
            }
        });
    }

    // Track wishlist additions
    trackWishlistAdditions() {
        document.addEventListener('click', (event) => {
            if (event.target.matches('.add-to-wishlist, .btn-wishlist')) {
                const productId = this.getProductIdFromElement(event.target);
                if (productId) {
                    this.recordInteraction(productId, 'wishlist');
                }
            }
        });
    }

    // Helper method to extract product ID from elements
    getProductIdFromElement(element) {
        // Try different ways to get product ID
        let productId = element.getAttribute('data-product-id');
        
        if (!productId) {
            // Look in parent elements
            const parentWithId = element.closest('[data-product-id]');
            if (parentWithId) {
                productId = parentWithId.getAttribute('data-product-id');
            }
        }

        if (!productId) {
            // Try to extract from URL in href
            const href = element.getAttribute('href');
            if (href) {
                const match = href.match(/\/product\/(\d+)/);
                if (match) {
                    productId = match[1];
                }
            }
        }

        return productId;
    }

    // Method to load and display recommendations
    async loadRecommendations(containerId, method = 'comprehensive', count = 6) {
        const container = document.getElementById(containerId);
        if (!container) return;

        try {
            const response = await fetch(`/recommendations/?method=${method}&count=${count}`, {
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.renderRecommendations(container, data.products);
            }
        } catch (error) {
            console.warn('Error loading recommendations:', error);
        }
    }

    // Method to load similar products
    async loadSimilarProducts(productId, containerId, count = 6) {
        const container = document.getElementById(containerId);
        if (!container) return;

        try {
            const response = await fetch(`/recommendations/api/similar/${productId}/?count=${count}`, {
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.renderRecommendations(container, data.similar_products);
            }
        } catch (error) {
            console.warn('Error loading similar products:', error);
        }
    }

    // Render recommendations in a container
    renderRecommendations(container, products) {
        if (!products || products.length === 0) {
            container.innerHTML = '<p class="text-muted text-center">پیشنهادی یافت نشد</p>';
            return;
        }

        const html = products.map(product => `
            <div class="col-md-4 col-sm-6 mb-3">
                <div class="card h-100">
                    <img src="${product.image_url || '/static/images/default-product.jpg'}" 
                         class="card-img-top" alt="${product.name}" 
                         style="height: 200px; object-fit: cover;">
                    <div class="card-body">
                        <h6 class="card-title">${product.name}</h6>
                        <p class="card-text text-muted">${product.brand}</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">${product.category}</small>
                            <strong class="text-primary">${product.price.toLocaleString()} تومان</strong>
                        </div>
                        <div class="mt-2">
                            <a href="/product/${product.id}/" class="btn btn-primary btn-sm btn-block">مشاهده محصول</a>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = `<div class="row">${html}</div>`;
    }
}

// Initialize recommendation tracker when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.recommendationTracker = new RecommendationTracker();
});

// Utility functions for manual integration
window.RecommendationUtils = {
    // Manual method to record interaction
    recordInteraction: (productId, interactionType) => {
        if (window.recommendationTracker) {
            window.recommendationTracker.recordInteraction(productId, interactionType);
        }
    },

    // Load recommendations into a specific container
    loadRecommendations: (containerId, method = 'comprehensive', count = 6) => {
        if (window.recommendationTracker) {
            window.recommendationTracker.loadRecommendations(containerId, method, count);
        }
    },

    // Load similar products
    loadSimilarProducts: (productId, containerId, count = 6) => {
        if (window.recommendationTracker) {
            window.recommendationTracker.loadSimilarProducts(productId, containerId, count);
        }
    }
};
