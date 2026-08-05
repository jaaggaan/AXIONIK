-- ========================================================
-- SHOPPERS STOP STOREFRONT — SEPARATE SUPABASE SCHEMA
-- Execute this SQL in the SQL Editor of your NEW Supabase Project
-- ========================================================

-- 1. Create Storefront Customers Table
CREATE TABLE IF NOT EXISTS storefront_customers (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT UNIQUE NOT NULL,
    email TEXT,
    vip_tier TEXT DEFAULT 'Black Tier',
    total_orders INT DEFAULT 0,
    total_spend NUMERIC DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_visit TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Create Storefront Orders Table
CREATE TABLE IF NOT EXISTS storefront_orders (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    order_number TEXT UNIQUE NOT NULL,
    customer_name TEXT NOT NULL,
    customer_phone TEXT NOT NULL,
    customer_email TEXT,
    items JSONB NOT NULL,
    subtotal NUMERIC NOT NULL,
    discount NUMERIC DEFAULT 0,
    coupon_applied TEXT,
    total_amount NUMERIC NOT NULL,
    payment_method TEXT NOT NULL,
    status TEXT DEFAULT 'CONFIRMED',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Create Storefront Coupon Redemptions Table
CREATE TABLE IF NOT EXISTS storefront_redemptions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    coupon_code TEXT NOT NULL,
    customer_name TEXT NOT NULL,
    customer_phone TEXT NOT NULL,
    discount_amount NUMERIC,
    redeemed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS (Row Level Security) and allow Public inserts
ALTER TABLE storefront_customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE storefront_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE storefront_redemptions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public insert to storefront_customers" ON storefront_customers FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public select to storefront_customers" ON storefront_customers FOR SELECT USING (true);

CREATE POLICY "Allow public insert to storefront_orders" ON storefront_orders FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public select to storefront_orders" ON storefront_orders FOR SELECT USING (true);

CREATE POLICY "Allow public insert to storefront_redemptions" ON storefront_redemptions FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public select to storefront_redemptions" ON storefront_redemptions FOR SELECT USING (true);
