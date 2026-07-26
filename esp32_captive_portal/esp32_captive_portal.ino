#if defined(ESP32)
  #include <WiFi.h>
  #include <WebServer.h>
  #include <DNSServer.h>
  #include <HTTPClient.h>
  WebServer server(80);
#elif defined(ESP8266)
  #include <ESP8266WiFi.h>
  #include <ESP8266WebServer.h>
  #include <DNSServer.h>
  #include <ESP8266HTTPClient.h>
  ESP8266WebServer server(80);
#else
  #include <WiFi.h>
  #include <WebServer.h>
  #include <DNSServer.h>
  WebServer server(80);
#endif

DNSServer dnsServer;

void logPrint(String msg) {
  Serial.print(msg);
}

void logPrintln(String msg) {
  Serial.println(msg);
}

struct Customer {
  String name;
  String phone;
  String email;
  String vipTier;
  long totalSpend;
  String lastVisit;
};

#define MAX_CUSTOMERS 30
Customer customerList[MAX_CUSTOMERS];
int customerCount = 0;
unsigned long lastHeartbeat = 0;

const char* STORE_WIFI_SSID     = "SHOPPERS_STOP";      // PC Mobile Hotspot SSID
const char* STORE_WIFI_PASSWORD = "12345678";           // PC Mobile Hotspot Password
const char* BACKEND_HOST        = "10.20.71.13";        // Verified active PC IP (Status 200)
const int   BACKEND_PORT        = 63265;                 // FastAPI port

