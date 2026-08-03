import express from 'express';

const app = express();
const PORT = 5000;

app.use(express.json());

// Enable CORS for all ports (3000, 3001, 3002, file://, etc.)
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  if (req.method === 'OPTIONS') {
    return res.sendStatus(200);
  }
  next();
});

// Shared In-Memory State
let STORED_CUSTOMERS = [
  {
    id: 'CUST-1001',
    name: 'Ananya Deshmukh',
    email: 'ananya.d@gmail.com',
    phone: '+91 98201 44512',
    loyaltyTier: 'Black',
    loyaltyPoints: 18450,
    totalSpent: 284900,
    totalOrders: 28,
    lastPurchaseDate: '2026-07-27',
    preferredCategory: 'Luxury Watches',
    joinedDate: '2021-03-15',
    avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=150',
  },
  {
    id: 'CUST-1002',
    name: 'Kavita Reddy',
    email: 'kavita.reddy@gmail.com',
    phone: '+91 97011 22900',
    loyaltyTier: 'Black',
    loyaltyPoints: 24100,
    totalSpent: 392000,
    totalOrders: 34,
    lastPurchaseDate: '2026-07-26',
    preferredCategory: 'Beauty & Perfumes',
    joinedDate: '2020-08-10',
    avatar: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&q=80&w=150',
  },
  {
    id: 'CUST-1003',
    name: 'Vikramaditya Roy',
    email: 'v.roy@consultant.com',
    phone: '+91 98112 09844',
    loyaltyTier: 'Platinum',
    loyaltyPoints: 9200,
    totalSpent: 142500,
    totalOrders: 16,
    lastPurchaseDate: '2026-07-27',
    preferredCategory: 'Beauty & Perfumes',
    joinedDate: '2022-11-04',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=150',
  },
  {
    id: 'CUST-1004',
    name: 'Tanvi Agarwal',
    email: 'tanvi.agarwal@corp.in',
    phone: '+91 98210 99887',
    loyaltyTier: 'Platinum',
    loyaltyPoints: 8400,
    totalSpent: 118000,
    totalOrders: 14,
    lastPurchaseDate: '2026-07-26',
    preferredCategory: 'Home & Living',
    joinedDate: '2023-01-20',
    avatar: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&q=80&w=150',
  },
  {
    id: 'CUST-1005',
    name: 'Priya Sundaram',
    email: 'priya.sundaram@tech.in',
    phone: '+91 99002 33110',
    loyaltyTier: 'Golden',
    loyaltyPoints: 4800,
    totalSpent: 68900,
    totalOrders: 9,
    lastPurchaseDate: '2026-07-27',
    preferredCategory: 'Womenswear',
    joinedDate: '2023-06-12',
    avatar: 'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&q=80&w=150',
  },
  {
    id: 'CUST-1006',
    name: 'Rohan Mehra',
    email: 'rohan.mehra@finance.com',
    phone: '+91 98300 77123',
    loyaltyTier: 'Silver',
    loyaltyPoints: 2100,
    totalSpent: 34500,
    totalOrders: 5,
    lastPurchaseDate: '2026-07-26',
    preferredCategory: 'Luxury Watches',
    joinedDate: '2023-09-18',
    avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&q=80&w=150',
  }
];

