#!/usr/bin/env python3
"""
Shopify Order Sync Script
Fetches orders from Shopify, calculates tart production, and syncs to GitHub.
Runs automatically every hour via scheduler.
"""

import os
import json
import subprocess
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd
from dotenv import load_dotenv
import shopify

# Load environment variables
load_dotenv()

SHOPIFY_SHOP_URL = os.getenv("SHOPIFY_SHOP_URL")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
SHOPIFY_API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2024-01")

# Recipes (same as in interface_new.py)
recipes = {
    # 🎂 Mixed Berries Almond Tart
    "Mixed Berries Almond Tart - 9\" Ring / Candle & Knife": {"Mixed Berries Almond Tart 9\" Ring / Candle & Knife": 1},
    "Mixed Berries Almond Tart - 9\" / Candle & Knife": {"Mixed Berries Almond Tart 9\" / Candle & Knife": 1},
    "Mixed Berries Almond Tart - 7\" / Candle & Knife": {"Mixed Berries Almond Tart 7\" / Candle & Knife": 1},
    "Mixed Berries Almond Tart - 9\" Ring / No Candle & Knife": {"Mixed Berries Almond Tart 9\" Ring / No Candle & Knife": 1},
    "Mixed Berries Almond Tart - 9\" / No Candle & Knife": {"Mixed Berries Almond Tart 9\" / No Candle & Knife": 1},
    "Mixed Berries Almond Tart - 7\" / No Candle & Knife": {"Mixed Berries Almond Tart 7\" / No Candle & Knife": 1},

    # 🎉 Grand & Party Sets
    "Grand Party Set - Type B: 36 Fruit + 36 Cheese + 25 Cheese": {
        "Strawberry": 6, "Kiwi": 6, "Lychee": 6, "Mango": 6, "Blueberry": 6, "Peach": 6,
        "Blueberry Cheese": 31, "Lotus Biscoff Cheese": 30
    },
    "Grand Party Set - Type A: 36 Fruit + 36 Fruit + 25 Cheese": {
        "Strawberry": 12, "Kiwi": 12, "Lychee": 12, "Mango": 12, "Blueberry": 12, "Peach": 12,
        "Blueberry Cheese": 13, "Lotus Biscoff Cheese": 12
    },
    "Premium Party Set": {
        "Matcha": 8, "Earl Grey": 8, "Lemon Cheese": 8, "Passion Fruit": 8,
        "Strawberry Cheesecake": 8, "Blueberry Almond": 8,
        "Chocolate Hazelnut": 8, "Chocolate Pistachio": 8
    },
    "Party Set - Type B: 36 Cheese + 25 Fruit": {
        "Strawberry": 5, "Kiwi": 5, "Lychee": 5, "Mango": 5, "Blueberry": 5, "Peach": 0,
        "Blueberry Cheese": 18, "Lotus Biscoff Cheese": 18
    },
    "Party Set - Type A: 36 Fruit + 25 Cheese": {
        "Strawberry": 6, "Kiwi": 6, "Lychee": 6, "Mango": 6, "Blueberry": 6, "Peach": 6,
        "Blueberry Cheese": 13, "Lotus Biscoff Cheese": 12
    },

    # 🥭 Musang King Tart
    "Musang King Tart (3pcs)": {"Musang King Tart (3pcs)": 1},

    # 🍓 Sweet Berry Duo
    "Sweet Berry Duo - Blueberry Almond only": {"Blueberry Almond": 16},
    "Sweet Berry Duo - Strawberry Cheesecake only": {"Strawberry Cheesecake": 16},
    "Sweet Berry Duo - Strawberry Cheesecake & Blueberry Almond": {"Strawberry Cheesecake": 8, "Blueberry Almond": 8},

    # 🍫 Chocolate Bliss
    "Chocolate Bliss - Chocolate Pistachio only": {"Chocolate Pistachio": 16},
    "Chocolate Bliss - Chocolate Hazelnut only": {"Chocolate Hazelnut": 16},
    "Chocolate Bliss - Chocolate Hazelnut & Chocolate Pistachio": {"Chocolate Hazelnut": 8, "Chocolate Pistachio": 8},

    # 🍋 The Tropical
    "The Tropical - Passionfruit only": {"Passion Fruit": 16},
    "The Tropical - Lemon Cheese only": {"Lemon Cheese": 16},
    "The Tropical - Lemon Cheese & Passionfruit": {"Lemon Cheese": 8, "Passion Fruit": 8},

    # 🍵 Tea Par-tea
    "Tea Par-tea - Earl Grey only": {"Earl Grey": 16},
    "Tea Par-tea - Matcha only": {"Matcha": 16},
    "Tea Par-tea - Matcha & Earl Grey": {"Matcha": 8, "Earl Grey": 8},

    # 🍓 Assorted Tarts
    "Assorted Tarts - 36pcs": {
        "Strawberry": 6, "Kiwi": 6, "Peach": 6, "Mango": 6,
        "Blueberry Cheese": 6, "Lotus Biscoff Cheese": 6
    },
    "Assorted Tarts - 25pcs": {
        "Strawberry": 5, "Kiwi": 5, "Peach": 0, "Mango": 5,
        "Blueberry Cheese": 5, "Lotus Biscoff Cheese": 5
    },

    # 🧀 Cheese Tarts
    "Cheese Tarts - 36pcs / Lotus Biscoff Cheese only": {"Lotus Biscoff Cheese": 36},
    "Cheese Tarts - 25pcs / Lotus Biscoff Cheese only": {"Lotus Biscoff Cheese": 25},
    "Cheese Tarts - 16pcs / Lotus Biscoff Cheese only": {"Lotus Biscoff Cheese": 16},

    "Cheese Tarts - 36pcs / Blueberry Cheese only": {"Blueberry Cheese": 36},
    "Cheese Tarts - 25pcs / Blueberry Cheese only": {"Blueberry Cheese": 25},
    "Cheese Tarts - 16pcs / Blueberry Cheese only": {"Blueberry Cheese": 16},

    "Cheese Tarts - 36pcs / Blueberry & Lotus Biscoff": {"Blueberry Cheese": 18, "Lotus Biscoff Cheese": 18},
    "Cheese Tarts - 25pcs / Blueberry & Lotus Biscoff": {"Blueberry Cheese": 13, "Lotus Biscoff Cheese": 12},
    "Cheese Tarts - 16pcs / Blueberry & Lotus Biscoff": {"Blueberry Cheese": 8, "Lotus Biscoff Cheese": 8},

    # 🍓 Fruit Tarts
    "Fruit Tarts - 36pcs": {"Strawberry": 6, "Kiwi": 6, "Lychee": 6, "Mango": 6, "Blueberry": 6, "Peach": 6},
    "Fruit Tarts - 25pcs": {"Strawberry": 5, "Kiwi": 5, "Lychee": 5, "Mango": 5, "Blueberry": 5, "Peach": 0},
    "Fruit Tarts - 16pcs": {"Strawberry": 4, "Kiwi": 4, "Lychee": 4, "Mango": 4, "Blueberry": 0, "Peach": 0},

    # Christmas Special
    "Christmas Special": {"Salted Caramel Chocolate": 5, "Christmas Matcha": 5, "Apple Crumble Cheese": 5,
                          "Pecan": 5, "Strawberry Almond": 5},
    "Christmas Special - 1 set": {"Salted Caramel Chocolate": 5, "Christmas Matcha": 5, "Apple Crumble Cheese": 5,
                          "Pecan": 5, "Strawberry Almond": 5},  
    "Christmas Special - 3 sets": {"Salted Caramel Chocolate": 15, "Christmas Matcha": 15, "Apple Crumble Cheese": 15,
                          "Pecan": 15, "Strawberry Almond": 15}
}