const char portal_html[] PROGMEM = R"rawliteral(<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>SHOPPERS STOP — Wi-Fi Portal & Stage 2 Designer Brands</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

  <style>
    :root {
      --primary: #C41E3A;
      --primary-dark: #9E152C;
      --secondary: #C9A96E;
      --secondary-gold: #D4AF37;
      --accent: #1A1A1A;
      --bg: #FFFFFF;
      --surface: #F8F7F5;
      --card-bg: #FFFFFF;
      --text-primary: #1A1A1A;
      --text-secondary: #6B6B6B;
      --text-muted: #9B9B9B;
      --success: #2E7D32;
      --border: #E8E8E8;
      --shadow-sm: 0 2px 8px rgba(0,0,0,0.04);
      --shadow-md: 0 4px 16px rgba(0,0,0,0.06);
      --shadow-lg: 0 8px 24px rgba(0,0,0,0.12);
      --font-heading: 'Playfair Display', Georgia, serif;
      --font-body: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
      --font-mono: SFMono-Regular, Consolas, monospace;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
    .btn-outline:hover { background: var(--primary); color: #FFFFFF; }
    #toastContainer { position: fixed; top: 20px; left: 50%; transform: translateX(-50%); z-index: 9999; display: flex; flex-direction: column; gap: 10px; pointer-events: none; width: 90%; max-width: 420px; }
    .toast { background: #FFFFFF; color: var(--text-primary); padding: 14px 20px; border-radius: 8px; box-shadow: var(--shadow-lg); font-size: 13px; font-weight: 600; border-left: 4px solid var(--primary); animation: toastSlideDown 0.3s cubic-bezier(0.25, 0.1, 0.25, 1) forwards; pointer-events: auto; }
    .toast.success { border-left-color: var(--success); }
    @keyframes toastSlideDown { from { opacity: 0; transform: translateY(-100%); } to { opacity: 1; transform: translateY(0); } }
    .svg-product-art { position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #FAF8F5 0%, #EFECE6 100%); overflow: hidden; }
    .svg-art-icon { width: 80%; height: 80%; filter: drop-shadow(0 6px 12px rgba(0,0,0,0.1)); transition: transform 0.4s ease; }
    .product-card:hover .svg-art-icon { transform: scale(1.06) translateY(-4px); }
    .svg-art-shimmer { animation: vectorShimmer 3s linear infinite; }
    @keyframes vectorShimmer { 0% { opacity: 0.85; } 50% { opacity: 1; filter: drop-shadow(0 8px 16px rgba(196, 30, 58, 0.25)); } 100% { opacity: 0.85; } }
    .svg-art-pulse { animation: vectorPulse 2.5s ease-in-out infinite; }
    @keyframes vectorPulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.04); } }
    #signinScreen { align-items: center; justify-content: center; padding: 24px 16px; background: linear-gradient(180deg, #FFFFFF 0%, var(--surface) 100%); }
    .signin-card { background: var(--card-bg); width: 100%; max-width: 440px; border-radius: 16px; padding: 40px 32px; box-shadow: var(--shadow-lg); border: 1px solid var(--border); text-align: center; position: relative; overflow: hidden; }
    .signin-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 5px; background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%); }
    .brand-logo { font-family: var(--font-heading); font-size: 28px; font-weight: 700; letter-spacing: 2px; color: var(--accent); margin-bottom: 2px; }
    .brand-tagline { font-size: 11px; text-transform: uppercase; letter-spacing: 3px; color: var(--secondary); font-weight: 700; margin-bottom: 24px; }
    .wifi-badge { display: inline-flex; align-items: center; gap: 6px; background: rgba(196, 30, 58, 0.06); color: var(--primary); padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 700; margin-bottom: 20px; }
    .signin-title { font-size: 22px; color: var(--text-primary); margin-bottom: 8px; }
    .signin-subtitle { font-size: 13px; color: var(--text-secondary); margin-bottom: 28px; }
    .form-group { text-align: left; margin-bottom: 20px; }
    .form-label { display: block; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-primary); margin-bottom: 6px; }
    .input-wrapper { position: relative; }
    .phone-prefix { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); font-size: 14px; font-weight: 700; color: var(--text-secondary); }
    .form-input { width: 100%; padding: 14px 16px; font-size: 14px; font-family: var(--font-body); border: 1px solid var(--border); border-radius: 8px; background: var(--surface); color: var(--text-primary); transition: border-color 0.2s ease, background-color 0.2s ease; }
    .form-input.has-prefix { padding-left: 54px; }
    .form-input:focus { outline: none; border-color: var(--primary); background: #FFFFFF; }
    .checkbox-group { display: flex; align-items: flex-start; gap: 10px; text-align: left; margin-bottom: 28px; }
    .checkbox-group input { margin-top: 3px; accent-color: var(--primary); width: 16px; height: 16px; }
    .checkbox-group label { font-size: 12px; color: var(--text-secondary); line-height: 1.4; cursor: pointer; }
    .modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.75); backdrop-filter: blur(4px); z-index: 2000; display: none; align-items: center; justify-content: center; padding: 20px; animation: fadeIn 0.3s ease forwards; }
    .modal-overlay.active { display: flex; }
    .coupon-card-modal { background: #FFFFFF; width: 100%; max-width: 400px; border-radius: 20px; padding: 32px 24px; text-align: center; position: relative; border-top: 5px solid var(--primary); box-shadow: 0 20px 40px rgba(0,0,0,0.25); }
    .coupon-header-title { font-size: 22px; color: var(--text-primary); margin-bottom: 4px; }
    .coupon-header-subtitle { font-size: 13px; color: var(--text-secondary); margin-bottom: 20px; }
    .scratch-container { position: relative; width: 300px; height: 160px; margin: 0 auto 20px auto; border-radius: 14px; overflow: hidden; box-shadow: var(--shadow-md); user-select: none; }
    .scratch-reward { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: #FFFFFF; border: 2px dashed var(--secondary); border-radius: 14px; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 16px; }
    .reward-tag { font-size: 11px; font-weight: 700; letter-spacing: 2px; color: var(--secondary); text-transform: uppercase; }
    .reward-discount { font-size: 44px; font-weight: 700; color: var(--primary); font-family: var(--font-heading); line-height: 1; margin: 6px 0; transition: transform 0.15s ease; }
    .reward-discount.pulse { transform: scale(1.15); }
    .reward-code { font-family: var(--font-mono); font-size: 16px; font-weight: 700; background: var(--surface); padding: 4px 14px; border-radius: 6px; color: var(--accent); border: 1px solid var(--border); }
    #scratchCanvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; cursor: pointer; touch-action: none; z-index: 2; transition: opacity 0.5s ease; }
    .confetti-container { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; overflow: hidden; z-index: 10; }
    .confetti-particle { position: absolute; width: 8px; height: 8px; border-radius: 2px; animation: confettiFly 1.8s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards; }
    @keyframes confettiFly { 0% { opacity: 1; transform: translate(0, 0) rotate(0deg); } 100% { opacity: 0; transform: translate(var(--x), var(--y)) rotate(var(--r)); } }
    #shopScreen { padding-bottom: 100px; }
    .header-bar { position: sticky; top: 0; z-index: 100; background: rgba(255, 255, 255, 0.96); backdrop-filter: blur(10px); border-bottom: 1px solid var(--border); padding: 14px 24px; display: flex; align-items: center; justify-content: space-between; }
    .header-left { display: flex; align-items: center; gap: 16px; }
    .header-logo { font-family: var(--font-heading); font-size: 22px; font-weight: 700; letter-spacing: 1.5px; color: var(--accent); line-height: 1; }
    .header-greeting { font-size: 13px; color: var(--text-secondary); }
    .header-right { display: flex; align-items: center; gap: 12px; }
    .portal-link-btn { font-size: 12px; color: var(--text-muted); cursor: pointer; text-decoration: underline; border: none; background: none; }
    .cart-trigger { position: relative; background: var(--surface); border: 1px solid var(--border); padding: 10px 18px; border-radius: 20px; font-size: 13px; font-weight: 700; color: var(--accent); cursor: pointer; display: flex; align-items: center; gap: 8px; transition: all 0.2s ease; }
    .cart-trigger:hover { background: #FFFFFF; border-color: var(--accent); }
    .cart-badge { background: var(--primary); color: #FFFFFF; font-size: 11px; font-weight: 800; width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: transform 0.3s ease; }
    .cart-badge.bump { transform: scale(1.35); }
    .coupon-banner { background: linear-gradient(90deg, var(--accent) 0%, #2A2A2A 100%); color: #FFFFFF; padding: 12px 20px; font-size: 13px; text-align: center; display: flex; align-items: center; justify-content: center; gap: 8px; }
    .coupon-banner-tag { background: var(--secondary-gold); color: var(--accent); padding: 2px 8px; border-radius: 4px; font-weight: 800; font-size: 11px; }
    .categories-wrapper { padding: 16px 24px; overflow-x: auto; white-space: nowrap; scrollbar-width: none; background: #FFFFFF; border-bottom: 1px solid var(--border); }
    .categories-wrapper::-webkit-scrollbar { display: none; }
    .category-pills { display: inline-flex; gap: 12px; }
    .pill { padding: 8px 20px; border-radius: 20px; font-size: 13px; font-weight: 600; color: var(--text-primary); background: #FFFFFF; border: 1px solid var(--border); cursor: pointer; transition: all 0.2s ease; }
    .pill:hover { background: var(--surface); }
    .pill.active { background: var(--primary); color: #FFFFFF; border-color: var(--primary); font-weight: 700; }
    .container { max-width: 1280px; margin: 0 auto; padding: 28px 20px; }
    .product-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
    @media (min-width: 768px) { .product-grid { grid-template-columns: repeat(3, 1fr); gap: 24px; } }
    @media (min-width: 1024px) { .product-grid { grid-template-columns: repeat(4, 1fr); gap: 28px; } }
    .product-card { background: var(--card-bg); border-radius: 14px; border: 1px solid var(--border); overflow: hidden; display: flex; flex-direction: column; position: relative; transition: transform 0.3s ease, box-shadow 0.3s ease; }
    .product-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-lg); }
    .image-container { position: relative; width: 100%; padding-top: 133.33%; background: var(--surface); overflow: hidden; }
    .product-img { position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; transition: transform 0.4s ease, opacity 0.3s ease; opacity: 0; z-index: 2; }
    .product-img.loaded { opacity: 1; }
    .product-card:hover .product-img { transform: scale(1.04); }
    .badge { position: absolute; top: 10px; right: 10px; background: var(--primary); color: #FFFFFF; font-size: 10px; font-weight: 800; padding: 4px 8px; border-radius: 3px; letter-spacing: 0.5px; transform: rotate(-2deg); box-shadow: 0 2px 6px rgba(0,0,0,0.15); z-index: 5; }
    .product-info { padding: 16px; display: flex; flex-direction: column; flex-grow: 1; }
    .product-brand { font-size: 10px; font-weight: 800; letter-spacing: 1px; color: var(--text-muted); text-transform: uppercase; margin-bottom: 2px; }
    .product-name { font-size: 14px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; line-height: 1.3; cursor: pointer; }
    .product-desc { font-size: 12px; color: var(--text-secondary); margin-bottom: 12px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; height: 32px; }
    .price-row { display: flex; align-items: baseline; gap: 8px; margin-bottom: 4px; }
    .deal-price { font-size: 16px; font-weight: 800; color: var(--primary); font-family: var(--font-mono); }
    .mrp-price { font-size: 12px; color: var(--text-muted); text-decoration: line-through; font-family: var(--font-mono); }
    .coupon-discount-tag { font-size: 11px; font-weight: 700; color: var(--success); margin-bottom: 12px; }
    .add-to-bag-btn { margin-top: auto; width: 100%; padding: 10px; font-size: 12px; font-weight: 700; }
    .floating-cart-bar { position: fixed; bottom: 0; left: 0; right: 0; background: var(--primary); color: #FFFFFF; padding: 16px 24px; display: flex; align-items: center; justify-content: space-between; border-top-left-radius: 20px; border-top-right-radius: 20px; box-shadow: 0 -4px 20px rgba(0,0,0,0.2); z-index: 90; transform: translateY(100%); transition: transform 0.3s cubic-bezier(0.32, 0.72, 0, 1); }
    .floating-cart-bar.active { transform: translateY(0); }
    .cart-summary-text { display: flex; flex-direction: column; }
    .cart-summary-main { font-size: 16px; font-weight: 800; }
    .cart-summary-savings { font-size: 12px; opacity: 0.9; }
    .view-bag-btn { background: #FFFFFF; color: var(--primary); padding: 10px 22px; border-radius: 20px; font-size: 12px; font-weight: 800; border: none; cursor: pointer; text-transform: uppercase; letter-spacing: 0.5px; }
    .sheet-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.6); z-index: 1000; display: none; align-items: flex-end; justify-content: center; animation: fadeIn 0.2s ease forwards; }
    .sheet-overlay.active { display: flex; }
    .cart-sheet { background: #FFFFFF; width: 100%; max-width: 600px; max-height: 85vh; border-top-left-radius: 24px; border-top-right-radius: 24px; display: flex; flex-direction: column; overflow: hidden; animation: slideUp 0.35s cubic-bezier(0.32, 0.72, 0, 1) forwards; }
    @keyframes slideUp { from { transform: translateY(100%); } to { transform: translateY(0); } }
    .cart-sheet-header { padding: 20px 24px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; }
    .cart-sheet-title { font-size: 18px; font-weight: 800; }
    .close-btn { background: none; border: none; font-size: 24px; color: var(--text-secondary); cursor: pointer; }
    .cart-items-list { padding: 20px 24px; overflow-y: auto; flex-grow: 1; display: flex; flex-direction: column; gap: 16px; }
    .cart-item { display: flex; gap: 16px; padding-bottom: 16px; border-bottom: 1px solid var(--border); }
    .cart-item-thumb-container { width: 70px; height: 93px; border-radius: 8px; overflow: hidden; position: relative; background: var(--surface); flex-shrink: 0; }
    .cart-item-details { display: flex; flex-direction: column; flex-grow: 1; }
    .cart-item-title { font-size: 14px; font-weight: 700; margin-bottom: 4px; }
    .cart-item-prices { display: flex; align-items: baseline; gap: 8px; margin-bottom: 8px; }
    .qty-controls { display: flex; align-items: center; gap: 12px; margin-top: auto; }
    .qty-btn { width: 26px; height: 26px; border: 1px solid var(--border); border-radius: 4px; background: var(--surface); font-weight: 700; display: flex; align-items: center; justify-content: center; cursor: pointer; }
    .cart-pricing-summary { background: var(--surface); padding: 20px 24px; border-top: 1px solid var(--border); }
    .price-row-item { display: flex; justify-content: space-between; font-size: 13px; color: var(--text-secondary); margin-bottom: 8px; }
    .price-row-item.highlight-green { color: var(--success); font-weight: 700; }
    .price-row-item.total-row { font-size: 18px; font-weight: 900; color: var(--primary); border-top: 1px dashed var(--border); padding-top: 10px; margin-top: 10px; margin-bottom: 16px; }
    .product-detail-modal-card { background: #FFFFFF; width: 100%; max-width: 540px; border-top-left-radius: 24px; border-top-right-radius: 24px; padding: 28px 24px; max-height: 90vh; overflow-y: auto; }
    #orderSuccessScreen { align-items: center; justify-content: center; padding: 32px 20px; background: var(--surface); }
    .success-card { background: #FFFFFF; border-radius: 20px; padding: 44px 32px; max-width: 480px; width: 100%; box-shadow: var(--shadow-lg); border: 1px solid var(--border); text-align: center; }
    .checkmark-svg { width: 72px; height: 72px; margin: 0 auto 20px auto; }
    .checkmark-circle { stroke: var(--success); stroke-width: 2; stroke-dasharray: 166; stroke-dashoffset: 166; animation: strokeDraw 0.6s cubic-bezier(0.65, 0, 0.45, 1) forwards; }
    .checkmark-check { stroke: var(--success); stroke-width: 3; stroke-dasharray: 48; stroke-dashoffset: 48; animation: strokeDraw 0.4s cubic-bezier(0.65, 0, 0.45, 1) 0.5s forwards; }
    @keyframes strokeDraw { to { stroke-dashoffset: 0; } }
    .success-title { font-size: 26px; color: var(--text-primary); margin-bottom: 6px; }
    .order-id-badge { display: inline-block; background: var(--surface); border: 1px solid var(--border); padding: 6px 16px; border-radius: 6px; font-family: var(--font-mono); font-size: 15px; font-weight: 800; color: var(--accent); margin-bottom: 20px; }
    .pay-badge { background: rgba(201, 169, 110, 0.15); color: #8A6D3B; padding: 8px 18px; border-radius: 20px; font-size: 13px; font-weight: 800; margin-bottom: 24px; display: inline-block; }
  </style>
</head>
<body>
  <div id="toastContainer"></div>
  <section id="signinScreen" class="view-section active">
    <div class="signin-card">
      <div class="brand-logo">SHOPPERS STOP</div>
      <div class="brand-tagline">Stop. Style. Save.</div>
      <div class="wifi-badge"><span>Wi-Fi Guest Access</span></div>
      <h1 class="signin-title">Welcome to In-Store Wi-Fi</h1>
      <p class="signin-subtitle">Sign in to connect &amp; unlock your exclusive surprise welcome voucher!</p>
      <form id="signinForm" onsubmit="handleSignin(event)">
        <div class="form-group"><label class="form-label" for="userName">Full Name</label><input type="text" id="userName" class="form-input" placeholder="e.g. Priya Sharma" value="Priya Sharma" required></div>
        <div class="form-group"><label class="form-label" for="userPhone">Phone Number</label><div class="input-wrapper"><span class="phone-prefix">+91</span><input type="tel" id="userPhone" class="form-input has-prefix" placeholder="9876543210" pattern="[0-9]{10}" maxlength="10" value="9876543210" required></div></div>
        <div class="form-group"><label class="form-label" for="userEmail">Email Address (Optional)</label><input type="email" id="userEmail" class="form-input" placeholder="priya@example.com"></div>
        <div class="checkbox-group"><input type="checkbox" id="userConsent" checked required><label for="userConsent">I want to receive exclusive offers, fashion updates &amp; VIP privileges from Shoppers Stop.</label></div>
        <button type="submit" class="btn btn-primary" style="width: 100%;">Unlock My Gift &rarr;</button>
      </form>
    </div>
  </section>

  <div id="couponModal" class="modal-overlay">
    <div class="coupon-card-modal">
      <h2 class="coupon-header-title">&#127873; Surprise Gift Unlocked!</h2>
      <p class="coupon-header-subtitle">Scratch below to reveal your exclusive Wi-Fi welcome voucher</p>
      <div class="scratch-container" id="scratchContainer">
        <div class="scratch-reward">
          <div class="reward-tag">SHOPPERS STOP GIFT</div>
          <div class="reward-discount" id="counterDiscount">0% OFF</div>
          <div class="reward-code" id="revealCode">Code: SS20</div>
          <div style="font-size: 11px; color: var(--text-muted); margin-top: 4px;">Applied at Checkout</div>
        </div>
        <canvas id="scratchCanvas" width="300" height="160"></canvas>
        <div id="confettiContainer" class="confetti-container"></div>
      </div>
      <div style="font-size: 12px; font-weight: 700; color: var(--primary); margin-bottom: 20px;">Valid for this session only!</div>
      <button id="startShoppingBtn" class="btn btn-primary" style="width: 100%; display: none;" onclick="closeCouponModal()">Start Shopping &rarr;</button>
      <button id="manualRevealBtn" class="btn btn-outline" style="width: 100%; font-size: 12px; padding: 10px;" onclick="forceRevealCoupon()">Tap to Reveal</button>
    </div>
  </div>

  <section id="shopScreen" class="view-section">
    <header class="header-bar">
      <div class="header-left"><div class="header-logo">SHOPPERS STOP</div><div class="header-greeting" id="userGreeting">Hi Shopper!</div></div>
      <div class="header-right"><button class="portal-link-btn" onclick="goToPortalSignin()">Wi-Fi Portal</button><button class="cart-trigger" onclick="openCart()"><span>Bag</span><span class="cart-badge" id="cartBadgeCount">0</span></button></div>
    </header>
    <div class="coupon-banner" id="couponBanner"><span>Wi-Fi Connected</span> &bull; <span>Coupon <strong id="bannerCode">SS20</strong> (<strong id="bannerDiscount">20% OFF</strong>) Active!</span></div>
    <div class="categories-wrapper"><div class="category-pills" id="categoryPills"></div></div>
    <main class="container"><div class="product-grid" id="productGrid"></div></main>
    <div class="floating-cart-bar" id="floatingCartBar">
      <div class="cart-summary-text"><span class="cart-summary-main" id="barMainText">0 items | ₹0</span><span class="cart-summary-savings" id="barSavingsText">You save ₹0</span></div>
      <button class="view-bag-btn" onclick="openCart()">View Bag &rarr;</button>
    </div>
  </section>

  <div id="cartSheetOverlay" class="sheet-overlay" onclick="handleCartOverlayClick(event)">
    <div class="cart-sheet">
      <div class="cart-sheet-header"><div class="cart-sheet-title">YOUR SHOPPING BAG</div><button class="close-btn" onclick="closeCart()">&times;</button></div>
      <div class="cart-items-list" id="cartItemsList"></div>
      <div class="cart-pricing-summary">
        <div class="price-row-item"><span>MRP Total</span><span id="summaryMrp">₹0</span></div>
        <div class="price-row-item"><span>Deal Price</span><span id="summaryDeal">₹0</span></div>
        <div class="price-row-item highlight-green"><span id="summaryCouponLabel">Coupon Discount</span><span id="summaryCouponValue">-₹0</span></div>
        <div class="price-row-item"><span>GST (5%)</span><span id="summaryGst">₹0</span></div>
        <div class="price-row-item highlight-green"><span>Delivery</span><span id="summaryDelivery">FREE</span></div>
        <div class="price-row-item highlight-green" style="font-weight: 800;"><span>TOTAL SAVINGS</span><span id="summaryTotalSavings">₹0</span></div>
        <div class="price-row-item total-row"><span>FINAL TOTAL</span><span id="summaryFinalTotal">₹0</span></div>
        <button class="btn btn-primary" style="width: 100%;" onclick="placeOrder()">Place Order &rarr;</button>
      </div>
    </div>
  </div>

  <div id="detailSheetOverlay" class="sheet-overlay" onclick="handleDetailOverlayClick(event)">
    <div class="product-detail-modal-card">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
        <div style="font-size:10px; font-weight:800; letter-spacing:1px; color:var(--text-muted);">SHOPPERS STOP EXCLUSIVE</div>
        <button class="close-btn" onclick="closeDetailModal()">&times;</button>
      </div>
      <div style="position:relative; width:100%; height:280px; border-radius:12px; overflow:hidden; margin-bottom:16px; background:var(--surface);">
        <img id="modalDetailHeroImg" src="" alt="Detail" style="width:100%; height:100%; object-fit:cover; z-index:2; position:relative;" onload="this.classList.add('loaded');" onerror="this.style.display='none';" />
        <div id="modalDetailSvgContainer" class="svg-product-art"></div>
      </div>
      <div id="modalDetailTitle" style="font-size:20px; font-weight:800; margin-bottom:4px;">Product Title</div>
      <div id="modalDetailDesc" style="font-size:13px; color:var(--text-secondary); margin-bottom:16px;">Description text</div>
      <div style="display:flex; align-items:baseline; gap:10px; margin-bottom:16px;">
        <span id="modalDetailPrice" style="font-size:22px; font-weight:900; color:var(--primary); font-family:var(--font-mono);">&#8377;0</span>
        <span id="modalDetailMrp" style="font-size:14px; color:var(--text-muted); text-decoration:line-through; font-family:var(--font-mono);">&#8377;0</span>
      </div>
      <div style="background:var(--surface); padding:14px; border-radius:10px; margin-bottom:20px;">
        <div style="font-size:12px; font-weight:800; margin-bottom:4px;">Fabric &amp; Specifications</div>
        <div style="font-size:11px; color:var(--text-secondary); line-height:1.5;">Inside: 100% Breathable Premium Blend.<br>Outside: Soft-touch finish, easy care &amp; durable stitch.</div>
      </div>
      <button class="btn btn-primary" style="width: 100%;" onclick="addFromDetailModal()">ADD TO BAG &rarr;</button>
    </div>
  </div>

  <section id="orderSuccessScreen" class="view-section">
    <div class="success-card">
      <svg class="checkmark-svg" viewBox="0 0 52 52">
        <circle class="checkmark-circle" cx="26" cy="26" r="25" fill="none"/>
        <path class="checkmark-check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8"/>
      </svg>
      <h1 class="success-title">Order Confirmed!</h1>
      <div class="order-id-badge" id="orderIdText">Order ID: SS-7842</div>
      <br>
      <div class="pay-badge">Pay at Counter &amp; Pick Up</div>
      <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 28px; line-height: 1.6;">
        Thank you for shopping at Shoppers Stop.<br>
        <strong id="successSavingsText">You saved ₹0 on this order!</strong><br>
        Show your Order ID at the checkout desk.
      </p>
      <div style="display: flex; flex-direction: column; gap: 12px;">
        <button class="btn btn-primary" onclick="resetToShop()">Continue Shopping</button>
        <button class="btn btn-outline" onclick="disconnectWifi()">Disconnect Wi-Fi</button>
      </div>
    </div>
  </section>

  <script>
    var SHIRT_IMG = 'data:image/jpeg;base64,SHIRT_BASE64_PLACEHOLDER';
    var JEANS_IMG = 'data:image/jpeg;base64,JEANS_BASE64_PLACEHOLDER';
    var TSHIRT_IMG = 'data:image/jpeg;base64,TSHIRT_BASE64_PLACEHOLDER';
    var KURTI_IMG = 'data:image/jpeg;base64,KURTI_BASE64_PLACEHOLDER';
    var DRESS_IMG = 'data:image/jpeg;base64,DRESS_BASE64_PLACEHOLDER';
    var HANDBAG_IMG = 'data:image/jpeg;base64,HANDBAG_BASE64_PLACEHOLDER';
    var KIDSTEE_IMG = 'data:image/jpeg;base64,KIDSTEE_BASE64_PLACEHOLDER';
    var SHOES_IMG = 'data:image/jpeg;base64,SHOES_BASE64_PLACEHOLDER';
    var BEDSHEET_IMG = 'data:image/jpeg;base64,BEDSHEET_BASE64_PLACEHOLDER';
    var CUSHION_IMG = 'data:image/jpeg;base64,CUSHION_BASE64_PLACEHOLDER';
    var PERFUME_IMG = 'data:image/jpeg;base64,PERFUME_BASE64_PLACEHOLDER';
    var SERUM_IMG = 'data:image/jpeg;base64,SERUM_BASE64_PLACEHOLDER';
    var WATCH_IMG = 'data:image/jpeg;base64,WATCH_BASE64_PLACEHOLDER';
    var SUNGLASSES_IMG = 'data:image/jpeg;base64,SUNGLASSES_BASE64_PLACEHOLDER';

    function getProductSVG(id) {
      var svgs = {
        shirt: '<svg class="svg-art-icon svg-art-shimmer" viewBox="0 0 100 120" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M25 25 L40 10 L60 10 L75 25 L90 35 L80 50 L70 42 L70 110 L30 110 L30 42 L20 50 L10 35 Z" fill="url(#shirtGrad)" stroke="#1A1A1A" stroke-width="2"/><path d="M40 10 L50 30 L60 10" fill="none" stroke="#C9A96E" stroke-width="2"/><circle cx="50" cy="45" r="2" fill="#D4AF37"/><circle cx="50" cy="65" r="2" fill="#D4AF37"/><circle cx="50" cy="85" r="2" fill="#D4AF37"/><defs><linearGradient id="shirtGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#1E3A5F"/><stop offset="100%" stop-color="#1A1A1A"/></linearGradient></defs></svg>',
        jeans: '<svg class="svg-art-icon svg-art-shimmer" viewBox="0 0 100 120" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M20 15 L80 15 L76 115 L52 115 L50 50 L48 115 L24 115 Z" fill="url(#jeansGrad)" stroke="#1A1A1A" stroke-width="2"/><path d="M20 28 L80 28" stroke="#D4AF37" stroke-width="2" stroke-dasharray="3 3"/><circle cx="50" cy="22" r="3" fill="#D4AF37"/><defs><linearGradient id="jeansGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#2B4C7E"/><stop offset="100%" stop-color="#0F1B29"/></linearGradient></defs></svg>',
        tshirt: '<svg class="svg-art-icon svg-art-pulse" viewBox="0 0 100 120" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M25 20 L38 12 L62 12 L75 20 L92 32 L82 48 L72 40 L72 105 L28 105 L28 40 L18 48 L8 32 Z" fill="url(#tshirtGrad)" stroke="#9E152C" stroke-width="2"/><path d="M38 12 C44 22 56 22 62 12" fill="none" stroke="#FFFFFF" stroke-width="3"/><defs><linearGradient id="tshirtGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#C41E3A"/><stop offset="100%" stop-color="#9E152C"/></linearGradient></defs></svg>',
        kurti: '<svg class="svg-art-icon svg-art-shimmer" viewBox="0 0 100 120" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M30 15 L42 10 L58 10 L70 15 L88 30 L78 45 L68 38 L72 112 L28 112 L32 38 L22 45 L12 30 Z" fill="url(#kurtiGrad)" stroke="#C9A96E" stroke-width="2"/><circle cx="50" cy="50" r="4" fill="#D4AF37"/><circle cx="50" cy="70" r="4" fill="#D4AF37"/><defs><linearGradient id="kurtiGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#D81B60"/><stop offset="100%" stop-color="#8E24AA"/></linearGradient></defs></svg>',
        dress: '<svg class="svg-art-icon svg-art-pulse" viewBox="0 0 100 120" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M40 10 L60 10 L65 30 L72 50 L85 115 L15 115 L28 50 L35 30 Z" fill="url(#dressGrad)" stroke="#1A1A1A" stroke-width="2"/><path d="M35 30 Q50 40 65 30" stroke="#D4AF37" stroke-width="2" fill="none"/><defs><linearGradient id="dressGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#C41E3A"/><stop offset="50%" stop-color="#1A1A1A"/><stop offset="100%" stop-color="#000000"/></linearGradient></defs></svg>',
        handbag: '<svg class="svg-art-icon svg-art-shimmer" viewBox="0 0 100 120" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M35 40 C35 15 65 15 65 40" fill="none" stroke="#D4AF37" stroke-width="4"/><path d="M15 40 L85 40 Q90 110 80 110 L20 110 Q10 110 15 40 Z" fill="url(#bagGrad)" stroke="#1A1A1A" stroke-width="2"/><rect x="44" y="50" width="12" height="14" rx="2" fill="#D4AF37"/><defs><linearGradient id="bagGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#8B4513"/><stop offset="100%" stop-color="#4A2306"/></linearGradient></defs></svg>',
        kidstee: '<svg class="svg-art-icon svg-art-pulse" viewBox="0 0 100 120" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M20 25 L35 15 L65 15 L80 25 L95 38 L82 52 L72 44 L72 105 L28 105 L28 44 L18 52 L5 38 Z" fill="url(#kidGrad)" stroke="#1E88E5" stroke-width="2"/><polygon points="50,45 54,55 65,55 56,62 59,72 50,66 41,72 44,62 35,55 46,55" fill="#FFD54F"/><defs><linearGradient id="kidGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#FF6347"/><stop offset="100%" stop-color="#FF8A65"/></linearGradient></defs></svg>',
        shoes: '<svg class="svg-art-icon svg-art-shimmer" viewBox="0 0 100 120" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M10 75 Q15 45 45 45 L75 55 Q92 65 92 85 L10 85 Z" fill="url(#shoeGrad)" stroke="#1A1A1A" stroke-width="2"/><rect x="8" y="85" width="86" height="12" rx="4" fill="#FFFFFF" stroke="#1A1A1A" stroke-width="2"/><defs><linearGradient id="shoeGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#1565C0"/><stop offset="100%" stop-color="#0D47A1"/></linearGradient></defs></svg>',
        bedsheet: '<svg class="svg-art-icon svg-art-pulse" viewBox="0 0 100 120" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="15" y="20" width="70" height="80" rx="6" fill="url(#bedGrad)" stroke="#C9A96E" stroke-width="2"/><defs><linearGradient id="bedGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#FFF9C4"/><stop offset="100%" stop-color="#FBC02D"/></linearGradient></defs></svg>',
        cushion: '<svg class="svg-art-icon svg-art-shimmer" viewBox="0 0 100 120" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="20" y="25" width="60" height="60" rx="8" transform="rotate(45 50 55)" fill="url(#cushGrad)" stroke="#1A1A1A" stroke-width="2"/><circle cx="50" cy="55" r="8" fill="#D4AF37"/><defs><linearGradient id="cushGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#E64A19"/><stop offset="100%" stop-color="#D81B60"/></linearGradient></defs></svg>',
        perfume: '<svg class="svg-art-icon svg-art-shimmer" viewBox="0 0 100 120" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="42" y="15" width="16" height="12" rx="2" fill="#D4AF37" stroke="#1A1A1A"/><path d="M22 35 L78 35 L82 105 Q82 110 75 110 L25 110 Q18 110 18 105 Z" fill="url(#perfGrad)" stroke="#D4AF37" stroke-width="2"/><rect x="32" y="55" width="36" height="35" rx="3" fill="#FFFFFF" opacity="0.9"/><text x="50" y="72" font-size="7" font-weight="bold" fill="#1A1A1A" text-anchor="middle">PARFUM</text><defs><linearGradient id="perfGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#FFF176"/><stop offset="100%" stop-color="#FF8F00"/></linearGradient></defs></svg>',
        serum: '<svg class="svg-art-icon svg-art-pulse" viewBox="0 0 100 120" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="44" y="10" width="12" height="16" rx="4" fill="#1A1A1A"/><path d="M28 34 L72 34 L76 108 Q76 112 70 112 L30 112 Q24 112 24 108 Z" fill="url(#serumGrad)" stroke="#FFA000" stroke-width="2"/><circle cx="50" cy="72" r="4" fill="#FFFFFF"/><defs><linearGradient id="serumGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#FFE082"/><stop offset="100%" stop-color="#FFB300"/></linearGradient></defs></svg>',
        watch: '<svg class="svg-art-icon svg-art-shimmer" viewBox="0 0 100 120" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="38" y="10" width="24" height="25" fill="#78909C" stroke="#1A1A1A"/><rect x="38" y="85" width="24" height="25" fill="#78909C" stroke="#1A1A1A"/><circle cx="50" cy="60" r="30" fill="url(#watchGrad)" stroke="#D4AF37" stroke-width="3"/><circle cx="50" cy="60" r="24" fill="#1A1A1A"/><path d="M50 60 L50 44 M50 60 L62 60" stroke="#D4AF37" stroke-width="2"/><defs><linearGradient id="watchGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#ECEFF1"/><stop offset="100%" stop-color="#B0BEC5"/></linearGradient></defs></svg>',
        sunglasses: '<svg class="svg-art-icon svg-art-pulse" viewBox="0 0 100 120" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 50 Q30 45 46 50 Q48 68 44 72 Q25 78 15 72 Z" fill="url(#glassGrad)" stroke="#D4AF37" stroke-width="2"/><path d="M54 50 Q70 45 88 50 Q85 72 75 78 Q56 72 54 50 Z" fill="url(#glassGrad)" stroke="#D4AF37" stroke-width="2"/><defs><linearGradient id="glassGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#37474F"/><stop offset="100%" stop-color="#212121"/></linearGradient></defs></svg>'
      };
      return svgs[id] || svgs.shirt;
    }

    var PRODUCTS = [
      {id:'shirt', name:'Slim Fit Formal Shirt', price:1299, mrp:2499, category:'Men', description:'Premium cotton, perfect for office', image:SHIRT_IMG, badge:'BESTSELLER', sizes:['S','M','L','XL','XXL'], colors:['#1A1A1A','#FFFFFF','#1E3A5F','#C41E3A']},
      {id:'jeans', name:'Slim Fit Jeans', price:1999, mrp:3499, category:'Men', description:'Stretch denim, modern tapered fit', image:JEANS_IMG, badge:'TRENDING', sizes:['28','30','32','34','36'], colors:['#000080','#708090','#1A1A1A']},
      {id:'tshirt', name:'Polo T-Shirt', price:699, mrp:1299, category:'Men', description:'Classic polo, breathable pique fabric', image:TSHIRT_IMG, sizes:['S','M','L','XL'], colors:['#FFFFFF','#000000','#C41E3A','#1E3A5F']},
      {id:'kurti', name:'Printed Cotton Kurti', price:899, mrp:1799, category:'Women', description:'Floral print, comfortable everyday wear', image:KURTI_IMG, badge:'ETHNIC', sizes:['S','M','L','XL','XXL'], colors:['#FF69B4','#FFA500','#9370DB','#2E7D32']},
      {id:'dress', name:'Evening Maxi Dress', price:2499, mrp:4999, category:'Women', description:'Elegant flowy dress for special occasions', image:DRESS_IMG, badge:'PREMIUM', sizes:['XS','S','M','L'], colors:['#000000','#C41E3A','#D4AF37']},
      {id:'handbag', name:'Leather Handbag', price:1599, mrp:2999, category:'Women', description:'Genuine leather, spacious compartments', image:HANDBAG_IMG, badge:'LUXURY', sizes:['One Size'], colors:['#8B4513','#000000','#A0522D']},
      {id:'kidstee', name:'Kids Graphic Tee', price:499, mrp:799, category:'Kids', description:'Fun prints, soft cotton for all-day comfort', image:KIDSTEE_IMG, sizes:['2-3Y','4-5Y','6-8Y','9-12Y'], colors:['#FF6347','#4169E1','#32CD32']},
      {id:'shoes', name:'Kids Running Shoes', price:799, mrp:1499, category:'Kids', description:'Lightweight, flexible, durable', image:SHOES_IMG, sizes:['11','12','13','1','2'], colors:['#0000FF','#FF0000','#000000']},
      {id:'bedsheet', name:'King Size Bedsheet', price:999, mrp:1999, category:'Home', description:'300 TC cotton, soft & breathable', image:BEDSHEET_IMG, badge:'VALUE PACK', sizes:['King','Queen'], colors:['#F5F5DC','#E6E6FA','#FFE4E1']},
      {id:'cushion', name:'Cushion Cover Set (5pc)', price:299, mrp:599, category:'Home', description:'Vibrant designs, easy to wash', image:CUSHION_IMG, sizes:['16x16','18x18'], colors:['#FF6347','#4169E1','#32CD32','#FFD700']},
      {id:'perfume', name:'Eau de Parfum 100ml', price:1999, mrp:3999, category:'Beauty', description:'Long-lasting, premium fragrance', image:PERFUME_IMG, badge:'SIGNATURE', sizes:['50ml','100ml'], colors:['#D4AF37']},
      {id:'serum', name:'Vitamin C Face Serum', price:599, mrp:1199, category:'Beauty', description:'Brightening, anti-aging formula', image:SERUM_IMG, sizes:['30ml','50ml'], colors:['#FFA500']},
      {id:'watch', name:'Analog Dress Watch', price:2999, mrp:5999, category:'Accessories', description:'Stainless steel, water resistant', image:WATCH_IMG, badge:'CLASSIC', sizes:['One Size'], colors:['#C0C0C0','#D4AF37','#1A1A1A']},
      {id:'sunglasses', name:'UV Polarized Sunglasses', price:1299, mrp:2499, category:'Accessories', description:'UV400 protection, stylish frames', image:SUNGLASSES_IMG, sizes:['One Size'], colors:['#000000','#8B4513','#4169E1']}
    ];

    var CATEGORIES = ['Popular', 'Men', 'Women', 'Kids', 'Home', 'Beauty', 'Accessories'];
    var POPULAR_IDS = ['shirt', 'kurti', 'perfume', 'watch'];

    var appState = { user: null, coupon: { discount: 20, code: 'SS20' }, cart: [], selectedCategory: 'Popular', selectedOptions: {}, activeDetailItem: null };

    document.addEventListener('DOMContentLoaded', function() { loadLocalStorage(); showView('signinScreen'); });

    function loadLocalStorage() {
      try {
        var u = localStorage.getItem('ss_user'); var c = localStorage.getItem('ss_coupon'); var crt = localStorage.getItem('ss_cart');
        if (u) appState.user = JSON.parse(u); if (c) appState.coupon = JSON.parse(c); if (crt) appState.cart = JSON.parse(crt);
      } catch(e) {}
      if (!appState.coupon) appState.coupon = { discount: 20, code: 'SS20' };
    }

    function saveLocalStorage() {
      try {
        if (appState.user) localStorage.setItem('ss_user', JSON.stringify(appState.user));
        if (appState.coupon) localStorage.setItem('ss_coupon', JSON.stringify(appState.coupon));
        localStorage.setItem('ss_cart', JSON.stringify(appState.cart));
      } catch(e) {}
    }

    function showView(viewId) {
      document.querySelectorAll('.view-section').forEach(function(sec) { sec.classList.remove('active'); });
      document.getElementById(viewId).classList.add('active'); window.scrollTo(0, 0);
    }

    function goToPortalSignin() { showView('signinScreen'); }

    function showToast(msg, type) {
      var container = document.getElementById('toastContainer');
      var t = document.createElement('div'); t.className = 'toast ' + (type || 'info'); t.innerText = msg;
      container.appendChild(t);
      setTimeout(function() { t.style.animation = 'toastFadeOut 0.3s forwards'; setTimeout(function() { t.remove(); }, 300); }, 2500);
    }

    function handleSignin(e) {
      e.preventDefault();
      var name = document.getElementById('userName').value.trim(); var phone = document.getElementById('userPhone').value.trim(); var email = document.getElementById('userEmail').value.trim();
      if (!name || !phone) { showToast('Please enter your name and phone number', 'error'); return; }
      appState.user = { name: name, phone: phone, email: email };
      var options = [10, 15, 20, 25, 30]; var discount = options[Math.floor(Math.random() * options.length)];
      appState.coupon = { discount: discount, code: 'SS' + discount };
      saveLocalStorage(); openCouponModal();

      // Save customer to localStorage for Dashboard Customer Directory
      try {
        var existingCusts = JSON.parse(localStorage.getItem('ss_registered_customers') || '[]');
        var newCust = { name: name, phone: phone, email: email, vip_tier: 'Gold', total_spend: 0, last_visit: new Date().toISOString().slice(0,16).replace('T',' ') };
        existingCusts.unshift(newCust);
        localStorage.setItem('ss_registered_customers', JSON.stringify(existingCusts));
      } catch(err){}

      // Send Serial Monitor Log & sync to PC Backend via ESP32
      try {
        var payloadData = JSON.stringify({ name: name, phone: phone, email: email, discount: discount, code: 'SS' + discount, source: 'wifi_portal' });
        fetch('/api/signin', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: payloadData });
      } catch(err){}
    }

    var scratchState = { isRevealed: false, canvas: null, ctx: null, isMouseDown: false };

    function openCouponModal() {
      var modal = document.getElementById('couponModal'); modal.classList.add('active');
      document.getElementById('revealCode').innerText = 'Code: ' + appState.coupon.code;
      document.getElementById('counterDiscount').innerText = '0% OFF';
      document.getElementById('startShoppingBtn').style.display = 'none';
      document.getElementById('manualRevealBtn').style.display = 'block';
      initScratchCanvas();
    }

    function initScratchCanvas() {
      var canvas = document.getElementById('scratchCanvas'); var ctx = canvas.getContext('2d');
      scratchState.canvas = canvas; scratchState.ctx = ctx; scratchState.isRevealed = false;
      canvas.style.opacity = '1'; canvas.style.pointerEvents = 'auto';

      var grad = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
      grad.addColorStop(0, '#D4AF37'); grad.addColorStop(0.3, '#FFF2B2'); grad.addColorStop(0.7, '#C9A96E'); grad.addColorStop(1, '#AA7C11');
      ctx.fillStyle = grad; ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = '#1A1A1A'; ctx.font = 'bold 15px Inter, sans-serif'; ctx.textAlign = 'center';
      ctx.fillText('SCRATCH TO REVEAL', canvas.width / 2, canvas.height / 2 + 5);

      canvas.onmousedown = function(e) { scratchState.isMouseDown = true; scratch(e); };
      canvas.onmousemove = function(e) { if(scratchState.isMouseDown) scratch(e); };
      window.onmouseup = function() { scratchState.isMouseDown = false; };
      canvas.ontouchstart = function(e) { scratchState.isMouseDown = true; scratch(e.touches[0]); };
      canvas.ontouchmove = function(e) { scratch(e.touches[0]); };
      canvas.ontouchend = function() { scratchState.isMouseDown = false; };
    }

    function scratch(e) {
      if (scratchState.isRevealed) return;
      var rect = scratchState.canvas.getBoundingClientRect(); var x = e.clientX - rect.left; var y = e.clientY - rect.top;
      var ctx = scratchState.ctx; ctx.globalCompositeOperation = 'destination-out';
      ctx.beginPath(); ctx.arc(x, y, 25, 0, Math.PI * 2); ctx.fill(); checkScratchedPercent();
    }

    function checkScratchedPercent() {
      if (scratchState.isRevealed) return;
      var ctx = scratchState.ctx; var imgData = ctx.getImageData(0, 0, scratchState.canvas.width, scratchState.canvas.height);
      var pixels = imgData.data; var clearCount = 0;
      for (var i = 3; i < pixels.length; i += 16) { if (pixels[i] === 0) clearCount++; }
      var percent = clearCount / (pixels.length / 16);
      if (percent > 0.45) triggerReveal();
    }

    function forceRevealCoupon() { if (!scratchState.isRevealed) triggerReveal(); }

    function triggerReveal() {
      scratchState.isRevealed = true; var canvas = scratchState.canvas;
      canvas.style.opacity = '0'; canvas.style.pointerEvents = 'none';
      document.getElementById('manualRevealBtn').style.display = 'none';
      document.getElementById('startShoppingBtn').style.display = 'block';

      var target = appState.coupon.discount; var current = 0; var discountEl = document.getElementById('counterDiscount');
      var timer = setInterval(function() {
        current += 1; discountEl.innerText = current + '% OFF'; discountEl.classList.add('pulse');
        setTimeout(function() { discountEl.classList.remove('pulse'); }, 50);
        if (current >= target) { clearInterval(timer); triggerConfetti(); }
      }, 30);
    }

    function triggerConfetti() {
      var container = document.getElementById('confettiContainer'); container.innerHTML = '';
      var colors = ['#C41E3A', '#D4AF37', '#FFFFFF', '#1A1A1A'];
      for (var i = 0; i < 30; i++) {
        var p = document.createElement('div'); p.className = 'confetti-particle';
        p.style.left = '50%'; p.style.top = '50%';
        p.style.setProperty('--x', ((Math.random() - 0.5) * 260) + 'px');
        p.style.setProperty('--y', ((Math.random() - 0.5) * 260) + 'px');
        p.style.setProperty('--r', (Math.random() * 720) + 'deg');
        p.style.background = colors[Math.floor(Math.random() * colors.length)];
        container.appendChild(p);
      }
    }

    function closeCouponModal() { document.getElementById('couponModal').classList.remove('active'); showView('shopScreen'); initShopView(); }

    function initShopView() {
      var userName = (appState.user && appState.user.name) ? appState.user.name : 'Shopper';
      document.getElementById('userGreeting').innerText = 'Hi ' + userName + '!';
      document.getElementById('bannerCode').innerText = appState.coupon.code;
      document.getElementById('bannerDiscount').innerText = appState.coupon.discount + '% OFF';
      renderCategories(); renderProducts(); updateCartUI();
    }

    function renderCategories() {
      var container = document.getElementById('categoryPills'); container.innerHTML = '';
      CATEGORIES.forEach(function(cat) {
        var btn = document.createElement('button');
        btn.className = 'pill' + (appState.selectedCategory === cat ? ' active' : '');
        btn.innerText = cat;
        btn.onclick = function() { appState.selectedCategory = cat; renderCategories(); renderProducts(); };
        container.appendChild(btn);
      });
    }

    function renderProducts() {
      var container = document.getElementById('productGrid'); container.innerHTML = '';
      var filtered = PRODUCTS.filter(function(p) {
        if (appState.selectedCategory === 'Popular') return POPULAR_IDS.indexOf(p.id) !== -1;
        return p.category === appState.selectedCategory;
      });

      var discPct = appState.coupon ? appState.coupon.discount : 20;
      var codeName = appState.coupon ? appState.coupon.code : 'SS20';

      filtered.forEach(function(p) {
        if (!appState.selectedOptions[p.id]) {
          appState.selectedOptions[p.id] = { size: p.sizes ? p.sizes[0] : null, color: p.colors ? p.colors[0] : null };
        }
        var card = document.createElement('div'); card.className = 'product-card';
        var couponPrice = Math.round(p.price * (1 - discPct / 100));
        var badgeHtml = p.badge ? '<div class="badge">' + p.badge + '</div>' : '';
        var svgArt = getProductSVG(p.id);

        card.innerHTML = 
          '<div class="image-container">' + badgeHtml +
            '<img class="product-img" src="' + p.image + '" alt="' + p.name + '" loading="lazy" onload="this.classList.add(\'loaded\');" onerror="this.style.display=\'none\';">' +
            '<div class="svg-product-art">' + svgArt + '</div>' +
          '</div>' +
          '<div class="product-info">' +
            '<div class="product-brand">SHOPPERS STOP</div>' +
            '<div class="product-name" onclick="openDetailModal(\'' + p.id + '\')">' + p.name + '</div>' +
            '<div class="product-desc">' + p.description + '</div>' +
            '<div class="price-row"><span class="deal-price">&#8377;' + p.price + '</span><span class="mrp-price">&#8377;' + p.mrp + '</span></div>' +
            '<div class="coupon-discount-tag">With ' + codeName + ': &#8377;' + couponPrice + '</div>' +
            '<button class="btn btn-outline add-to-bag-btn" id="btn-add-' + p.id + '" onclick="addToBag(\'' + p.id + '\')">ADD TO BAG</button>' +
          '</div>';

        container.appendChild(card);
      });
    }

    function openDetailModal(productId) {
      var p = PRODUCTS.find(function(item) { return item.id === productId; }); if (!p) return;
      appState.activeDetailItem = p;
      document.getElementById('modalDetailTitle').innerText = p.name;
      document.getElementById('modalDetailDesc').innerText = p.description;
      document.getElementById('modalDetailPrice').innerText = '\u20B9' + p.price;
      document.getElementById('modalDetailMrp').innerText = '\u20B9' + p.mrp;
      document.getElementById('modalDetailHeroImg').src = p.image;
      document.getElementById('modalDetailSvgContainer').innerHTML = getProductSVG(p.id);
      document.getElementById('detailSheetOverlay').classList.add('active');
    }

    function closeDetailModal() { document.getElementById('detailSheetOverlay').classList.remove('active'); }
    function handleDetailOverlayClick(e) { if (e.target.id === 'detailSheetOverlay') closeDetailModal(); }
    function addFromDetailModal() { if (appState.activeDetailItem) { addToBag(appState.activeDetailItem.id); closeDetailModal(); } }

    function addToBag(productId) {
      var prod = PRODUCTS.find(function(p) { return p.id === productId; }); if (!prod) return;
      var existing = appState.cart.find(function(item) { return item.id === productId; });
      if (existing) { existing.qty += 1; } else { appState.cart.push({ id: productId, qty: 1 }); }

      saveLocalStorage(); updateCartUI();
      if (document.getElementById('cartSheetOverlay').classList.contains('active')) { renderCartItems(); renderCartSummary(); }

      var btn = document.getElementById('btn-add-' + productId);
      if (btn) {
        var orig = btn.innerText; btn.innerText = 'Added \u2713'; btn.style.background = 'var(--primary)'; btn.style.color = '#FFFFFF';
        setTimeout(function() { btn.innerText = orig; btn.style.background = ''; btn.style.color = ''; }, 1000);
      }
      var badge = document.getElementById('cartBadgeCount'); badge.classList.add('bump');
      setTimeout(function() { badge.classList.remove('bump'); }, 300);
      showToast(prod.name + ' added to Bag', 'success');
    }

    function calculateCartTotals() {
      var mrpTotal = 0, dealSubtotal = 0, itemCount = 0;
      appState.cart.forEach(function(item) {
        var p = PRODUCTS.find(function(prod) { return prod.id === item.id; });
        if (p) { mrpTotal += p.mrp * item.qty; dealSubtotal += p.price * item.qty; itemCount += item.qty; }
      });
      var discPct = appState.coupon ? appState.coupon.discount : 20;
      var couponVal = Math.round(dealSubtotal * (discPct / 100));
      var discountedSub = dealSubtotal - couponVal;
      var gst = Math.round(discountedSub * 0.05);
      var delivery = (discountedSub >= 999 || itemCount === 0) ? 0 : 49;
      var finalTotal = discountedSub + gst + delivery;
      var totalSavings = (mrpTotal - dealSubtotal) + couponVal;

      return { itemCount: itemCount, mrpTotal: mrpTotal, dealSubtotal: dealSubtotal, couponVal: couponVal, gst: gst, delivery: delivery, finalTotal: finalTotal, totalSavings: totalSavings };
    }

    function updateCartUI() {
      var totals = calculateCartTotals();
      document.getElementById('cartBadgeCount').innerText = totals.itemCount;
      var bar = document.getElementById('floatingCartBar');
      if (totals.itemCount > 0) {
        bar.classList.add('active');
        document.getElementById('barMainText').innerText = totals.itemCount + ' items | \u20B9' + totals.finalTotal.toLocaleString('en-IN');
        document.getElementById('barSavingsText').innerText = 'You save \u20B9' + totals.totalSavings.toLocaleString('en-IN');
      } else { bar.classList.remove('active'); }
    }

    function openCart() {
      var totals = calculateCartTotals();
      if (totals.itemCount === 0) { showToast('Your shopping bag is empty', 'info'); return; }
      renderCartItems(); renderCartSummary();
      document.getElementById('cartSheetOverlay').classList.add('active');
    }

    function closeCart() { document.getElementById('cartSheetOverlay').classList.remove('active'); }
    function handleCartOverlayClick(e) { if (e.target.id === 'cartSheetOverlay') closeCart(); }

    function renderCartItems() {
      var container = document.getElementById('cartItemsList'); container.innerHTML = '';
      appState.cart.forEach(function(item, idx) {
        var p = PRODUCTS.find(function(prod) { return prod.id === item.id; }); if (!p) return;
        var row = document.createElement('div'); row.className = 'cart-item';
        var svgArt = getProductSVG(p.id);

        row.innerHTML = 
          '<div class="cart-item-thumb-container">' +
            '<img src="' + p.image + '" alt="' + p.name + '" style="width:100%; height:100%; object-fit:cover; z-index:2; position:relative;" onload="this.classList.add(\'loaded\');" onerror="this.style.display=\'none\';">' +
            '<div class="svg-product-art">' + svgArt + '</div>' +
          '</div>' +
          '<div class="cart-item-details">' +
            '<div class="cart-item-title">' + p.name + '</div>' +
            '<div class="cart-item-prices">' +
              '<span style="font-weight:700; color:var(--primary); font-family:var(--font-mono);">&#8377;' + p.price + '</span>' +
              '<span style="font-size:11px; color:var(--text-muted); text-decoration:line-through; font-family:var(--font-mono);">&#8377;' + p.mrp + '</span>' +
            '</div>' +
            '<div class="qty-controls">' +
              '<button class="qty-btn" onclick="updateQty(' + idx + ', -1)">-</button>' +
              '<span style="font-weight:700; font-size:13px;">' + item.qty + '</span>' +
              '<button class="qty-btn" onclick="updateQty(' + idx + ', 1)">+</button>' +
              '<button style="margin-left:auto; font-size:12px; color:var(--text-muted); border:none; background:none; cursor:pointer; text-decoration:underline;" onclick="removeCartItem(' + idx + ')">Remove</button>' +
            '</div>' +
          '</div>';
        container.appendChild(row);
      });
    }

    function updateQty(idx, change) {
      if (appState.cart[idx]) {
        appState.cart[idx].qty += change;
        if (appState.cart[idx].qty <= 0) appState.cart.splice(idx, 1);
      }
      saveLocalStorage(); updateCartUI();
      if (appState.cart.length === 0) closeCart(); else { renderCartItems(); renderCartSummary(); }
    }

    function removeCartItem(idx) {
      appState.cart.splice(idx, 1); saveLocalStorage(); updateCartUI();
      if (appState.cart.length === 0) closeCart(); else { renderCartItems(); renderCartSummary(); }
    }

    function renderCartSummary() {
      var totals = calculateCartTotals();
      var codeName = appState.coupon ? appState.coupon.code : 'SS20';
      var discPct = appState.coupon ? appState.coupon.discount : 20;

      document.getElementById('summaryMrp').innerText = '\u20B9' + totals.mrpTotal.toLocaleString('en-IN');
      document.getElementById('summaryDeal').innerText = '\u20B9' + totals.dealSubtotal.toLocaleString('en-IN');
      document.getElementById('summaryCouponLabel').innerText = 'Coupon (' + codeName + ' -' + discPct + '%)';
      document.getElementById('summaryCouponValue').innerText = '-\u20B9' + totals.couponVal.toLocaleString('en-IN');
      document.getElementById('summaryGst').innerText = '\u20B9' + totals.gst.toLocaleString('en-IN');
      document.getElementById('summaryDelivery').innerText = totals.delivery === 0 ? 'FREE' : '\u20B9' + totals.delivery;
      document.getElementById('summaryTotalSavings').innerText = '\u20B9' + totals.totalSavings.toLocaleString('en-IN');
      document.getElementById('summaryFinalTotal').innerText = '\u20B9' + totals.finalTotal.toLocaleString('en-IN');
    }

    function placeOrder() {
      var totals = calculateCartTotals(); if (totals.itemCount === 0) return;
      var orderId = 'SS-' + Math.floor(1000 + Math.random() * 9000);
      var codeName = appState.coupon ? appState.coupon.code : 'SS20';
      document.getElementById('orderIdText').innerText = 'Order ID: ' + orderId;
      document.getElementById('successSavingsText').innerText = 'You saved \u20B9' + totals.totalSavings.toLocaleString('en-IN') + ' with ' + codeName + '!';

      // Update customer total spend in localStorage for Customer Directory
      try {
        var existingCusts = JSON.parse(localStorage.getItem('ss_registered_customers') || '[]');
        if (existingCusts.length > 0 && appState.user) {
          existingCusts[0].total_spend = (existingCusts[0].total_spend || 0) + totals.finalTotal;
          localStorage.setItem('ss_registered_customers', JSON.stringify(existingCusts));
        }
      } catch(err){}

      // Send Serial Monitor Log to ESP32 Hardware
      try {
        fetch('/api/order', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ orderId: orderId, user: appState.user, finalTotal: totals.finalTotal, savings: totals.totalSavings, itemCount: totals.itemCount })
        });
      } catch(err){}

      appState.cart = []; saveLocalStorage(); updateCartUI(); closeCart(); showView('orderSuccessScreen');
    }

    function resetToShop() { showView('shopScreen'); initShopView(); }
    function disconnectWifi() {
      localStorage.clear(); appState.user = null; appState.coupon = { discount: 20, code: 'SS20' }; appState.cart = [];
      showView('signinScreen'); showToast('Disconnected from SHOPPERS_STOP_WiFi', 'info');
    }
  </script>
</body>
</html>
)rawliteral";

void handleRoot() {
  server.sendHeader("Cache-Control", "no-cache, no-store, must-revalidate");
  server.send_P(200, "text/html", portal_html);
}

void forwardCheckinToBackend(String jsonBody) {
#if defined(ESP32)
  HTTPClient http;
  
  // Try 1: BACKEND_HOST
  String url1 = "http://" + String(BACKEND_HOST) + ":" + String(BACKEND_PORT) + "/api/signin";
  http.begin(url1);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(3000);
  int code = http.POST(jsonBody);
  http.end();

  if (code > 0) {
    logPrintln("  [BACKEND SYNC SUCCESS] HTTP " + String(code) + " -> " + url1);
    return;
  }

  // Try 2: Gateway IP (PC Hotspot IP)
  if (WiFi.status() == WL_CONNECTED) {
    String gatewayIP = WiFi.gatewayIP().toString();
    if (gatewayIP != String(BACKEND_HOST) && gatewayIP != "0.0.0.0") {
      String url2 = "http://" + gatewayIP + ":" + String(BACKEND_PORT) + "/api/signin";
      http.begin(url2);
      http.addHeader("Content-Type", "application/json");
      http.setTimeout(3000);
      int code2 = http.POST(jsonBody);
      http.end();
      if (code2 > 0) {
        logPrintln("  [BACKEND SYNC SUCCESS VIA GATEWAY] HTTP " + String(code2) + " -> " + url2);
        return;
      }
    }
  }

  logPrintln("  [BACKEND SYNC FAILED] Could not reach PC on " + String(BACKEND_HOST) + " or Gateway IP");
#endif
}

void handleApiSignin() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  if (server.hasArg("plain")) {
    String body = server.arg("plain");
    logPrintln("\n==========================================");
    logPrintln("  [LOGIN LOG] NEW USER SIGNED IN TO PORTAL!");
    logPrintln("==========================================");
    logPrint("User Data: ");
    logPrintln(body);
    logPrintln("==========================================\n");

    String name = ""; String phone = ""; String email = "";
    int nameIdx = body.indexOf("\"name\":\"");
    if (nameIdx != -1) {
      int endIdx = body.indexOf("\"", nameIdx + 8);
      if (endIdx != -1) name = body.substring(nameIdx + 8, endIdx);
    }
    int phoneIdx = body.indexOf("\"phone\":\"");
    if (phoneIdx != -1) {
      int endIdx = body.indexOf("\"", phoneIdx + 9);
      if (endIdx != -1) phone = body.substring(phoneIdx + 9, endIdx);
    }
    int emailIdx = body.indexOf("\"email\":\"");
    if (emailIdx != -1) {
      int endIdx = body.indexOf("\"", emailIdx + 9);
      if (endIdx != -1) email = body.substring(emailIdx + 9, endIdx);
    }

    if (name.length() > 0 && customerCount < MAX_CUSTOMERS) {
      for (int i = customerCount; i > 0; i--) {
        customerList[i] = customerList[i - 1];
      }
      customerList[0].name = name;
      customerList[0].phone = phone;
      customerList[0].email = email;
      customerList[0].vipTier = "Gold";
      customerList[0].totalSpend = 0;
      customerList[0].lastVisit = "2026-07-26 11:45";
      customerCount++;
    }

    // Forward check-in to FastAPI backend on PC
    forwardCheckinToBackend(body);
  }
  server.send(200, "application/json", "{\"status\":\"ok\"}");
}

void handleGetCustomers() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  String json = "[";
  for (int i = 0; i < customerCount; i++) {
    json += "{\"name\":\"" + customerList[i].name + "\",\"phone\":\"" + customerList[i].phone + "\",\"email\":\"" + customerList[i].email + "\",\"vip_tier\":\"" + customerList[i].vipTier + "\",\"total_spend\":" + String(customerList[i].totalSpend) + ",\"last_visit\":\"" + customerList[i].lastVisit + "\"}";
    if (i < customerCount - 1) json += ",";
  }
  json += "]";
  server.send(200, "application/json", json);
}

void handleApiOrder() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  if (server.hasArg("plain")) {
    String body = server.arg("plain");
    logPrintln("\n==========================================");
    logPrintln("  [ORDER LOG] NEW ORDER PLACED!");
    logPrintln("==========================================");
    logPrint("Order Details: ");
    logPrintln(body);
    logPrintln("==========================================\n");
  }
  server.send(200, "application/json", "{\"status\":\"ok\"}");
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  logPrintln("\n=============================================");
  logPrintln("  SHOPPERS STOP Captive Portal — AXIONIK");
  logPrintln("=============================================");
  logPrintln("Status: AP+STA Dual Mode Online");

  IPAddress local_IP(192, 168, 4, 1);
  IPAddress gateway(192, 168, 4, 1);
  IPAddress subnet(255, 255, 255, 0);

  WiFi.mode(WIFI_AP_STA);
  WiFi.softAPConfig(local_IP, gateway, subnet);

  if (WiFi.softAP("SHOPPERS_STOP_WiFi", "", 1, 0, 8)) {
    logPrintln("AP Name: SHOPPERS_STOP_WiFi");
    logPrint("AP IP: ");
    logPrintln(WiFi.softAPIP().toString());
  } else {
    logPrintln("AP Setup Failed!");
  }

  // Connect to main WiFi so ESP32 can forward checkins to PC at BACKEND_HOST
  if (String(STORE_WIFI_SSID).length() > 0 && String(STORE_WIFI_SSID) != "SHOPPERS_STOP_WiFi") {
    logPrintln("Connecting to Main WiFi: " + String(STORE_WIFI_SSID));
    WiFi.begin(STORE_WIFI_SSID, STORE_WIFI_PASSWORD);
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
      delay(500);
      Serial.print(".");
      attempts++;
    }
    if (WiFi.status() == WL_CONNECTED) {
      logPrintln("\nConnected to Main WiFi! STA IP: " + WiFi.localIP().toString());
    } else {
      logPrintln("\nMain WiFi not connected (running AP standalone)");
    }
  }

  dnsServer.setErrorReplyCode(DNSReplyCode::NoError);
  dnsServer.start(53, "*", local_IP);

  server.on("/", HTTP_GET, handleRoot);
  server.on("/api/signin", HTTP_POST, handleApiSignin);
  server.on("/api/customers", HTTP_GET, handleGetCustomers);
  server.on("/api/order", HTTP_POST, handleApiOrder);
  server.on("/generate_204", HTTP_GET, handleRoot);
  server.on("/hotspot-detect.html", HTTP_GET, handleRoot);
  server.on("/connectivity-check.html", HTTP_GET, handleRoot);
  server.on("/ncsi.txt", HTTP_GET, [](){ server.send(200, "text/plain", "Microsoft NCSI"); });
  server.onNotFound(handleRoot);

  server.begin();
  logPrintln("HTTP Server: Started (Listening on port 80)");
  logPrintln("=============================================\n");
}

void loop() {
  dnsServer.processNextRequest();
  server.handleClient();
  delay(5);

  if (millis() - lastHeartbeat > 3000) {
    lastHeartbeat = millis();
    logPrintln("[ESP32 OK] SHOPPERS_STOP_WiFi running... Waiting for user sign-in");
  }
}
