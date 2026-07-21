// FILE: esp32_captive_portal.ino
// CLEANED: 2026-07-21
// DESCRIPTION: AXIONIX SoftAP Captive Portal Firmware with refactored glassmorphism form

#include <WiFi.h>
#include <DNSServer.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>

// --- AP Parameters ---
const char* ap_ssid = "FreeSaleWiFi";
const char* ap_password = "";

const IPAddress ap_ip(192, 168, 4, 1);
const IPAddress ap_subnet(255, 255, 255, 0);

const byte DNS_PORT = 53;
DNSServer dnsServer;
AsyncWebServer server(80);

// --- Captive Portal HTML Template ---
const char portal_html[] PROGMEM = R"rawliteral(<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>AXIONIX — Guest Wi-Fi Portal</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --bg: #000000;
      --text-primary: #f4f1ea;
      --text-muted: #8b8a93;
      --accent: #ff9a6b;
      --accent-hover: #ff7a3c;
      --success: #10b981;
      --error: #ef4444;
      --border: rgba(255, 255, 255, 0.08);
      --card-bg: linear-gradient(180deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02));
      --glass-blur: blur(20px);
      --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    body {
      background-color: var(--bg);
      color: var(--text-primary);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
      position: relative;
      padding: 1.5rem 1rem;
    }
    .bg-orbs {
      position: absolute; top: 0; left: 0; width: 100%; height: 100%;
      z-index: 1; overflow: hidden; pointer-events: none;
    }
    .orb { position: absolute; border-radius: 50%; filter: blur(120px); opacity: 0.2; }
    .orb-1 { background: var(--accent); width: 350px; height: 350px; top: -10%; left: -10%; }
    .orb-2 { background: #6366f1; width: 400px; height: 400px; bottom: -10%; right: -10%; }
    .portal-card {
      position: relative; z-index: 10; width: 100%; max-width: 420px;
      background: var(--card-bg); backdrop-filter: var(--glass-blur); -webkit-backdrop-filter: var(--glass-blur);
      border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 24px; padding: 2.25rem 2rem;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6); display: flex; flex-direction: column; gap: 1.5rem;
    }
    header { display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border); padding-bottom: 1rem; }
    .brand-logo { display: flex; align-items: center; gap: 8px; font-weight: 700; letter-spacing: 0.5px; }
    .logo-box { width: 28px; height: 28px; background: linear-gradient(135deg, var(--accent), var(--accent-hover)); border-radius: 6px; display: grid; place-items: center; font-weight: 800; font-size: 0.75rem; color: #000; }
    .status-area { display: flex; align-items: center; gap: 6px; font-size: 0.72rem; color: var(--success); }
    .pulse-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--success); box-shadow: 0 0 8px var(--success); }
    .title-area { text-align: center; margin: 0.5rem 0; }
    .main-title { font-size: 1.5rem; font-weight: 400; margin-bottom: 0.4rem; }
    .main-title em { font-family: Georgia, serif; font-style: italic; color: var(--accent); }
    .subtitle { font-size: 0.8rem; color: var(--text-muted); line-height: 1.4; }
    .welcome-banner { display: none; background: rgba(255, 154, 107, 0.08); border: 1px solid rgba(255, 154, 107, 0.2); border-radius: 12px; padding: 0.85rem; font-size: 0.8rem; line-height: 1.4; text-align: center; }
    .welcome-banner strong { color: var(--accent); }
    .form-group { display: flex; flex-direction: column; gap: 12px; }
    .input-wrapper { position: relative; display: flex; align-items: center; }
    .input-icon { position: absolute; left: 14px; width: 16px; height: 16px; color: var(--text-muted); display: flex; align-items: center; }
    .phone-prefix { position: absolute; left: 14px; font-size: 0.85rem; color: var(--text-primary); font-weight: 500; }
    .input-field { width: 100%; background: rgba(255, 255, 255, 0.03); border: 1px solid var(--border); color: var(--text-primary); padding: 0.85rem 1rem 0.85rem 2.6rem; border-radius: 12px; font-size: 0.88rem; outline: none; transition: var(--transition); }
    .input-field.input-phone { padding-left: 4.5rem; }
    .input-field:focus { border-color: var(--accent); background: rgba(255, 255, 255, 0.05); }
    select.input-field { appearance: none; -webkit-appearance: none; cursor: pointer; }
    .consent-area { display: flex; align-items: flex-start; gap: 12px; background: rgba(255, 255, 255, 0.02); border: 1px solid var(--border); border-radius: 14px; padding: 1rem; cursor: pointer; }
    .switch-label { flex: 1; display: flex; flex-direction: column; gap: 4px; cursor: pointer; }
    .switch-title { font-size: 0.85rem; font-weight: 600; }
    .switch-desc { font-size: 0.7rem; color: var(--text-muted); line-height: 1.4; }
    .toggle-switch { position: relative; width: 38px; height: 20px; background: rgba(255, 255, 255, 0.1); border-radius: 10px; flex-shrink: 0; margin-top: 2px; transition: var(--transition); }
    .toggle-switch::after { content: ''; position: absolute; width: 16px; height: 16px; border-radius: 50%; background: var(--text-primary); top: 2px; left: 2px; transition: var(--transition); }
    .consent-checkbox { display: none; }
    .consent-checkbox:checked + .toggle-switch { background: linear-gradient(135deg, var(--accent), var(--accent-hover)); }
    .consent-checkbox:checked + .toggle-switch::after { left: 20px; background: #000; }
    .btn-connect { width: 100%; background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03)); border: 1px solid rgba(255, 255, 255, 0.1); color: rgba(255, 255, 255, 0.3); padding: 0.95rem; border-radius: 14px; font-size: 0.9rem; font-weight: 700; cursor: not-allowed; display: flex; align-items: center; justify-content: center; gap: 10px; transition: var(--transition); }
    .btn-connect.valid { background: linear-gradient(135deg, var(--accent), var(--accent-hover)); color: #000; border-color: transparent; cursor: pointer; box-shadow: 0 4px 15px rgba(255, 154, 107, 0.25); }
    .spinner { display: none; width: 16px; height: 16px; border: 2.5px solid transparent; border-radius: 50%; border-top-color: #000; border-right-color: #000; border-bottom-color: #000; animation: spin 0.6s linear infinite; }
    @keyframes spin { to { transform: rotate(360deg); } }
    .error-card { display: none; background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 12px; padding: 0.85rem; font-size: 0.78rem; color: var(--error); align-items: center; justify-content: space-between; }
    .error-card.visible { display: flex; }
    .btn-retry { background: none; border: none; color: var(--text-primary); text-decoration: underline; font-weight: 600; cursor: pointer; }
    .modal-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0, 0, 0, 0.85); backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px); z-index: 1000; display: none; align-items: center; justify-content: center; padding: 1.5rem 1rem; }
    .modal-overlay.open { display: flex; }
    .modal-card { background: var(--card-bg); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; width: 100%; max-width: 400px; padding: 2rem; display: flex; flex-direction: column; align-items: center; gap: 1.25rem; text-align: center; }
    .checkmark-box { width: 60px; height: 60px; border-radius: 50%; background: rgba(16, 185, 129, 0.1); display: grid; place-items: center; color: var(--success); }
    .modal-title { font-size: 1.3rem; font-weight: 500; }
    .modal-desc { font-size: 0.82rem; color: var(--text-muted); line-height: 1.5; }
    .btn-modal-action { width: 100%; background: linear-gradient(135deg, var(--accent), var(--accent-hover)); border: none; color: #000; padding: 0.85rem; border-radius: 12px; font-size: 0.85rem; font-weight: 700; cursor: pointer; transition: var(--transition); }
  </style>
</head>
<body>
  <div class="bg-orbs">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
  </div>
  <main class="portal-card">
    <header>
      <div class="brand-logo"><div class="logo-box">AX</div><span>AXIONIX</span></div>
      <div class="status-area"><div class="pulse-dot"></div><span>Secure Gateway</span></div>
    </header>
    <div class="title-area">
      <h2 class="main-title">Guest Wi-Fi <em>Portal</em></h2>
      <p class="subtitle">Complete quick registration to initiate secure node access.</p>
    </div>
    <div class="welcome-banner" id="welcomeBackBanner">
      Welcome back, <strong id="returningUserName">Guest</strong>! prefilled saved details.
    </div>
    <form id="authForm" onsubmit="handleConnect(event)">
      <div class="form-group">
        <div class="input-wrapper">
          <span class="input-icon">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
          </span>
          <input type="text" id="fullName" class="input-field" placeholder="Full Name" required autocomplete="name">
        </div>
        <div class="input-wrapper">
          <span class="phone-prefix">🇮🇳 +91</span>
          <input type="tel" id="phoneNumber" class="input-field input-phone" placeholder="Phone Number" required autocomplete="tel">
        </div>
        <div class="input-wrapper">
          <span class="input-icon">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
          </span>
          <input type="email" id="emailAddress" class="input-field" placeholder="Email Address (optional)" autocomplete="email">
        </div>
        <div class="input-wrapper">
          <span class="input-icon">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
          </span>
          <select id="storeSelect" class="input-field" required>
            <option value="" disabled selected>Select Current Store Location</option>
            <option value="store_001">TechHub Electronics</option>
            <option value="store_002">Urban Style Fashion</option>
            <option value="store_003">FreshBite Gourmet</option>
          </select>
        </div>
        <div class="consent-area" onclick="toggleConsent()">
          <div class="switch-label">
            <span class="switch-title">Fair Usage Acceptance</span>
            <span class="switch-desc">Accept basic node routing and telemetry usage policy rules.</span>
          </div>
          <input type="checkbox" id="consentToggle" class="consent-checkbox" onchange="validateForm()">
          <div class="toggle-switch"></div>
        </div>
        <div class="error-card" id="errorCard">
          <span id="errorText">Connection failed. Please retry.</span>
          <button type="button" class="btn-retry" onclick="dismissError()">Dismiss</button>
        </div>
        <button type="submit" class="btn-connect" id="connectButton" disabled>
          <span class="spinner" id="connectSpinner"></span>
          <span id="connectBtnText">Request Wi-Fi Access</span>
        </button>
      </div>
    </form>
  </main>
  <div class="modal-overlay" id="successOverlay">
    <div class="modal-card">
      <div class="checkmark-box">
        <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
      </div>
      <h3 class="modal-title">Access Authorized</h3>
      <p class="modal-desc">Identity verified on local node. Connected to high-speed gateway routing.</p>
      <button type="button" class="btn-modal-action" onclick="dismissSuccess()">Begin Browsing</button>
    </div>
  </div>
  <script>
    const fName = document.getElementById('fullName');
    const pNumber = document.getElementById('phoneNumber');
    const eAddress = document.getElementById('emailAddress');
    const sSelect = document.getElementById('storeSelect');
    const cToggle = document.getElementById('consentToggle');
    const cButton = document.getElementById('connectButton');
    const cSpinner = document.getElementById('connectSpinner');
    const cBtnText = document.getElementById('connectBtnText');
    const errCard = document.getElementById('errorCard');
    const errText = document.getElementById('errorText');

    pNumber.addEventListener('input', (e) => {
      let val = e.target.value.replace(/\D/g, '');
      if (val.length > 10) val = val.substring(0, 10);
      let formatted = '';
      if (val.length > 0) formatted += val.substring(0, 3);
      if (val.length >= 4) formatted += ' ' + val.substring(3, 6);
      if (val.length >= 7) formatted += ' ' + val.substring(6, 10);
      e.target.value = formatted.trim();
      validateForm();
    });

    fName.addEventListener('input', validateForm);
    eAddress.addEventListener('input', validateForm);
    sSelect.addEventListener('change', validateForm);

    function toggleConsent() {
      cToggle.checked = !cToggle.checked;
      validateForm();
    }

    function validateForm() {
      const isNameValid = fName.value.trim().length >= 2;
      const isPhoneValid = pNumber.value.replace(/\s/g, '').length === 10;
      const isStoreValid = sSelect.value !== '';
      const isConsentValid = cToggle.checked;

      if (isNameValid && isPhoneValid && isStoreValid && isConsentValid) {
        cButton.disabled = false;
        cButton.classList.add('valid');
      } else {
        cButton.disabled = true;
        cButton.classList.remove('valid');
      }
    }

    window.addEventListener('load', () => {
      const stored = localStorage.getItem('ax_user');
      if (stored) {
        try {
          const user = JSON.parse(stored);
          if (user.name && user.phone) {
            fName.value = user.name;
            pNumber.value = user.phone;
            if (user.email) eAddress.value = user.email;
            if (user.store_id) sSelect.value = user.store_id;
            cToggle.checked = true;
            validateForm();
            document.getElementById('returningUserName').innerText = user.name.split(' ')[0];
            document.getElementById('welcomeBackBanner').style.display = 'block';
          }
        } catch(e) {
          localStorage.removeItem('ax_user');
        }
      }
    });

    function handleConnect(event) {
      event.preventDefault();
      if (cButton.disabled) return;

      cButton.disabled = true;
      cButton.classList.remove('valid');
      cSpinner.style.display = 'inline-block';
      cBtnText.innerText = 'Authorizing...';
      dismissError();

      const payload = {
        name: fName.value.trim(),
        phone: '+91' + pNumber.value.replace(/\s/g, ''),
        email: eAddress.value.trim() || null,
        store_id: sSelect.value,
        consent: true
      };

      setTimeout(() => {
        // Send register payload to gateway server API
        fetch('/register-customer', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        .then(response => {
          if (!response.ok) throw new Error('Gateway rejected credentials');
          return response.json();
        })
        .then(data => {
          localStorage.setItem('ax_user', JSON.stringify({
            name: payload.name,
            phone: pNumber.value.trim(),
            email: payload.email,
            store_id: payload.store_id
          }));
          cSpinner.style.display = 'none';
          cBtnText.innerText = 'Request Wi-Fi Access';
          validateForm();
          document.getElementById('successOverlay').classList.add('open');
        })
        .catch(err => {
          cSpinner.style.display = 'none';
          cBtnText.innerText = 'Request Wi-Fi Access';
          validateForm();
          showToast(err.message || 'Authorization failed.', 'error');
        });
      }, 1500);
    }

    function showToast(msg, type = 'info') {
      errText.innerText = msg;
      errCard.style.borderColor = type === 'error' ? 'var(--error)' : 'var(--accent)';
      errCard.classList.add('visible');
    }
    function dismissError() {
      errCard.classList.remove('visible');
    }
    function dismissSuccess() {
      document.getElementById('successOverlay').classList.remove('open');
      window.location.href = 'https://www.google.com';
    }
  </script>
</body>
</html>
)rawliteral";

// --- Route Handlers ---
void handleRoot(AsyncWebServerRequest *request) {
  request->send_P(200, "text/html", portal_html);
}

void handlePostRegister(AsyncWebServerRequest *request, uint8_t *data, size_t len, size_t index, size_t total) {
  String body = "";
  for (size_t i = 0; i < len; i++) {
    body += (char)data[i];
  }
  Serial.println("--- Node Registration API Called ---");
  Serial.println(body);
  request->send(200, "application/json", "{\"status\":\"success\",\"message\":\"Access authorized\"}");
}

class CaptiveRequestHandler : public AsyncWebHandler {
public:
  CaptiveRequestHandler() {}
  virtual ~CaptiveRequestHandler() {}
  bool canHandle(AsyncWebServerRequest *request) override {
    if (request->method() == HTTP_POST) return false;
    return true;
  }
  void handleRequest(AsyncWebServerRequest *request) override {
    AsyncWebServerResponse *response = request->beginResponse(302, "text/plain", "");
    response->addHeader("Location", "http://192.168.4.1/");
    request->send(response);
  }
};

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Initializing Node AP...");

  WiFi.mode(WIFI_AP);
  WiFi.softAPConfig(ap_ip, ap_ip, ap_subnet);
  WiFi.softAP(ap_ssid, ap_password);

  dnsServer.setErrorReplyCode(DNSReplyCode::NoError);
  dnsServer.start(DNS_PORT, "*", ap_ip);

  server.on("/", HTTP_GET, handleRoot);
  server.on("/hotspot-detect.html", HTTP_GET, handleRoot);
  server.on("/generate_204", HTTP_GET, handleRoot);
  server.on("/connectivity-check.html", HTTP_GET, handleRoot);
  server.on("/library/test/success.html", HTTP_GET, handleRoot);
  server.on("/ncsi.txt", HTTP_GET, handleRoot);
  
  server.on("/register-customer", HTTP_POST, [](AsyncWebServerRequest *request) {}, NULL, handlePostRegister);
  server.addHandler(new CaptiveRequestHandler()).setFilter(ON_AP_FILTER);
  server.begin();
  
  Serial.println("AXIONIX SoftAP Captive Node Online.");
}

void loop() {
  dnsServer.processNextRequest();
}
