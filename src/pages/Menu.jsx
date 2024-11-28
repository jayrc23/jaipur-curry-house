import React, { useState } from 'react';
import QRCode from 'qrcode.react';

const Menu = () => {
  const [cart, setCart] = useState([]);
  
  const menuItems = [
    {
      category: 'Appetizers',
      items: [
        { id: 1, name: 'Garlic Bread', price: 5.99, description: 'Freshly baked bread with garlic butter' },
        { id: 2, name: 'Bruschetta', price: 6.99, description: 'Toasted bread topped with tomatoes, garlic, and basil' },
        { id: 3, name: 'Calamari', price: 8.99, description: 'Crispy fried squid rings with marinara sauce' },
      ]
    },
    {
      category: 'Main Courses',
      items: [
        { id: 4, name: 'Grilled Salmon', price: 24.99, description: 'Fresh salmon with lemon herb sauce' },
        { id: 5, name: 'Beef Tenderloin', price: 29.99, description: '8oz tenderloin with red wine reduction' },
        { id: 6, name: 'Chicken Marsala', price: 19.99, description: 'Chicken breast in mushroom marsala sauce' },
      ]
    },
    {
      category: 'Desserts',
      items: [
        { id: 7, name: 'Tiramisu', price: 7.99, description: 'Classic Italian coffee-flavored dessert' },
        { id: 8, name: 'Chocolate Lava Cake', price: 8.99, description: 'Warm chocolate cake with molten center' },
        { id: 9, name: 'Cheesecake', price: 6.99, description: 'New York style cheesecake' },
      ]
    }
  ];

  const addToCart = (item) => {
    setCart([...cart, item]);
  };

  const removeFromCart = (itemId) => {
    const index = cart.findIndex(item => item.id === itemId);
    if (index > -1) {
      const newCart = [...cart];
      newCart.splice(index, 1);
      setCart(newCart);
    }
  };

  const getTotalPrice = () => {
    return cart.reduce((total, item) => total + item.price, 0).toFixed(2);
  };

  const getOrderData = () => {
    const orderData = {
      items: cart,
      total: getTotalPrice(),
      timestamp: new Date().toISOString()
    };
    return JSON.stringify(orderData);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold text-center mb-8">Our Menu</h1>
      
      <div className="grid md:grid-cols-2 gap-8">
        {/* Menu Section */}
        <div>
          {menuItems.map((category) => (
            <div key={category.category} className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">{category.category}</h2>
              <div className="space-y-4">
                {category.items.map((item) => (
                  <div key={item.id} className="border p-4 rounded-lg shadow-sm">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="text-xl font-medium">{item.name}</h3>
                        <p className="text-gray-600">{item.description}</p>
                        <p className="text-lg font-semibold mt-2">${item.price}</p>
                      </div>
                      <button
                        onClick={() => addToCart(item)}
                        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                      >
                        Add to Cart
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Cart Section */}
        <div className="sticky top-4">
          <div className="border p-6 rounded-lg shadow-lg">
            <h2 className="text-2xl font-semibold mb-4">Your Order</h2>
            {cart.length === 0 ? (
              <p className="text-gray-500">Your cart is empty</p>
            ) : (
              <>
                <div className="space-y-2 mb-4">
                  {cart.map((item, index) => (
                    <div key={index} className="flex justify-between items-center">
                      <span>{item.name}</span>
                      <div>
                        <span className="mr-4">${item.price}</span>
                        <button
                          onClick={() => removeFromCart(item.id)}
                          className="text-red-500 hover:text-red-700"
                        >
                          Remove
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="border-t pt-4">
                  <div className="flex justify-between items-center text-xl font-semibold">
                    <span>Total:</span>
                    <span>${getTotalPrice()}</span>
                  </div>
                </div>
                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-2">Scan to Order</h3>
                  <div className="bg-white p-4 inline-block rounded-lg">
                    <QRCode value={getOrderData()} size={128} />
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Menu;
