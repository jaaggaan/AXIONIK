-- ===========================================================================
-- Supabase PostgreSQL Database Schema for Shoppers Stop Retail System
-- Run this script in your Supabase Dashboard SQL Editor (https://supabase.com)
-- ===========================================================================

-- 1. Customers Table
CREATE TABLE IF NOT EXISTS customers (
    id TEXT PRIMARY KEY,
    user_id TEXT UNIQUE,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    vip_tier TEXT DEFAULT 'Silver',
    total_spend NUMERIC DEFAULT 0.0,
    points INTEGER DEFAULT 500,
    assigned_coupon TEXT DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_visit TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS assigned_coupon TEXT DEFAULT '';

-- 2. Coupons Table
CREATE TABLE IF NOT EXISTS coupons (
    id TEXT PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    title TEXT,
    description TEXT,
    discount_type TEXT,
    discount_value NUMERIC,
    min_order_value NUMERIC,
    usage_count INTEGER DEFAULT 0,
    max_usage INTEGER DEFAULT 5000,
    status TEXT DEFAULT 'Active',
    start_date DATE,
    end_date DATE,
    applicable_category TEXT,
    redeemed_customers TEXT DEFAULT ''
);
-- IMPORTANT: Run this if the column was not created above
ALTER TABLE coupons ADD COLUMN IF NOT EXISTS redeemed_customers TEXT DEFAULT '';

-- 3. Redemptions Table
CREATE TABLE IF NOT EXISTS redemptions (
    id TEXT PRIMARY KEY,
    coupon_code TEXT,
    customer_name TEXT,
    customer_email TEXT,
    customer_phone TEXT,
    loyalty_tier TEXT,
    order_id TEXT,
    order_total NUMERIC,
    discount_saved NUMERIC,
    redeemed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    store_location TEXT
);

-- 4. Orders Table
CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    order_id TEXT UNIQUE,
    customer_name TEXT,
    customer_phone TEXT,
    customer_email TEXT,
    items JSONB DEFAULT '[]'::jsonb,
    total_amount NUMERIC,
    coupon_code TEXT,
    discount_saved NUMERIC,
    status TEXT DEFAULT 'Completed',
    order_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    store_location TEXT,
    channel TEXT
);

-- 5. Customer Feedbacks Table
CREATE TABLE IF NOT EXISTS feedbacks (
    id TEXT PRIMARY KEY,
    customer_name TEXT,
    customer_email TEXT,
    customer_phone TEXT,
    loyalty_tier TEXT,
    store_location TEXT,
    category TEXT,
    rating INTEGER,
    title TEXT,
    comment TEXT,
    date DATE,
    time TEXT,
    sentiment TEXT,
    verified_purchase BOOLEAN DEFAULT TRUE,
    helpful_count INTEGER DEFAULT 0,
    manager_response TEXT
);

-- Enable Row Level Security (RLS) policies allowing full access
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE coupons ENABLE ROW LEVEL SECURITY;
ALTER TABLE redemptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedbacks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read/write on customers" ON customers FOR ALL USING (true);
CREATE POLICY "Allow public read/write on coupons" ON coupons FOR ALL USING (true);
CREATE POLICY "Allow public read/write on redemptions" ON redemptions FOR ALL USING (true);
CREATE POLICY "Allow public read/write on orders" ON orders FOR ALL USING (true);
CREATE POLICY "Allow public read/write on feedbacks" ON feedbacks FOR ALL USING (true);
