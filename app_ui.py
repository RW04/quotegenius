# app_ui.py
import streamlit as st
import requests
import json
import pandas as pd
import time
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# Set page configuration
st.set_page_config(
    page_title="QuoteGenius - Manufacturing Quote System",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
API_URL = "http://localhost:8000"  # URL of FastAPI backend

# Initialize session state for demo mode
if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = True

if 'current_quote' not in st.session_state:
    st.session_state.current_quote = None

# Logo and header
col1, col2 = st.columns([1, 3])
with col1:
    st.image("https://via.placeholder.com/100x100.png?text=QG", width=100)
with col2:
    st.title("QuoteGenius")
    st.subheader("AI-Powered Manufacturing Quote System")

# Main navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Page", ["Dashboard", "Generate Quote", "Quote History", "Market Insights"])

# Demo mode toggle
st.sidebar.title("Demo Settings")
demo_mode = st.sidebar.checkbox("Demo Mode", value=st.session_state.demo_mode)
st.session_state.demo_mode = demo_mode

if demo_mode:
    st.sidebar.info("🔄 Demo mode is enabled. API calls will be simulated with mock data.")

if page == "Dashboard":
    st.header("Quote Performance Dashboard")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Total Quotes (YTD)", value="387")
    with col2:
        st.metric(label="Win Rate", value="63.8%", delta="+4.2%")
    with col3:
        st.metric(label="Avg. Quote Value", value="$145,750", delta="+$12,500")
    with col4:
        st.metric(label="Response Time", value="1.2 days", delta="-0.3 days")
    
    # Quotes over time chart
    st.subheader("Quote Activity")
    
    # Generate mock data for chart
    dates = [(datetime.now() - timedelta(days=x)).strftime("%Y-%m-%d") for x in range(90, 0, -1)]
    quotes_data = {
        "date": dates,
        "total_quotes": [random.randint(2, 8) for _ in range(len(dates))],
        "won_quotes": [random.randint(1, 5) for _ in range(len(dates))]
    }
    quotes_df = pd.DataFrame(quotes_data)
    
    # Calculate 7-day moving average
    quotes_df["7d_avg"] = quotes_df["total_quotes"].rolling(7).mean()
    
    # Plot chart
    fig = go.Figure()
    fig.add_bar(x=quotes_df["date"], y=quotes_df["total_quotes"], name="Total Quotes", marker_color="lightblue")
    fig.add_bar(x=quotes_df["date"], y=quotes_df["won_quotes"], name="Won Quotes", marker_color="green")
    fig.add_scatter(x=quotes_df["date"], y=quotes_df["7d_avg"], name="7-Day Avg", line=dict(color="darkblue", width=2))
    
    fig.update_layout(
        title="Quote Volume (Last 90 Days)",
        xaxis_title="Date",
        yaxis_title="Number of Quotes",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        barmode="overlay"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Quote win rate by industry
    st.subheader("Win Rate by Industry")
    
    industry_data = {
        "industry": ["Aerospace", "Automotive", "Electronics", "Medical", "Energy", "Construction"],
        "win_rate": [72.4, 58.9, 67.2, 76.8, 54.3, 61.5],
        "quote_count": [58, 76, 43, 32, 27, 41]
    }
    industry_df = pd.DataFrame(industry_data)
    
    # Create a modified version of the bar chart that properly shows quote count
    fig = px.bar(
        industry_df, 
        x="industry", 
        y="win_rate",
        text=industry_df["win_rate"].apply(lambda x: f"{x}%"),
        color="win_rate",
        color_continuous_scale=["red", "yellow", "green"],
        range_color=[50, 80],
        labels={"win_rate": "Win Rate (%)", "industry": "Industry"}
    )

    # Add a secondary y-axis with a line for quote count
    fig.add_trace(
        go.Scatter(
            x=industry_df["industry"],
            y=industry_df["quote_count"],
            mode="lines+markers",
            name="Quote Count",
            yaxis="y2",
            line=dict(color="darkblue", width=2),
            marker=dict(size=8)
        )
    )

    # Update layout to include the secondary y-axis
    fig.update_layout(
        title="Win Rate by Industry",
        yaxis=dict(title="Win Rate (%)"),
        yaxis2=dict(
            title="Quote Count",
            overlaying="y",
            side="right",
            showgrid=False
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.subheader("Recent Quote Activity")
    
    recent_quotes = [
        {"id": "Q-2025-0387", "customer": "Aerospace Dynamics", "amount": "$287,500", "status": "Won", "date": "2025-04-05"},
        {"id": "Q-2025-0386", "customer": "MediTech Solutions", "amount": "$142,800", "status": "Pending", "date": "2025-04-04"},
        {"id": "Q-2025-0385", "customer": "GreenEnergy Corp", "amount": "$98,750", "status": "Won", "date": "2025-04-03"},
        {"id": "Q-2025-0384", "customer": "Industrial Automation", "amount": "$215,300", "status": "Lost", "date": "2025-04-02"},
        {"id": "Q-2025-0383", "customer": "Precision Parts Inc", "amount": "$67,200", "status": "Won", "date": "2025-04-01"}
    ]
    
    # Create a DataFrame for the recent quotes
    recent_df = pd.DataFrame(recent_quotes)
    
    # Apply styling to the status column
    def style_status(val):
        if val == "Won":
            return "background-color: #d4edda; color: #155724"
        elif val == "Lost":
            return "background-color: #f8d7da; color: #721c24"
        else:
            return "background-color: #fff3cd; color: #856404"
    
    st.dataframe(recent_df.style.map(style_status, subset=["status"]), use_container_width=True)

elif page == "Generate Quote":
    st.header("Generate New Quote")
    
    # Customer selection
    customer_options = [
        "Aerospace Dynamics (AER001)",
        "Industrial Solutions Inc. (IND002)",
        "MedTech Innovations (MED003)",
        "Precision Manufacturing (PRE004)",
        "EnergyTech Systems (ENE005)",
        "Add New Customer..."
    ]
    
    selected_customer = st.selectbox("Select Customer", customer_options)
    
    if selected_customer == "Add New Customer...":
        with st.expander("New Customer Details", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                new_customer_name = st.text_input("Customer Name")
                new_customer_industry = st.selectbox("Industry", [
                    "Aerospace", "Automotive", "Electronics", "Medical", 
                    "Energy", "Construction", "Other"
                ])
            with col2:
                new_customer_contact = st.text_input("Primary Contact")
                new_customer_email = st.text_input("Email")
                new_customer_phone = st.text_input("Phone")
            
            st.button("Add Customer")
    
    # Project details
    st.subheader("Project Information")
    
    col1, col2 = st.columns(2)
    with col1:
        project_name = st.text_input("Project Name")
        project_description = st.text_area("Project Description", height=100)
        deadline = st.date_input("Deadline", datetime.now() + timedelta(days=30))
    
    with col2:
        labor_hours = st.number_input("Estimated Labor Hours", min_value=0, value=240)
        upload_files = st.file_uploader("Upload Specifications/Drawings", accept_multiple_files=True)
        special_requirements = st.text_area("Special Requirements/Constraints", height=100)
    
    # Materials section with dynamic rows
    st.subheader("Materials")
    
    if "materials" not in st.session_state:
        st.session_state.materials = [{"name": "", "quantity": 1, "unit": "units"}]
    
    # Function to add a new material row
    def add_material():
        st.session_state.materials.append({"name": "", "quantity": 1, "unit": "units"})
    
    # Function to remove a material row
    def remove_material(index):
        st.session_state.materials.pop(index)
    
    # Display materials table
    for i, material in enumerate(st.session_state.materials):
        col1, col2, col3, col4 = st.columns([3, 1, 1, 0.5])
        
        with col1:
            st.session_state.materials[i]["name"] = st.text_input(
                "Material Name", 
                value=material["name"], 
                key=f"mat_name_{i}"
            )
        
        with col2:
            st.session_state.materials[i]["quantity"] = st.number_input(
                "Quantity", 
                min_value=1, 
                value=material["quantity"], 
                key=f"mat_qty_{i}"
            )
        
        with col3:
            st.session_state.materials[i]["unit"] = st.selectbox(
                "Unit", 
                ["units", "kg", "lbs", "m", "ft", "sqm", "sqft", "hours"],
                index=["units", "kg", "lbs", "m", "ft", "sqm", "sqft", "hours"].index(material["unit"]),
                key=f"mat_unit_{i}"
            )
        
        with col4:
            if i > 0:  # Don't allow removing the first row
                st.button("🗑️", key=f"remove_{i}", on_click=remove_material, args=(i,))
    
    st.button("Add Material", on_click=add_material)
    
    # Generate quote button
    if st.button("Generate Quote"):
        with st.spinner("QuoteGenius AI is analyzing your project..."):
            # In demo mode, simulate API call delay
            if st.session_state.demo_mode:
                progress_bar = st.progress(0)
                
                # Display AI thinking steps
                thinking_container = st.empty()
                
                steps = [
                    "Analyzing project requirements...",
                    "Retrieving similar historical projects...",
                    "Calculating material costs...",
                    "Estimating labor requirements...",
                    "Applying business rules and pricing strategies...",
                    "Optimizing margins based on market conditions...",
                    "Generating final quote with recommendations..."
                ]
                
                for i, step in enumerate(steps):
                    thinking_container.text(step)
                    progress_bar.progress((i + 1) / len(steps))
                    time.sleep(0.8)
                
                # Generate a mock quote response
                mock_quote = {
                    "quote_id": f"QG-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
                    "customer_id": selected_customer.split(" (")[1][:-1] if "(" in selected_customer else "NEW001",
                    "project_name": project_name,
                    "total_price": round(random.uniform(50000, 300000), 2),
                    "breakdown": {
                        "materials": round(random.uniform(20000, 150000), 2),
                        "labor": round(labor_hours * random.uniform(85, 125), 2),
                        "equipment": round(random.uniform(5000, 30000), 2),
                        "overhead": round(random.uniform(8000, 25000), 2),
                        "profit_margin": round(random.uniform(10000, 50000), 2)
                    },
                    "confidence_score": random.randint(75, 98),
                    "recommendations": [
                        "Consider bulk ordering materials to reduce costs by approximately 8-12%",
                        "The current lead time can be reduced by 2 weeks if production begins before final approval",
                        "Similar projects typically include extended warranty options which increase margin by 5-7%",
                        "Historical data suggests offering a phased delivery plan increases win rate by 15%",
                        "Consider adding preventative maintenance package to increase total value and customer satisfaction"
                    ],
                    "generated_at": datetime.now().isoformat()
                }
                
                st.session_state.current_quote = mock_quote
            else:
                # In real mode, actually call the API
                payload = {
                    "customer_id": selected_customer.split(" (")[1][:-1] if "(" in selected_customer else "NEW001",
                    "project_name": project_name,
                    "project_description": project_description,
                    "materials": st.session_state.materials,
                    "labor_hours": labor_hours,
                    "deadline": deadline.isoformat(),
                    "special_requirements": special_requirements
                }
                
                response = requests.post(f"{API_URL}/generate-quote", json=payload)
                
                if response.status_code == 200:
                    st.session_state.current_quote = response.json()
                else:
                    st.error(f"Error generating quote: {response.text}")
        
        # Clear the progress elements
        if st.session_state.demo_mode:
            progress_bar.empty()
            thinking_container.empty()
        
        # Display the quote details
        if st.session_state.current_quote:
            quote = st.session_state.current_quote
            
            st.success(f"Quote {quote['quote_id']} generated successfully!")
            
            # Quote summary card
            st.subheader("Quote Summary")
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.info(f"**Project**: {quote['project_name']}")
                st.info(f"**Customer**: {selected_customer.split(' (')[0] if '(' in selected_customer else 'New Customer'}")
                st.info(f"**Generated**: {datetime.fromisoformat(quote['generated_at']).strftime('%B %d, %Y %H:%M')}")
            
            with col2:
                st.metric("Total Quote Value", f"${quote['total_price']:,.2f}")
                st.metric("Confidence Score", f"{quote['confidence_score']}%")
            
            with col3:
                if "optimization" in quote and "price_change_percentage" in quote["optimization"]:
                    st.metric("Price Optimization", f"{quote['optimization']['price_change_percentage']:.1f}%")
                
                # Add margin calculation
                total = quote['total_price']
                cost = sum([v for k, v in quote['breakdown'].items() if k != 'profit_margin'])
                margin_pct = (quote['breakdown']['profit_margin'] / total) * 100
                st.metric("Profit Margin", f"{margin_pct:.1f}%")
            
            # Cost breakdown
            st.subheader("Cost Breakdown")
            
            # Prepare data for pie chart
            breakdown_items = []
            breakdown_values = []
            
            for key, value in quote['breakdown'].items():
                breakdown_items.append(key.replace("_", " ").title())
                breakdown_values.append(value)
            
            breakdown_df = pd.DataFrame({
                'Category': breakdown_items,
                'Amount': breakdown_values
            })
            
            col1, col2 = st.columns([2, 3])
            
            with col1:
                # Table view
                for category, amount in zip(breakdown_items, breakdown_values):
                    st.text(f"{category}: ${amount:,.2f}")
                st.text("―" * 20)
                st.text(f"Total: ${sum(breakdown_values):,.2f}")
            
            with col2:
                # Pie chart view
                fig = px.pie(
                    breakdown_df, 
                    values='Amount', 
                    names='Category',
                    color_discrete_sequence=px.colors.sequential.Bluyl
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)
            
            # AI Recommendations
            st.subheader("AI Recommendations")
            
            for recommendation in quote['recommendations']:
                st.markdown(f"✅ {recommendation}")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.download_button(
                    "Download Quote PDF",
                    data=f"Mock PDF content for quote {quote['quote_id']}",
                    file_name=f"Quote_{quote['quote_id']}.pdf",
                    mime="application/pdf"
                )
            
            with col2:
                if st.button("Optimize Quote"):
                    with st.spinner("Optimizing quote..."):
                        time.sleep(2)
                        
                        # Update the optimization in mock quote
                        quote['total_price'] = round(quote['total_price'] * 0.95, 2)  # 5% reduction
                        quote['breakdown']['profit_margin'] = round(quote['breakdown']['profit_margin'] * 0.85, 2)
                        quote['recommendations'].append("Further reduced pricing by 5% to improve win probability based on competitive analysis")
                        quote['confidence_score'] += 5  # Increase confidence score
                        
                        st.session_state.current_quote = quote
                        st.experimental_rerun()
            
            with col3:
                st.button("Send to Customer")

elif page == "Quote History":
    st.header("Quote History")
    
    # Filter options
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.multiselect(
            "Status",
            ["All", "Won", "Lost", "Pending"],
            default=["All"]
        )
    
    with col2:
        customer_filter = st.multiselect(
            "Customer",
            ["All", "Aerospace Dynamics", "Industrial Solutions", "MedTech Innovations", "EnergyTech Systems"],
            default=["All"]
        )
    
    with col3:
        date_range = st.date_input(
            "Date Range",
            value=[datetime.now() - timedelta(days=90), datetime.now()]
        )
    
    with col4:
        min_value, max_value = st.slider(
            "Quote Value Range ($)",
            0, 500000, (0, 500000)
        )
    
    # Generate mock quote history data
    customers = ["Aerospace Dynamics", "Industrial Solutions", "MedTech Innovations", "EnergyTech Systems", 
                "Precision Manufacturing", "Global Construction"]
    statuses = ["Won", "Lost", "Pending"]
    
    history_data = []
    
    for i in range(1, 51):  # Generate 50 quotes
        quote_date = datetime.now() - timedelta(days=random.randint(1, 180))
        status = random.choices(statuses, weights=[0.6, 0.3, 0.1])[0]
        value = random.randint(25000, 400000)
        
        history_data.append({
            "id": f"Q-{quote_date.strftime('%Y')}-{i:04d}",
            "customer": random.choice(customers),
            "project": f"Project {random.choice(['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Omega'])}-{i:02d}",
            "date": quote_date.strftime("%Y-%m-%d"),
            "value": value,
            "status": status,
            "margin": random.randint(15, 35),
            "win_probability": random.randint(50, 95) if status == "Pending" else None
        })
    
    # Create DataFrame
    history_df = pd.DataFrame(history_data)
    
    # Apply filters
    filtered_df = history_df.copy()
    
    if "All" not in status_filter:
        filtered_df = filtered_df[filtered_df["status"].isin(status_filter)]
    
    if "All" not in customer_filter:
        filtered_df = filtered_df[filtered_df["customer"].isin(customer_filter)]
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[(filtered_df["date"] >= start_date.strftime("%Y-%m-%d")) & 
                                (filtered_df["date"] <= end_date.strftime("%Y-%m-%d"))]
    
    filtered_df = filtered_df[(filtered_df["value"] >= min_value) & (filtered_df["value"] <= max_value)]
    
    # Show results
    st.write(f"Found {len(filtered_df)} quotes")
    
    # Format DataFrame for display
    display_df = filtered_df.copy()
    display_df["value"] = display_df["value"].apply(lambda x: f"${x:,}")
    display_df["margin"] = display_df["margin"].apply(lambda x: f"{x}%")
    display_df["win_probability"] = display_df["win_probability"].apply(lambda x: f"{x}%" if x else "")
    
    # Apply styling based on status
    def color_status(val):
        colors = {"Won": "green", "Lost": "red", "Pending": "orange"}
        return f"color: {colors.get(val, 'black')}"
    
    st.dataframe(
        display_df.style.map(color_status, subset=["status"]),
        use_container_width=True
    )
    
    # Add a view details option
    selected_quote_id = st.selectbox("View Quote Details", ["Select a quote..."] + filtered_df["id"].tolist())
    
    if selected_quote_id != "Select a quote...":
        # In a real app, this would fetch the quote details from the API
        # For the demo, we'll just show mock data
        
        selected_row = filtered_df[filtered_df["id"] == selected_quote_id].iloc[0]
        
        st.subheader(f"Quote Details: {selected_quote_id}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"**Customer**: {selected_row['customer']}")
            st.info(f"**Project**: {selected_row['project']}")
            st.info(f"**Date**: {selected_row['date']}")
        
        with col2:
            st.metric("Quote Value", f"${selected_row['value']:,}" if isinstance(selected_row['value'], (int, float)) else selected_row['value'])
            st.metric("Margin", f"{selected_row['margin']}%" if isinstance(selected_row['margin'], (int, float)) else selected_row['margin'])
        
        with col3:
            status_color = {"Won": "success", "Lost": "error", "Pending": "warning"}
            getattr(st, status_color.get(selected_row['status'], "info"))(f"Status: {selected_row['status']}")
            
            if selected_row['status'] == "Pending":
                st.metric("Win Probability", f"{selected_row['win_probability']}%" if isinstance(selected_row['win_probability'], (int, float)) else selected_row['win_probability'])
        
        # Quote feedback (only for Won/Lost)
        if selected_row['status'] in ["Won", "Lost"]:
            st.subheader("Customer Feedback")
            
            feedback = {
                "Won": [
                    "Competitive pricing and detailed breakdown gave us confidence in your quote.",
                    "Your team's expertise in optimizing the manufacturing process was evident in the proposal.",
                    "The quote was precise and addressed all our concerns upfront."
                ],
                "Lost": [
                    "Competitor offered more aggressive pricing.",
                    "Timeline was not aligned with our project schedule.",
                    "Required modifications to meet our specific technical requirements."
                ]
            }
            
            st.info(random.choice(feedback[selected_row['status']]))

elif page == "Market Insights":
    st.header("Market Insights")
    
    # Tabs for different insights
    tab1, tab2, tab3, tab4 = st.tabs(["Price Trends", "Win Rate Analysis", "Customer Insights", "Material Costs"])
    
    with tab1:
        st.subheader("Industry Price Trends")
        
        # Mock data for price trends
        industries = ["Aerospace", "Automotive", "Electronics", "Medical", "Energy", "Construction"]
        months = [(datetime.now() - timedelta(days=30*i)).strftime("%b %Y") for i in range(12, 0, -1)]
        
        price_trends = {}
        for industry in industries:
            # Create a baseline with some randomness
            baseline = random.randint(80, 120)
            # Add some trend
            trend = random.choice([0.02, -0.01, 0.01, 0.03, -0.02])
            
            prices = []
            current = baseline
            for i in range(12):
                # Add some noise to the trend
                current = current * (1 + trend + random.uniform(-0.02, 0.02))
                prices.append(current)
            
            price_trends[industry] = prices
        
        # Create DataFrame
        trends_df = pd.DataFrame(price_trends, index=months)
        
        # Plot
        fig = px.line(trends_df, markers=True)
        fig.update_layout(
            title="Average Quote Prices by Industry (12-Month Trend)",
            xaxis_title="Month",
            yaxis_title="Relative Price Index (100 = Baseline)",
            legend_title="Industry"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        ### Key Observations
        - **Aerospace** shows consistent price increases due to material supply constraints
        - **Medical** sector experiencing high demand, driving price increases
        - **Automotive** prices stabilizing after earlier fluctuations
        - **Construction** showing seasonal variations aligned with project cycles
        """)
    
    with tab2:
        st.subheader("Win Rate Analysis")
        
        # Mock data for win rates by different factors
        
        # 1. Win Rate by Quote Response Time
        response_data = {
            "response_time": ["Same Day", "1-2 Days", "3-5 Days", "6+ Days"],
            "win_rate": [72.5, 65.2, 48.7, 31.9]
        }
        response_df = pd.DataFrame(response_data)
        
        fig1 = px.bar(
            response_df,
            x="response_time",
            y="win_rate",
            text=response_df["win_rate"].apply(lambda x: f"{x}%"),
            title="Win Rate by Quote Response Time",
            labels={"response_time": "Response Time", "win_rate": "Win Rate (%)"},
            color="win_rate",
            color_continuous_scale=["red", "yellow", "green"],
            range_color=[30, 80]
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # 2. Win Rate by Quote Value Range
        value_data = {
            "value_range": ["<$50K", "$50K-$100K", "$100K-$200K", "$200K-$500K", ">$500K"],
            "win_rate": [68.2, 59.7, 62.4, 57.8, 43.5],
            "quote_count": [120, 95, 73, 45, 18]
        }
        value_df = pd.DataFrame(value_data)
        
        # Fixed version of win rate by quote value chart
        fig2 = px.bar(
            value_df,
            x="value_range",
            y="win_rate",
            text=value_df["win_rate"].apply(lambda x: f"{x}%"),
            title="Win Rate by Quote Value",
            labels={"value_range": "Quote Value Range", "win_rate": "Win Rate (%)"},
            color="win_rate",
            color_continuous_scale=["red", "yellow", "green"],
            range_color=[40, 70]
        )

        # Add a secondary axis for quote count
        fig2.add_trace(
            go.Scatter(
                x=value_df["value_range"],
                y=value_df["quote_count"],
                mode="lines+markers",
                name="Quote Count",
                yaxis="y2",
                line=dict(color="darkblue", width=2),
                marker=dict(size=8)
            )
        )

        fig2.update_layout(
            yaxis=dict(title="Win Rate (%)"),
            yaxis2=dict(
                title="Quote Count",
                overlaying="y",
                side="right",
                showgrid=False
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("""
        ### Key Insights from Win Rate Analysis
        
        - **Quick response time** is strongly correlated with higher win rates
        - Quotes under **$50K** have the highest win rate (68.2%)
        - Win probability decreases significantly for very large quotes (>$500K)
        - The **sweet spot** appears to be in the $100K-$200K range, balancing win rate with quote value
        """)
    
    with tab3:
        st.subheader("Customer Insights")
        
        # Mock data for customer insights
        customer_data = {
            "customer": ["Aerospace Dynamics", "Industrial Solutions", "MedTech Innovations", 
                        "EnergyTech Systems", "Precision Manufacturing", "Global Construction"],
            "quotes_ytd": [42, 35, 28, 22, 18, 15],
            "win_rate": [72, 65, 81, 54, 67, 60],
            "avg_value": [185000, 127500, 215000, 97500, 145000, 320000],
            "relationship_years": [5, 3, 7, 2, 4, 1]
        }
        customer_df = pd.DataFrame(customer_data)
        
        # Scatter plot of customers
        fig = px.scatter(
            customer_df,
            x="avg_value",
            y="win_rate",
            size="quotes_ytd",
            color="relationship_years",
            hover_name="customer",
            size_max=60,
            title="Customer Portfolio Analysis",
            labels={
                "avg_value": "Average Quote Value ($)",
                "win_rate": "Win Rate (%)",
                "quotes_ytd": "Number of Quotes YTD",
                "relationship_years": "Relationship Length (Years)"
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Customer segments
        st.subheader("Customer Segmentation")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Key Accounts", "3", "high-value, established relationships")
            st.markdown("""
            - Aerospace Dynamics
            - MedTech Innovations
            - Precision Manufacturing
            """)
        
        with col2:
            st.metric("Growth Targets", "2", "emerging relationships")
            st.markdown("""
            - Industrial Solutions
            - EnergyTech Systems
            """)
            
        with col3:
            st.metric("New Opportunities", "1", "new client")
            st.markdown("""
            - Global Construction
            """)
        
        st.info("""
        **AI Recommendation**: Focus on cross-selling opportunities with MedTech Innovations. 
        Historical data shows they're 75% more likely to accept quotes that include preventative 
        maintenance packages and extended warranties.
        """)
    
    with tab4:
        st.subheader("Material Cost Trends")
        
        # Mock data for material costs
        materials = ["Steel", "Aluminum", "Copper", "Titanium", "Plastics", "Electronics"]
        quarters = ["Q2 2024", "Q3 2024", "Q4 2024", "Q1 2025", "Q2 2025 (Forecast)"]
        
        # Create random trends with some correlation
        base_trend = [1.0]
        for i in range(4):
            next_val = base_trend[-1] * (1 + random.uniform(-0.05, 0.08))
            base_trend.append(next_val)
        
        material_trends = {}
        for material in materials:
            # Add some correlation to base trend but with variations
            material_trend = []
            for i, base in enumerate(base_trend):
                factor = 1 + random.uniform(-0.1, 0.1)
                material_trend.append(base * factor)
            
            material_trends[material] = material_trend
        
        # Create DataFrame
        materials_df = pd.DataFrame(material_trends, index=quarters)
        
        # Plot
        fig = px.line(materials_df, markers=True)
        fig.update_layout(
            title="Material Cost Index Trends (Base 1.0 = Q2 2024)",
            xaxis_title="Quarter",
            yaxis_title="Cost Index",
            legend_title="Material"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        ### Material Cost Insights
        
        - **Titanium** prices showing significant volatility due to supply chain constraints
        - **Electronics** components experiencing continued upward pressure
        - **Steel** prices stabilizing after previous increases
        - **Plastics** expected to see moderate increases in coming quarter
        
        **Recommendation**: Consider locking in pricing for titanium and electronic components
        to mitigate volatility risk for upcoming projects.
        """)

# Add footer with credits
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: gray; font-size: 12px;">
        QuoteGenius | AI-Powered Manufacturing Quote System | Demo Version
    </div>
    """,
    unsafe_allow_html=True
)