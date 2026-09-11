"""
Vectorized generation of 2,000+ realistic product records for Veyra E-Commerce.
"""

import numpy as np
import pandas as pd
from config import (
    RAW_DATA_DIR,
    NUM_PRODUCTS,
    RANDOM_SEED,
    CATEGORIES,
    setup_logger
)

logger = setup_logger("generate_products")

def generate_products(num_products: int = NUM_PRODUCTS) -> pd.DataFrame:
    """Generates product catalog across 10 retail categories with realistic pricing and margins."""
    logger.info(f"Generating {num_products:,} product records across 10 categories...")
    rng = np.random.default_rng(RANDOM_SEED)

    category_metadata = {
        1: {
            "name": "Electronics",
            "brands": ["VeyraTech", "Sony", "Samsung", "Apple", "Dell", "Anker", "Bose", "LG", "Asus", "Logitech"],
            "items": ["Wireless Earbuds", "Smartwatch Ultra", "4K OLED Monitor", "Noise Cancelling Headphones",
                      "Mechanical Keyboard", "USB-C Hub Pro", "Portable Bluetooth Speaker", "Smartphone 5G",
                      "Gaming Mouse", "Webcam 4K HD", "External SSD 1TB", "Smart Home Hub", "Fast Wireless Charger"]
        },
        2: {
            "name": "Fashion",
            "brands": ["Veyra Apparel", "Zara", "Nike", "Adidas", "Levi's", "H&M", "Under Armour", "Calvin Klein", "Uniqlo", "Tommy Hilfiger"],
            "items": ["Slim Fit Chinos", "Classic Cotton T-Shirt", "Merino Wool Sweater", "Denim Jacket",
                      "Performance Running Shorts", "Waterproof Parka", "Tailored Blazer", "Athletic Joggers",
                      "Silk Blend Dress", "Fleece Hoodie", "Linen Casual Shirt", "Stretch Fit Jeans"]
        },
        3: {
            "name": "Home & Kitchen",
            "brands": ["VeyraHome", "Philips", "KitchenAid", "Ninja", "Instant Pot", "Cuisinart", "Dyson", "T-fal", "Nespresso", "Breville"],
            "items": ["Air Fryer Deluxe", "Espresso Machine", "Stainless Steel Cookware Set", "Robot Vacuum",
                      "Cast Iron Skillet", "Smart Electric Kettle", "High-Speed Blender", "Chef Knife 8-inch",
                      "Non-Stick Wok", "Toaster Oven Air Fryer", "French Press Coffee Maker", "Slow Cooker 6Qt"]
        },
        4: {
            "name": "Beauty",
            "brands": ["Veyra Glow", "L'Oreal", "Neutrogena", "The Ordinary", "CeraVe", "Estee Lauder", "Clinique", "Olay", "Fenty", "Kiehl's"],
            "items": ["Hydrating Hyaluronic Serum", "Daily Mineral Sunscreen SPF50", "Vitamin C Radiance Cream",
                      "Niacinamide Pore Refining Solution", "Gentle Hydrating Cleanser", "Revitalizing Night Serum",
                      "Exfoliating Facial Scrub", "Moisturizing Ceramide Balm", "Matte Velvety Lipstick", "Rosewater Toning Mist"]
        },
        5: {
            "name": "Sports & Fitness",
            "brands": ["Veyra Athletics", "Nike", "Adidas", "Bowflex", "Garmin", "Under Armour", "Lululemon", "Spalding", "Wilson", "Yeti"],
            "items": ["Adjustable Dumbbell Set", "High-Density Yoga Mat", "Insulated Sports Water Bottle",
                      "Compression Knee Sleeves", "Resistance Bands Pro Pack", "Trail Running Hydration Vest",
                      "GPS Fitness Tracker Watch", "Speed Jump Rope", "Deep Tissue Foam Roller", "Gym Duffel Bag Waterproof"]
        },
        6: {
            "name": "Grocery",
            "brands": ["Veyra Organic", "Nature Valley", "Twinings", "Lavazza", "Nestle", "Quaker", "Bob's Red Mill", "KIND", "Barilla", "Lindt"],
            "items": ["Artisan Roasted Coffee Beans", "Organic Raw Honey", "Extra Virgin Olive Oil 1L",
                      "Dark Chocolate Sea Salt Bar", "Ancient Grain Rolled Oats", "Organic Chamomile Tea",
                      "Gluten-Free Almond Flour", "Pure Maple Syrup Grade A", "Handcrafted Trail Mix", "Balsamic Vinegar of Modena"]
        },
        7: {
            "name": "Books",
            "brands": ["Penguin Random House", "HarperCollins", "Simon & Schuster", "Macmillan", "Hachette", "O'Reilly", "Wiley", "Bloomsbury"],
            "items": ["Mastering Data Analytics", "The E-Commerce Revolution", "Atomic Productivity",
                      "Principles of Modern Economics", "Deep Work and Focus", "The Future of AI & Retail",
                      "Designing Data-Intensive Systems", "The Psychology of Buying", "Global Supply Chain Essentials", "Strategic Thinking"]
        },
        8: {
            "name": "Accessories",
            "brands": ["Veyra Luxe", "Fossil", "Ray-Ban", "Bellroy", "Samsonite", "Kate Spade", "Oakley", "Herschel", "Michael Kors", "Coach"],
            "items": ["Polarized Aviator Sunglasses", "Full-Grain Leather Wallet", "Anti-Theft Commuter Backpack",
                      "Chronograph Leather Watch", "RFID Blocking Cardholder", "Canvas Weekender Duffle",
                      "Reversible Leather Belt", "Silk Travel Scarf", "Hard-Shell Passport Case", "Sterling Silver Cufflinks"]
        },
        9: {
            "name": "Furniture",
            "brands": ["Veyra Living", "Herman Miller", "IKEA", "West Elm", "Steelcase", "CB2", "Ashley Furniture", "Zinus", "Wayfair", "Article"],
            "items": ["Ergonomic Mesh Office Chair", "Electric Dual-Motor Standing Desk", "Mid-Century Modern Lounge Chair",
                      "Solid Oak Coffee Table", "Minimalist 5-Shelf Bookcase", "Velvet Accent Armchair",
                      "Queen Upholstered Bed Frame", "Industrial Dining Table Set", "Memory Foam Ergonomic Cushion", "Scandinavian Entryway Bench"]
        },
        10: {
            "name": "Toys",
            "brands": ["LEGO", "Hasbro", "Mattel", "Fisher-Price", "Melissa & Doug", "Bandai", "Funko", "Ravensburger", "Nerf", "Play-Doh"],
            "items": ["Space Exploration Building Blocks", "1000-Piece Panoramic Puzzle", "Remote Control All-Terrain Vehicle",
                      "Classic Strategy Board Game", "Educational STEM Robotics Kit", "Interactive Plush Companion",
                      "Art & Craft Studio Set", "Die-Cast Racing Car Collection", "Wooden Train Set 50-Piece", "Kinetic Sand Play Case"]
        }
    }

    products_per_cat = num_products // len(CATEGORIES)
    remainder = num_products % len(CATEGORIES)

    records = []
    prod_id_counter = 1

    # Product launch dates: 2020-01-01 to 2024-12-31
    launch_start_ts = pd.Timestamp("2020-01-01").value // 10**9
    launch_end_ts = pd.Timestamp("2024-12-31").value // 10**9

    for cat_id, cat_cfg in CATEGORIES.items():
        count = products_per_cat + (1 if cat_id <= remainder else 0)
        meta = category_metadata[cat_id]
        brands = meta["brands"]
        items = meta["items"]

        # Generate costs
        costs = rng.uniform(cat_cfg["cost_min"], cat_cfg["cost_max"], size=count)
        # Generate target margins
        margins = rng.uniform(cat_cfg["margin_min"], cat_cfg["margin_max"], size=count)
        # UnitPrice = Cost / (1 - Margin) rounded to .99 or .49
        raw_prices = costs / (1 - margins)
        # Make retail prices realistic ending in .99 or .49
        prices = np.round(raw_prices) - 0.01
        # In case price <= cost, ensure price > cost
        prices = np.maximum(prices, np.round(costs * 1.15, 2))
        costs = np.round(costs, 2)
        prices = np.round(prices, 2)

        # Launch dates
        launch_ts = rng.uniform(launch_start_ts, launch_end_ts, size=count)
        launch_dates = pd.to_datetime(launch_ts, unit='s').strftime('%Y-%m-%d')

        # Brands and Item Names
        chosen_brands = rng.choice(brands, size=count)
        chosen_items = rng.choice(items, size=count)
        modifiers = ["Pro", "Plus", "Elite", "Signature", "Classic", "Essential", "Max", "Prime", "Studio", "Ultra"]
        chosen_mods = rng.choice(modifiers, size=count)

        for i in range(count):
            prod_name = f"{chosen_brands[i]} {chosen_items[i]} {chosen_mods[i]} - Model {prod_id_counter}"
            records.append({
                "ProductID": prod_id_counter,
                "ProductName": prod_name,
                "Brand": chosen_brands[i],
                "CategoryID": cat_id,
                "CategoryName": cat_cfg["name"],
                "UnitCost": costs[i],
                "UnitPrice": prices[i],
                "ProductLaunchDate": launch_dates[i]
            })
            prod_id_counter += 1

    df = pd.DataFrame(records)
    out_file = RAW_DATA_DIR / "products.csv"
    df.to_csv(out_file, index=False)
    logger.info(f"Successfully generated {len(df):,} products -> {out_file}")
    return df

if __name__ == "__main__":
    generate_products()
