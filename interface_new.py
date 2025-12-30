import streamlit as st
import pandas as pd
import re
from collections import defaultdict

st.set_page_config(page_title="Order Processing", layout="wide")
st.title("📦 Order Processing Tool")

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

#     # 
#     ("Snowskin Mooncake", "5 sets"): {"Snowskin Mooncake": 5},
#     ("Snowskin Mooncake", "10 sets"): {"Snowskin Mooncake": 10},
#     ("Snowskin Mooncake", "1 set"): {"Snowskin Mooncake": 1}
# ------------------------ UPLOAD FILES ------------------------
uploaded_files = st.file_uploader(
    "Upload up to 5 CSV files (orders / pickups)", 
    type=["csv"], 
    accept_multiple_files=True
)

exclude_input = st.text_area(
    "Exclude Order Numbers (comma-separated)", 
    placeholder="e.g. 12040, 12041"
)
exclude_orders = [f"#{x.strip()}" for x in exclude_input.split(",") if x.strip()] if exclude_input else []

run = st.button("▶️ Run Processing")



# ------------------------ PROCESSING ------------------------
if run:
    if uploaded_files:
        # ======================================================
        # --- LOAD & CLEAN FILES ---
        # ======================================================
        dfs = [pd.read_csv(f) for f in uploaded_files]
        orders_all = pd.concat(dfs, ignore_index=True)

        if exclude_orders:
            exclude_orders = [x.strip() for x in exclude_orders if x.strip()]
            orders_all = orders_all[~orders_all["Name"].isin(exclude_orders)]

        st.success(f"✅ Loaded {len(orders_all)} rows from {len(uploaded_files)} file(s).")
        st.write(f"Unique orders: {orders_all['Name'].nunique()}")
        st.write(sorted(orders_all["Name"].unique()))


        # ======================================================
        # --- 1️⃣ PRODUCTION SUMMARY ---
        # ======================================================
        production = defaultdict(int)
        for _, row in orders_all.iterrows():
            key = str(row["Lineitem name"]).strip()
            qty = int(row["Lineitem quantity"])
            if key in recipes:
                for flavor, qty_per_item in recipes[key].items():
                    production[flavor] += qty_per_item * qty
            else:
                print(f"Warning: recipe not found for {key}")

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

        st.subheader("🍓 Production Summary")
        st.dataframe(production_summary_df)


        # ======================================================
        # --- 2️⃣ TOTAL SUMMARY ---
        # ======================================================
        def total_summary_table(summary_df):
            totals = dict(zip(summary_df["Flavor"], summary_df["Total Qty"]))

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

            return pd.DataFrame([
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

        st.subheader("📊 Total Summary")
        st.dataframe(total_summary_table(production_summary_df))


        # ======================================================
        # --- 3️⃣ BOX SUMMARY (WITH PARTY SET EXPANSION) ---
        # ======================================================
        from collections import defaultdict

        # --- Define expansion rules for party sets ---
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

            # --- Expand Party Sets into their components ---
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

        # --- Summarise expanded items ---
        expanded_df = pd.DataFrame(expanded_rows)

        # --- Normalize names ---
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

        # --- Sort logically ---
        sort_order = [
            "Assorted Tarts", "Cheese Tarts", "Fruit Tarts",
            "Chocolate Bliss", "Sweet Berry Duo", "The Tropical", "Tea par tea",
            "Christmas Special"
        ]
        box_summary["SortKey"] = box_summary["Item Name"].apply(
            lambda x: next((i for i, name in enumerate(sort_order) if name in x), 999)
        )
        box_summary = box_summary.sort_values(["SortKey", "Item Name"]).drop(columns="SortKey")

        # --- Add grand total ---
        grand_total = pd.DataFrame([{
            "Item Name": "ALL",
            "Total Boxes": box_summary["Total Boxes"].sum()
        }])
        box_summary = pd.concat([box_summary, grand_total], ignore_index=True)

        st.subheader("📦 Box Summary (Including Party Set Expansions)")
        st.dataframe(box_summary)



        # ======================================================
        # --- 4️⃣ PARTY SET SUMMARY ---
        # ======================================================
        party_sets = orders_all[
            orders_all["Lineitem name"].str.contains("Party Set|Grand Party Set|Premium Party Set", case=False, na=False)
        ]

        if not party_sets.empty:
            party_summary = (
                party_sets.groupby(["Lineitem name"], as_index=False)["Lineitem quantity"]
                .sum()
                .rename(columns={"Lineitem name": "Item Name", "Lineitem quantity": "Total Party Sets"})
            )

            st.subheader("🎉 Party Set Summary")
            st.dataframe(party_summary)

    else:
        st.warning("⚠️ Please upload at least one CSV file before running.")
else:
    st.info("Upload CSV(s) and press **Run Processing** to start.")




#         # ------------------------ PRODUCTION SUMMARY ------------------------
#         production = defaultdict(int)        
#         for _, row in orders_all.iterrows():
#             key = row["Lineitem name"].strip()
#             qty = int(row["Lineitem quantity"])

#             if key in recipes:
#                 for flavor, qty_per_item in recipes[key].items():
#                     production[flavor] += qty_per_item * qty
#             else:
#                 print(f"Warning: recipe not found for {key}")

#         flavor_order = [
#             "Strawberry", "Kiwi", "Lychee", "Mango", "Blueberry", "Peach", 
#             "Blueberry Cheese", "Lotus Biscoff Cheese",
#             "Passion Fruit", "Lemon Cheese", 
#             "Matcha", "Earl Grey", 
#             "Strawberry Cheesecake", "Blueberry Almond", 
#             "Chocolate Hazelnut", "Chocolate Pistachio"
#         ]

#         production_summary_df = pd.DataFrame([
#             {"Flavor": flavor, "Total Qty": int(total)} 
#             for flavor, total in production.items()
#         ])
#         extra_flavors = [f for f in production_summary_df["Flavor"] if f not in flavor_order]
#         full_order = flavor_order + extra_flavors

#         production_summary_df["Flavor"] = pd.Categorical(production_summary_df["Flavor"], categories=full_order, ordered=True)
#         production_summary_df = production_summary_df.sort_values("Flavor")
#         production_summary_df.to_csv("production_summary.csv", index=False)
#         st.subheader("📦 Production Summary")
#         st.dataframe(production_summary_df)

#         # ------------------------ EXPANSION MAP ------------------------
#         expansion_map = {
#             # Party Set (30~40pax)
#             ("Party Set (30~40pax)", "36pcs Fruit + 25pcs Cheese"): [
#                 ("Fruit Tarts", "36pcs"),
#                 ("Cheese Tarts", "25pcs"),
#             ],
#             ("Party Set (30~40pax)", "Type A: 36pcs Fruit + 25pcs Cheese"): [
#                 ("Fruit Tarts", "36pcs"),
#                 ("Cheese Tarts", "25pcs"),
#             ],
#             ("Party Set (30~40pax)", "36pcs Cheese + 25pcs Fruit"): [
#                 ("Cheese Tarts", "36pcs"),
#                 ("Fruit Tarts", "25pcs"),
#             ],
#             ("Party Set (30~40pax)", "Type B: 36pcs Cheese + 25pcs Fruit"): [
#                 ("Cheese Tarts", "36pcs"),
#                 ("Fruit Tarts", "25pcs"),
#             ],

#             # Grand Party Set (~50 pax & above)
#             ("Grand Party Set (~50 pax & above)", "Type A: 36pcs fruit + 36pcs fruit + 25pcs cheese"): [
#                 ("Fruit Tarts", "36pcs"),
#                 ("Fruit Tarts", "36pcs"),
#                 ("Cheese Tarts", "25pcs"),
#             ],
#             ("Grand Party Set (~50 pax & above)", "36pcs fruit + 36pcs fruit + 25pcs cheese"): [
#                 ("Fruit Tarts", "36pcs"),
#                 ("Fruit Tarts", "36pcs"),
#                 ("Cheese Tarts", "25pcs"),
#             ],
#             ("Grand Party Set (~50 pax & above)", "36pcs fruit + 36pcs cheese + 25pcs cheese"): [
#                 ("Fruit Tarts", "36pcs"),
#                 ("Cheese Tarts", "36pcs"),
#                 ("Cheese Tarts", "25pcs"),
#             ],
#             ("Grand Party Set (~50 pax & above)", "Type B: 36pcs fruit + 36pcs cheese + 25pcs cheese"): [
#                 ("Fruit Tarts", "36pcs"),
#                 ("Cheese Tarts", "36pcs"),
#                 ("Cheese Tarts", "25pcs"),
#             ],

#             # Premium Party Set (30~40pax)
#             ("Premium Party Set (30~40pax)", "16pcs + 16pcs + 16pcs + 16pcs"): [
#                 ("Tea Par-tea", "16pcs, Matcha & Earl Grey"),
#                 ("Chocolate Bliss", "16pcs, Chocolate Hazelnut & Chocolate Pistachio"),
#                 ("Sweet Berry Duo", "16pcs, Strawberry Cheesecake & Blueberry Almond"),
#                 ("The Tropical", "16pcs, Lemon Cheese & Passion Fruit"),
#             ],
#         }

#         # ------------------------ EXPAND ORDERS ------------------------
#         expanded_rows = []

#         for _, row in orders_all.iterrows():
#             item_name = str(row.get("Item Name", ""))
#             item_variant = str(row.get("Item Variant", ""))
#             qty = row.get("Quantity", 0)

#             if pd.isna(qty) or float(qty) == 0:
#                 continue
#             qty = float(qty)

#             key = (item_name, item_variant)
#             if key in expansion_map:
#                 for sub_item, sub_size in expansion_map[key]:
#                     m = re.search(r"(16pcs|25pcs|36pcs)", sub_size)
#                     box_size = m.group(1) if m else ""
#                     expanded_rows.append({
#                         "Item Name": sub_item,
#                         "Item Variant": sub_size,
#                         "Box Size": sub_size,
#                         "Quantity": qty
#                     })
#             else:
#                 m = re.search(r"(16pcs|25pcs|36pcs)", item_variant)
#                 if m:
#                     expanded_rows.append({
#                         "Item Name": item_name,
#                         "Item Variant": item_variant,
#                         "Box Size": m.group(1),
#                         "Quantity": qty
#                     })

#         expanded_df = pd.DataFrame(expanded_rows)

#         if expanded_df.empty:
#             st.warning("No matches found — sample unique values from your data:")
#             st.write(orders_all[["Item Name", "Item Variant"]].drop_duplicates().head(25))
#         else:
#             # ------------------------ SUMMARY ------------------------
#             summary_df = (
#                 expanded_df
#                 .groupby(["Item Name", "Item Variant", "Box Size"], as_index=False)["Quantity"]
#                 .sum()
#                 .rename(columns={"Quantity": "Total Boxes"})
#             )

#             grand_total = pd.DataFrame([{
#                 "Item Name": "ALL",
#                 "Item Variant": "TOTAL",
#                 "Box Size": "TOTAL",
#                 "Total Boxes": summary_df["Total Boxes"].sum()
#             }])
#             summary_df = pd.concat([summary_df, grand_total], ignore_index=True)

#             # ------------------------ TOTAL SUMMARY ------------------------
#             def total_summary_table(summary_df):
#                 totals = dict(zip(summary_df["Flavor"], summary_df["Total Qty"]))

#                 total_custard = sum(totals.get(f, 0) for f in ["Strawberry", "Kiwi", "Lychee", "Mango", "Blueberry", "Peach"])
#                 cheese_blueberry_lotus = sum(totals.get(f, 0) for f in ["Blueberry Cheese", "Lotus Biscoff Cheese"])
#                 cheese_lemon_strawberry = sum(totals.get(f, 0) for f in ["Lemon Cheese", "Strawberry Cheesecake"])
#                 total_cheese = cheese_blueberry_lotus + cheese_lemon_strawberry
#                 total_premium = sum(totals.get(f, 0) for f in [
#                     "Passion Fruit", "Lemon Cheese", "Matcha", "Earl Grey", 
#                     "Strawberry Cheesecake", "Blueberry Almond", "Chocolate Hazelnut", "Chocolate Pistachio"
#                 ])

#                 total_shells = total_custard + cheese_blueberry_lotus + total_premium
#                 butter_required = total_shells / 70

#                 summary_data = [
#                     {"Category": "Total Custard Tarts", "Total": total_custard}, #, "Color": "#fbe4d5"},
#                     {"Category": "Cheese (Blueberry & Lotus)", "Total": cheese_blueberry_lotus}, #, "Color": "white"},
#                     {"Category": "Cheese (Lemon & Strawberry)", "Total": cheese_lemon_strawberry}, #, "Color": "lightgray"},
#                     {"Category": "Total Cheese Tarts", "Total": total_cheese}, #, "Color": "lightblue"},
#                     {"Category": "Total No. of Premium", "Total": total_premium}, #, "Color": "lightgreen"},
#                     {"Category": "Total Tart Shells Required", "Total": total_shells}, #, "Color": "#fde68a"},
#                     {"Category": "Approx Butter Required", "Total": round(butter_required, 3)}, #, "Color": "#fde68a"},
#                 ]
#                 return pd.DataFrame(summary_data)

#             total_summary_df = total_summary_table(production_summary_df)

#             st.subheader("📊 Total Summary")
#             st.dataframe(total_summary_df)
#             # st.dataframe(
#             #     total_summary_df.style.apply(lambda row: [f"background-color: {row.Color}"]*len(row), axis=1)
#             # )

#             # ------------------------ BOX SUMMARY ------------------------
#             summary_df_final = (
#                 summary_df
#                 .groupby(["Item Name", "Item Variant"], as_index=False)["Total Boxes"]
#                 .sum()
#             )
#             # --- Add Mooncakes & Mixed Berries ---
#             extra_items = orders_all[
#                 orders_all["Item Name"].str.contains("Snowskin Mooncake|Mixed Berries Almond Tart|Musang King Tart", case=False, na=False)
#             ]

#             if not extra_items.empty:
#                 extra_summary = (
#                     extra_items
#                     .groupby(["Item Name", "Item Variant"], as_index=False)["Quantity"]
#                     .sum()
#                     .rename(columns={"Quantity": "Total Boxes"})
#                 )
#                 summary_df_final = pd.concat([summary_df_final, extra_summary], ignore_index=True)


#             st.subheader("📦 Box Summary")
#             st.dataframe(summary_df_final)

#             # ------------------------ DOWNLOAD OUTPUT ------------------------
#             csv = summary_df_final.to_csv(index=False).encode("utf-8")
#             st.download_button(
#                 "📥 Download Clean Summary (CSV)",
#                 csv,
#                 "clean_summary.csv",
#                 "text/csv",
#                 key="download-csv"
#             )

#             # ------------------------ PARTY SET SUMMARY ------------------------
#             party_sets = orders_all[
#                 orders_all["Item Name"].str.contains("Party Set|Grand Party Set|Premium Party Set", case=False, na=False)
#             ]

#             if not party_sets.empty:
#                 party_summary = (
#                     party_sets
#                     .groupby(["Item Name", "Item Variant"], as_index=False)["Quantity"]
#                     .sum()
#                     .rename(columns={"Quantity": "Total Party Sets"})
#                 )
#                 st.subheader("🎉 Party Sets Summary (before expansion)")
#                 st.dataframe(party_summary)

#                 # Optional: export to CSV
#                 party_csv = party_summary.to_csv(index=False).encode("utf-8")
#                 st.download_button(
#                     "📥 Download Party Sets Summary (CSV)",
#                     party_csv,
#                     "party_sets_summary.csv",
#                     "text/csv",
#                     key="download-party-csv"
#                 )


                
#     else:
#         st.warning("⚠️ Please upload at least one CSV file before running.")
# else:
#     st.info("Upload CSV(s) and press **Run Processing** to start.")