party_expansions = {
    "Party Set - Type A": [
        "Fruit Tarts - 36pcs",
        "Cheese Tarts - 25pcs / Blueberry & Lotus Biscoff"
    ],
    "Party Set - Type B": [
        "Cheese Tarts - 36pcs / Blueberry & Lotus Biscoff",
        "Fruit Tarts - 25pcs"
    ],
    "Grand Party Set - Type A": [
        "Fruit Tarts - 36pcs",
        "Fruit Tarts - 36pcs",
        "Cheese Tarts - 25pcs / Blueberry & Lotus Biscoff"
    ],
    "Grand Party Set - Type B": [
        "Fruit Tarts - 36pcs",
        "Cheese Tarts - 36pcs / Blueberry & Lotus Biscoff",
        "Cheese Tarts - 25pcs / Blueberry & Lotus Biscoff"
    ],
    "Premium Party Set": [
        "Chocolate Bliss",
        "Sweet Berry Duo",
        "The Tropical",
        "Tea par tea"
    ]
}


def connect_to_shopify():
    """Initialize Shopify API connection."""
    if not SHOPIFY_SHOP_URL or not SHOPIFY_ACCESS_TOKEN:
        raise ValueError("Missing Shopify credentials. Check your .env file.")
    
    shop_url = f"https://{SHOPIFY_SHOP_URL}"
    session = shopify.Session(shop_url, SHOPIFY_API_VERSION, SHOPIFY_ACCESS_TOKEN)
    shopify.ShopifyResource.activate_session(session)
    print(f"✅ Connected to Shopify: {SHOPIFY_SHOP_URL}")


