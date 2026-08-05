-- ========================================================
-- SHOPPERS STOP OMNICHANNEL & STOREFRONT — COMPLETE SUPABASE SCHEMA
-- Run this in your Supabase SQL Editor
-- ========================================================

-- 1. CUSTOMERS TABLE
CREATE TABLE IF NOT EXISTS customers (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT NOT NULL,
    vip_tier TEXT DEFAULT 'Black Tier',
    total_spend NUMERIC DEFAULT 0.0,
    points INT DEFAULT 500,
    assigned_coupon TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_visit TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. ORDERS TABLE (Captures Full Online Cart & Razorpay Orders)
CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    customer_name TEXT NOT NULL,
    customer_phone TEXT NOT NULL,
    customer_email TEXT,
    items JSONB NOT NULL,                   -- List of purchased items [{title, brand, price, qty}]
    total_amount NUMERIC NOT NULL,          -- Paid price
    coupon_code TEXT,                       -- Coupon used: FESTIVE20, FIRSTCITIZEN15, BEAUTYBUY2, ENDOFSEASON50
    discount_saved NUMERIC DEFAULT 0.0,    -- Amount saved via coupon
    payment_method TEXT DEFAULT 'Razorpay', -- Razorpay UPI, Card, NetBanking, COD
    status TEXT DEFAULT 'CONFIRMED',
    store_location TEXT DEFAULT 'Online Storefront',
    channel TEXT DEFAULT 'Online E-Commerce',-- 'Online E-Commerce' vs 'In-Store / WiFi'
    order_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. REDEMPTIONS TABLE (Captures Coupon Usage per Customer)
CREATE TABLE IF NOT EXISTS redemptions (
    id TEXT PRIMARY KEY,
    coupon_code TEXT NOT NULL,              -- FESTIVE20, FIRSTCITIZEN15, BEAUTYBUY2, ENDOFSEASON50
    customer_name TEXT NOT NULL,
    customer_phone TEXT NOT NULL,
    customer_email TEXT,
    loyalty_tier TEXT DEFAULT 'Black Tier',
    order_id TEXT,
    order_total NUMERIC DEFAULT 0.0,
    discount_saved NUMERIC DEFAULT 0.0,
    store_location TEXT DEFAULT 'Online Storefront',
    channel TEXT DEFAULT 'Online E-Commerce',
    redeemed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. FEEDBACKS TABLE (Store & Service Sentiment)
CREATE TABLE IF NOT EXISTS feedbacks (
    id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    customer_phone TEXT,
    rating INT DEFAULT 5,
    sentiment TEXT DEFAULT 'Positive',
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ENABLE ROW LEVEL SECURITY (RLS) & ALLOW PUBLIC ACCESS
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE redemptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedbacks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public insert customers" ON customers FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public select customers" ON customers FOR SELECT USING (true);
CREATE POLICY "Allow public update customers" ON customers FOR UPDATE USING (true);

CREATE POLICY "Allow public insert orders" ON orders FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public select orders" ON orders FOR SELECT USING (true);

CREATE POLICY "Allow public insert redemptions" ON redemptions FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public select redemptions" ON redemptions FOR SELECT USING (true);

CREATE POLICY "Allow public insert feedbacks" ON feedbacks FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public select feedbacks" ON feedbacks FOR SELECT USING (true);
