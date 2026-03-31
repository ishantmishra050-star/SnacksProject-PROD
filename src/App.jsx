import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter, Routes, Route, Link, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { CartProvider, useCart } from './context/CartContext';
import { snacksData } from './data/snacks';
import Login from './pages/Login';
import Register from './pages/Register';
import StoreDirectory from './pages/StoreDirectory';
import StorePage from './pages/StorePage';
import Cart from './pages/Cart';
import OrderHistory from './pages/OrderHistory';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import Admin from './pages/Admin';
import './index.css';

/* ─── Navbar ─── */
function Navbar() {
    const { user, logout } = useAuth();
    const { cartCount } = useCart();

    return (
        <nav className="main-navbar">
            <Link to="/" className="nav-logo">🍘 Snacko</Link>
            <div className="nav-links">
                <Link to="/" className="nav-link">Home</Link>
                <Link to="/stores" className="nav-link">🏪 Shops</Link>
                {user ? (
                    <>
                        <Link to="/cart" className="nav-link cart-link">
                            🛒 Cart {cartCount > 0 && <span className="cart-badge">{cartCount}</span>}
                        </Link>
                        <Link to="/orders" className="nav-link">📦 Orders</Link>
                        {['store_owner', 'admin'].includes(user.role) && (
                            <Link to="/admin" className="nav-link" style={{ color: '#e67e22', fontWeight: '700' }}>🛡️ Admin</Link>
                        )}
                        <div className="nav-user">
                            <span className="nav-greeting">Hi, {user.name.split(' ')[0]}</span>
                            <button className="nav-logout" onClick={logout}>Logout</button>
                        </div>
                    </>
                ) : (
                    <Link to="/login" className="nav-link login-link">Sign In</Link>
                )}
            </div>
        </nav>
    );
}

/* ─── Animated Counter Hook ─── */
function useAnimatedCount(target, duration = 1500) {
    const [count, setCount] = useState(0);
    useEffect(() => {
        let start = 0;
        const increment = target / (duration / 16);
        const timer = setInterval(() => {
            start += increment;
            if (start >= target) { setCount(target); clearInterval(timer); }
            else setCount(Math.floor(start));
        }, 16);
        return () => clearInterval(timer);
    }, [target, duration]);
    return count;
}

function StatCard({ icon, value, label, suffix = '' }) {
    const animated = useAnimatedCount(value);
    return (
        <div className="stat-card">
            <span className="stat-icon">{icon}</span>
            <span className="stat-value">{animated}{suffix}</span>
            <span className="stat-label">{label}</span>
        </div>
    );
}

/* ─── Snack Card ─── */
function SnackCard({ snack, onClick, index }) {
    return (
        <div className="snack-card" onClick={onClick} style={{ animationDelay: `${index * 0.08}s` }}>
            <div className="card-image-wrap">
                <span className="card-badge">{snack.category}</span>
                <span className="card-difficulty" data-level={snack.difficulty}>{snack.difficulty}</span>
                <img src={snack.image} alt={snack.name} className="card-image" loading="lazy" />
            </div>
            <div className="card-content">
                <div className="card-title-row">
                    <h3 className="card-title">{snack.emoji} {snack.name}</h3>
                    <span className="regional-name">{snack.regionalName}</span>
                </div>
                <p className="card-desc">{snack.description}</p>
                <div className="card-tags">
                    {snack.key_ingredients.slice(0, 3).map((ing, i) => <span key={i} className="tag">{ing}</span>)}
                </div>
                <div className="card-footer">
                    <span className="prep-time">⏱ {snack.preparation_time}</span>
                    <span className="shelf-life">📦 {snack.shelfLife}</span>
                </div>
                <div className="read-more-row"><span className="read-more">Read the Story →</span></div>
            </div>
        </div>
    );
}