let STORED_COUPONS = [
  {
    id: 'CPN-100',
    code: 'ANANYA',
    title: 'Festive 25% Off',
    description: 'Festive 25% Off across all designer categories',
    discountType: 'Percentage',
    discountValue: 25,
    minOrderValue: 3999,
    usageCount: 0,
    maxUsage: 1000,
    status: 'Active',
    startDate: '2026-07-01',
    endDate: '2026-08-31',
    applicableCategory: 'Site-wide'
  },
  {
    id: 'CPN-101',
    code: 'FESTIVE20',
    title: 'Festive Special 20% OFF',
    description: 'Flat 20% off on all Ethnic & Designer Collections for First Citizen Members',
    discountType: 'Percentage',
    discountValue: 20,
    minOrderValue: 4999,
    usageCount: 1420,
    maxUsage: 5000,
    status: 'Active',
    startDate: '2026-07-01',
    endDate: '2026-08-15',
    applicableCategory: 'Ethnic & Womenswear'
  },
  {
    id: 'CPN-102',
    code: 'FIRSTCITIZEN15',
    title: 'First Citizen Loyalty 15%',
    description: 'Exclusive 15% bonus discount for Black & Platinum tier members',
    discountType: 'Percentage',
    discountValue: 15,
    minOrderValue: 2999,
    usageCount: 3840,
    maxUsage: 10000,
    status: 'Active',
    startDate: '2026-01-01',
    endDate: '2026-12-31',
    applicableCategory: 'Site-wide'
  },
  {
    id: 'CPN-103',
    code: 'BEAUTYBUY2',
    title: 'Beauty & Fragrance ₹1000 OFF',
    description: 'Buy Beauty & Fragrance items above ₹5000 and get ₹1000 Instant Off',
    discountType: 'Flat Amount',
    discountValue: 1000,
    minOrderValue: 5000,
    usageCount: 890,
    maxUsage: 2500,
    status: 'Active',
    startDate: '2026-07-10',
    endDate: '2026-08-01',
    applicableCategory: 'Beauty & Perfumes'
  }
];

let STORED_ORDERS = [
  {
    id: 'SS-ORD-98421',
    customerName: 'Ananya Deshmukh',
    customerEmail: 'ananya.d@gmail.com',
    customerPhone: '+91 98201 44512',
    loyaltyTier: 'Black',
    storeLocation: 'Mumbai - Malad West Flagship',
    date: '27.07.2026',
    time: '11:42 AM',
    items: [
      {
        id: 'ITM-101',
        name: 'Tommy Hilfiger Slim Fit Linen Blazer - Navy',
        sku: 'TH-BLZ-NV-42',
        category: 'Menswear',
        quantity: 1,
        unitPrice: 31494,
        image: 'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&q=80&w=200',
      }
    ],
    totalAmount: 31494,
    paymentMethod: 'First Citizen Pay',
    status: 'Shipped',
    shippingAddress: 'Apt 1204, Oberoi Springs, Andheri West, Mumbai 400053',
    trackingNumber: 'AWB-DEL-9928114',
  },
  {
    id: 'SS-ORD-98420',
    customerName: 'Tanvi Agarwal',
    customerEmail: 'tanvi.agarwal@corp.in',
    customerPhone: '+91 98210 99887',
    loyaltyTier: 'Platinum',
    storeLocation: 'Mumbai - Malad West Flagship',
    date: '26.07.2026',
    time: '03:15 PM',
    items: [
      {
        id: 'ITM-103',
        name: 'Home Centre 6-Piece Percale Bedding Set - Blue',
        sku: 'HC-BED-BLU-KING',
        category: 'Home & Living',
        quantity: 2,
        unitPrice: 4999,
        image: 'https://images.unsplash.com/photo-1616594039964-ae9021a400a0?auto=format&fit=crop&q=80&w=200',
      }
    ],
    totalAmount: 9998,
    paymentMethod: 'UPI QR Code',
    status: 'Processing',
    shippingAddress: '42 Vasant Vihar, Block C, New Delhi 110057',
    trackingNumber: 'AWB-BLU-4410928',
  }
];

let STORED_REDEMPTIONS = [];

// GET All Customers
app.get('/api/customers', (req, res) => {
  res.json({ success: true, customers: STORED_CUSTOMERS });
});