import re

def fetch_orders(days_back=None):
    """Fetch all open (unfulfilled/active) orders."""
    # We fetch 'open' orders to catch pre-orders made months ago but not yet fulfilled.
    # We remove the created_at_min filter to ensure we get everything active.
    
    print(f"📥 Fetching ALL open orders (processing active pre-orders)...")
    orders = shopify.Order.find(
        status="open",
        limit=250
    )
    
    all_orders = list(orders)
    while orders.has_next_page():
        print(f"    ...fetching next page ({len(all_orders)} so far)")
        orders = orders.next_page()
        all_orders.extend(orders)
        
    print(f"✅ Found {len(all_orders)} orders in total")
    return all_orders


def extract_date_tag(tags):
    """Extract DD-MM-YYYY date tag from a comma-separated tag string."""
    if not tags:
        return None
    
    # Regex for DD-MM-YYYY
    match = re.search(r"\b(\d{2}-\d{2}-\d{4})\b", tags)
    if match:
        return match.group(1)
    return "No Date Tag"


def calculate_summary_for_group(orders_df):
    """Calculate production, box, and total summaries for a specific group of orders."""
    if orders_df.empty:
        return {}

    # 1️⃣ PRODUCTION SUMMARY
    production = defaultdict(int)
    for _, row in orders_df.iterrows():
        key = str(row["Lineitem name"]).strip()
        qty = int(row["Lineitem quantity"])
        if key in recipes:
            for flavor, qty_per_item in recipes[key].items():
                production[flavor] += qty_per_item * qty

    flavor_order = [
        "Strawberry", "Kiwi", "Lychee", "Mango", "Blueberry", "Peach",
        "Blueberry Cheese", "Lotus Biscoff Cheese",
        "Passion Fruit", "Lemon Cheese",
        "Matcha", "Earl Grey",
        "Strawberry Cheesecake", "Blueberry Almond",
        "Chocolate Hazelnut", "Chocolate Pistachio",
        "Salted Caramel Chocolate", "Christmas Matcha", "Strawberry Almond", "Apple Crumble Cheese", "Pecan"
    ]

    production_summary_df = pd.DataFrame([
        {"Flavor": f, "Total Qty": int(t)} for f, t in production.items()
    ])
    
    if not production_summary_df.empty:
        extra_flavors = [f for f in production_summary_df["Flavor"] if f not in flavor_order]
        full_order = flavor_order + extra_flavors
        production_summary_df["Flavor"] = pd.Categorical(
            production_summary_df["Flavor"], categories=full_order, ordered=True
        )
        production_summary_df = production_summary_df.sort_values("Flavor")

    # 2️⃣ TOTAL SUMMARY
    if not production_summary_df.empty:
        totals = dict(zip(production_summary_df["Flavor"], production_summary_df["Total Qty"]))
    else:
        totals = {}

    total_custard = sum(totals.get(f, 0) for f in ["Strawberry", "Kiwi", "Lychee", "Mango", "Blueberry", "Peach"])
    cheese_blueberry_lotus = sum(totals.get(f, 0) for f in ["Blueberry Cheese", "Lotus Biscoff Cheese"])
    cheese_lemon_strawberry = sum(totals.get(f, 0) for f in ["Lemon Cheese", "Strawberry Cheesecake"])
    cheese_apple = sum(totals.get(f, 0) for f in ["Apple Crumble Cheese"])
    total_cheese = cheese_blueberry_lotus + cheese_lemon_strawberry + cheese_apple

    total_premium = sum(totals.get(f, 0) for f in [
        "Passion Fruit", "Lemon Cheese", "Matcha", "Earl Grey",
        "Strawberry Cheesecake", "Blueberry Almond", "Chocolate Hazelnut", "Chocolate Pistachio"
    ])

    total_christmas = sum(totals.get(f, 0) for f in [
        "Salted Caramel Chocolate", "Christmas Matcha", "Strawberry Almond", "Apple Crumble Cheese", "Pecan"
    ])

    total_shells = total_custard + cheese_blueberry_lotus + total_premium + total_christmas
    butter_required = total_shells / 70

    total_summary_df = pd.DataFrame([
        {"Category": "Total Custard Tarts", "Total": total_custard},
        {"Category": "Cheese (Blueberry & Lotus)", "Total": cheese_blueberry_lotus},
        {"Category": "Cheese (Lemon & Strawberry)", "Total": cheese_lemon_strawberry},
        {"Category": "Cheese (Apple Crumble)", "Total": cheese_apple},
        {"Category": "Total Cheese Tarts", "Total": total_cheese},
        {"Category": "Total No. of Premium", "Total": total_premium},
        {"Category": "Total No. of Christmas", "Total": total_christmas},
        {"Category": "Total Tart Shells Required", "Total": total_shells},
        {"Category": "Approx Butter Required (kg)", "Total": round(butter_required, 3)},
    ])

    # 3️⃣ BOX SUMMARY
    expanded_rows = []
    for _, row in orders_df.iterrows():
        name = str(row["Lineitem name"]).strip()
        qty = int(row["Lineitem quantity"])

        if any(name.startswith(key) for key in party_expansions.keys()):
            for set_name, expansions in party_expansions.items():
                if name.startswith(set_name):
                    for expanded_item in expansions:
                        expanded_rows.append({
                            "Lineitem name": expanded_item,
                            "Lineitem quantity": qty
                        })
                    break
        else:
            expanded_rows.append({
                "Lineitem name": name,
                "Lineitem quantity": qty
            })

    expanded_df = pd.DataFrame(expanded_rows)
    rename_map = {
        "Tea Par-tea - Matcha & Earl Grey": "Tea par tea",
        "The Tropical - Lemon Cheese & Passionfruit": "The Tropical",
        "Sweet Berry Duo - Strawberry Cheesecake & Blueberry Almond": "Sweet Berry Duo",
        "Chocolate Bliss - Chocolate Hazelnut & Chocolate Pistachio": "Chocolate Bliss",
        "Cheese Tarts - 16pcs / Blueberry & Lotus Biscoff": "Cheese Tarts - 16pcs",
        "Cheese Tarts - 25pcs / Blueberry & Lotus Biscoff": "Cheese Tarts - 25pcs",
        "Cheese Tarts - 36pcs / Blueberry & Lotus Biscoff": "Cheese Tarts - 36pcs",
        "Christmas Special - 1 set": "Christmas Special"
    }
    if not expanded_df.empty:
        expanded_df["Lineitem name"] = expanded_df["Lineitem name"].replace(rename_map)

        box_summary = (
            expanded_df.groupby(["Lineitem name"], dropna=False, as_index=False)["Lineitem quantity"]
            .sum()
            .rename(columns={"Lineitem name": "Item Name", "Lineitem quantity": "Total Boxes"})
        )

        sort_order = [
            "Assorted Tarts", "Cheese Tarts", "Fruit Tarts",
            "Chocolate Bliss", "Sweet Berry Duo", "The Tropical", "Tea par tea",
            "Christmas Special"
        ]
        box_summary["SortKey"] = box_summary["Item Name"].apply(
            lambda x: next((i for i, name in enumerate(sort_order) if name in x), 999)
        )
        box_summary = box_summary.sort_values(["SortKey", "Item Name"]).drop(columns="SortKey")
        
        grand_total = pd.DataFrame([{
            "Item Name": "ALL",
            "Total Boxes": box_summary["Total Boxes"].sum()
        }])
        box_summary = pd.concat([box_summary, grand_total], ignore_index=True)
    else:
        box_summary = pd.DataFrame()

    # 4️⃣ PARTY SET SUMMARY
    party_sets = orders_df[
        orders_df["Lineitem name"].str.contains("Party Set|Grand Party Set|Premium Party Set", case=False, na=False)
    ]

    party_summary = pd.DataFrame()
    if not party_sets.empty:
        party_summary = (
            party_sets.groupby(["Lineitem name"], as_index=False)["Lineitem quantity"]
            .sum()
            .rename(columns={"Lineitem name": "Item Name", "Lineitem quantity": "Total Party Sets"})
        )

    return {
        "production_summary": production_summary_df.to_dict(orient="records"),
        "total_summary": total_summary_df.to_dict(orient="records"),
        "box_summary": box_summary.to_dict(orient="records") if not box_summary.empty else [],
        "party_summary": party_summary.to_dict(orient="records") if not party_summary.empty else [],
        "order_ids": sorted(list(orders_df["Name"].unique())) if not orders_df.empty else []
    }


