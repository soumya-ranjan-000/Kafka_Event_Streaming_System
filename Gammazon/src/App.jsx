import React, { useState, useEffect } from 'react';
import { ShoppingCart, Package, ShoppingBag, CheckCircle, Clock, Trash2, X, RefreshCcw } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { getProducts, placeOrder, getOrders } from './api';
import './App.css';

function App() {
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const [orders, setOrders] = useState([]);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [placingOrder, setPlacingOrder] = useState(false);
  const [activeTab, setActiveTab] = useState('shop'); // 'shop' or 'orders'

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchOrders, 5000); // Poll for orders every 5s
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const productsData = await getProducts();
      setProducts(productsData);
      await fetchOrders();
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchOrders = async () => {
    try {
      const ordersData = await getOrders();
      // Sort orders by timestamp descending
      setOrders(ordersData.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)));
    } catch (error) {
      console.error("Error fetching orders:", error);
    }
  };

  const addToCart = (product) => {
    setCart(prev => {
      const existing = prev.find(item => item._id === product._id);
      if (existing) {
        return prev.map(item => item._id === product._id ? { ...item, quantity: item.quantity + 1 } : item);
      }
      return [...prev, { ...product, quantity: 1 }];
    });
  };

  const removeFromCart = (productId) => {
    setCart(prev => prev.filter(item => item._id !== productId));
  };

  const handlePlaceOrder = async () => {
    if (cart.length === 0) return;
    setPlacingOrder(true);
    try {
      // For this scenario, we place orders for each item in cart
      // In a real app, you might have a single order with multiple items
      // But the producer expects productId, quantity, price.
      for (const item of cart) {
        await placeOrder({
          customerId: "cust-123",
          productId: item._id,
          quantity: item.quantity,
          price: item.price
        });
      }
      setCart([]);
      setIsCartOpen(false);
      setActiveTab('orders');
      fetchOrders();
    } catch (error) {
      alert("Failed to place order. Is the producer running?");
    } finally {
      setPlacingOrder(false);
    }
  };

  const cartTotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

  return (
    <div className="app-container">
      {/* Header */}
      <header className="glass-morphism">
        <div className="container header-content">
          <div className="logo">
            <ShoppingBag className="primary-icon" />
            <span className="gradient-text">GAMMAZON</span>
          </div>
          <nav>
            <button 
              className={activeTab === 'shop' ? 'active' : ''} 
              onClick={() => setActiveTab('shop')}
            >
              Shop
            </button>
            <button 
              className={activeTab === 'orders' ? 'active' : ''} 
              onClick={() => setActiveTab('orders')}
            >
              My Orders {orders.length > 0 && <span className="badge">{orders.length}</span>}
            </button>
          </nav>
          <div className="cart-trigger" onClick={() => setIsCartOpen(true)}>
            <ShoppingCart />
            {cart.length > 0 && <span className="cart-badge">{cart.reduce((a, b) => a + b.quantity, 0)}</span>}
          </div>
        </div>
      </header>

      <main className="container">
        {activeTab === 'shop' ? (
          <section className="shop-section">
            <div className="section-header">
              <h2>Featured Products</h2>
              <button className="refresh-btn" onClick={fetchData}><RefreshCcw size={16} /></button>
            </div>
            
            {loading ? (
              <div className="loading">Loading amazing products...</div>
            ) : products.length === 0 ? (
              <div className="empty-state">
                <p>No products found. Did you run the seed script?</p>
                <code className="code-hint">python seed_products.py</code>
              </div>
            ) : (
              <div className="product-grid">
                {products.map((product) => (
                  <motion.div 
                    key={product._id} 
                    className="product-card glass-morphism"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    whileHover={{ y: -5 }}
                  >
                    <div className="product-image">
                      <img src={product.image} alt={product.name} />
                      <div className="category-tag">{product.category}</div>
                    </div>
                    <div className="product-info">
                      <h3>{product.name}</h3>
                      <p className="description">{product.description}</p>
                      <div className="product-footer">
                        <span className="price">${product.price.toLocaleString()}</span>
                        <div className="stock-info">
                          <span className="label">STOCK</span>
                          <span className={`value ${product.stock < 10 ? 'low-stock' : ''}`}>
                            {product.stock}
                          </span>
                        </div>
                        <button className="btn-primary" onClick={() => addToCart(product)} disabled={product.stock <= 0}>
                          {product.stock <= 0 ? 'Out of Stock' : 'Add to Cart'}
                        </button>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </section>
        ) : (
          <section className="orders-section">
            <div className="section-header">
              <h2>Recent Orders</h2>
              <button className="refresh-btn" onClick={fetchOrders}><RefreshCcw size={16} /></button>
            </div>
            
            {orders.length === 0 ? (
              <div className="empty-state">
                <Package size={48} />
                <p>No orders yet. Place your first order!</p>
              </div>
            ) : (
              <div className="orders-table-container glass-morphism">
                <table className="orders-table">
                  <thead>
                    <tr>
                      <th>Order ID</th>
                      <th>Product</th>
                      <th>Quantity</th>
                      <th>Total</th>
                      <th>Status</th>
                      <th>Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {orders.map((order) => (
                      <motion.tr 
                        key={order.id || order._id}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        whileHover={{ background: 'rgba(255, 255, 255, 0.03)' }}
                      >
                        <td className="order-id" data-label="Order ID">#{(order.id || order._id || '').slice(0, 8)}</td>
                        <td data-label="Product">{order.product_id}</td>
                        <td data-label="Quantity">{order.quantity}</td>
                        <td className="order-total" data-label="Total">${(order.price * order.quantity).toLocaleString()}</td>
                        <td data-label="Status">
                          <div className={`status-pill ${order.status.toLowerCase()}`}>
                            {order.status === 'PROCESSED' ? <CheckCircle size={14} /> : <Clock size={14} />}
                            {order.status}
                          </div>
                        </td>
                        <td className="order-date" data-label="Date">
                          {new Date(order.created_at).toLocaleDateString()}
                          <span className="order-time">{new Date(order.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                        </td>
                      </motion.tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        )}
      </main>

      {/* Cart Drawer */}
      <AnimatePresence>
        {isCartOpen && (
          <>
            <motion.div 
              className="cart-overlay"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsCartOpen(false)}
            />
            <motion.div 
              className="cart-drawer glass-morphism"
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            >
              <div className="cart-header">
                <h2>Your Cart</h2>
                <button className="close-btn" onClick={() => setIsCartOpen(false)}>
                  <X />
                </button>
              </div>

              <div className="cart-items">
                {cart.length === 0 ? (
                  <div className="empty-cart">
                    <ShoppingCart size={48} />
                    <p>Your cart is empty</p>
                  </div>
                ) : (
                  cart.map((item) => (
                    <div key={item._id} className="cart-item">
                      <img src={item.image} alt={item.name} />
                      <div className="item-info">
                        <h4>{item.name}</h4>
                        <p>{item.quantity} x ${item.price}</p>
                      </div>
                      <button className="remove-btn" onClick={() => removeFromCart(item._id)}>
                        <Trash2 size={18} />
                      </button>
                    </div>
                  ))
                )}
              </div>

              {cart.length > 0 && (
                <div className="cart-footer">
                  <div className="total">
                    <span>Total</span>
                    <span>${cartTotal.toLocaleString()}</span>
                  </div>
                  <button 
                    className="btn-primary checkout-btn" 
                    onClick={handlePlaceOrder}
                    disabled={placingOrder}
                  >
                    {placingOrder ? 'Processing...' : 'Place Order'}
                  </button>
                </div>
              )}
            </motion.div>
          </>
        )}
      </AnimatePresence>

      <footer className="footer container">
        <p>&copy; 2026 Gammazon E-commerce. Powered by Kafka & MongoDB.</p>
      </footer>
    </div>
  );
}

export default App;