// POST New Customer Sign-In (From Captive Portal or Site)
app.post('/api/customers', (req, res) => {
  const { name, phone, email } = req.body;
  if (!name) {
    return res.status(400).json({ success: false, message: 'Name is required' });
  }

  const cleanName = name.trim();
  const cleanPhone = phone ? (phone.startsWith('+91') ? phone : `+91 ${phone}`) : '+91 98765 43210';
  const cleanEmail = email ? email.trim() : `${phone || 'guest'}@ss-wifi.in`;

  // Remove existing duplicate by name or phone if any
  STORED_CUSTOMERS = STORED_CUSTOMERS.filter(c => c.name.toLowerCase() !== cleanName.toLowerCase());

  const newCust = {
    id: `CUST-${Math.floor(1000 + Math.random() * 9000)}`,
    name: cleanName,
    email: cleanEmail,
    phone: cleanPhone,
    loyaltyTier: 'Black',
    loyaltyPoints: 1250,
    totalSpent: 0,
    totalOrders: 0,
    lastPurchaseDate: '2026-07-27',
    preferredCategory: 'In-Store Guest Wi-Fi',
    joinedDate: '2026-07-27',
    avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=150'
  };

  // Prepend to top
  STORED_CUSTOMERS.unshift(newCust);
  console.log(`[SYNC API] Added new customer: ${cleanName} (${cleanPhone})`);

  res.json({ success: true, customer: newCust, customers: STORED_CUSTOMERS });
});

// GET All Coupons
app.get('/api/coupons', (req, res) => {
  res.json({ success: true, coupons: STORED_COUPONS });
});

// POST Create New Coupon (From Dashboard)
app.post('/api/coupons', (req, res) => {
  const cpn = req.body;
  if (!cpn || !cpn.code) {
    return res.status(400).json({ success: false, message: 'Coupon code is required' });
  }

  const cleanCode = cpn.code.trim().toUpperCase();
  // Remove existing coupon with same code if any
  STORED_COUPONS = STORED_COUPONS.filter(c => c.code.toUpperCase() !== cleanCode);

  const newCoupon = {
    id: cpn.id || `CPN-${Math.floor(100 + Math.random() * 900)}`,
    code: cleanCode,
    title: cpn.title || `${cleanCode} Special Discount`,
    description: cpn.description || `Flat promotional offer code ${cleanCode}`,
    discountType: cpn.discountType || (cpn.discountValue <= 100 ? 'Percentage' : 'Flat Amount'),
    discountValue: Number(cpn.discountValue) || 15,
    minOrderValue: Number(cpn.minOrderValue) || 1999,
    usageCount: 0,
    maxUsage: Number(cpn.maxUsage) || 1000,
    status: 'Active',
    startDate: cpn.startDate || '2026-07-01',
    endDate: cpn.endDate || '2026-12-31',
    applicableCategory: cpn.applicableCategory || 'Site-wide'
  };

  STORED_COUPONS.unshift(newCoupon);
  console.log(`[SYNC API] Created New Coupon Campaign: ${cleanCode} (${newCoupon.discountValue}% / ₹${newCoupon.discountValue} OFF)`);

  res.json({ success: true, coupon: newCoupon, coupons: STORED_COUPONS });
});

// GET All Orders
app.get('/api/orders', (req, res) => {
  res.json({ success: true, orders: STORED_ORDERS });
});

