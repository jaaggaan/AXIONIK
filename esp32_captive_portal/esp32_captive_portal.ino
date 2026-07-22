#include <WiFi.h>
#include <WebServer.h>
#include <DNSServer.h>

// ====== CONFIGURATION ======
const char* ssid = "AXIONIK";
const char* password = "12345678";
const byte DNS_PORT = 53;
IPAddress apIP(192, 168, 4, 1);

// ====== GLOBALS ======
WebServer server(80);
DNSServer dnsServer;

// ====== CAPTIVE PORTAL HTML ======
// Complete CRAV BISTRO ordering site — sign-in, menu, cart, checkout
const char portal_html[] PROGMEM = R"rawliteral(<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>CRAV BISTRO - AXIONIK WiFi</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{height:100%;overflow:hidden;font-family:'Sora',system-ui,sans-serif;background:#f6f2e9}
::-webkit-scrollbar{width:6px}
::-webkit-scrollbar-track{background:#fdfbf7;border-left:2px solid #1c1e19}
::-webkit-scrollbar-thumb{background:#1c1e19;border:1px solid #fdfbf7;border-radius:3px}
#app{max-width:480px;height:100vh;margin:0 auto;background:#fdfbf7;border-left:3px solid #1c1e19;border-right:3px solid #1c1e19;display:flex;flex-direction:column;position:relative;overflow:hidden}
.header{background:#cb4b31;border-bottom:3px solid #1c1e19;padding:12px 16px;text-align:center;position:relative;z-index:30;flex-shrink:0}
.header-brand{display:flex;align-items:center;justify-content:center;gap:8px}
.header-logo{width:36px;height:36px;background:#faf5eb;border:2px solid #1c1e19;border-radius:10px;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:18px;color:#cb4b31;transform:rotate(-3deg);box-shadow:2px 2px 0 #1c1e19}
.header-title{font-size:20px;font-weight:900;color:#faf5eb;letter-spacing:-0.5px;text-transform:uppercase;font-style:italic}
.header-badge{font-size:8px;background:#dd9d47;color:#1c1e19;font-weight:900;padding:2px 6px;border-radius:6px;border:2px solid #1c1e19;text-transform:uppercase;letter-spacing:1px;transform:rotate(2deg);box-shadow:2px 2px 0 #1c1e19}
.header-sub{font-size:8px;color:#faf5eb;font-weight:800;letter-spacing:2px;margin-top:4px;text-transform:uppercase;opacity:0.9}
.marquee{background:#dd9d47;border-bottom:3px solid #1c1e19;padding:6px 0;overflow:hidden;white-space:nowrap;position:relative;z-index:20;flex-shrink:0}
.marquee-inner{display:inline-flex;gap:32px;animation:marquee 20s linear infinite;font-size:9px;font-weight:900;color:#1c1e19;text-transform:uppercase;letter-spacing:1px}
@keyframes marquee{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
.main{flex:1;overflow-y:auto;overflow-x:hidden;position:relative;background:#fdfbf7}
.main::before{content:'';position:absolute;inset:0;background-image:linear-gradient(to right,rgba(28,30,25,0.03) 1px,transparent 1px),linear-gradient(to bottom,rgba(28,30,25,0.03) 1px,transparent 1px);background-size:30px 30px;pointer-events:none;z-index:0}
.toast{position:absolute;top:12px;left:50%;transform:translateX(-50%) translateY(-80px);background:#1c1e19;color:#fff;font-size:10px;font-weight:900;padding:10px 16px;border-radius:12px;border:2px solid #1c1e19;box-shadow:4px 4px 0 #1c1e19;z-index:100;display:flex;align-items:center;gap:6px;white-space:nowrap;opacity:0;transition:all 0.3s ease;pointer-events:none}
.toast.show{transform:translateX(-50%) translateY(0);opacity:1}
.toast-emoji{font-size:14px}
.card{background:#faf5eb;border:3px solid #1c1e19;border-radius:24px;padding:20px;position:relative;overflow:hidden;box-shadow:4px 4px 0 #1c1e19;margin:16px}
.card::before{content:'';position:absolute;top:0;right:0;width:120px;height:120px;background:rgba(221,157,71,0.08);border-radius:50%;filter:blur(20px);pointer-events:none}
.stamp{position:absolute;top:-8px;right:-8px;width:64px;height:64px;background:#dd9d47;border:3px solid #1c1e19;border-radius:50%;display:flex;align-items:center;justify-content:center;box-shadow:2px 2px 0 #1c1e19;transform:rotate(12deg);z-index:5;pointer-events:none}
.stamp-inner{width:52px;height:52px;border:1px dashed #1c1e19;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-direction:column}
.stamp-text{font-size:7px;font-weight:900;color:#1c1e19;text-align:center;line-height:1.2;text-transform:uppercase;letter-spacing:1px}
.form-title{text-align:center;margin-bottom:16px;position:relative}
.form-emoji{width:48px;height:48px;background:#faf5eb;border:3px solid #1c1e19;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:24px;margin:0 auto 8px;box-shadow:2px 2px 0 #1c1e19;transform:rotate(-3deg);animation:stickerWiggle 4s ease-in-out infinite}
@keyframes stickerWiggle{0%,100%{transform:rotate(-3deg)}50%{transform:rotate(3deg)}}
.form-heading{font-size:22px;font-weight:900;color:#1c1e19;line-height:1.1;text-transform:uppercase;font-style:italic;letter-spacing:-0.5px}
.form-heading span{color:#cb4b31}
.form-sub{font-size:9px;color:#606356;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-top:4px}
.input-group{margin-bottom:12px}
.input-label{display:block;font-size:9px;font-weight:900;color:#1c1e19;margin-bottom:4px;text-transform:uppercase;letter-spacing:1.5px}
.input-label .req{color:#cb4b31}
.input-wrap{position:relative}
.input-icon{position:absolute;left:12px;top:50%;transform:translateY(-50%);font-size:14px;color:#1c1e19;z-index:2}
.input-prefix{position:absolute;left:12px;top:50%;transform:translateY(-50%);font-size:11px;font-weight:900;color:#cb4b31;border-right:2px solid #1c1e19;padding-right:8px;font-family:'JetBrains Mono',monospace;z-index:2}
.input-field{width:100%;background:#fff;border:3px solid #1c1e19;border-radius:12px;padding:12px 12px 12px 40px;font-size:12px;font-weight:700;color:#1c1e19;font-family:'Sora',sans-serif;box-shadow:2px 2px 0 #1c1e19;transition:all 0.2s ease;outline:none}
.input-field:focus{transform:translateY(-2px);box-shadow:4px 4px 0 #1c1e19;background:#fff}
.input-field::placeholder{color:#9c9a8f;font-weight:600}
.input-field.phone{padding-left:52px}
.error{background:#fef2f2;border:2px solid #1c1e19;border-radius:10px;padding:10px 12px;font-size:10px;color:#dc2626;font-weight:800;display:flex;align-items:center;gap:6px;margin-bottom:12px;box-shadow:2px 2px 0 #1c1e19}
.consent{display:flex;gap:8px;align-items:flex-start;margin:16px 0;cursor:pointer}
.consent input{width:16px;height:16px;accent-color:#cb4b31;margin-top:1px;flex-shrink:0;cursor:pointer}
.consent-text{font-size:9px;color:#606356;font-weight:700;line-height:1.5;text-transform:uppercase;letter-spacing:0.5px}
.btn{width:100%;background:#dd9d47;color:#1c1e19;border:3px solid #1c1e19;border-radius:12px;padding:14px;font-size:11px;font-weight:900;text-transform:uppercase;letter-spacing:1px;cursor:pointer;box-shadow:4px 4px 0 #1c1e19;transition:all 0.15s ease;display:flex;align-items:center;justify-content:center;gap:6px;font-family:'Sora',sans-serif}
.btn:hover{transform:translateY(-2px);box-shadow:6px 6px 0 #1c1e19}
.btn:active{transform:translateY(2px);box-shadow:0 0 0 #1c1e19}
.btn:disabled{opacity:0.7;cursor:not-allowed}
.btn-primary{background:#cb4b31;color:#fff}
.btn-ghost{background:#faf5eb;color:#1c1e19;border:2px solid #1c1e19;box-shadow:2px 2px 0 #1c1e19}
.btn-ghost:hover{box-shadow:4px 4px 0 #1c1e19}
.btn-red{background:#fef2f2;color:#dc2626;border:2px solid #1c1e19}
.menu-header{background:#faf5eb;border-bottom:3px solid #1c1e19;padding:12px 16px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:20;flex-shrink:0}
.menu-header-left{flex:1}
.menu-status{font-size:8px;color:#cb4b31;font-weight:900;text-transform:uppercase;letter-spacing:2px;display:flex;align-items:center;gap:4px}
.menu-status::before{content:'';width:6px;height:6px;background:#10b981;border-radius:50%;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.3}}
.menu-greeting{font-size:13px;font-weight:900;color:#1c1e19;margin-top:2px;text-transform:uppercase;font-style:italic}
.menu-greeting span{color:#cb4b31}
.menu-header-right{display:flex;align-items:center;gap:8px}
.menu-table{background:#faf5eb;border:2px solid #1c1e19;padding:4px 10px;border-radius:10px;font-size:9px;font-weight:900;color:#cb4b31;letter-spacing:1px;box-shadow:2px 2px 0 #1c1e19;transform:rotate(-1deg)}
.menu-exit{background:#fef2f2;border:2px solid #1c1e19;padding:6px 10px;border-radius:10px;font-size:9px;font-weight:900;color:#dc2626;cursor:pointer;box-shadow:2px 2px 0 #1c1e19;transition:all 0.15s ease;display:flex;align-items:center;gap:4px}
.menu-exit:hover{transform:translateY(-1px);box-shadow:3px 3px 0 #1c1e19}
.menu-exit:active{transform:translateY(1px);box-shadow:0 0 0 #1c1e19}
.categories{display:flex;gap:8px;overflow-x:auto;padding:12px 16px;background:#faf5eb;border-bottom:3px solid #1c1e19;scrollbar-width:none;position:sticky;top:0;z-index:15;flex-shrink:0}
.categories::-webkit-scrollbar{display:none}
.cat-btn{flex-shrink:0;padding:8px 16px;border-radius:10px;font-size:10px;font-weight:900;text-transform:uppercase;letter-spacing:1px;cursor:pointer;border:2px solid #1c1e19;box-shadow:2px 2px 0 #1c1e19;transition:all 0.15s ease;font-family:'Sora',sans-serif;background:#fff;color:#1c1e19}
.cat-btn:hover{transform:translateY(-1px);box-shadow:3px 3px 0 #1c1e19}
.cat-btn.active{background:#cb4b31;color:#faf5eb;box-shadow:none;transform:translate(1px,1px)}
.crave-card{background:#faf5eb;border:3px solid #1c1e19;border-radius:20px;padding:16px;margin:12px 16px;box-shadow:4px 4px 0 #1c1e19;position:relative;overflow:hidden}
.crave-badge{display:inline-block;background:#cb4b31;color:#faf5eb;font-size:8px;font-weight:900;padding:2px 8px;border-radius:6px;border:2px solid #1c1e19;text-transform:uppercase;letter-spacing:1px}
.crave-title{font-size:12px;font-weight:900;color:#1c1e19;margin-top:8px;text-transform:uppercase;font-style:italic}
.crave-title span{color:#cb4b31}
.crave-desc{font-size:9px;color:#606356;font-weight:700;margin-top:4px;text-transform:uppercase;letter-spacing:0.5px;line-height:1.4}
.crave-bar{width:100%;background:#fff;border:2px solid #1c1e19;height:18px;border-radius:10px;margin-top:10px;overflow:hidden;padding:2px;box-shadow:inset 1px 1px 3px rgba(0,0,0,0.1)}
.crave-fill{height:100%;background:linear-gradient(90deg,#dd9d47,#cb4b31);border-radius:8px;transition:width 0.5s ease;position:relative}
.crave-fill::after{content:'';position:absolute;inset:0;background:repeating-linear-gradient(45deg,rgba(255,255,255,0.2) 0,rgba(255,255,255,0.2) 6px,transparent 6px,transparent 12px);animation:slideStripes 1s linear infinite}
@keyframes slideStripes{0%{background-position:0 0}100%{background-position:12px 0}}
.crave-btn{background:#dd9d47;color:#1c1e19;border:2px solid #1c1e19;border-radius:10px;padding:8px 14px;font-size:9px;font-weight:900;text-transform:uppercase;letter-spacing:1px;cursor:pointer;box-shadow:2px 2px 0 #1c1e19;margin-top:10px;transition:all 0.15s ease;font-family:'Sora',sans-serif;display:inline-flex;align-items:center;gap:4px}
.crave-btn:hover{transform:translateY(-1px);box-shadow:3px 3px 0 #1c1e19}
.crave-btn:active{transform:translateY(1px);box-shadow:0 0 0 #1c1e19}
.burst-container{position:absolute;inset:0;pointer-events:none;overflow:hidden;z-index:5}
.burst{position:absolute;bottom:20px;left:50%;font-size:20px;animation:burstUp 0.8s ease-out forwards;pointer-events:none}
@keyframes burstUp{0%{opacity:1;transform:translate(-50%,0) scale(0.5)}100%{opacity:0;transform:translate(var(--tx),var(--ty)) scale(1.5) rotate(360deg)}}
.menu-grid{padding:12px 16px 100px;display:grid;grid-template-columns:1fr;gap:12px}
@media(min-width:400px){.menu-grid{grid-template-columns:1fr 1fr}}
.menu-item{background:#fff;border:3px solid #1c1e19;border-radius:16px;padding:14px;display:flex;gap:12px;position:relative;box-shadow:3px 3px 0 #1c1e19;transition:all 0.2s ease;cursor:default}
.menu-item:hover{transform:translateY(-2px);box-shadow:5px 5px 0 #1c1e19}
.menu-item:active{transform:translateY(1px);box-shadow:1px 1px 0 #1c1e19}
.item-badge{position:absolute;top:-6px;right:10px;background:#dd9d47;color:#1c1e19;font-size:7px;font-weight:900;padding:2px 6px;border-radius:5px;border:2px solid #1c1e19;text-transform:uppercase;letter-spacing:0.5px;box-shadow:1px 1px 0 #1c1e19;transform:rotate(-2deg);z-index:2}
.item-badge.red{background:#cb4b31;color:#faf5eb}
.item-badge.green{background:#d1fae5;color:#065f46;border-color:#1c1e19}
.item-badge.orange{background:#ffedd5;color:#9a3412;border-color:#1c1e19}
.item-badge.blue{background:#dbeafe;color:#1e40af;border-color:#1c1e19}
.item-emoji{width:52px;height:52px;background:#faf5eb;border:3px solid #1c1e19;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:28px;flex-shrink:0;box-shadow:2px 2px 0 #1c1e19}
.item-info{flex:1;min-width:0}
.item-name{font-size:12px;font-weight:900;color:#1c1e19;text-transform:uppercase;font-style:italic;line-height:1.2;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.item-desc{font-size:9px;color:#606356;font-weight:700;margin-top:3px;line-height:1.4;text-transform:uppercase;letter-spacing:0.3px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.item-sizes{display:flex;gap:4px;margin-top:6px}
.size-btn{padding:3px 8px;border-radius:6px;font-size:8px;font-weight:900;text-transform:uppercase;letter-spacing:0.5px;cursor:pointer;border:2px solid #1c1e19;box-shadow:1px 1px 0 #1c1e19;transition:all 0.1s ease;font-family:'Sora',sans-serif;background:#faf5eb;color:#1c1e19}
.size-btn:hover{transform:translateY(-1px)}
.size-btn.active{background:#cb4b31;color:#faf5eb;box-shadow:none;transform:translate(1px,1px)}
.item-footer{display:flex;align-items:center;justify-content:space-between;margin-top:8px;padding-top:6px;border-top:2px dashed rgba(28,30,25,0.1)}
.item-price{font-size:14px;font-weight:900;color:#cb4b31;font-family:'JetBrains Mono',monospace;letter-spacing:-0.5px}
.item-add{background:#dd9d47;color:#1c1e19;border:2px solid #1c1e19;border-radius:8px;padding:5px 10px;font-size:9px;font-weight:900;text-transform:uppercase;letter-spacing:0.5px;cursor:pointer;box-shadow:2px 2px 0 #1c1e19;transition:all 0.15s ease;display:flex;align-items:center;gap:3px;font-family:'Sora',sans-serif}
.item-add:hover{transform:translateY(-1px);box-shadow:3px 3px 0 #1c1e19}
.item-add:active{transform:translateY(1px);box-shadow:0 0 0 #1c1e19}
.cart-bar{position:absolute;bottom:16px;left:16px;right:16px;height:60px;background:#1c1e19;border:3px solid #1c1e19;border-radius:16px;z-index:30;box-shadow:4px 4px 0 rgba(28,30,25,0.3);display:flex;align-items:center;justify-content:space-between;padding:0 16px;cursor:pointer;transition:all 0.2s ease}
.cart-bar:hover{transform:translateY(-2px);box-shadow:6px 6px 0 rgba(28,30,25,0.3)}
.cart-bar:active{transform:translateY(1px)}
.cart-info{flex:1}
.cart-label{font-size:8px;color:#dd9d47;font-weight:900;text-transform:uppercase;letter-spacing:2px}
.cart-count{font-size:11px;font-weight:900;color:#faf5eb;margin-top:1px}
.cart-count span{color:#dd9d47;font-family:'JetBrains Mono',monospace}
.cart-btn{background:#cb4b31;color:#faf5eb;border:2px solid #1c1e19;border-radius:10px;padding:8px 14px;font-size:9px;font-weight:900;text-transform:uppercase;letter-spacing:1px;box-shadow:2px 2px 0 #1c1e19;transition:all 0.15s ease;display:flex;align-items:center;gap:4px;font-family:'Sora',sans-serif;cursor:pointer}
.cart-btn:hover{transform:translateY(-1px);box-shadow:3px 3px 0 #1c1e19}
.cart-btn:active{transform:translateY(1px);box-shadow:0 0 0 #1c1e19}
.modal-overlay{position:absolute;inset:0;background:rgba(0,0,0,0.6);z-index:50;opacity:0;pointer-events:none;transition:opacity 0.3s ease}
.modal-overlay.show{opacity:1;pointer-events:auto}
.cart-sheet{position:absolute;bottom:0;left:0;right:0;max-height:85%;background:#faf5eb;border-top:4px solid #1c1e19;border-left:4px solid #1c1e19;border-right:4px solid #1c1e19;border-radius:24px 24px 0 0;z-index:60;transform:translateY(100%);transition:transform 0.3s cubic-bezier(0.25,1,0.5,1);display:flex;flex-direction:column;overflow:hidden}
.cart-sheet.show{transform:translateY(0)}
.cart-header{padding:16px 20px;background:#fff;border-bottom:3px solid #1c1e19;display:flex;align-items:center;justify-content:space-between;flex-shrink:0}
.cart-header-title{display:flex;align-items:center;gap:8px;font-size:12px;font-weight:900;color:#1c1e19;text-transform:uppercase;font-style:italic}
.cart-close{width:32px;height:32px;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:900;color:#1c1e19;border:2px solid #1c1e19;border-radius:10px;background:#faf5eb;cursor:pointer;box-shadow:2px 2px 0 #1c1e19;transition:all 0.1s ease}
.cart-close:hover{background:#fef2f2;color:#cb4b31}
.cart-items{flex:1;overflow-y:auto;padding:16px 20px;background:#fdfbf7}
.cart-item{display:flex;align-items:center;justify-content:space-between;padding:12px 0;border-bottom:2px dashed rgba(28,30,25,0.1)}
.cart-item:last-child{border-bottom:none}
.cart-item-left{flex:1;min-width:0;padding-right:12px}
.cart-item-top{display:flex;align-items:center;gap:6px}
.cart-item-emoji{font-size:20px}
.cart-item-name{font-size:11px;font-weight:900;color:#1c1e19;text-transform:uppercase;font-style:italic;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.cart-item-size{display:inline-block;background:#cb4b31;color:#faf5eb;font-size:7px;font-weight:900;padding:1px 5px;border-radius:4px;border:1px solid #1c1e19;margin-top:3px;text-transform:uppercase;letter-spacing:0.5px;box-shadow:1px 1px 0 #1c1e19}
.cart-item-price{font-size:9px;color:#606356;font-weight:700;margin-top:2px;font-family:'JetBrains Mono',monospace}
.cart-qty{display:flex;align-items:center;gap:6px;flex-shrink:0}
.qty-btn{width:24px;height:24px;display:flex;align-items:center;justify-content:center;background:#fff;border:2px solid #1c1e19;border-radius:6px;font-size:12px;font-weight:900;color:#1c1e19;cursor:pointer;box-shadow:1px 1px 0 #1c1e19;transition:all 0.1s ease;font-family:'Sora',sans-serif}
.qty-btn:hover{color:#cb4b31}
.qty-btn:active{transform:translateY(1px);box-shadow:0 0 0 #1c1e19}
.qty-val{width:20px;text-align:center;font-size:11px;font-weight:900;color:#1c1e19;font-family:'JetBrains Mono',monospace}
.cart-del{width:28px;height:28px;display:flex;align-items:center;justify-content:center;background:#fef2f2;border:2px solid #1c1e19;border-radius:8px;color:#dc2626;cursor:pointer;box-shadow:1px 1px 0 #1c1e19;transition:all 0.1s ease;margin-left:6px;font-size:12px}
.cart-del:hover{background:#dc2626;color:#fff}
.cart-footer{padding:16px 20px;background:#fff;border-top:3px solid #1c1e19;flex-shrink:0}
.cart-row{display:flex;justify-content:space-between;font-size:9px;font-weight:700;color:#606356;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px}
.cart-row.total{font-size:13px;font-weight:900;color:#1c1e19;border-top:2px dashed rgba(28,30,25,0.2);padding-top:8px;margin-top:8px;text-transform:uppercase}
.cart-row.total span{color:#cb4b31;font-family:'JetBrains Mono',monospace;font-size:15px}
.cart-actions{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:12px}
.success-card{background:#fff;border:3px solid #1c1e19;border-radius:24px;padding:24px 20px;text-align:center;box-shadow:4px 4px 0 #1c1e19;margin:16px;position:relative;overflow:hidden}
.success-icon{width:56px;height:56px;background:#faf5eb;border:3px solid #1c1e19;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 12px;font-size:24px;box-shadow:2px 2px 0 #1c1e19;transform:rotate(-3deg)}
.success-title{font-size:18px;font-weight:900;color:#1c1e19;text-transform:uppercase;font-style:italic;letter-spacing:-0.5px}
.success-badge{display:inline-block;background:#dd9d47;color:#1c1e19;font-size:8px;font-weight:900;padding:3px 10px;border-radius:6px;border:2px solid #1c1e19;margin-top:8px;text-transform:uppercase;letter-spacing:1px;box-shadow:2px 2px 0 #1c1e19;transform:rotate(1deg)}
.receipt{background:#faf5eb;border:3px solid #1c1e19;border-radius:16px;padding:16px;margin:16px 0;text-align:left;box-shadow:2px 2px 0 #1c1e19}
.receipt-row{display:flex;justify-content:space-between;font-size:10px;padding:6px 0;border-bottom:1px dashed rgba(28,30,25,0.15)}
.receipt-row:last-child{border-bottom:none}
.receipt-label{color:#606356;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;font-size:9px}
.receipt-val{color:#1c1e19;font-weight:900;font-family:'JetBrains Mono',monospace}
.receipt-val.red{color:#cb4b31;font-size:13px}
.receipt-items{margin:8px 0;padding:8px 0;border-top:2px dashed rgba(28,30,25,0.15);border-bottom:2px dashed rgba(28,30,25,0.15)}
.receipt-item{display:flex;justify-content:space-between;font-size:10px;padding:4px 0}
.receipt-item span{font-weight:700;color:#1c1e19}
.receipt-item span.qty{color:#cb4b31;font-weight:900}
.receipt-total{display:flex;justify-content:space-between;font-size:12px;font-weight:900;color:#1c1e19;padding-top:8px;border-top:3px double #1c1e19;text-transform:uppercase}
.receipt-total span{color:#cb4b31;font-family:'JetBrains Mono',monospace;font-size:16px}
.success-note{font-size:9px;color:#606356;font-weight:700;line-height:1.5;text-transform:uppercase;letter-spacing:0.5px;margin-top:12px}
.success-note strong{color:#cb4b31;font-family:'JetBrains Mono',monospace}
.success-btns > * + *{margin-top:8px}
.footer{background:#fff;border-top:3px solid #1c1e19;padding:16px;text-align:center;flex-shrink:0}
.footer-text{font-size:8px;color:#606356;font-weight:800;text-transform:uppercase;letter-spacing:1px;line-height:1.5}
.footer-badge{display:inline-block;background:#dd9d47;color:#1c1e19;font-size:8px;font-weight:900;padding:2px 8px;border-radius:4px;border:2px solid #1c1e19;margin-top:6px;text-transform:uppercase;letter-spacing:2px;box-shadow:2px 2px 0 #1c1e19;font-family:'JetBrains Mono',monospace}
.view{display:none}
.view.active{display:block}
@keyframes fadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.fade-in{animation:fadeIn 0.3s ease forwards}
@keyframes scaleIn{from{transform:scale(0)}50%{transform:scale(1.1)}to{transform:scale(1)}}
.scale-in{animation:scaleIn 0.4s ease forwards}
.spinner{width:16px;height:16px;border:2px solid rgba(28,30,25,0.2);border-top-color:#1c1e19;border-radius:50%;animation:spin 0.8s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
</style>
</head>
<body>
<div id="app">
<div class="header"><div class="header-brand"><div class="header-logo">C</div><div class="header-title">CRAV BISTRO</div><div class="header-badge">WiFi</div></div><div class="header-sub">★ LOCAL CRAVINGS • INSTANTLY CONNECTED BY AXIONIK ★</div></div>
<div class="marquee"><div class="marquee-inner"><span>★ UNLIMITED HIGH-SPEED WIFI</span><span>★ BURGERS CRAVED CONSTANTLY</span><span>★ ORDER FRESH SEARING BURGERS & SIDES</span><span>★ CRUNCHY GOLDEN FRIES</span><span>★ ZERO LAG • PURE CRUNCH</span><span>★ CRAV BISTRO EXPERIENCE</span><span>★ UNLIMITED HIGH-SPEED WIFI</span><span>★ BURGERS CRAVED CONSTANTLY</span><span>★ ORDER FRESH SEARING BURGERS & SIDES</span><span>★ CRUNCHY GOLDEN FRIES</span><span>★ ZERO LAG • PURE CRUNCH</span><span>★ CRAV BISTRO EXPERIENCE</span></div></div>
<div class="toast" id="toast"><span class="toast-emoji" id="toastEmoji">🍔</span><span id="toastText">Welcome!</span></div>
<div class="main" id="mainContent">
<div class="view active" id="viewSignin"><div class="card fade-in"><div class="stamp"><div class="stamp-inner"><div class="stamp-text">★ FRESH<br/>GUARANTEED ★</div></div></div><div class="form-title"><div class="form-emoji">🍟</div><h2 class="form-heading">CRAVING<br/><span>HIGH-SPEED</span><br/>WIFI?</h2><p class="form-sub">Connect to Free WiFi & Order Instantly!</p></div><div class="error" id="formError" style="display:none"><span>⚠️</span><span id="errorText">Error</span></div><form id="signinForm" onsubmit="return false"><div class="input-group"><label class="input-label">Your Full Name <span class="req">*</span></label><div class="input-wrap"><span class="input-icon">👤</span><input type="text" class="input-field" id="inputName" placeholder="Enter your name" autocomplete="name"></div></div><div class="input-group"><label class="input-label">Mobile Phone <span class="req">*</span></label><div class="input-wrap"><span class="input-prefix">+91</span><input type="tel" class="input-field phone" id="inputPhone" maxlength="10" placeholder="Enter 10-digit number" autocomplete="tel"></div></div><div class="input-group"><label class="input-label">Email Address <span style="color:#606356;font-weight:600">(Optional)</span></label><div class="input-wrap"><span class="input-icon">✉️</span><input type="email" class="input-field" id="inputEmail" placeholder="you@example.com" autocomplete="email"></div></div><label class="consent"><input type="checkbox" id="inputConsent" checked><span class="consent-text">I agree to terms of service and consent to receive digital dining notifications & bill receipts.</span></label><button type="submit" class="btn" id="btnSubmit" onclick="handleSignin()"><span id="btnSubmitText">AGREE & CONNECT NOW →</span><span id="btnSubmitLoading" style="display:none"><span class="spinner"></span></span></button></form></div></div>
<div class="view" id="viewMenu"><div class="menu-header"><div class="menu-header-left"><div class="menu-status">CRAV BISTRO STATION</div><div class="menu-greeting">Hello, <span id="menuUserName">Guest</span>! 👋</div></div><div class="menu-header-right"><div class="menu-table">TABLE <span id="menuTableNum">15</span></div><button class="menu-exit" onclick="handleDisconnect()">← Exit</button></div></div><div class="categories" id="categories"><button class="cat-btn active" data-cat="Popular" onclick="setCategory('Popular')">Popular</button><button class="cat-btn" data-cat="Burgers" onclick="setCategory('Burgers')">Burgers</button><button class="cat-btn" data-cat="Sides" onclick="setCategory('Sides')">Sides</button><button class="cat-btn" data-cat="Drinks" onclick="setCategory('Drinks')">Drinks</button><button class="cat-btn" data-cat="Desserts" onclick="setCategory('Desserts')">Desserts</button></div><div class="crave-card"><div class="burst-container" id="burstContainer"></div><span class="crave-badge">🔥 CRAV-O-METER</span><h4 class="crave-title">CRAVING LEVEL: <span id="cravePercent">30%</span></h4><p class="crave-desc" id="craveDesc">Tap the boost button to fire up your cravings and unlock a 10% promo!</p><div class="crave-bar"><div class="crave-fill" id="craveFill" style="width:30%"></div></div><button class="crave-btn" onclick="boostCrave()"><span>BOOST CRAVING</span><span style="font-size:12px">🔥</span></button></div><div class="menu-grid" id="menuGrid"></div></div>
<div class="view" id="viewSuccess"><div class="success-card scale-in"><div class="success-icon">✅</div><h2 class="success-title">ORDER PLACED! 🎉</h2><div class="success-badge">Pay at Counter</div><div class="receipt"><div class="receipt-row"><span class="receipt-label">Order Reference:</span><span class="receipt-val red" id="successOrderId">AX-7842</span></div><div class="receipt-row"><span class="receipt-label">Table Number:</span><span class="receipt-val">Table <span id="successTable">15</span></span></div><div class="receipt-row"><span class="receipt-label">Est. Prep Time:</span><span class="receipt-val">⏱️ 15-20 min</span></div><div class="receipt-items" id="successItems"></div><div class="receipt-total"><span>Grand Total</span><span id="successTotal">₹557</span></div></div><p class="success-note">Show Order ID <strong id="successOrderId2">AX-7842</strong> at the counter to complete cash/card checkout.</p><div class="success-btns"><button class="btn btn-primary" onclick="orderMore()">ORDER MORE ITEMS</button><button class="btn" onclick="callWaiter()">🔔 CALL WAITER</button><button class="btn btn-red" onclick="handleDisconnect()">DISCONNECT WIFI & LOGOUT</button></div></div></div>
</div>
<div class="cart-bar" id="cartBar" style="display:none" onclick="openCart()"><div class="cart-info"><div class="cart-label">CRAV BASKET</div><div class="cart-count"><span id="cartBarCount">0</span> items • ₹<span id="cartBarTotal">0</span></div></div><button class="cart-btn">🛒 VIEW BASKET →</button></div>
<div class="modal-overlay" id="cartOverlay" onclick="closeCart()"></div>
<div class="cart-sheet" id="cartSheet"><div class="cart-header"><div class="cart-header-title">🛒 YOUR BASKET</div><button class="cart-close" onclick="closeCart()">×</button></div><div class="cart-items" id="cartItems"></div><div class="cart-footer"><div class="cart-row"><span>Subtotal</span><span>₹<span id="cartSubtotal">0</span></span></div><div class="cart-row"><span>GST Tax (5%)</span><span>₹<span id="cartTax">0</span></span></div><div class="cart-row total"><span>Grand Total</span><span>₹<span id="cartTotal">0</span></span></div><div class="cart-actions"><button class="btn btn-ghost" onclick="closeCart()">ADD MORE</button><button class="btn btn-primary" onclick="placeOrder()">PLACE ORDER</button></div></div></div>
<div class="footer"><p class="footer-text">🍔 THIS PORTAL IS HOSTED BY AXIONIK. ALL RIGHTS RESERVED. ENJOY YOUR CRAVINGS!</p><div class="footer-badge">AXIONIK v2.4.0</div></div>
</div>
<script>
const MENU_ITEMS=[{id:'mcchicken',name:'McChicken',price:199,category:'Burgers',description:'Crispy chicken patty with mayo',emoji:'🍔',badge:'BEST SELLER ⭐',badgeClass:'red'},{id:'mcveggie',name:'McVeggie',price:149,category:'Burgers',description:'Veg patty with fresh veggies',emoji:'🥬',badge:'CRUNCHY 🥬',badgeClass:'green'},{id:'mcaloo-tikki',name:'McAloo Tikki',price:89,category:'Burgers',description:'Classic Indian favorite',emoji:'🥔',badge:'LOCAL HERO 🥔',badgeClass:'orange'},{id:'fries',name:'Fries',price:89,category:'Sides',description:'Crispy golden french fries',emoji:'🍟',badge:'CRAVED 🔥',badgeClass:'red',sizes:[{label:'Medium',price:89},{label:'Large',price:119}]},{id:'mcnuggets',name:'McNuggets',price:149,category:'Sides',description:'Crispy chicken nuggets',emoji:'🍗',badge:'SHAREPACK 🍗',badgeClass:'orange'},{id:'coke',name:'Coke',price:60,category:'Drinks',description:'Ice cold refreshing cola',emoji:'🥤',badge:'ICE COLD 🥤',badgeClass:'blue'},{id:'mcflurry-oreo',name:'McFlurry Oreo',price:99,category:'Desserts',description:'Creamy oreo ice cream',emoji:'🍦',badge:'SWEET TOOTH 🍦',badgeClass:'red'},{id:'mcspicy',name:'McSpicy Chicken',price:249,category:'Burgers',description:'Spicy chicken with jalapeños',emoji:'🌶️'},{id:'mcpaneer',name:'McPaneer',price:179,category:'Burgers',description:'Grilled paneer tikka',emoji:'🧀'},{id:'shake',name:'Chocolate Shake',price:129,category:'Drinks',description:'Rich chocolate thick shake',emoji:'🍫'},{id:'mcwrap',name:'McWrap Veggie',price:159,category:'Sides',description:'Veggie wrap with sauces',emoji:'🌯'},{id:'blackcurrant',name:'Black Currant',price:109,category:'Desserts',description:'Tangy black currant swirls',emoji:'🫐'}];
const POPULAR_IDS=['mcchicken','mcaloo-tikki','fries','mcflurry-oreo'];
let session=null,cart=[],selectedSizes={fries:'Medium'},craveLevel=30,unlockedDiscount=false,currentCategory='Popular',assignedTable='15';
function init(){const storedUser=localStorage.getItem('axionik_user'),storedCart=localStorage.getItem('axionik_cart'),storedTable=localStorage.getItem('axionik_assigned_table');if(storedTable)assignedTable=storedTable;else localStorage.setItem('axionik_assigned_table','15');if(storedUser){try{session=JSON.parse(storedUser);showView('viewMenu');updateMenuHeader();renderMenu()}catch(e){localStorage.removeItem('axionik_user')}}if(storedCart){try{cart=JSON.parse(storedCart)}catch(e){cart=[]}}updateCartBar()}
function showView(id){document.querySelectorAll('.view').forEach(v=>v.classList.remove('active'));document.getElementById(id).classList.add('active')}
function showToast(text,emoji){const toast=document.getElementById('toast');document.getElementById('toastEmoji').textContent=emoji;document.getElementById('toastText').textContent=text;toast.classList.add('show');setTimeout(()=>toast.classList.remove('show'),2200)}
function handleSignin(){const name=document.getElementById('inputName').value.trim(),phone=document.getElementById('inputPhone').value.trim(),email=document.getElementById('inputEmail').value.trim(),consent=document.getElementById('inputConsent').checked,errorDiv=document.getElementById('formError'),errorText=document.getElementById('errorText');errorDiv.style.display='none';if(!name){errorText.textContent='Full name is required';errorDiv.style.display='flex';return}if(!/^[6-9][0-9]{9}$/.test(phone)){errorText.textContent='Please enter a valid Indian 10-digit mobile number';errorDiv.style.display='flex';return}if(!consent){errorText.textContent='Consent is required to enable free WiFi access';errorDiv.style.display='flex';return}const btnText=document.getElementById('btnSubmitText'),btnLoad=document.getElementById('btnSubmitLoading');btnText.style.display='none';btnLoad.style.display='inline';document.getElementById('btnSubmit').disabled=true;setTimeout(()=>{const token='AX-'+Math.floor(100000+Math.random()*900000);session={name,phone,email,token,consent,tableNumber:assignedTable};localStorage.setItem('axionik_user',JSON.stringify(session));btnText.style.display='inline';btnLoad.style.display='none';document.getElementById('btnSubmit').disabled=false;showToast('Welcome, '+name+'!','🍽️');showView('viewMenu');updateMenuHeader();renderMenu()},1200)}
function updateMenuHeader(){if(session){document.getElementById('menuUserName').textContent=session.name;document.getElementById('menuTableNum').textContent=assignedTable}}
function boostCrave(){if(craveLevel>=100){showToast('Cravings fully satisfied! Code CRAV10 unlocked!','🔥');return}craveLevel=Math.min(craveLevel+14,100);document.getElementById('cravePercent').textContent=craveLevel+'%';document.getElementById('craveFill').style.width=craveLevel+'%';const emojis=['🍔','🍟','🔥','🍦','🥤','🍗','👅','✨','⚡'],container=document.getElementById('burstContainer');for(let i=0;i<10;i++){const burst=document.createElement('div');burst.className='burst';burst.textContent=emojis[Math.floor(Math.random()*emojis.length)];burst.style.setProperty('--tx',(Math.random()-0.5)*220+'px');burst.style.setProperty('--ty',-60-Math.random()*150+'px');burst.style.animationDelay=Math.random()*0.2+'s';container.appendChild(burst);setTimeout(()=>burst.remove(),1000)}if(craveLevel===100){unlockedDiscount=true;document.getElementById('craveDesc').textContent='🎉 100% MAXIMUM CRUNCH! USE PROMO CODE CRAV10 FOR 10% OFF!';showToast('CRAVE METER hits 100%! Use CRAV10 for 10% off!','🔥')}else{document.getElementById('craveDesc').textContent='Cravings now at '+craveLevel+'%! Keep boosting!';showToast('Cravings now at '+craveLevel+'%!','🔥')}}
function setCategory(cat){currentCategory=cat;document.querySelectorAll('.cat-btn').forEach(b=>{b.classList.toggle('active',b.dataset.cat===cat)});renderMenu()}
function renderMenu(){const grid=document.getElementById('menuGrid');let items=MENU_ITEMS;if(currentCategory==='Popular'){items=items.filter(i=>POPULAR_IDS.includes(i.id))}else{items=items.filter(i=>i.category===currentCategory)}grid.innerHTML=items.map((item,idx)=>{const isFries=item.id==='fries',size=selectedSizes[item.id]||'Medium',price=isFries?(item.sizes?.find(s=>s.label===size)?.price||item.price):item.price,badge=item.badge?`<span class="item-badge ${item.badgeClass}">${item.badge}</span>`:'';let sizesHtml='';if(item.sizes){sizesHtml=`<div class="item-sizes">${item.sizes.map(sz=>{const active=(selectedSizes[item.id]||'Medium')===sz.label;return `<button class="size-btn ${active?'active':''}" onclick="event.stopPropagation();setSize('${item.id}','${sz.label}')">${sz.label}</button>`}).join('')}</div>`}return `<div class="menu-item fade-in" style="animation-delay:${idx*0.05}s">${badge}<div class="item-emoji">${item.emoji}</div><div class="item-info"><div class="item-name">${item.name}</div><div class="item-desc">${item.description}</div>${sizesHtml}<div class="item-footer"><span class="item-price">₹${price}</span><button class="item-add" onclick="addToCart('${item.id}')">+ ADD</button></div></div></div>`}).join('')}
function setSize(itemId,label){selectedSizes[itemId]=label;renderMenu()}
function addToCart(itemId){const item=MENU_ITEMS.find(i=>i.id===itemId);if(!item)return;let price=item.price,sizeLabel=null,cartId=item.id;if(item.sizes){sizeLabel=selectedSizes[item.id]||'Medium';const sz=item.sizes.find(s=>s.label===sizeLabel);price=sz?sz.price:item.price;cartId=item.id+'-'+sizeLabel}const existing=cart.findIndex(c=>c.id===cartId);if(existing>-1){cart[existing].quantity+=1}else{cart.push({id:cartId,menuItemId:item.id,name:item.name,description:item.description,emoji:item.emoji,sizeLabel:sizeLabel,unitPrice:price,quantity:1})}saveCart();showToast(item.name+' added!',item.emoji)}
function updateQty(cartId,delta){const idx=cart.findIndex(c=>c.id===cartId);if(idx===-1)return;cart[idx].quantity+=delta;if(cart[idx].quantity<=0)cart.splice(idx,1);saveCart();renderCart();if(cart.length===0)closeCart()}
function removeItem(cartId){cart=cart.filter(c=>c.id!==cartId);saveCart();renderCart();if(cart.length===0)closeCart()}
function saveCart(){localStorage.setItem('axionik_cart',JSON.stringify(cart));updateCartBar()}
function updateCartBar(){const count=cart.reduce((s,i)=>s+i.quantity,0),total=cart.reduce((s,i)=>s+i.unitPrice*i.quantity,0),bar=document.getElementById('cartBar');if(count>0){bar.style.display='flex';document.getElementById('cartBarCount').textContent=count;document.getElementById('cartBarTotal').textContent=total}else{bar.style.display='none'}}
function openCart(){renderCart();document.getElementById('cartOverlay').classList.add('show');document.getElementById('cartSheet').classList.add('show')}
function closeCart(){document.getElementById('cartOverlay').classList.remove('show');document.getElementById('cartSheet').classList.remove('show')}
function renderCart(){const container=document.getElementById('cartItems'),subtotal=cart.reduce((s,i)=>s+i.unitPrice*i.quantity,0),tax=Math.round(subtotal*0.05),total=subtotal+tax;document.getElementById('cartSubtotal').textContent=subtotal;document.getElementById('cartTax').textContent=tax;document.getElementById('cartTotal').textContent=total;container.innerHTML=cart.map(item=>`<div class="cart-item"><div class="cart-item-left"><div class="cart-item-top"><span class="cart-item-emoji">${item.emoji}</span><span class="cart-item-name">${item.name}</span></div>${item.sizeLabel?`<span class="cart-item-size">${item.sizeLabel}</span>`:''}<div class="cart-item-price">₹${item.unitPrice} each</div></div><div style="display:flex;align-items:center"><div class="cart-qty"><button class="qty-btn" onclick="updateQty('${item.id}',-1)">−</button><span class="qty-val">${item.quantity}</span><button class="qty-btn" onclick="updateQty('${item.id}',1)">+</button></div><button class="cart-del" onclick="removeItem('${item.id}')">🗑</button></div></div>`).join('')}
function placeOrder(){if(cart.length===0||!session)return;const orderId='AX-'+Math.floor(1000+Math.random()*9000),subtotal=cart.reduce((s,i)=>s+i.unitPrice*i.quantity,0),tax=Math.round(subtotal*0.05),total=subtotal+tax;const order={id:orderId,customerName:session.name,phone:session.phone,email:session.email,tableNumber:assignedTable,items:[...cart],subtotal,tax,total,status:'Preparing',paymentStatus:'Pay at Counter',timestamp:new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})};let history=[];const stored=localStorage.getItem('axionik_orders_history');if(stored){try{history=JSON.parse(stored)}catch(e){}}history.unshift(order);localStorage.setItem('axionik_orders_history',JSON.stringify(history));document.getElementById('successOrderId').textContent=orderId;document.getElementById('successOrderId2').textContent=orderId;document.getElementById('successTable').textContent=assignedTable;document.getElementById('successTotal').textContent='₹'+total;document.getElementById('successItems').innerHTML=order.items.map(i=>`<div class="receipt-item"><span>${i.emoji} ${i.name} ${i.sizeLabel?'('+i.sizeLabel+')':''} <span class="qty">x${i.quantity}</span></span><span style="font-family:monospace;font-weight:700">₹${i.unitPrice*i.quantity}</span></div>`).join('');cart=[];saveCart();closeCart();showView('viewSuccess')}
function orderMore(){showView('viewMenu');renderMenu()}
function callWaiter(){showToast('Staff notified! A waiter is on the way.','🔔')}
function handleDisconnect(){localStorage.removeItem('axionik_user');localStorage.removeItem('axionik_cart');session=null;cart=[];craveLevel=30;unlockedDiscount=false;document.getElementById('cravePercent').textContent='30%';document.getElementById('craveFill').style.width='30%';document.getElementById('craveDesc').textContent='Tap the boost button to fire up your cravings and unlock a 10% promo!';document.getElementById('inputName').value='';document.getElementById('inputPhone').value='';document.getElementById('inputEmail').value='';document.getElementById('formError').style.display='none';updateCartBar();showView('viewSignin')}
init();
</script>
</body>
</html>)rawliteral";

// ====== SETUP ======
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n\n=== AXIONIK CRAV BISTRO Captive Portal ===");
  Serial.println("Starting ESP32...");

  // Configure AP
  WiFi.softAPConfig(apIP, apIP, IPAddress(255, 255, 255, 0));
  WiFi.softAP(ssid, password);

  IPAddress myIP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(myIP);

  // Start DNS server for captive portal
  dnsServer.start(DNS_PORT, "*", apIP);

  // Handle root
  server.on("/", HTTP_GET, handleRoot);

  // Handle register (forwards customer data to backend)
  server.on("/register-customer", HTTP_POST, handleRegister);

  // Handle all other requests (captive portal catch-all)
  server.onNotFound(handleRoot);

  server.begin();
  Serial.println("HTTP server started");
  Serial.println("Connect to '" + String(ssid) + "' and open any URL");
}

void loop() {
  dnsServer.processNextRequest();
  server.handleClient();
}

// ====== HANDLERS ======
void handleRoot() {
  Serial.println("Served portal page to: " + server.client().remoteIP().toString());
  server.send(200, "text/html", portal_html);
}

void handleRegister() {
  if (!server.hasArg("plain")) {
    server.send(400, "application/json", "{\"status\":\"error\",\"message\":\"No data\"}");
    return;
  }

  String body = server.arg("plain");
  Serial.println("=== RECEIVED CUSTOMER DATA ===");
  Serial.println(body);
  Serial.println("==============================");

  // Generate token
  String token = "AX-" + String(random(100000, 999999));

  String response = "{\"status\":\"success\",\"token\":\"" + token + "\",\"message\":\"Welcome to CRAV BISTRO!\",\"table\":\"15\"}";
  server.send(200, "application/json", response);
}