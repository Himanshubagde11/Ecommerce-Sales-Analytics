import os
import io
import json
import base64
from PIL import Image

# 1. Load and compress wallpaper to Base64
wallpaper_src = r"C:\Users\himan\.gemini\antigravity-ide\brain\add5d2bc-0cf1-4c1e-a83f-b0d651a3b4ba\liquid_glass_wallpaper_1789136363298.jpg"
im = Image.open(wallpaper_src)
im = im.resize((1920, 1080), Image.Resampling.LANCZOS)
buf = io.BytesIO()
im.save(buf, format="JPEG", quality=85, optimize=True)
wallpaper_bytes = buf.getvalue()
b64_wallpaper = "data:image/jpeg;base64," + base64.b64encode(wallpaper_bytes).decode("ascii")

# Save image file to RegisteredResources
registered_img_path = r"powerbi/Veyra_Ecommerce_Analytics.Report/StaticResources/RegisteredResources/liquid_glass_wallpaper.jpg"
with open(registered_img_path, "wb") as f:
    f.write(wallpaper_bytes)
print(f"Saved wallpaper ({len(wallpaper_bytes)} bytes) to {registered_img_path}")

# 2. Construct Liquid Glass Theme
liquid_glass_theme = {
    "name": "Veyra Liquid Glass Theme",
    "dataColors": [
        "#00F2FE",  # Liquid Cyan
        "#A855F7",  # Luminous Amethyst
        "#00F5A0",  # Luminous Mint
        "#FF007F",  # Hot Neon Pink
        "#FFB800",  # Liquid Amber
        "#38BDF8",  # Sapphire Glaze
        "#14B8A6",  # Teal Glass
        "#F43F5E",  # Rose Quartz
        "#6366F1",  # Indigo Glow
        "#EC4899"   # Fluorescent Fuchsia
    ],
    "background": "#080B11",
    "foreground": "#FFFFFF",
    "tableAccent": "#00F2FE",
    "visualStyles": {
        "*": {
            "*": {
                "*": [
                    {
                        "fontFamily": "Segoe UI"
                    }
                ],
                "background": [
                    {
                        "show": True,
                        "color": {"solid": {"color": "#111827"}},
                        "transparency": 32
                    }
                ],
                "border": [
                    {
                        "show": True,
                        "color": {"solid": {"color": "#25334A"}},
                        "radius": 16
                    }
                ],
                "dropShadow": [
                    {
                        "show": True,
                        "color": {"solid": {"color": "#000000"}},
                        "position": "Outer",
                        "preset": "BottomRight"
                    }
                ],
                "title": [
                    {
                        "show": True,
                        "fontColor": {"solid": {"color": "#FFFFFF"}},
                        "fontSize": 13,
                        "fontFamily": "Segoe UI Semibold",
                        "alignment": "Left"
                    }
                ],
                "grid": [
                    {
                        "gridVertical": False,
                        "gridVerticalColor": {"solid": {"color": "#1E293B"}},
                        "gridHorizontal": True,
                        "gridHorizontalColor": {"solid": {"color": "#1E293B"}}
                    }
                ]
            }
        },
        "page": {
            "*": {
                "background": [
                    {
                        "image": {
                            "name": "liquid_glass_wallpaper",
                            "scaling": "Fit",
                            "url": b64_wallpaper
                        },
                        "transparency": 0
                    }
                ],
                "outspace": [
                    {
                        "color": {"solid": {"color": "#040609"}}
                    }
                ]
            }
        },
        "card": {
            "*": {
                "labels": [
                    {
                        "color": {"solid": {"color": "#FFFFFF"}},
                        "fontSize": 24,
                        "fontFamily": "Segoe UI Bold"
                    }
                ],
                "categoryLabels": [
                    {
                        "color": {"solid": {"color": "#94A3B8"}},
                        "fontSize": 10,
                        "fontFamily": "Segoe UI"
                    }
                ],
                "background": [
                    {
                        "show": True,
                        "color": {"solid": {"color": "#121C2E"}},
                        "transparency": 30
                    }
                ],
                "border": [
                    {
                        "show": True,
                        "color": {"solid": {"color": "#25334A"}},
                        "radius": 16
                    }
                ]
            }
        },
        "slicer": {
            "*": {
                "header": [
                    {
                        "show": True,
                        "fontColor": {"solid": {"color": "#00F2FE"}},
                        "fontSize": 10,
                        "fontFamily": "Segoe UI Semibold"
                    }
                ],
                "items": [
                    {
                        "fontColor": {"solid": {"color": "#F8FAFC"}},
                        "background": {"solid": {"color": "#121C2E"}},
                        "fontSize": 10
                    }
                ],
                "background": [
                    {
                        "show": True,
                        "color": {"solid": {"color": "#121C2E"}},
                        "transparency": 30
                    }
                ],
                "border": [
                    {
                        "show": True,
                        "color": {"solid": {"color": "#25334A"}},
                        "radius": 16
                    }
                ]
            }
        }
    }
}

# 3. Write theme files strictly in UTF-8 without BOM
theme_json_str = json.dumps(liquid_glass_theme, indent=2)
theme_bytes = theme_json_str.encode("utf-8")

theme_paths = [
    "powerbi/veyra_theme.json",
    "powerbi/Veyra_Ecommerce_Analytics.Report/StaticResources/RegisteredResources/veyra_theme.json"
]

for tp in theme_paths:
    with open(tp, "wb") as f:
        f.write(theme_bytes)
    print(f"Updated {tp} ({len(theme_bytes)} bytes, UTF-8 without BOM)")

# 4. Update report.json
report_path = "powerbi/Veyra_Ecommerce_Analytics.Report/report.json"
with open(report_path, "r", encoding="utf-8") as f:
    report_dict = json.load(f)

# Update config string
config_str = report_dict.get("config", "{}")
config_data = json.loads(config_str)
config_data["themeCollection"] = {
    "baseTheme": {
        "name": "Veyra Liquid Glass Theme",
        "reportVersionAtImport": "5.50",
        "type": 2
    }
}
report_dict["config"] = json.dumps(config_data)

# Ensure resourcePackages contains wallpaper as well
res_pkg = report_dict.get("resourcePackages", [])
if res_pkg and "items" in res_pkg[0].get("resourcePackage", {}):
    items = res_pkg[0]["resourcePackage"]["items"]
    # Check if wallpaper already listed
    has_wp = any(it.get("name") == "liquid_glass_wallpaper" for it in items)
    if not has_wp:
        items.append({
            "name": "liquid_glass_wallpaper",
            "path": "StaticResources/RegisteredResources/liquid_glass_wallpaper.jpg",
            "type": 1
        })

# Write report.json strictly UTF-8 without BOM
with open(report_path, "wb") as f:
    f.write(json.dumps(report_dict, indent=2).encode("utf-8"))
print(f"Updated {report_path} with Liquid Glass theme and wallpaper resource.")

# 5. Verification
for check_path in theme_paths + [report_path]:
    with open(check_path, "rb") as f:
        raw = f.read()
    assert not raw.startswith(b"\xef\xbb\xbf"), f"ERROR: BOM found in {check_path}"
print("All files strictly verified UTF-8 without BOM!")