/* ─── Detail Modal ─── */
function SnackModal({ snack, onClose }) {
    if (!snack) return null;
    return (
        <div className={`modal-overlay ${snack ? 'open' : ''}`} onClick={onClose}>
            <div className="modal-content" onClick={e => e.stopPropagation()}>
                <button className="modal-close" onClick={onClose}>✕</button>
                <div className="modal-hero">
                    <img src={snack.image} alt={snack.name} />
                    <div className="modal-hero-overlay">
                        <div className="modal-hero-text">
                            <h2>{snack.emoji} {snack.name}</h2>
                            <div className="regional">{snack.regionalName} &bull; {snack.region}</div>
                        </div>
                    </div>
                </div>
                <div className="modal-body">
                    <div className="modal-main-col">
                        <div className="modal-section"><h3>📜 The Origin Story</h3><p>{snack.origin_story}</p></div>
                        <div className="modal-section fun-fact-box"><h3>💡 Fun Fact</h3><p>{snack.funFact}</p></div>
                    </div>
                    <div className="modal-sidebar">
                        <div className="ingredients-box">
                            <h3>🌶 Key Ingredients</h3>
                            <ul className="ingredients-list">{snack.key_ingredients.map((ing, i) => <li key={i}>{ing}</li>)}</ul>
                            <div className="meta-grid">
                                <div className="meta-item"><strong>⏱ Prep Time</strong><div className="meta-value">{snack.preparation_time}</div></div>
                                <div className="meta-item"><strong>📊 Difficulty</strong><div className="meta-value" data-level={snack.difficulty}>{snack.difficulty}</div></div>
                                <div className="meta-item"><strong>📦 Shelf Life</strong><div className="meta-value">{snack.shelfLife}</div></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

/* ─── Home Page ─── */
function HomePage() {
    const [activeFilter, setActiveFilter] = useState('All');
    const [selectedSnack, setSelectedSnack] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');

    const filteredSnacks = snacksData
        .filter(s => activeFilter === 'All' || s.region === activeFilter)
        .filter(s => s.name.toLowerCase().includes(searchQuery.toLowerCase()) || s.description.toLowerCase().includes(searchQuery.toLowerCase()));

    useEffect(() => {
        const h = (e) => { if (e.key === 'Escape') setSelectedSnack(null); };
        window.addEventListener('keydown', h);
        return () => window.removeEventListener('keydown', h);
    }, []);

    useEffect(() => { document.body.style.overflow = selectedSnack ? 'hidden' : 'unset'; }, [selectedSnack]);

    return (
        <>
            <section className="hero-section">
                <div className="hero-content">
                    <div className="hero-badge">🇮🇳 A Culinary Heritage Project</div>
                    <h1 className="hero-title">Timeless Tastes of India</h1>
                    <p className="hero-subtitle">Discover the vintage culinary treasures of Gujarat and Maharashtra — snacks perfected over generations.</p>
                    <Link to="/stores" className="hero-cta">🏪 Shop from Vintage Stores →</Link>
                </div>
                <div className="hero-stats">
                    <StatCard icon="🍽️" value={snacksData.length} label="Snacks Featured" />
                    <StatCard icon="🏠" value={4} label="Gujarati Classics" />
                    <StatCard icon="🌿" value={4} label="Marathi Delights" />
                    <StatCard icon="🌍" value={100} suffix="+" label="Countries Reached" />
                </div>
            </section>

            <nav className="filter-nav no-sticky">
                <div className="filter-buttons">
                    {['All', 'Gujarat', 'Maharashtra'].map(r => (
                        <button key={r} className={`filter-btn ${activeFilter === r ? 'active' : ''}`} onClick={() => setActiveFilter(r)}>
                            {r === 'Gujarat' && '🪔 '}{r === 'Maharashtra' && '🏔️ '}{r === 'All' && '✨ '}{r}
                        </button>
                    ))}
                </div>
                <div className="search-wrap">
                    <input type="text" className="search-input" placeholder="Search snacks..." value={searchQuery} onChange={e => setSearchQuery(e.target.value)} />
                </div>
            </nav>

            <main className="main-content">
                {filteredSnacks.length === 0 ? (
                    <div className="empty-state"><span className="empty-icon">🔍</span><h3>No snacks found</h3></div>
                ) : (
                    <div className="snack-grid">
                        {filteredSnacks.map((snack, i) => <SnackCard key={snack.id} snack={snack} index={i} onClick={() => setSelectedSnack(snack)} />)}
                    </div>
                )}
            </main>

            <SnackModal snack={selectedSnack} onClose={() => setSelectedSnack(null)} />
        </>
    );
}

/* ─── App Shell ─── */
function AppShell() {
    return (
        <div className="app-container">
            <Navbar />
            <div className="app-body">
                <Routes>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="/stores" element={<StoreDirectory />} />
                    <Route path="/stores/:id" element={<StorePage />} />
                    <Route path="/cart" element={<Cart />} />
                    <Route path="/orders" element={<OrderHistory />} />
                    <Route path="/forgot-password" element={<ForgotPassword />} />
                    <Route path="/reset-password" element={<ResetPassword />} />
                    <Route path="/admin" element={<Admin />} />
                </Routes>
            </div>
            <footer className="footer">
                <div className="footer-content">
                    <p className="footer-tagline">Made with ❤️ for Indian Culinary Heritage</p>
                    <p>Snacko &copy; 2026</p>
                </div>
            </footer>
        </div>
    );
}

function App() {
    return (
        <BrowserRouter>
            <AuthProvider>
                <CartProvider>
                    <AppShell />
                </CartProvider>
            </AuthProvider>
        </BrowserRouter>
    );
}

export default App;
