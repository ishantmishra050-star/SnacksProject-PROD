import React, { useState, useEffect } from 'react';
import api from '../api';

const STATUS_STEPS = ['pending', 'confirmed', 'preparing', 'shipped', 'delivered'];

const STATUS_COLORS = {
    pending: '#f59e0b',
    confirmed: '#3b82f6',
    preparing: '#8b5cf6',
    shipped: '#06b6d4',
    delivered: '#10b981',
    cancelled: '#ef4444',
};

const PAYMENT_COLORS = {
    pending: '#f59e0b',
    completed: '#10b981',
    failed: '#ef4444',
    refunded: '#6366f1',
};

function StatusTimeline({ status }) {
    if (status === 'cancelled') {
        return (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '10px' }}>
                <span style={{ background: '#fef2f2', color: '#ef4444', padding: '4px 12px', borderRadius: '20px', fontSize: '13px', fontWeight: '600' }}>
                    ❌ Order Cancelled
                </span>
            </div>
        );
    }
    const currentIdx = STATUS_STEPS.indexOf(status);
    return (
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginTop: '12px', flexWrap: 'wrap' }}>
            {STATUS_STEPS.map((step, i) => (
                <React.Fragment key={step}>
                    <div style={{
                        padding: '4px 10px',
                        borderRadius: '20px',
                        fontSize: '12px',
                        fontWeight: i <= currentIdx ? '600' : '400',
                        background: i < currentIdx ? '#d1fae5' : i === currentIdx ? STATUS_COLORS[step] : '#f3f4f6',
                        color: i < currentIdx ? '#065f46' : i === currentIdx ? '#fff' : '#9ca3af',
                    }}>
                        {step.charAt(0).toUpperCase() + step.slice(1)}
                    </div>
                    {i < STATUS_STEPS.length - 1 && (
                        <div style={{ width: '20px', height: '2px', background: i < currentIdx ? '#10b981' : '#e5e7eb' }} />
                    )}
                </React.Fragment>
            ))}
        </div>
    );
}

