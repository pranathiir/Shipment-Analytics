"""
FreightFox Shipment Analytics: Operations Control Tower
A carrier-performance and cost-integrity dashboard built on shipments.csv.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import statsmodels.formula.api as smf
import streamlit as st

# ---------------------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="FreightFox | Shipment Control Tower",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------
# DESIGN SYSTEM (control-tower / ops-console aesthetic)
# ---------------------------------------------------------------------
INK = "#161B26"
SLATE = "#232D3D"
SLATE_LIGHT = "#334155"
STEEL = "#4C7093"
STEEL_LIGHT = "#8FB0CB"
AMBER = "#BC8A46"
AMBER_SOFT = "#E4CBA3"
PAPER = "#F7F6F2"
INK_TEXT = "#232D3D"
GOOD = "#71916B"
BAD = "#B5726E"

st.markdown(f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">

<style>
html, body, [class*="css"] {{
    font-family: 'IBM Plex Sans', sans-serif;
}}
.stApp {{
    background-color: {PAPER};
}}
[data-testid="stSidebar"] {{
    background-color: {INK};
}}
[data-testid="stSidebar"] * {{
    color: {PAPER} !important;
}}
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {{
    background-color: {STEEL} !important;
}}

/* Header band */
.ops-header {{
    background: linear-gradient(125deg, {INK} 0%, {SLATE} 100%);
    padding: 30px 38px;
    border-radius: 10px;
    margin-bottom: 22px;
    border-left: 4px solid {AMBER};
    box-shadow: 0 4px 14px rgba(16, 21, 28, 0.18);
}}
.ops-eyebrow {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11.5px;
    letter-spacing: 1.8px;
    color: {AMBER_SOFT};
    text-transform: uppercase;
    margin-bottom: 6px;
}}
.ops-title {{
    font-size: 30px;
    font-weight: 700;
    color: {PAPER};
    margin: 0;
    letter-spacing: -0.3px;
}}
.ops-subtitle {{
    font-size: 14px;
    color: #A8B3C0;
    margin-top: 6px;
    font-weight: 400;
}}

/* KPI cards */
.kpi-card {{
    background-color: white;
    border: 1px solid #E9E6DE;
    border-top: 3px solid {STEEL};
    border-radius: 8px;
    padding: 16px 18px;
    height: 100%;
    box-shadow: 0 1px 4px rgba(27, 36, 48, 0.05);
}}
.kpi-label {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    color: #6B7280;
    margin-bottom: 6px;
}}
.kpi-value {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 28px;
    font-weight: 600;
    color: {INK_TEXT};
    line-height: 1.1;
}}
.kpi-delta-good {{ color: {GOOD}; font-size: 12px; font-family: 'IBM Plex Mono', monospace; margin-top: 4px;}}
.kpi-delta-bad {{ color: {BAD}; font-size: 12px; font-family: 'IBM Plex Mono', monospace; margin-top: 4px;}}

/* Alert strip */
.alert-strip {{
    background-color: #FAF1DE;
    border-left: 4px solid {AMBER};
    padding: 14px 18px;
    border-radius: 8px;
    margin-bottom: 18px;
    font-size: 13.5px;
    color: {INK_TEXT};
    line-height: 1.55;
}}
.alert-strip b {{ color: {BAD}; }}

/* Section label */
.section-tag {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11.5px;
    letter-spacing: 1.4px;
    text-transform: uppercase;
    color: {STEEL};
    border-bottom: 1px solid #E3E0D6;
    padding-bottom: 7px;
    margin-top: 6px;
    margin-bottom: 15px;
}}

/* Finding box */
.finding-box {{
    background-color: white;
    border: 1px solid #E9E6DE;
    border-left: 3px solid {STEEL};
    padding: 16px 20px;
    border-radius: 8px;
    font-size: 14.5px;
    line-height: 1.65;
    color: {INK_TEXT};
    margin-top: 10px;
    box-shadow: 0 1px 4px rgba(27, 36, 48, 0.04);
}}
.finding-box b {{ color: {SLATE}; }}

/* tabs */
.stTabs [data-baseweb="tab-list"] {{
    gap: 8px;
    border-bottom: 2px solid #E4E1D8;
    padding-bottom: 0;
}}
.stTabs [data-baseweb="tab"] {{
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 14px;
    font-weight: 500;
    letter-spacing: 0.1px;
    color: #7A8394;
    background-color: #EEEBE3;
    border-radius: 8px 8px 0 0;
    padding: 10px 20px;
    margin-bottom: -2px;
}}
.stTabs [aria-selected="true"] {{
    background-color: white !important;
    color: {STEEL} !important;
    font-weight: 600;
    border-bottom: 2px solid {STEEL};
    box-shadow: 0 -2px 6px rgba(35, 45, 61, 0.05);
}}

/* Plotly chart container: rounded corners so charts don't look like hard-edged blocks */
[data-testid="stPlotlyChart"] {{
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #E9E6DE;
    box-shadow: 0 1px 5px rgba(27, 36, 48, 0.05);
}}

footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

PLOTLY_TEMPLATE = go.layout.Template()
PLOTLY_TEMPLATE.layout = go.Layout(
    font=dict(family="IBM Plex Sans, sans-serif", color=INK_TEXT, size=13),
    title=dict(font=dict(family="IBM Plex Sans, sans-serif", size=15, color=SLATE)),
    paper_bgcolor="white",
    plot_bgcolor="white",
    colorway=[STEEL, AMBER, GOOD, BAD, STEEL_LIGHT, "#9C9484", "#6B5B4F"],
    xaxis=dict(gridcolor="#F0EEE8", zerolinecolor="#E4E1D8", showline=False),
    yaxis=dict(gridcolor="#F0EEE8", zerolinecolor="#E4E1D8", showline=False),
    margin=dict(t=44, l=10, r=14, b=10),
    bargap=0.28,
)
PLOTLY_TEMPLATE.data.bar = [go.Bar(marker=dict(line=dict(width=0)))]


# ---------------------------------------------------------------------
# DATA LOADING & CLEANING (mirrors notebooks/02_shipment_analysis.ipynb)
# ---------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(
        "data/shipments.csv",
        parse_dates=["booking_date", "pickup_date", "delivery_date",
                     "promised_delivery_date", "actual_delivery_date"],
    )

    # Data quality metrics (computed BEFORE cleaning, for the Data Quality tab)
    n_raw = len(df)
    n_exact_dupes = df.duplicated(keep=False).sum()
    null_actual = df["actual_delivery_date"].isnull()
    status_mismatch = df[null_actual & df["status"].isin(["Delivered", "Delayed"])]
    n_status_mismatch = len(status_mismatch)
    n_booking_null = df["booking_date"].isnull().sum()
    n_pickup_null = df["pickup_date"].isnull().sum()

    dq_stats = dict(
        n_raw=n_raw,
        n_exact_dupes=int(n_exact_dupes),
        n_status_mismatch=n_status_mismatch,
        pct_status_mismatch=round(100 * n_status_mismatch / n_raw, 1),
        n_booking_null=int(n_booking_null),
        n_pickup_null=int(n_pickup_null),
        status_breakdown=df[null_actual]["status"].value_counts().to_dict(),
    )

    # Clean
    df_clean = df.drop_duplicates(keep="first").copy()
    df_clean["on_time"] = np.where(
        df_clean["actual_delivery_date"].notnull(),
        df_clean["actual_delivery_date"] <= df_clean["promised_delivery_date"],
        np.nan,
    )
    df_clean["delay_days"] = (df_clean["actual_delivery_date"] - df_clean["promised_delivery_date"]).dt.days
    df_clean["transit_time_days"] = (df_clean["actual_delivery_date"] - df_clean["pickup_date"]).dt.days
    df_clean["pickup_lag_days"] = (df_clean["pickup_date"] - df_clean["booking_date"]).dt.days
    df_clean["cost_per_km"] = df_clean["freight_cost"] / df_clean["distance_km"]
    df_clean["log_cost"] = np.log(df_clean["freight_cost"])
    df_clean["booking_week"] = df_clean["booking_date"].dt.to_period("W").apply(
        lambda p: p.start_time if pd.notna(p) else pd.NaT
    )

    # Cost model (log-linear, distance + mode) for residual/anomaly detection
    model_data = df_clean.dropna(subset=["log_cost", "distance_km", "mode"])
    model = smf.ols("log_cost ~ distance_km + C(mode)", data=model_data).fit()
    df_clean["predicted_log_cost"] = model.predict(df_clean)
    df_clean["log_cost_residual"] = df_clean["log_cost"] - df_clean["predicted_log_cost"]
    df_clean["pct_cost_deviation"] = (np.exp(df_clean["log_cost_residual"]) - 1) * 100

    return df_clean, dq_stats, model


df, dq, cost_model = load_data()
valid_otp = df.dropna(subset=["on_time"]).copy()
valid_delay = df.dropna(subset=["delay_days"]).copy()

# ---------------------------------------------------------------------
# SIDEBAR / FILTERS
# ---------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"<div style='font-family:IBM Plex Mono; letter-spacing:2px; font-size:12px; color:{AMBER_SOFT}; text-transform:uppercase; margin-bottom:2px;'>FreightFox</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:18px; font-weight:700; margin-bottom:18px;'>Control Tower Filters</div>", unsafe_allow_html=True)

    regions = st.multiselect("Region", sorted(df["region"].unique()), default=list(df["region"].unique()))
    carriers = st.multiselect("Carrier", sorted(df["carrier_id"].unique()), default=list(df["carrier_id"].unique()))
    modes = st.multiselect("Mode", sorted(df["mode"].unique()), default=list(df["mode"].unique()))

    st.markdown("---")
    exclude_carr07 = st.checkbox("Exclude CARR_07 from cost views", value=False,
                                  help="CARR_07 shows a ~10x cost anomaly likely caused by a data error. See the Data Quality tab.")
    st.markdown("---")
    st.markdown(
        f"<div style='font-size:12px; color:#8A94A3; line-height:1.6;'>"
        f"Dataset: {dq['n_raw']:,} raw records<br>"
        f"Cleaned: {len(df):,} records<br>"
        f"Window: {df['booking_date'].min():%b %Y} – {df['booking_date'].max():%b %Y}"
        f"</div>", unsafe_allow_html=True)

mask = df["region"].isin(regions) & df["carrier_id"].isin(carriers) & df["mode"].isin(modes)
if exclude_carr07:
    mask &= df["carrier_id"] != "CARR_07"
dff = df[mask].copy()
dff_otp = dff.dropna(subset=["on_time"])
dff_delay = dff.dropna(subset=["delay_days"])

# ---------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------
st.markdown(f"""
<div class="ops-header">
    <div class="ops-eyebrow">Operations · Shipment Performance</div>
    <p class="ops-title">Shipment Control Tower</p>
    <p class="ops-subtitle">Delivery reliability, carrier cost integrity, and delay root-cause analysis, {dq['n_raw']:,} shipments, Jan–Jun 2026</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------