def process_orders(orders):
    """Process orders and calculate tart production."""
    # Convert to DataFrame format
    order_data = []
    
    for order in orders:
        date_tag = extract_date_tag(order.tags)
        
        for line_item in order.line_items:
            order_data.append({
                "Name": f"#{order.order_number}",
                "Lineitem name": line_item.name,
                "Lineitem quantity": line_item.quantity,
                "DateTag": date_tag
            })
            
    if not order_data:
        print("⚠️ No line items found in orders")
        return None
    
    orders_df = pd.DataFrame(order_data)
    print(f"📊 Processing {len(orders_df)} line items from {orders_df['Name'].nunique()} orders")
    
    # Group by Date Tag
    datasets = {}
    
    # Get all unique dates found
    dates = orders_df["DateTag"].unique()
    
    for date in dates:
        print(f"   Processing date group: {date}")
        group_df = orders_df[orders_df["DateTag"] == date]
        datasets[date] = calculate_summary_for_group(group_df)
        
    return datasets


def save_data(datasets):
    """Save processed data to JSON file."""
    os.makedirs("data", exist_ok=True)
    
    data_to_save = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "datasets": datasets
    }
    
    with open("data/production_data.json", "w") as f:
        json.dump(data_to_save, f, indent=2)
    
    print("✅ Data saved to data/production_data.json")