export default function OrderHistory() {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [expanded, setExpanded] = useState({});
    const [cancelling, setCancelling] = useState(null);

    const fetchOrders = () => {
        api.get('/api/orders/')
            .then(res => setOrders(res.data))
            .catch(console.error)
            .finally(() => setLoading(false));
    };

    useEffect(() => { fetchOrders(); }, []);

    const toggleExpand = (id) => setExpanded(prev => ({ ...prev, [id]: !prev[id] }));

    const handleCancel = async (orderId) => {
        if (!window.confirm('Are you sure you want to cancel this order?')) return;
        setCancelling(orderId);
        try {
            await api.patch(`/api/orders/${orderId}/cancel`);
            fetchOrders(); // refresh
        } catch (err) {
            alert(err.response?.data?.detail || 'Failed to cancel order');
        } finally {
            setCancelling(null);
        }
    };

    if (loading) return (
        <div className="page-container">
            <div className="loading-state">Loading your orders...</div>
        </div>
    );

    return (
        <div className="page-container">
            <h1 className="page-title">📦 My Orders</h1>

            {orders.length === 0 ? (
                <div className="empty-state">
                    <span className="empty-icon">📦</span>
                    <h3>No orders yet</h3>
                    <p>Place your first order from a vintage snack shop!</p>
                </div>
            ) : (
                <div className="orders-list">
                    {orders.map(order => (
                        <div key={order.id} className="order-card" style={{ borderLeft: `4px solid ${STATUS_COLORS[order.status] || '#e5e7eb'}` }}>
                            {/* Header */}
                            <div className="order-card-header" onClick={() => toggleExpand(order.id)} style={{ cursor: 'pointer' }}>
                                <div>
                                    <h3 style={{ margin: 0 }}>Order #{order.id}</h3>
                                    <span className="order-date">
                                        {new Date(order.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}
                                    </span>
                                    <StatusTimeline status={order.status} />
                                </div>
                                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '6px' }}>
                                    <span className="order-total" style={{ fontSize: '18px', fontWeight: '700', color: '#1f2937' }}>
                                        ₹{order.total_amount.toFixed(2)}
                                    </span>
                                    <span style={{
                                        padding: '4px 10px',
                                        borderRadius: '12px',
                                        fontSize: '12px',
                                        fontWeight: '600',
                                        background: PAYMENT_COLORS[order.payment_status] + '20',
                                        color: PAYMENT_COLORS[order.payment_status],
                                    }}>
                                        💳 {order.payment_method.toUpperCase()} · {order.payment_status}
                                    </span>
                                    <span style={{ fontSize: '12px', color: '#9ca3af' }}>{expanded[order.id] ? '▲ Hide details' : '▼ Show details'}</span>
                                </div>
                            </div>

                            {/* Expanded Details */}
                            {expanded[order.id] && (
                                <div className="order-card-body" style={{ borderTop: '1px solid #f3f4f6', paddingTop: '16px', marginTop: '12px' }}>
                                    {/* Items */}
                                    <h4 style={{ margin: '0 0 10px', color: '#374151', fontSize: '14px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Items</h4>
                                    <div className="order-items-list">
                                        {order.items.map(item => (
                                            <div key={item.id} className="order-item-row" style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '8px 0', borderBottom: '1px solid #f9fafb' }}>
                                                {item.product_image && (
                                                    <img src={item.product_image} alt={item.product_name} style={{ width: '48px', height: '48px', objectFit: 'cover', borderRadius: '8px', flexShrink: 0 }} onError={e => e.target.style.display = 'none'} />
                                                )}
                                                <div style={{ flex: 1 }}>
                                                    <div style={{ fontWeight: '600', color: '#1f2937' }}>{item.product_name || `Product #${item.store_product_id}`}</div>
                                                    <div style={{ fontSize: '13px', color: '#6b7280' }}>₹{item.unit_price.toFixed(2)} × {item.quantity}</div>
                                                </div>
                                                <span style={{ fontWeight: '700', color: '#1f2937' }}>₹{(item.unit_price * item.quantity).toFixed(2)}</span>
                                            </div>
                                        ))}
                                    </div>

                                    {/* Bill Summary */}
                                    <div style={{ marginTop: '16px', background: '#f9fafb', borderRadius: '10px', padding: '14px', fontSize: '14px' }}>
                                        <h4 style={{ margin: '0 0 10px', fontSize: '14px', color: '#374151', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Bill Summary</h4>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', color: '#4b5563' }}>
                                            <span>Subtotal</span><span>₹{order.subtotal.toFixed(2)}</span>
                                        </div>
                                        {order.discount_amount > 0 && (
                                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', color: '#059669' }}>
                                                <span>🎉 Bulk Discount (10%)</span><span>− ₹{order.discount_amount.toFixed(2)}</span>
                                            </div>
                                        )}
                                        {order.cgst_amount > 0 && (
                                            <>
                                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px', color: '#6b7280' }}>
                                                    <span>CGST</span><span>₹{order.cgst_amount.toFixed(2)}</span>
                                                </div>
                                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px', color: '#6b7280' }}>
                                                    <span>SGST</span><span>₹{order.sgst_amount.toFixed(2)}</span>
                                                </div>
                                            </>
                                        )}
                                        {order.igst_amount > 0 && (
                                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px', color: '#6b7280' }}>
                                                <span>IGST</span><span>₹{order.igst_amount.toFixed(2)}</span>
                                            </div>
                                        )}
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '10px', paddingTop: '10px', borderTop: '1px solid #e5e7eb', fontWeight: '700', fontSize: '16px', color: '#1f2937' }}>
                                            <span>Grand Total</span><span>₹{order.total_amount.toFixed(2)}</span>
                                        </div>
                                    </div>

                                    {/* Delivery Address */}
                                    <div style={{ marginTop: '16px', fontSize: '14px', color: '#4b5563' }}>
                                        <h4 style={{ margin: '0 0 6px', fontSize: '14px', color: '#374151', textTransform: 'uppercase', letterSpacing: '0.5px' }}>📍 Delivery Address</h4>
                                        <pre style={{ fontFamily: 'inherit', margin: 0, whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>{order.delivery_address}</pre>
                                    </div>

                                    {/* Cancel Button */}
                                    {(order.status === 'pending' || order.status === 'confirmed') && (
                                        <button
                                            onClick={() => handleCancel(order.id)}
                                            disabled={cancelling === order.id}
                                            style={{
                                                marginTop: '16px',
                                                padding: '10px 20px',
                                                borderRadius: '8px',
                                                border: '2px solid #ef4444',
                                                background: 'transparent',
                                                color: '#ef4444',
                                                fontWeight: '600',
                                                cursor: 'pointer',
                                                fontSize: '14px',
                                                transition: 'all 0.2s',
                                            }}
                                            onMouseEnter={e => { e.target.style.background = '#ef4444'; e.target.style.color = '#fff'; }}
                                            onMouseLeave={e => { e.target.style.background = 'transparent'; e.target.style.color = '#ef4444'; }}
                                        >
                                            {cancelling === order.id ? 'Cancelling...' : '✕ Cancel Order'}
                                        </button>
                                    )}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
