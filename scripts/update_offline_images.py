import re
import os

# SVG Data URIs with escaped single quotes for offline high-resolution display on ESP32 Wi-Fi AP
SVG_IMAGES = {
    'HERO_AUTUMN': '''data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 600' width='100%' height='100%'><defs><linearGradient id='bg' x1='0%' y1='0%' x2='100%' y2='100%'><stop offset='0%' stop-color='%232b1810'/><stop offset='100%' stop-color='%235a2d1a'/></linearGradient><linearGradient id='gold' x1='0%' y1='0%' x2='100%' y2='0%'><stop offset='0%' stop-color='%23d4af37'/><stop offset='100%' stop-color='%23f3e5ab'/></linearGradient></defs><rect width='1200' height='600' fill='url(%23bg)'/><line x1='200' y1='120' x2='1000' y2='120' stroke='url(%23gold)' stroke-width='8' stroke-linecap='round'/><g stroke='%23d4af37' stroke-width='4' fill='none'><path d='M350 120 V160 L380 200 H320 Z'/><path d='M500 120 V160 L530 200 H470 Z'/><path d='M650 120 V160 L680 200 H620 Z'/><path d='M800 120 V160 L830 200 H770 Z'/></g><path d='M300 200 L320 500 H400 L380 200 Z' fill='%23c41e3a' opacity='0.85'/><path d='M450 200 L470 520 H550 L530 200 Z' fill='%23c9a96e' opacity='0.85'/><path d='M600 200 L620 480 H700 L680 200 Z' fill='%232e493e' opacity='0.85'/><path d='M750 200 L770 510 H850 L830 200 Z' fill='%238a3c2a' opacity='0.85'/><text x='600' y='560' font-family='Georgia, serif' font-size='32' fill='%23f3e5ab' text-anchor='middle' letter-spacing='4'>AUTUMN RUNWAY &amp; CONTEMPORARY ELEGANCE</text></svg>''',

    'WOMEN': '''data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 600' width='100%' height='100%'><rect width='800' height='600' fill='%23f7f4ee'/><circle cx='400' cy='220' r='140' fill='%23e8ded1'/><path d='M320 180 Q400 120 480 180 L520 500 H280 Z' fill='%23c41e3a' opacity='0.9'/><path d='M360 180 Q400 140 440 180 L460 500 H340 Z' fill='%23d4af37' opacity='0.8'/><text x='400' y='550' font-family='sans-serif' font-weight='bold' font-size='28' fill='%233d241d' text-anchor='middle' letter-spacing='3'>NEW SEASON EDIT</text></svg>''',

    'MEN': '''data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 600' width='100%' height='100%'><rect width='800' height='600' fill='%231a2634'/><path d='M250 150 L400 220 L550 150 L620 550 H180 Z' fill='%230f172a'/><path d='M330 150 L400 300 L470 150' fill='%23ffffff'/><path d='M380 200 L400 550 L420 200' fill='%23c41e3a'/><polygon points='400,220 385,190 415,190' fill='%23c41e3a'/><text x='400' y='540' font-family='sans-serif' font-weight='bold' font-size='28' fill='%23c9a96e' text-anchor='middle' letter-spacing='3'>LATEST STYLES</text></svg>''',

    'BEAUTY': '''data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 600' width='100%' height='100%'><rect width='800' height='600' fill='%23fdf2f4'/><circle cx='400' cy='280' r='160' fill='%23fbcfe8' opacity='0.6'/><rect x='320' y='200' width='160' height='220' rx='30' fill='%23d4af37' opacity='0.85'/><rect x='360' y='140' width='80' height='60' rx='10' fill='%231a1a1a'/><rect x='375' y='110' width='50' height='30' rx='5' fill='%23c41e3a'/><circle cx='400' cy='310' r='40' fill='%23ffffff' opacity='0.4'/><text x='400' y='520' font-family='sans-serif' font-weight='bold' font-size='28' fill='%23831843' text-anchor='middle' letter-spacing='3'>NEW &amp; TRENDING</text></svg>''',

    'ACCESSORIES': '''data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 600' width='100%' height='100%'><rect width='800' height='600' fill='%230f172a'/><circle cx='400' cy='260' r='130' fill='%231e293b' stroke='%23d4af37' stroke-width='8'/><rect x='365' y='80' width='70' height='60' fill='%23d4af37' rx='8'/><rect x='365' y='380' width='70' height='60' fill='%23d4af37' rx='8'/><path d='M400 260 L400 170 M400 260 L460 260' stroke='%23ffffff' stroke-width='8' stroke-linecap='round'/><text x='400' y='520' font-family='sans-serif' font-weight='bold' font-size='28' fill='%23f3e5ab' text-anchor='middle' letter-spacing='3'>FRESH ARRIVALS</text></svg>''',

    'GROUND': '''data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 500' width='100%' height='100%'><rect width='800' height='500' fill='%232b1810'/><text x='400' y='230' font-family='Georgia, serif' font-size='42' fill='%23d4af37' text-anchor='middle' font-weight='bold'>GROUND FLOOR</text><text x='400' y='290' font-family='sans-serif' font-size='20' fill='%23ffffff' text-anchor='middle' letter-spacing='2'>Beauty, Fragrances, Watches &amp; Eyewear</text></svg>''',

    'FIRST': '''data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 500' width='100%' height='100%'><rect width='800' height='500' fill='%230f172a'/><text x='400' y='230' font-family='Georgia, serif' font-size='42' fill='%23d4af37' text-anchor='middle' font-weight='bold'>FIRST FLOOR</text><text x='400' y='290' font-family='sans-serif' font-size='20' fill='%23ffffff' text-anchor='middle' letter-spacing='2'>Men's Fashion, Formalwear &amp; Denim Studio</text></svg>''',

    'SECOND': '''data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 500' width='100%' height='100%'><rect width='800' height='500' fill='%235a1827'/><text x='400' y='230' font-family='Georgia, serif' font-size='42' fill='%23d4af37' text-anchor='middle' font-weight='bold'>SECOND FLOOR</text><text x='400' y='290' font-family='sans-serif' font-size='20' fill='%23ffffff' text-anchor='middle' letter-spacing='2'>Women's Fashion, Ethnic Pavilion &amp; Couture</text></svg>''',

    'THIRD': '''data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 500' width='100%' height='100%'><rect width='800' height='500' fill='%231c2e26'/><text x='400' y='230' font-family='Georgia, serif' font-size='42' fill='%23d4af37' text-anchor='middle' font-weight='bold'>THIRD FLOOR</text><text x='400' y='290' font-family='sans-serif' font-size='20' fill='%23ffffff' text-anchor='middle' letter-spacing='2'>Kids' Fashion, Home Decor &amp; Travel</text></svg>''',
}

