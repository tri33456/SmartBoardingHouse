import streamlit as st
from db import run_query
import pandas as pd


# =====================================
# MAIN DASHBOARD
# =====================================
def show_landlord_dashboard():

    st.title("🏠 Landlord Dashboard - System Overview")

    # =====================================
    # 1. SYSTEM OVERVIEW METRICS
    # =====================================
    st.subheader("📊 Tổng quan hệ thống")

    overview_query = """
    SELECT
        COUNT(DISTINCT room_id) as total_rooms
    FROM rooms
    """
    rooms_df = run_query(overview_query)
    total_rooms = int(rooms_df.iloc[0]["total_rooms"])

    revenue_query = """
    SELECT COALESCE(SUM(total_amount),0) as revenue
    FROM billing
    """
    revenue_df = run_query(revenue_query)
    revenue = float(revenue_df.iloc[0]["revenue"])

    energy_query = """
    SELECT SUM(diff_energy) as total_energy
    FROM (
        SELECT
            room_id,
            MAX(energy) - MIN(energy) as diff_energy
        FROM sensor_data
        GROUP BY room_id
    ) t
    """
    energy_df = run_query(energy_query)
    total_energy = float(energy_df.iloc[0]["total_energy"] or 0)

    water_query = """
    SELECT SUM(diff_water) as total_water
    FROM (
        SELECT
            room_id,
            (MAX(total_water) - MIN(total_water))/1000 as diff_water
        FROM sensor_data
        GROUP BY room_id
    ) t
    """
    water_df = run_query(water_query)
    total_water = float(water_df.iloc[0]["total_water"] or 0)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🏠 Rooms", total_rooms)
    col2.metric("⚡ Electricity", f"{total_energy:.2f} kWh")
    col3.metric("🚰 Water", f"{total_water:.2f} m³")
    col4.metric("💰 Revenue", f"{revenue:,.0f} VNĐ")

    st.divider()

    # =====================================
    # 2. ROOM STATUS TABLE
    # =====================================
    st.subheader("🏠 Trạng thái phòng")

    room_status_query = """
    SELECT
        r.room_id,
        r.room_name,

        COALESCE(MAX(s.energy) - MIN(s.energy),0) as electric,
        COALESCE((MAX(s.total_water)-MIN(s.total_water))/1000,0) as water,
        MAX(s.gas_value) as gas,
        MAX(s.created_at) as last_update

    FROM rooms r
    LEFT JOIN sensor_data s ON r.room_id = s.room_id
    GROUP BY r.room_id, r.room_name
    """

    df = run_query(room_status_query)

    def get_status(row):

        if pd.isna(row["last_update"]):
            return "🔴 OFFLINE"

        if row["gas"] is not None and row["gas"] > 500:
            return "🚨 GAS WARNING"

        if row["electric"] > 1000:
            return "⚡ HIGH ELECTRIC"

        return "🟢 SAFE"

    df["status"] = df.apply(get_status, axis=1)

    st.dataframe(
        df[["room_name", "electric", "water", "status"]],
        use_container_width=True
    )

    st.divider()

    # =====================================
    # 3. TOP CONSUMPTION
    # =====================================
    st.subheader("🏆 Top tiêu thụ")

    top_query = """
    SELECT
        r.room_name,
        MAX(s.energy) - MIN(s.energy) as electric_usage
    FROM sensor_data s
    JOIN rooms r ON s.room_id = r.room_id
    GROUP BY r.room_id
    ORDER BY electric_usage DESC
    LIMIT 5
    """

    top_df = run_query(top_query)

    st.write("⚡ Top điện năng")
    st.dataframe(top_df, use_container_width=True)

    top_water_query = """
    SELECT
        r.room_name,
        (MAX(s.total_water)-MIN(s.total_water))/1000 as water_usage
    FROM sensor_data s
    JOIN rooms r ON s.room_id = r.room_id
    GROUP BY r.room_id
    ORDER BY water_usage DESC
    LIMIT 5
    """

    top_water_df = run_query(top_water_query)

    st.write("🚰 Top nước")
    st.dataframe(top_water_df, use_container_width=True)

    st.divider()

    # =====================================
    # 4. BILLING OVERVIEW
    # =====================================
    st.subheader("💰 Doanh thu & Billing")

    billing_query = """
    SELECT
        billing_month,
        SUM(total_amount) as revenue
    FROM billing
    GROUP BY billing_month
    ORDER BY billing_month DESC
    """

    billing_df = run_query(billing_query)

    st.dataframe(billing_df, use_container_width=True)

    st.divider()

    # =====================================
    # 5. GAS ALERT SYSTEM
    # =====================================
    st.subheader("🚨 Lịch sử cảnh báo Gas")

    gas_query = """
    SELECT
        r.room_name,
        s.gas_value,
        s.created_at
    FROM sensor_data s
    JOIN rooms r ON s.room_id = r.room_id
    WHERE s.gas_value > 500
    ORDER BY s.created_at DESC
    """

    gas_df = run_query(gas_query)

    if not gas_df.empty:
        st.error("🚨 Có cảnh báo gas vượt ngưỡng!")

        st.dataframe(
            gas_df.rename(columns={
                "room_name": "Phòng",
                "gas_value": "Mức Gas",
                "created_at": "Thời gian"
            }),
            use_container_width=True
        )

    else:
        st.success("✅ Không có cảnh báo gas")

    st.divider()

    # =====================================
    # 6. SENSOR LATEST ACTIVITY
    # =====================================
    st.subheader("📡 Realtime trạng thái phòng")

    realtime_query = """
    SELECT
        r.room_name,
        MAX(s.created_at) as last_update
    FROM rooms r
    LEFT JOIN sensor_data s ON r.room_id = s.room_id
    GROUP BY r.room_id
    """

    realtime_df = run_query(realtime_query)

    realtime_df["status"] = realtime_df["last_update"].apply(
        lambda x: "🟢 ONLINE" if pd.notna(x) else "🔴 OFFLINE"
    )

    st.dataframe(realtime_df, use_container_width=True)