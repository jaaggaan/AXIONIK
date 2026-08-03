import os
import glob
import re

dist_dir = r"c:\Users\rentk\Projects\freesalewifi\frontend\captive-portal-app\dist"
html_path = os.path.join(dist_dir, "index.html")

with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

css_files = glob.glob(os.path.join(dist_dir, "assets", "*.css"))
js_files = glob.glob(os.path.join(dist_dir, "assets", "*.js"))

css_content = ""
for c in css_files:
    with open(c, "r", encoding="utf-8") as f:
        css_content += f.read() + "\n"

js_content = ""
for j in js_files:
    with open(j, "r", encoding="utf-8") as f:
        js_content += f.read() + "\n"

# Remove script module link and CSS link tags
html_clean = re.sub(r'<link\s+rel="stylesheet"[^>]*>', '', html)
html_clean = re.sub(r'<script\s+type="module"[^>]*></script>', '', html_clean)

# Minify CSS: strip comments & redundant spaces
css_clean = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
css_clean = re.sub(r'\s+', ' ', css_clean)

style_tag = "<style>\n" + css_clean + "\n</style>\n"
script_tag = "<script>\n" + js_content + "\n</script>\n"

final_html = html_clean.replace("</head>", style_tag + "</head>").replace("</body>", script_tag + "</body>")

# Replace any sequence of )=====" with )====" to prevent PROGMEM delimiter clash
final_html = final_html.replace(')====="', ')===="')

out_html_path = os.path.join(dist_dir, "single_portal.html")
with open(out_html_path, "w", encoding="utf-8") as f:
    f.write(final_html)

print(f"Generated single_portal.html ({os.path.getsize(out_html_path)} bytes)")

# Now generate portal_html.h for both esp32_captive_portal folders
h_content = f'''#ifndef PORTAL_HTML_H
#define PORTAL_HTML_H

#include <Arduino.h>

const char portal_html[] PROGMEM = R"=====({final_html})=====";

#endif
'''

dest1 = r"c:\Users\rentk\Projects\freesalewifi\esp32_captive_portal\portal_html.h"
dest2 = r"c:\Users\rentk\Projects\freesalewifi\firmware\esp32_captive_portal\portal_html.h"

with open(dest1, "w", encoding="utf-8") as f:
    f.write(h_content)

with open(dest2, "w", encoding="utf-8") as f:
    f.write(h_content)

print(f"Successfully updated portal_html.h in both directories!")
