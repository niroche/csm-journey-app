import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64

# App Configuration
st.set_page_config(page_title="CSM Customer Journey Generator", layout="wide")

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Your 1-Year Growth Roadmap', 0, 1, 'C')
        self.ln(5)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 10, title, 0, 1, 'L', 1)
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 7, body)
        self.ln()

def generate_journey(inputs):
    journey = []
    
    # --- MONTH 1: ONBOARDING ---
    m1_actions = []
    m1_actions.append("**Step 1: Prep Call (3-4 weeks before start)** - Introduction, goals setting, and product data collection.")
    m1_actions.append("**Step 2: Launch Call (Start Date)** - Profile presentation, training on features, and business lever explanation.")
    
    # Segment-specific Onboarding Step
    if inputs['segment'] in ["High Churn", "Low Churn", "High Churn & High AOV"]:
        m1_actions.append("**Step 3: Analytics Deep Dive** - Video call to explain the statistics module and share best practices.")
    elif inputs['segment'] == "Medium Churn":
        m1_actions.append("**Step 4: Performance Kick-off** - Baseline setup for quarterly performance tracking.")
    
    journey.append({"Month": "Month 1: Onboarding", "Focus": "Foundation & Education", "Actions": "\n".join([f"- {a}" for a in m1_actions])})

    # --- MONTHS 2-11: EXECUTION & GROWTH ---
    boosts_per_month = inputs['boosts'] // 11
    
    for month in range(2, 12):
        actions = []
        focus = "Business Generation"
        
        # Periodic Levers (Simplified for SMBs)
        if month % 2 == 0:
            actions.append("**Weekly Task: QDR Management** - Reply to every inquiry (QDR) within 24h. Quality and speed are key.")
            actions.append("**Weekly Task: Recommended RFQs** - Monitor the RFQ dashboard. Reply to leads that perfectly match your offer.")
        else:
            actions.append("**Weekly Task: Profile Visitors** - Review 'Who visited my profile'. Reach out to companies from relevant industries.")
            actions.append("**Weekly Task: Proactive Search** - Manually search for potential buyers/partners on Europages/wlw.")

        actions.append("**Ongoing: Non-Recommended RFQs** - Check RFQs that partially match your offer to expand your reach.")
        
        # Boost Management
        if boosts_per_month > 0:
            actions.append(f"**Action: Apply Boosts** - Use {boosts_per_month} boosts on your priority products: {inputs['priority_products']}.")

        # Quarterly Reviews ONLY for Medium Churn (Step 4)
        if month in [4, 7, 10] and inputs['segment'] == "Medium Churn":
            actions.append("**Step 4: Quarterly Performance Call** - Sync call with your CSM to review goals and adjust strategy.")

        # Upsell / Expansion Review
        if month == 3:
            actions.append("**Strategic Review: Top Ranking** - Are you visible enough on your core keywords? Consider buying positions 1-3.")
        if month == 6:
            actions.append("**Strategic Review: Sponsored Brands** - Boost your brand awareness with high-visibility banners.")
        if month == 9:
            actions.append("**Strategic Review: Global Expansion** - Explore AliBaba Ads or DACH region visibility (WLW add-on).")

        journey.append({"Month": f"Month {month}", "Focus": focus, "Actions": "\n".join([f"- {a}" for a in actions])})

    # --- MONTH 12: RENEWAL ---
    m12_actions = [
        "**Performance Summary** - Review all QDRs, RFQs, and leads generated during the year.",
        "**ROI Analysis** - Evaluate business value generated vs. investment.",
        "**Year 2 Planning** - Discuss contract renewal and new growth objectives."
    ]
    journey.append({"Month": "Month 12: Renewal", "Focus": "Retention & Planning", "Actions": "\n".join([f"- {a}" for a in m12_actions])})

    return pd.DataFrame(journey)

def create_pdf(df, inputs):
    pdf = PDF()
    pdf.add_page()
    
    # Helper to make text safe for FPDF Latin-1
    def safe_text(text):
        return str(text).encode('latin-1', 'replace').decode('latin-1')

    # Intro info
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, safe_text(f"Supplier: {inputs['industry']} ({inputs['supplier_type']})"), 0, 1)
    pdf.cell(0, 10, safe_text(f"Segment: {inputs['segment']} | Area: {inputs['delivery_area']}"), 0, 1)
    pdf.ln(5)
    
    for _, row in df.iterrows():
        pdf.chapter_title(safe_text(f"{row['Month']} - {row['Focus']}"))
        # Clean markdown and encode safely
        clean_actions = row['Actions'].replace('**', '').replace('- ', '  - ')
        pdf.chapter_body(safe_text(clean_actions))
        
    return pdf.output(dest='S')

# --- UI INTERFACE ---
st.title("🚀 B2B Customer Journey Generator")
st.subheader("Personalized 1-Year Roadmap for Europages & wlw")

with st.sidebar:
    st.header("📋 Client Details")
    segment = st.selectbox("Customer Segment", ["High Churn", "Medium Churn", "High Churn & High AOV", "Low Churn"])
    industry = st.text_input("Industry", "Mechanical Engineering")
    supplier_type = st.selectbox("Supplier Type", [
        "Producer/Manufacturer", 
        "Customer Specific Manufacturer", 
        "Service Provider", 
        "Distributor", 
        "Wholesaler"
    ])
    
    st.header("🌍 Reach & Strategy")
    delivery_area = st.text_input("Delivery Area", "Europe")
    visibility = st.selectbox("Visibility Scope", ["European", "Worldwide"])
    boosts = st.selectbox("Number of Boosts", [10, 25, 50])
    priority_products = st.text_area("Priority Products (to focus on)", "Industrial valves, pumps")

if st.button("Generate Roadmap"):
    inputs = {
        "segment": segment,
        "industry": industry,
        "supplier_type": supplier_type,
        "delivery_area": delivery_area,
        "visibility": visibility,
        "boosts": boosts,
        "priority_products": priority_products
    }
    
    df_journey = generate_journey(inputs)
    
    st.success(f"Roadmap generated for {industry} ({segment})")
    
    # PDF and CSV Download columns
    col_csv, col_pdf = st.columns(2)
    
    with col_csv:
        csv = df_journey.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download as CSV", csv, "customer_journey.csv", "text/csv")
        
    with col_pdf:
        pdf_data = create_pdf(df_journey, inputs)
        st.download_button(
            label="📄 Download as PDF",
            data=pdf_data,
            file_name="Customer_Journey_Roadmap.pdf",
            mime="application/pdf",
        )

    # Visual Display
    for _, row in df_journey.iterrows():
        with st.expander(f"📅 {row['Month']} - {row['Focus']}", expanded=(row['Month'] == "Month 1: Onboarding")):
            st.markdown(row['Actions'])

    st.divider()
    st.info("### 💡 Strategic Reminder for Client\n" +
            "To maximize results, consistently activate the 5 business levers: Inquiries (QDR), Recommended RFQs, Non-Recommended RFQs, Profile Visitors, and Manual Prospecting.")

else:
    st.info("Please fill in the details in the sidebar and click 'Generate Roadmap'.")
