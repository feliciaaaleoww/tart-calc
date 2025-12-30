import streamlit as st
import pandas as pd
import json
from datetime import datetime
from collections import defaultdict
import os

st.set_page_config(page_title="Admin - Upload Orders", page_icon="👤", layout="wide")

# ------------------------ PASSWORD PROTECTION ------------------------
def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets.get("admin_password", "admin123"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password
        st.text_input(
            "🔒 Admin Password", type="password", on_change=password_entered, key="password"
        )
        st.info("Enter the admin password to access the upload interface.")
        return False
    elif not st.session_state["password_correct"]:
        # Password incorrect, show input + error
        st.text_input(
            "🔒 Admin Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct
        return True

if not check_password():
    st.stop()

# ------------------------ MAIN ADMIN INTERFACE ------------------------
st.title("👤 Admin - Upload Orders")

# Logout button
if st.button("🚪 Logout"):
    st.session_state["password_correct"] = False
    st.rerun()

st.markdown("---")

# ------------------------ RECIPES ------------------------
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

# ------------------------ UPLOAD FILES ------------------------
uploaded_files = st.file_uploader(
    "📤 Upload Order CSV Files (up to 5 files)", 
    type=["csv"], 
    accept_multiple_files=True
)

exclude_input = st.text_area(
    "🚫 Exclude Order Numbers (comma-separated)", 
    placeholder="e.g. 12040, 12041"
)
exclude_orders = [f"#{x.strip()}" for x in exclude_input.split(",") if x.strip()] if exclude_input else []

run = st.button("▶️ Process Orders & Save", type="primary")

# ------------------------ PROCESSING ------------------------
if run:
    if uploaded_files:
        # Load & Clean Files
        dfs = [pd.read_csv(f) for f in uploaded_files]
        orders_all = pd.concat(dfs, ignore_index=True)

        if exclude_orders:
            exclude_orders = [x.strip() for x in exclude_orders if x.strip()]
            orders_all = orders_all[~orders_all["Name"].isin(exclude_orders)]

        st.success(f"✅ Loaded {len(orders_all)} rows from {len(uploaded_files)} file(s).")
        st.write(f"Unique orders: {orders_all['Name'].nunique()}")

        # 1️⃣ PRODUCTION SUMMARY
        production = defaultdict(int)
        for _, row in orders_all.iterrows():
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
        extra_flavors = [f for f in production_summary_df["Flavor"] if f not in flavor_order]
        full_order = flavor_order + extra_flavors

        production_summary_df["Flavor"] = pd.Categorical(
            production_summary_df["Flavor"], categories=full_order, ordered=True
        )
        production_summary_df = production_summary_df.sort_values("Flavor")

        # 2️⃣ TOTAL SUMMARY
        totals = dict(zip(production_summary_df["Flavor"], production_summary_df["Total Qty"]))

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

        expanded_rows = []
        for _, row in orders_all.iterrows():
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
            "Cheese Tarts - 16pcs / Blueberry & Lotus Biscoff" : "Cheese Tarts - 16pcs",
            "Cheese Tarts - 25pcs / Blueberry & Lotus Biscoff" : "Cheese Tarts - 25pcs",
            "Cheese Tarts - 36pcs / Blueberry & Lotus Biscoff" : "Cheese Tarts - 36pcs",
            "Christmas Special - 1 set" : "Christmas Special"
        }
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

        # 4️⃣ PARTY SET SUMMARY
        party_sets = orders_all[
            orders_all["Lineitem name"].str.contains("Party Set|Grand Party Set|Premium Party Set", case=False, na=False)
        ]

        party_summary = pd.DataFrame()
        if not party_sets.empty:
            party_summary = (
                party_sets.groupby(["Lineitem name"], as_index=False)["Lineitem quantity"]
                .sum()
                .rename(columns={"Lineitem name": "Item Name", "Lineitem quantity": "Total Party Sets"})
            )

        # ------------------------ SAVE TO JSON ------------------------
        data_to_save = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "production_summary": production_summary_df.to_dict(orient="records"),
            "total_summary": total_summary_df.to_dict(orient="records"),
            "box_summary": box_summary.to_dict(orient="records"),
            "party_summary": party_summary.to_dict(orient="records") if not party_summary.empty else []
        }

        os.makedirs("data", exist_ok=True)
        with open("data/production_data.json", "w") as f:
            json.dump(data_to_save, f, indent=2)

        st.success("✅ **Data saved successfully!** Bakers can now view the updated counts.")

        # Display preview
        st.markdown("---")
        st.subheader("📊 Preview of Saved Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🍓 Production Summary")
            st.dataframe(production_summary_df, use_container_width=True)
            
            st.markdown("### 📦 Box Summary")
            st.dataframe(box_summary, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Total Summary")
            st.dataframe(total_summary_df, use_container_width=True)
            
            if not party_summary.empty:
                st.markdown("### 🎉 Party Set Summary")
                st.dataframe(party_summary, use_container_width=True)

    else:
        st.warning("⚠️ Please upload at least one CSV file before running.")
