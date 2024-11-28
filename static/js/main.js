document.addEventListener('DOMContentLoaded', function() {
    // Handle add to cart forms
    const addToCartForms = document.querySelectorAll('.add-to-cart-form');
    addToCartForms.forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            const quantity = this.querySelector('input[name="quantity"]').value;
            
            try {
                const response = await fetch(`/add_to_cart/${productId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `quantity=${quantity}`
                });
                
                const data = await response.json();
                if (response.ok) {
                    showAlert('Product added to cart successfully', 'success');
                } else {
                    showAlert(data.error || 'Error adding product to cart', 'danger');
                }
            } catch (error) {
                showAlert('Error adding product to cart', 'danger');
            }
        });
    });

    // Load cart items if on cart page
    if (document.getElementById('cart-items')) {
        loadCartItems();
    }
});

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}

async function loadCartItems() {
    const cartData = document.cookie.split('; ').find(row => row.startsWith('cart='));
    if (!cartData) {
        showEmptyCart();
        return;
    }

    const cart = JSON.parse(cartData.split('=')[1].replace(/'/g, '"'));
    const cartItemsContainer = document.getElementById('cart-items');
    const template = document.getElementById('cart-item-template');
    let total = 0;

    cartItemsContainer.innerHTML = '';

    for (const [productId, quantity] of Object.entries(cart)) {
        try {
            const response = await fetch(`/product/${productId}`);
            const product = await response.json();
            
            const cartItem = template.content.cloneNode(true);
            
            cartItem.querySelector('img').src = product.image_url;
            cartItem.querySelector('img').alt = product.name;
            cartItem.querySelector('.card-title').textContent = product.name;
            cartItem.querySelector('.item-price').textContent = product.price.toFixed(2);
            cartItem.querySelector('.quantity-input').value = quantity;
            
            const subtotal = product.price * quantity;
            total += subtotal;
            
            cartItemsContainer.appendChild(cartItem);
        } catch (error) {
            console.error('Error loading cart item:', error);
        }
    }

    document.getElementById('cart-total').textContent = total.toFixed(2);
    document.getElementById('checkout-button').disabled = total === 0;
}

function showEmptyCart() {
    const cartItemsContainer = document.getElementById('cart-items');
    cartItemsContainer.innerHTML = `
        <div class="alert alert-info">
            Your cart is empty. <a href="/" class="alert-link">Continue shopping</a>
        </div>
    `;
    document.getElementById('checkout-button').disabled = true;
}
