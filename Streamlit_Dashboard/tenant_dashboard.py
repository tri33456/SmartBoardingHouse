import streamlit as st
from db import run_query


def show_tenant_dashboard(user):

    st.title("👤 Tenant Dashboard")

    room_id = user["room_id"]

    # =====================================
    # AI GAS MONITORING
    # =====================================
    st.subheader("🧠 AI Gas Prediction")

    gas_query = f"""
    SELECT gas_value
    FROM sensor_data
    WHERE room_id = {room_id}
    ORDER BY created_at DESC
    LIMIT 1
    """

    gas_df = run_query(gas_query)

    actual_gas = None

    if not gas_df.empty:

        actual_gas = int(gas_df.iloc[0]["gas_value"])
        predicted_gas = 500

        col1, col2, col3 = st.columns(3)

        col1.metric("Actual Gas", actual_gas)
        col2.metric("Predicted Gas", predicted_gas)

        if actual_gas > predicted_gas + 100 or actual_gas > 500:
            col3.error("🚨 WARNING")
        else:
            col3.success("✅ SAFE")

    st.divider()

    # =====================================
    # TEMPERATURE & HUMIDITY
    # =====================================
    st.subheader("🌡️ Environment")

    temp_query = f"""
    SELECT temperature, humidity
    FROM sensor_data
    WHERE room_id = {room_id}
    ORDER BY created_at DESC
    LIMIT 1
    """

    temp_df = run_query(temp_query)

    col1, col2 = st.columns(2)

    if not temp_df.empty:

        temperature = temp_df.iloc[0]["temperature"]
        humidity = temp_df.iloc[0]["humidity"]

        col1.metric("🌡️ Temperature", f"{temperature} °C")
        col2.metric("💧 Humidity", f"{humidity} %")

        # alerts nhẹ
        if temperature > 35:
            st.warning("🔥 Nhiệt độ trong phòng cao bất thường!")

        if humidity > 80:
            st.info("💧 Độ ẩm cao - dễ gây ẩm mốc")

    else:
        col1.metric("🌡️ Temperature", "N/A")
        col2.metric("💧 Humidity", "N/A")

    st.divider()

    # =====================================
    # METRICS (ENERGY / WATER / BILL)
    # =====================================
    metric_query = f"""
    SELECT
        MAX(energy) - MIN(energy) as total_energy,
        (MAX(total_water) - MIN(total_water))/1000 as total_water
    FROM sensor_data
    WHERE room_id = {room_id}
    """

    metric_df = run_query(metric_query)

    total_energy = 0
    total_water = 0

    if not metric_df.empty:
        total_energy = round(metric_df.iloc[0]["total_energy"] or 0, 2)
        total_water = round(metric_df.iloc[0]["total_water"] or 0, 2)

    estimated_bill = (total_energy * 3500) + (total_water * 15000)

    col1, col2, col3 = st.columns(3)

    col1.metric("⚡ Electricity Usage", f"{total_energy:.2f} kWh")
    col2.metric("🚰 Water Usage", f"{total_water:.2f} m³")
    col3.metric("💰 Estimated Bill", f"{estimated_bill:,.0f} VNĐ")

    st.divider()

    # =====================================
    # TABS
    # =====================================
    tab1, tab2 = st.tabs(["⚡ Electricity", "🚰 Water"])

    # =====================================
    # ELECTRICITY TAB
    # =====================================
    with tab1:

        st.subheader("Electricity Usage Per Month")

        electric_query = f"""
        SELECT
            DATE_FORMAT(created_at, '%%Y-%%m') as month,
            MAX(energy) - MIN(energy) as electric_usage
        FROM sensor_data
        WHERE room_id = {room_id}
        GROUP BY DATE_FORMAT(created_at, '%%Y-%%m')
        ORDER BY month
        """

        electric_df = run_query(electric_query)

        if not electric_df.empty:
            st.bar_chart(electric_df.set_index("month")["electric_usage"])

    # =====================================
    # WATER TAB
    # =====================================
    with tab2:

        st.subheader("Water Usage Per Week")

        water_query = f"""
        SELECT
            WEEK(created_at) as week,
            (MAX(total_water) - MIN(total_water))/1000 as water_usage
        FROM sensor_data
        WHERE room_id = {room_id}
        GROUP BY WEEK(created_at)
        ORDER BY week
        """

        water_df = run_query(water_query)

        if not water_df.empty:
            st.area_chart(water_df.set_index("week")["water_usage"])

    st.divider()

    # =====================================
    # BILLING
    # =====================================
    st.subheader("💵 Billing")

    billing_query = f"""
    SELECT
        electric_usage,
        water_usage,
        electric_cost,
        water_cost,
        total_amount,
        billing_month
    FROM billing
    WHERE room_id = {room_id}
    ORDER BY billing_month DESC
    """

    billing_df = run_query(billing_query)

    st.dataframe(billing_df, use_container_width=True)

    # =====================================
    # SENSOR HISTORY
    # =====================================
    with st.expander("📋 Last 50 Sensor Records"):

        sensor_query = f"""
        SELECT
            temperature,
            humidity,
            gas_value,
            total_water,
            power,
            energy,
            created_at
        FROM sensor_data
        WHERE room_id = {room_id}
        ORDER BY created_at DESC
        LIMIT 50
        """

        sensor_df = run_query(sensor_query)

        st.dataframe(sensor_df, use_container_width=True)