mock_file = r"c:\Users\rentk\Projects\freesalewifi\frontend\captive-portal-app\src\data\mockStoreData.ts"
with open(mock_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Unsplash URLs or data: URIs with clean single-quoted SVG Data URIs
content = re.sub(r'imageUrl:\s*"[^"]*"', f'imageUrl: "{SVG_IMAGES["WOMEN"]}"', content, count=1)
content = re.sub(r'imageUrl:\s*"[^"]*"', f'imageUrl: "{SVG_IMAGES["MEN"]}"', content, count=1)
content = re.sub(r'imageUrl:\s*"[^"]*"', f'imageUrl: "{SVG_IMAGES["BEAUTY"]}"', content, count=1)
content = re.sub(r'imageUrl:\s*"[^"]*"', f'imageUrl: "{SVG_IMAGES["ACCESSORIES"]}"', content, count=1)

content = re.sub(r'imageUrl:\s*"[^"]*"', f'imageUrl: "{SVG_IMAGES["GROUND"]}"', content, count=1)
content = re.sub(r'imageUrl:\s*"[^"]*"', f'imageUrl: "{SVG_IMAGES["FIRST"]}"', content, count=1)
content = re.sub(r'imageUrl:\s*"[^"]*"', f'imageUrl: "{SVG_IMAGES["SECOND"]}"', content, count=1)
content = re.sub(r'imageUrl:\s*"[^"]*"', f'imageUrl: "{SVG_IMAGES["THIRD"]}"', content, count=1)

# Replace all remaining imageUrl strings
content = re.sub(r'imageUrl:\s*"https://images\.unsplash\.com/[^"]*"', f'imageUrl: "{SVG_IMAGES["HERO_AUTUMN"]}"', content)

with open(mock_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated mockStoreData.ts with clean single-quoted SVG Data URIs!")