def commit_and_push():
    """Commit and push changes to GitHub."""
    try:
        # Check if there are changes
        result = subprocess.run(
            ["git", "diff", "--quiet", "data/production_data.json"],
            cwd=os.path.dirname(__file__),
            capture_output=True
        )
        
        if result.returncode == 0:
            print("ℹ️ No changes to commit")
            return
        
        # Add, commit, and push
        subprocess.run(["git", "add", "-f", "data/production_data.json"], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"Auto-update: Shopify sync at {datetime.now().strftime('%Y-%m-%d %H:%M')}"],
            check=True
        )
        subprocess.run(["git", "push"], check=True)
        
        print("✅ Changes pushed to GitHub")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error pushing to GitHub: {e}")


def main():
    """Main sync function."""
    print(f"\n🚀 Starting Shopify sync at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Connect to Shopify
        connect_to_shopify()
        
        # Fetch all open orders (ignores archived/completed ones)
        orders = fetch_orders()
        
        if not orders:
            print("⚠️ No orders found")
            return
        
        # Process orders
        data = process_orders(orders)
        
        if not data:
            print("⚠️ No data to save")
            return
        
        # Save data
        save_data(data)
        
        # Commit and push to GitHub
        commit_and_push()
        
        print("=" * 60)
        print("✅ Sync completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during sync: {e}")
        raise
    finally:
        shopify.ShopifyResource.clear_session()


if __name__ == "__main__":
    main()