// POST New Order (From Kiosk/Shopping Site Checkout)
app.post('/api/orders', (req, res) => {
  const body = req.body;
  if (!body) return res.status(400).json({ success: false });

  const orderId = body.orderId || `SS-ORD-${Math.floor(98000 + Math.random() * 999)}`;

  // Format line items with high-res images
  const formattedItems = (body.items || []).map((itm, idx) => ({
    id: `ITM-${Date.now()}-${idx}`,
    name: itm.product ? itm.product.name : (itm.name || 'Shoppers Stop Fashion Item'),
    sku: itm.product ? itm.product.id : (itm.sku || `SS-SKU-${idx}`),
    category: itm.product ? itm.product.category : (itm.category || 'In-Store Kiosk'),
    quantity: itm.quantity || 1,
    unitPrice: itm.product ? itm.product.price : (itm.unitPrice || 1999),
    image: (itm.product && itm.product.images && itm.product.images[0])
      ? itm.product.images[0]
      : 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?auto=format&fit=crop&q=80&w=200'
  }));

  const now = new Date();
  const formattedDate = `${String(now.getDate()).padStart(2, '0')}.${String(now.getMonth() + 1).padStart(2, '0')}.${now.getFullYear()}`;
  const formattedTime = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  const newOrder = {
    id: orderId,
    customerName: body.customerName || 'Wi-Fi Kiosk Guest',
    customerEmail: body.customerEmail || 'guest@ss-wifi.in',
    customerPhone: body.customerPhone || '+91 98765 43210',
    loyaltyTier: 'Black',
    storeLocation: 'Mumbai - Malad West Flagship',
    date: formattedDate,
    time: formattedTime,
    items: formattedItems,
    totalAmount: body.pricing ? body.pricing.netPayable : (body.totalAmount || 2999),
    paymentMethod: body.paymentMethod === 'upi_qr' ? 'UPI QR Code' : (body.paymentMethod || 'Kiosk Express Pay'),
    status: 'In-Store Kiosk',
    shippingAddress: body.deliveryAddress || body.fittingRoomNo || body.pickupCounter || 'Store Pick-up Counter B',
    trackingNumber: `AWB-SS-${Math.floor(100000 + Math.random() * 900000)}`
  };

  // Prepend to top of orders list
  STORED_ORDERS.unshift(newOrder);

  // Update Customer order stats
  const targetCust = STORED_CUSTOMERS.find(c => c.name.toLowerCase() === newOrder.customerName.toLowerCase());
  if (targetCust) {
    targetCust.totalOrders += 1;
    targetCust.totalSpent += newOrder.totalAmount;
    targetCust.lastPurchaseDate = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
  }

  console.log(`[SYNC API] Order Recorded: ${newOrder.id} by ${newOrder.customerName} (₹${newOrder.totalAmount})`);

  res.json({ success: true, order: newOrder, orders: STORED_ORDERS });
});

// POST Coupon Redemption (From Captive Portal or Checkout)
app.post('/api/redemptions', (req, res) => {
  const { couponCode, customerName, customerEmail, customerPhone, orderId, orderTotal, discountSaved } = req.body;
  const cleanCode = (couponCode || 'SHOPPERS500').trim().toUpperCase();

  const redemption = {
    id: `RED-${Date.now().toString().slice(-4)}`,
    couponCode: cleanCode,
    customerName: customerName || 'Wi-Fi Guest',
    customerEmail: customerEmail || 'guest@ss-wifi.in',
    customerPhone: customerPhone || '+91 98765 43210',
    orderId: orderId || `SS-ORD-${Math.floor(98000 + Math.random() * 999)}`,
    orderTotal: orderTotal || 4999,
    discountSaved: discountSaved || 500,
    redeemedAt: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  };

  // Increment usage count in STORED_COUPONS
  const targetCpn = STORED_COUPONS.find(c => c.code.toUpperCase() === cleanCode);
  if (targetCpn) {
    targetCpn.usageCount += 1;
  }

  STORED_REDEMPTIONS.unshift(redemption);
  console.log(`[SYNC API] Coupon ${cleanCode} redeemed by: ${customerName} (Order Total: ₹${orderTotal || 0})`);

  res.json({ success: true, redemption, redemptions: STORED_REDEMPTIONS, coupons: STORED_COUPONS });
});

// GET All Redemptions
app.get('/api/redemptions', (req, res) => {
  res.json({ success: true, redemptions: STORED_REDEMPTIONS });
});

app.listen(PORT, () => {
  console.log(`🚀 Telemetry, Coupon & Order Sync Server running on http://localhost:${PORT}`);
});