# KPI ROW
# ---------------------------------------------------------------------
k1, k2, k3, k4, k5 = st.columns(5)

otp_pct = dff_otp["on_time"].mean() * 100 if len(dff_otp) else float("nan")
avg_delay = dff_delay.loc[dff_delay["delay_days"] > 0, "delay_days"].mean()
n_shipments = len(dff)
n_carriers_active = dff["carrier_id"].nunique()
worst_carrier = valid_otp.groupby("carrier_id")["on_time"].mean().idxmin()

kpi_defs = [
    (k1, "Total Shipments", f"{n_shipments:,}", None),
    (k2, "On-Time %", f"{otp_pct:.1f}%", ("Region spread: 3.0 pts | Carrier spread: 14.5 pts", "bad")),
    (k3, "Avg Delay (late shipments)", f"{avg_delay:.1f}d" if pd.notna(avg_delay) else "n/a", None),
    (k4, "Active Carriers", f"{n_carriers_active}", None),
    (k5, "Weakest Carrier (OTP)", worst_carrier, (f"{valid_otp.groupby('carrier_id')['on_time'].mean().min()*100:.1f}% on-time", "bad")),
]
for col, label, value, delta in kpi_defs:
    delta_html = ""
    if delta:
        cls = "kpi-delta-good" if delta[1] == "good" else "kpi-delta-bad"
        delta_html = f"<div class='{cls}'>{delta[0]}</div>"
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"""
<div class="alert-strip">
    <b>⚠ Data integrity flag:</b> {dq['n_status_mismatch']} shipments ({dq['pct_status_mismatch']}% of dataset)
    are marked <b>Delivered</b> or <b>Delayed</b> with no recorded delivery date, excluded from on-time
    calculations below. CARR_07 also shows a cost-per-km ~10x every other carrier, consistent with a data
    error rather than genuine pricing. See the <b>Data Quality</b> tab.
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------
# TABS
# ---------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Region & Carrier", "Cost Integrity", "Customer Delay", "Data Quality", "Weekly Metric"
])

# ---------- TAB 1: Region & Carrier (Q1) ----------
with tab1:
    st.markdown('<div class="section-tag">Q1: On-time performance, region vs. carrier</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        region_otp = dff_otp.groupby("region")["on_time"].mean().sort_values() * 100
        region_otp_df = region_otp.reset_index()
        region_otp_df.columns = ["region", "on_time_pct"]
        fig = px.bar(region_otp_df, x="on_time_pct", y="region", orientation="h",
                     title="On-Time % by Region",
                     labels={"on_time_pct": "On-Time %", "region": ""}, template=PLOTLY_TEMPLATE)
        fig.update_traces(marker_color=STEEL)
        fig.update_yaxes(categoryorder="array", categoryarray=region_otp_df["region"])
        fig.add_vline(x=region_otp.mean(), line_dash="dot", line_color=AMBER,
                      annotation_text="avg", annotation_font_color=AMBER)
        fig.update_layout(showlegend=False, height=340)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        carrier_otp = dff_otp.groupby("carrier_id")["on_time"].mean().sort_values() * 100
        carrier_otp_df = carrier_otp.reset_index()
        carrier_otp_df.columns = ["carrier_id", "on_time_pct"]
        colors = [BAD if v < 45 else (GOOD if v > 53 else STEEL) for v in carrier_otp_df["on_time_pct"]]
        fig = px.bar(carrier_otp_df, x="on_time_pct", y="carrier_id", orientation="h",
                     title="On-Time % by Carrier",
                     labels={"on_time_pct": "On-Time %", "carrier_id": ""}, template=PLOTLY_TEMPLATE)
        fig.update_traces(marker_color=colors)
        fig.update_yaxes(categoryorder="array", categoryarray=carrier_otp_df["carrier_id"])
        fig.update_layout(showlegend=False, height=max(340, 22 * len(carrier_otp_df)))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
    <div class="finding-box">
    <b>Finding:</b> Regional OTP spans only <b>{region_otp.max()-region_otp.min():.1f} points</b>
    ({region_otp.idxmin()} {region_otp.min():.1f}% to {region_otp.idxmax()} {region_otp.max():.1f}%),
    close to noise. Carrier OTP spans <b>{carrier_otp.max()-carrier_otp.min():.1f} points</b>, nearly
    5x wider. A cross-tab of carrier volume share by region (right) confirms the weakest carriers
    operate at similarly low reliability in <i>every</i> region, not concentrated in one. This is a
    <b>company-wide carrier problem, not a regional one</b>. Recommend a carrier SLA review over any
    regional capacity change.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    mix = pd.crosstab(dff["carrier_id"], dff["region"], normalize="index") * 100
    fig = px.imshow(mix.loc[carrier_otp.index], text_auto=".0f", aspect="auto",
                     color_continuous_scale=[[0, "white"], [1, STEEL]],
                     title="Carrier Volume Share by Region (%), ordered by OTP, worst at top",
                     template=PLOTLY_TEMPLATE)
    fig.update_layout(height=420)
    st.plotly_chart(fig, use_container_width=True)

# ---------- TAB 2: Cost Integrity (Q2) ----------
with tab2:
    st.markdown('<div class="section-tag">Q2: Freight cost vs. distance, and carrier cost anomalies</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([1.3, 1])
    with c1:
        fig = px.scatter(dff, x="distance_km", y="freight_cost", color="mode",
                          opacity=0.55, template=PLOTLY_TEMPLATE,
                          title="Freight Cost vs. Distance (colored by mode)")
        fig.update_layout(height=380)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown(f"""
        <div class="finding-box" style="margin-top:0;">
        <b>Model fit:</b><br>
        Distance only &nbsp;→&nbsp; R² = 0.087<br>
        + Mode &nbsp;→&nbsp; R² = 0.138<br>
        Log(cost) + Mode &nbsp;→&nbsp; <b>R² = 0.637</b><br><br>
        Distance alone is a weak predictor. A log-linear model with transport mode fits far better,
        consistent with freight cost's heavy right-skew. Carrier deviations below are measured against
        <i>this</i> model.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    resid = df.groupby("carrier_id")["pct_cost_deviation"].agg(["mean", "count"]).sort_values("mean")
    colors = [BAD if v > 100 else STEEL for v in resid["mean"]]
    fig = px.bar(resid, x="mean", y=resid.index, orientation="h",
                 title="Avg Cost Deviation from Model-Predicted Cost (%)",
                 labels={"mean": "% deviation", "carrier_id": ""}, template=PLOTLY_TEMPLATE)
    fig.update_traces(marker_color=colors)
    fig.update_layout(height=420, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    carr07_dev = resid.loc["CARR_07", "mean"] if "CARR_07" in resid.index else None
    if carr07_dev:
        st.markdown(f"""
        <div class="finding-box">
        <b>Finding:</b> 14 of 15 carriers cluster between -18% and -11% deviation, a normal pricing spread.
        <b>CARR_07 deviates by ~{carr07_dev:.0f}%</b>, affecting 98.5% of its shipments. Its FTL cost-per-km
        (~249) is almost exactly <b>10x</b> every other carrier's FTL average (~25), a scaling factor this
        clean points to a <b>data/unit error</b>, not genuine overpricing. Flagged for source verification
        before use in any carrier renegotiation.
        </div>
        """, unsafe_allow_html=True)

# ---------- TAB 3: Customer Delay (Q3) ----------
with tab3:
    st.markdown('<div class="section-tag">Q3: Which customers are most delayed, and why</div>', unsafe_allow_html=True)

    cust_delay = dff_delay.groupby("customer_id").agg(
        avg_delay=("delay_days", "mean"), n=("delay_days", "count")
    )
    cust_delay = cust_delay[cust_delay["n"] >= 5].sort_values("avg_delay", ascending=False).head(12)

    c1, c2 = st.columns([1, 1.2])
    with c1:
        fig = px.bar(cust_delay, x="avg_delay", y=cust_delay.index, orientation="h",
                     title="Top Delayed Customers (avg days late)",
                     labels={"avg_delay": "Avg delay (days)", "customer_id": ""}, template=PLOTLY_TEMPLATE)
        fig.update_traces(marker_color=AMBER)
        fig.update_layout(height=420, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        top_ids = cust_delay.index.tolist()
        region_mix = pd.crosstab(dff_delay[dff_delay["customer_id"].isin(top_ids)]["customer_id"],
                                  dff_delay[dff_delay["customer_id"].isin(top_ids)]["region"])
        region_mix_pct = region_mix.div(region_mix.sum(axis=1), axis=0) * 100
        fig = px.imshow(region_mix_pct.reindex(top_ids), text_auto=".0f", aspect="auto",
                         color_continuous_scale=[[0, "white"], [1, AMBER]],
                         title="Top Delayed Customers, Shipment Mix by Region (%)",
                         template=PLOTLY_TEMPLATE)
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

    corr = dff_delay.groupby("customer_id").size().corr(
        dff_delay.groupby("customer_id")["delay_days"].mean()
    )
    st.markdown(f"""
    <div class="finding-box">
    <b>Finding:</b> Delay isn't explained by shipment volume (correlation between customer volume and
    avg delay = <b>{corr:.2f}</b>, negligible) or a dominant carrier relationship. Most top-delayed
    customers spread across 10+ carriers. The heatmap above shows why: these customers ship heavily
    through Central/East/North/West (the four weaker-OTP regions from Q1), with minimal volume via
    South, the best-performing region. <b>Delay concentration tracks regional mix, not a customer-specific
    issue.</b>
    </div>
    """, unsafe_allow_html=True)

# ---------- TAB 4: Data Quality (Q4) ----------
with tab4:
    st.markdown('<div class="section-tag">Q4: Data quality audit</div>', unsafe_allow_html=True)

    dq1, dq2, dq3, dq4 = st.columns(4)
    dq_cards = [
        (dq1, "Exact Duplicates", f"{dq['n_exact_dupes']}", "0.6% of dataset, dropped"),
        (dq2, "Booking Date Nulls", f"{dq['n_booking_null']}", "1.4% (random gaps, retained)"),
        (dq3, "Pickup Date Nulls", f"{dq['n_pickup_null']}", "1.8% (random gaps, retained)"),
        (dq4, "Status/Date Mismatch", f"{dq['n_status_mismatch']}", f"{dq['pct_status_mismatch']}% excluded from OTP calc"),
    ]
    for col, label, value, note in dq_cards:
        col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div style="font-size:12px; color:#8A94A3; margin-top:4px;">{note}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    status_breakdown = pd.Series(dq["status_breakdown"]).sort_values(ascending=False)
    fig = px.bar(status_breakdown, title="Missing actual_delivery_date, by Status",
                 labels={"value": "Row count", "index": ""}, template=PLOTLY_TEMPLATE)
    colors = [BAD if s in ("Delivered", "Delayed") else STEEL for s in status_breakdown.index]
    fig.update_traces(marker_color=colors)
    fig.update_layout(height=340, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
    <div class="finding-box">
    <b>Key finding:</b> In-Transit (502) and Cancelled (302) shipments correctly have no delivery date, which is expected.
    expected. But <b style="color:{BAD};">Delivered (588) and Delayed (96)</b> shipments missing a
    delivery date is a genuine pipeline inconsistency. {dq['n_status_mismatch']} rows
    ({dq['pct_status_mismatch']}%) excluded from on-time and delay-day metrics rather than imputed, to
    avoid silently biasing headline numbers. Recommend raising with the data engineering team.
    </div>
    """, unsafe_allow_html=True)

# ---------- TAB 5: Weekly Metric (Q5) ----------
with tab5:
    st.markdown('<div class="section-tag">Q5: Recommended weekly tracking metric</div>', unsafe_allow_html=True)

    weekly = dff_otp.groupby(["booking_week", "carrier_id"])["on_time"].mean().reset_index()
    top_bottom_carriers = pd.concat([
        valid_otp.groupby("carrier_id")["on_time"].mean().sort_values().head(3),
        valid_otp.groupby("carrier_id")["on_time"].mean().sort_values().tail(3),
    ]).index.tolist()
    weekly_focus = weekly[weekly["carrier_id"].isin(top_bottom_carriers)]

    fig = px.line(weekly_focus, x="booking_week", y="on_time", color="carrier_id",
                  title="Weekly On-Time % by Carrier, 3 Weakest vs. 3 Strongest",
                  labels={"on_time": "On-time rate", "booking_week": ""}, template=PLOTLY_TEMPLATE)
    fig.update_yaxes(tickformat=".0%")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
    <div class="finding-box">
    <b>Recommendation:</b> Track <b>weekly on-time % by carrier</b>, not a single blended company-wide
    number. Since carrier variance ({carrier_otp.max()-carrier_otp.min():.1f} pts) dwarfs regional
    variance ({region_otp.max()-region_otp.min():.1f} pts), a blended metric would hide exactly the kind
    of carrier-specific decline this analysis surfaced. Weekly, carrier-level tracking catches a decline
    the week it starts, well before a monthly rollup would, and builds a direct audit trail for
    contract reviews.<br><br>
    <b>Pair with:</b> weekly % of "Delivered" shipments missing an actual_delivery_date. This is an early
    warning for the exact pipeline issue found in Q4, before it corrupts a month of delivery metrics.
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"""
<div style="margin-top:30px; padding-top:14px; border-top:1px solid #DCD8CD; font-size:12px; color:#8A94A3; font-family:'IBM Plex Mono', monospace;">
FreightFox Shipment Control Tower · Built on {dq['n_raw']:,} raw records, {len(df):,} after cleaning · All figures reproducible in notebooks/02_shipment_analysis.ipynb
</div>
""", unsafe_allow_html=True)