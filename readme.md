# 🚚 Shipment Analytics Dashboard

An end-to-end data analytics project that explores shipment operations, identifies logistics bottlenecks, and provides actionable business insights through an interactive Streamlit dashboard.

This project was developed as part of a Business Analyst assessment to demonstrate data cleaning, exploratory analysis, KPI development, visualization, and business decision-making using Python.

---

## 📌 Project Overview

Efficient logistics operations depend on timely deliveries, optimized freight costs, and reliable carrier performance.

Using a shipment dataset containing over **5,000 shipment records**, this project analyzes operational performance across customers, carriers, transportation modes, and regions to answer key business questions.

The project includes:

- Data cleaning and preprocessing
- Exploratory Data Analysis (EDA)
- Interactive Streamlit dashboard
- Business KPI monitoring
- Statistical analysis
- Business recommendations backed by data

---

## 🎯 Business Objectives

The analysis answers questions such as:

- Which regions have the poorest delivery performance?
- Which carriers consistently underperform?
- How does freight cost vary with shipment distance?
- Which customers experience the most delivery delays?
- What operational improvements would generate the greatest impact?

Detailed business findings are available in:

```
BUSINESS_ANSWERS.md
```

---

# 📊 Dashboard Features

The Streamlit dashboard provides interactive analytics including:

### Executive KPIs

- Total Shipments
- On-Time Delivery %
- Average Freight Cost
- Average Transit Time
- Delayed Shipment %
- Average Distance

### Operational Analysis

- Shipment status distribution
- Regional shipment analysis
- Carrier performance comparison
- Transportation mode analysis
- Customer shipment trends
- Delivery delay analysis
- Freight cost distribution
- Distance analysis

### Interactive Filters

Users can filter results by:

- Region
- Carrier
- Customer
- Shipment Status
- Transport Mode

---

# 📂 Project Structure

```
Shipment-Analytics/
│
├── app.py                      # Streamlit dashboard
├── BUSINESS_ANSWERS.md         # Business insights & recommendations
├── requirements.txt
│
├── data/
│   ├── shipments.csv
│   └── shipments_clean.csv
│
├── notebooks/
│   └── 02_shipment_analysis.ipynb
│
└── docs/
    └── shipments_profile_report.html
```

---

# 🛠️ Tech Stack

- Python
- Streamlit
- Pandas
- NumPy
- Plotly
- Matplotlib
- Scikit-learn
- Jupyter Notebook

---

# 📈 Key Insights

Some important findings from the analysis include:

### 🚛 Carrier Performance

- Carrier performance contributes more to delivery delays than geographic region.
- Several carriers consistently underperform across all regions, indicating systemic operational issues.

### 💰 Freight Cost Analysis

- Distance alone explains only a small portion of freight cost variation.
- Transportation mode significantly improves cost prediction.
- One carrier exhibits unusually high freight costs, suggesting a possible pricing or data-quality issue.

### 📦 Delivery Performance

- Regional delivery performance varies only slightly.
- Operational improvements should prioritize carrier optimization rather than regional interventions.

### 📊 Data Quality

The project identifies missing delivery dates, validates shipment records, and excludes unreliable observations to ensure accurate KPI calculations.

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/pranathiir/Shipment-Analytics.git
```

Move into the project directory

```bash
cd Shipment-Analytics
```

Create a virtual environment

```bash
python -m venv venv
```

Activate the environment

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Running the Dashboard

```bash
streamlit run app.py
```

The application will launch locally in your browser.

---

# 📊 Dataset

The dataset contains shipment-level operational information including:

- Shipment ID
- Customer
- Carrier
- Region
- Transportation Mode
- Shipment Status
- Freight Cost
- Shipment Distance
- Pickup Date
- Delivery Date
- Transit Time

---

# 📄 Business Analysis

A detailed written analysis answering the assessment questions is included in:

```
BUSINESS_ANSWERS.md
```

The notebook documents all data cleaning, statistical analysis, visualizations, and methodology used to derive these insights.

---


# ⭐ If you found this project useful

Feel free to star the repository and connect with me!
