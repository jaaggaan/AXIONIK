-- ============================================================================
-- SHOPPERS STOP RETAIL PLATFORM — ENTERPRISE DATABASE SCHEMA (SQL)
-- Database Engine: PostgreSQL / MySQL / SQLite compatible
-- Description: Complete schema for Captive Portal Logins, Omnichannel Orders,
--              First Citizen Loyalty CRM, Coupon Redemptions, and Customer Feedbacks.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. CUSTOMERS TABLE (First Citizen Loyalty CRM & Portal Registrations)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS customers (
    id VARCHAR(64) PRIMARY KEY,                         -- FC-10089 or UUID
    username VARCHAR(100) NOT NULL,                     -- Customer Full Name / Username
    email VARCHAR(150) UNIQUE NOT NULL,                 -- Email Address
    phone_number VARCHAR(20) NOT NULL,                  -- Phone Number (+91...)
    loyalty_tier VARCHAR(30) DEFAULT 'Silver',          -- Silver, Golden, Platinum, Black
    loyalty_points INT DEFAULT 500,                     -- First Citizen Points Balance
    lifetime_spend DECIMAL(12, 2) DEFAULT 0.00,         -- Total Amount Spent (₹)
    total_orders INT DEFAULT 0,                         -- Total Completed Orders Count
    preferred_category VARCHAR(100) DEFAULT 'General',  -- Ethnic & Womenswear, Beauty, Watches...
    last_visit_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Last Visit / Portal Login
    joined_date DATE DEFAULT CURRENT_DATE,              -- Registration Date
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexing for fast query search
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_phone ON customers(phone_number);
CREATE INDEX idx_customers_tier ON customers(loyalty_tier);


-- ----------------------------------------------------------------------------
-- 2. VISITS AND ORDERS TABLE (In-Store Captive Portal & Online Orders)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS visits_and_orders (
    id VARCHAR(64) PRIMARY KEY,                         -- SS-ORD-98421 or ORD-UUID
    customer_id VARCHAR(64) REFERENCES customers(id) ON DELETE CASCADE,
    customer_name VARCHAR(100) NOT NULL,
    customer_email VARCHAR(150) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL,
    store_location VARCHAR(150) NOT NULL,               -- e.g. Mumbai - Malad West Flagship
    order_type VARCHAR(20) NOT NULL DEFAULT 'In-Store', -- 'In-Store' or 'Online'
    total_amount DECIMAL(12, 2) NOT NULL DEFAULT 0.00,  -- Order Value (₹)
    payment_method VARCHAR(50) DEFAULT 'UPI',           # UPI, Credit Card, COD, First Citizen Pay
    status VARCHAR(30) DEFAULT 'Delivered',            # Delivered, Processing, In Transit, Returned
    coupons_used VARCHAR(100) DEFAULT NULL,             -- Code of applied voucher e.g. FESTIVE20
    discount_amount DECIMAL(10, 2) DEFAULT 0.00,        -- Savings (₹)
    visit_date DATE DEFAULT CURRENT_DATE,
    visit_time TIME DEFAULT CURRENT_TIME,
    ip_address VARCHAR(45) DEFAULT NULL,                -- Captive Portal IP
    device_mac VARCHAR(50) DEFAULT NULL,                -- ESP32 Wi-Fi Station MAC Address
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_customer_id ON visits_and_orders(customer_id);
CREATE INDEX idx_orders_store ON visits_and_orders(store_location);
CREATE INDEX idx_orders_type ON visits_and_orders(order_type);


-- ----------------------------------------------------------------------------
-- 3. COUPONS & PROMOTIONAL VOUCHERS TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS coupons (
    id VARCHAR(64) PRIMARY KEY,                         -- CPN-101
    code VARCHAR(50) UNIQUE NOT NULL,                   -- FESTIVE20, FIRSTCITIZEN15
    title VARCHAR(150) NOT NULL,
    description TEXT,
    discount_type VARCHAR(20) NOT NULL DEFAULT 'Percentage', -- 'Percentage' or 'Flat'
    discount_value DECIMAL(10, 2) NOT NULL,
    min_order_value DECIMAL(10, 2) DEFAULT 0.00,
    usage_count INT DEFAULT 0,
    max_usage INT DEFAULT 5000,
    status VARCHAR(20) DEFAULT 'Active',                -- 'Active' or 'Expired'
    start_date DATE,
    end_date DATE,
    applicable_category VARCHAR(100) DEFAULT 'All Categories',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ----------------------------------------------------------------------------
-- 4. COUPON REDEMPTIONS LOG TABLE (Tracks Customers Who Used Coupons)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS coupon_redemptions (
    id VARCHAR(64) PRIMARY KEY,                         -- RED-101 or RED-UUID
    coupon_id VARCHAR(64) REFERENCES coupons(id) ON DELETE CASCADE,
    coupon_code VARCHAR(50) NOT NULL,
    customer_id VARCHAR(64) REFERENCES customers(id),
    customer_name VARCHAR(100) NOT NULL,
    customer_email VARCHAR(150) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL,
    loyalty_tier VARCHAR(30) DEFAULT 'Silver',
    order_id VARCHAR(64) REFERENCES visits_and_orders(id),
    order_total DECIMAL(12, 2) NOT NULL,
    discount_saved DECIMAL(10, 2) NOT NULL,
    store_location VARCHAR(150) NOT NULL,
    redeemed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_redemptions_code ON coupon_redemptions(coupon_code);
CREATE INDEX idx_redemptions_customer ON coupon_redemptions(customer_email);


-- ----------------------------------------------------------------------------
-- 5. CUSTOMER FEEDBACKS TABLE (Store Service Reviews & CSAT Audit)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS customer_feedbacks (
    id VARCHAR(64) PRIMARY KEY,                         -- REV-1001 or REV-UUID
    customer_id VARCHAR(64) REFERENCES customers(id),
    customer_name VARCHAR(100) NOT NULL,
    customer_email VARCHAR(150) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL,
    loyalty_tier VARCHAR(30) DEFAULT 'Silver',
    store_location VARCHAR(150) NOT NULL,               -- Store Branch
    category VARCHAR(100) NOT NULL,                     -- Department (e.g., Beauty, Menswear, Wi-Fi)
    rating INT CHECK (rating >= 1 AND rating <= 5),     -- 1 to 5 Stars
    review_title VARCHAR(200) NOT NULL,
    feedback_comment TEXT NOT NULL,
    sentiment VARCHAR(30) DEFAULT 'Positive',           -- 'Delighted', 'Positive', 'Needs Improvement'
    verified_purchase BOOLEAN DEFAULT TRUE,
    manager_response TEXT DEFAULT NULL,                -- Official Store Reply
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_feedbacks_rating ON customer_feedbacks(rating);
CREATE INDEX idx_feedbacks_store ON customer_feedbacks(store_location);


-- ============================================================================
-- SAMPLE DATA INSERTION (FOR IMMEDIATE TESTING & DEMO REPLICA)
-- ============================================================================

-- Insert Customers
INSERT INTO customers (id, username, email, phone_number, loyalty_tier, loyalty_points, lifetime_spend, total_orders, preferred_category, joined_date)
VALUES 
('FC-10089', 'Ananya Deshmukh', 'ananya.d@gmail.com', '+91 98201 44321', 'Black', 18450, 245000.00, 14, 'Ethnic & Womenswear', '2026-01-15'),
('FC-10090', 'Rahul Verma', 'rahul.verma@techcorp.io', '+91 97112 88401', 'Platinum', 9200, 98500.00, 8, 'Wi-Fi & Digital Kiosk', '2026-02-10'),
('FC-10091', 'Priya Sundaram', 'priya.sundaram@yahoo.co.in', '+91 98450 12903', 'Golden', 4800, 45200.00, 5, 'Beauty & Perfumes', '2026-03-01')
ON CONFLICT (email) DO NOTHING;

-- Insert Coupons
INSERT INTO coupons (id, code, title, description, discount_type, discount_value, min_order_value, usage_count, max_usage, status, applicable_category)
VALUES 
('CPN-101', 'FESTIVE20', 'Welcome Discount', 'Flat 20% off on all Ethnic & Designer Collections', 'Percentage', 20.00, 4999.00, 1420, 5000, 'Active', 'Ethnic & Womenswear'),
('CPN-102', 'FIRSTCITIZEN15', 'First Citizen Bonus', 'Exclusive 15% bonus discount for Black & Platinum tier members', 'Percentage', 15.00, 2999.00, 3840, 10000, 'Active', 'Site-wide')
ON CONFLICT (code) DO NOTHING;

-- Insert Redemptions
INSERT INTO coupon_redemptions (id, coupon_id, coupon_code, customer_name, customer_email, customer_phone, loyalty_tier, order_id, order_total, discount_saved, store_location, redeemed_at)
VALUES 
('RED-101', 'CPN-101', 'FESTIVE20', 'Ananya Deshmukh', 'ananya.d@gmail.com', '+91 98201 44321', 'Black', 'SS-ORD-98421', 12999.00, 2599.00, 'Mumbai - Malad West Flagship', CURRENT_TIMESTAMP)
ON CONFLICT (id) DO NOTHING;

-- Insert Feedbacks
INSERT INTO customer_feedbacks (id, customer_name, customer_email, customer_phone, loyalty_tier, store_location, category, rating, review_title, feedback_comment, sentiment, verified_purchase)
VALUES 
('REV-1001', 'Ananya Deshmukh', 'ananya.d@gmail.com', '+91 98201 44321', 'Black', 'Mumbai - Malad West Flagship', 'Ethnic & Womenswear', 5, 'Exceptional Bridal Saree Consultation', 'The personal shopper service in Ethnic Wear was world-class. VIP Lounge billing was seamless!', 'Delighted', TRUE)
ON CONFLICT (id) DO NOTHING;
