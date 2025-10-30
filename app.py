import streamlit as st
import pandas as pd
import json
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Healthcare Customer Insight Engine",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-top: 0;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for chat
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'current_context' not in st.session_state:
    st.session_state.current_context = None

# Initialize Gemini
@st.cache_resource
def init_gemini():
    """Initialize Gemini AI"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return None
    
    try:
        genai.configure(api_key=api_key)
        
        system_instruction = """You are an elite Customer Success Intelligence AI specializing in Healthcare SaaS products. 

Your expertise includes:
- Healthcare workflows (scheduling, billing, EHR integration, patient engagement)
- Compliance requirements (HIPAA, HITECH, state privacy laws)
- Provider pain points and challenges
- Financial pressures in healthcare organizations
- Key stakeholders (Practice Managers, CMOs, CFOs, IT Directors)

When analyzing customers, you:
1. Understand context from multiple data sources
2. Identify specific, actionable insights
3. Prioritize based on business impact
4. Provide clear recommendations with reasoning
5. Consider patient care impact and compliance risks

Communication style:
- Concise but thorough
- Evidence-based (cite specific data points)
- Action-oriented (always include next steps)
- Healthcare terminology when appropriate
- Empathetic to customer challenges"""
        
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash-lite-preview-06-17',
            generation_config={
                'temperature': 0.3,
                'top_k': 20,
                'top_p': 0.95,
                'max_output_tokens': 4096,
            },
            system_instruction=system_instruction
        )
        return model
    except Exception as e:
        st.error(f"Error initializing Gemini: {e}")
        return None

# Load data
@st.cache_data
def load_data():
    """Load customer data"""
    try:
        customers = pd.read_csv('healthcare_customers.csv')
        interactions = pd.read_csv('healthcare_interactions.csv')
        calls = pd.read_csv('healthcare_calls.csv')
        return customers, interactions, calls
    except FileNotFoundError as e:
        st.error(f"Error loading data: {e}")
        return None, None, None

@st.cache_data
def load_rag_documents():
    """Load RAG documents for context"""
    try:
        with open('healthcare_rag_documents.jsonl', 'r', encoding='utf-8') as f:
            docs = [json.loads(line) for line in f]
        return docs
    except FileNotFoundError:
        return []

def get_customer_context(customer_id, customers_df, interactions_df, calls_df, rag_docs):
    """Get comprehensive context for a customer"""
    
    customer = customers_df[customers_df['customer_id'] == customer_id].iloc[0]
    cust_interactions = interactions_df[interactions_df['customer_id'] == customer_id]
    cust_calls = calls_df[calls_df['customer_id'] == customer_id]
    
    rag_content = ""
    for doc in rag_docs:
        if doc.get('customer_id') == customer_id:
            rag_content = doc.get('content', '')[:2000]
            break
    
    context = f"""
CUSTOMER PROFILE: {customer['organization_name']} ({customer_id})

BASIC INFO:
- Segment: {customer['segment']}
- Monthly Revenue: ${customer['mrr']:,}
- Health Score: {customer['health_score']}/100
- Customer Since: {customer['signup_date']} ({customer['tenure_months']} months)
- Providers: {customer['num_providers']} across {customer['num_locations']} location(s)

TECHNOLOGY:
- EHR System: {customer['ehr_system']}
- Integration Status: {'✓ Integrated' if customer['ehr_integrated'] else '✗ Not Integrated'}

ACCOUNT HEALTH:
- Champion Status: {'Active' if customer['champion_exists'] else 'No active champion'}
- Payment Status: {customer['payment_status']}

RECENT ACTIVITY:
Support Interactions (Last 10):"""
    
    recent_interactions = cust_interactions.sort_values('date', ascending=False).head(10)
    for _, interaction in recent_interactions.iterrows():
        context += f"\n- [{interaction['date']}] {interaction['topic'].replace('_', ' ').title()} - {interaction['sentiment']} (Priority: {interaction['priority']})"
    
    if len(cust_calls) > 0:
        context += f"\n\nRecent Calls:"
        for _, call in cust_calls.head(5).iterrows():
            context += f"\n- [{call['date']}] {call['call_type']} - {call['sentiment']}"
    
    if rag_content:
        context += f"\n\nDETAILED ANALYSIS:\n{rag_content}"
    
    return context

def get_portfolio_context(customers_df, interactions_df):
    """Get portfolio-level context"""
    
    at_risk = len(customers_df[customers_df['health_score'] < 50])
    expansion_ready = len(customers_df[(customers_df['health_score'] > 70) & (customers_df['tenure_months'] > 6)])
    total_mrr = customers_df['mrr'].sum()
    
    top_topics = interactions_df['topic'].value_counts().head(5)
    
    context = f"""
PORTFOLIO OVERVIEW:
- Total Customers: {len(customers_df)}
- Total MRR: ${total_mrr:,}
- Average Health Score: {customers_df['health_score'].mean():.0f}/100

RISK ANALYSIS:
- At Risk (Health <50): {at_risk} customers
- Critical (Health <40): {len(customers_df[customers_df['health_score'] < 40])}

OPPORTUNITIES:
- Expansion Ready: {expansion_ready} customers

TOP SUPPORT TOPICS:
{chr(10).join([f"- {topic.replace('_', ' ').title()}: {count} tickets" for topic, count in top_topics.items()])}

CRITICAL CUSTOMERS:
{customers_df.nsmallest(5, 'health_score')[['organization_name', 'health_score', 'mrr']].to_string(index=False)}
"""
    return context

# Visualization functions
def create_health_distribution_chart(customers_df):
    """Create health score distribution chart"""
    
    # Create bins
    bins = [0, 40, 60, 75, 100]
    labels = ['Critical (<40)', 'At Risk (40-60)', 'Stable (60-75)', 'Healthy (75+)']
    customers_df['health_category'] = pd.cut(customers_df['health_score'], bins=bins, labels=labels)
    
    # Count by category
    health_counts = customers_df['health_category'].value_counts().sort_index()
    
    # Create figure
    fig = go.Figure(data=[
        go.Bar(
            x=health_counts.index,
            y=health_counts.values,
            marker_color=['#ff4444', '#ffaa00', '#ffdd00', '#44ff44'],
            text=health_counts.values,
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Customer Health Distribution",
        xaxis_title="Health Category",
        yaxis_title="Number of Customers",
        height=400,
        showlegend=False
    )
    
    return fig

def create_mrr_at_risk_chart(customers_df):
    """Create MRR at risk visualization"""
    
    risk_categories = {
        'Critical (<40)': customers_df[customers_df['health_score'] < 40]['mrr'].sum(),
        'High Risk (40-60)': customers_df[(customers_df['health_score'] >= 40) & (customers_df['health_score'] < 60)]['mrr'].sum(),
        'Medium Risk (60-75)': customers_df[(customers_df['health_score'] >= 60) & (customers_df['health_score'] < 75)]['mrr'].sum(),
        'Healthy (75+)': customers_df[customers_df['health_score'] >= 75]['mrr'].sum(),
    }
    
    fig = go.Figure(data=[
        go.Pie(
            labels=list(risk_categories.keys()),
            values=list(risk_categories.values()),
            hole=.4,
            marker_colors=['#ff4444', '#ffaa00', '#ffdd00', '#44ff44'],
            textinfo='label+percent',
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title="MRR Distribution by Risk Level",
        height=400,
        annotations=[dict(text=f'${sum(risk_categories.values())/1000:.0f}K<br>Total MRR', x=0.5, y=0.5, font_size=16, showarrow=False)]
    )
    
    return fig

def create_segment_health_chart(customers_df):
    """Create segment health comparison"""
    
    segment_stats = customers_df.groupby('segment').agg({
        'health_score': 'mean',
        'customer_id': 'count',
        'mrr': 'sum'
    }).round(1)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Avg Health Score',
        x=segment_stats.index,
        y=segment_stats['health_score'],
        marker_color='#1f77b4',
        yaxis='y',
        offsetgroup=1,
    ))
    
    fig.add_trace(go.Bar(
        name='Customer Count',
        x=segment_stats.index,
        y=segment_stats['customer_id'],
        marker_color='#ff7f0e',
        yaxis='y2',
        offsetgroup=2,
    ))
    
    fig.update_layout(
        title='Health Score & Customer Count by Segment',
        xaxis=dict(title='Segment'),
        yaxis=dict(title='Avg Health Score', side='left'),
        yaxis2=dict(title='Customer Count', overlaying='y', side='right'),
        barmode='group',
        height=400,
        legend=dict(x=0.7, y=1.1, orientation='h')
    )
    
    return fig

def create_churn_risk_timeline(customers_df):
    """Create churn risk trend"""
    
    # Simulate trend data (in real app, this would be historical)
    import numpy as np
    
    dates = pd.date_range(end=datetime.now(), periods=12, freq='W')
    
    # Simulate weekly risk counts
    critical = np.random.randint(8, 15, 12)
    high_risk = np.random.randint(15, 25, 12)
    medium = np.random.randint(20, 35, 12)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates, y=critical,
        name='Critical Risk',
        fill='tonexty',
        marker_color='#ff4444',
        stackgroup='one'
    ))
    
    fig.add_trace(go.Scatter(
        x=dates, y=high_risk,
        name='High Risk',
        fill='tonexty',
        marker_color='#ffaa00',
        stackgroup='one'
    ))
    
    fig.add_trace(go.Scatter(
        x=dates, y=medium,
        name='Medium Risk',
        fill='tonexty',
        marker_color='#ffdd00',
        stackgroup='one'
    ))
    
    fig.update_layout(
        title='Churn Risk Trend (Last 12 Weeks)',
        xaxis_title='Week',
        yaxis_title='Number of At-Risk Customers',
        height=400,
        hovermode='x unified'
    )
    
    return fig

def create_ehr_integration_chart(customers_df):
    """Create EHR integration impact chart"""
    
    # Group by EHR system
    ehr_stats = customers_df.groupby(['ehr_system', 'ehr_integrated']).agg({
        'health_score': 'mean',
        'customer_id': 'count'
    }).round(1).reset_index()
    
    fig = go.Figure()
    
    # Integrated customers
    integrated = ehr_stats[ehr_stats['ehr_integrated'] == True]
    fig.add_trace(go.Bar(
        name='Integrated',
        x=integrated['ehr_system'],
        y=integrated['health_score'],
        marker_color='#44ff44',
        text=integrated['health_score'].round(0),
        textposition='auto',
    ))
    
    # Not integrated
    not_integrated = ehr_stats[ehr_stats['ehr_integrated'] == False]
    fig.add_trace(go.Bar(
        name='Not Integrated',
        x=not_integrated['ehr_system'],
        y=not_integrated['health_score'],
        marker_color='#ff4444',
        text=not_integrated['health_score'].round(0),
        textposition='auto',
    ))
    
    fig.update_layout(
        title='Average Health Score by EHR System & Integration Status',
        xaxis_title='EHR System',
        yaxis_title='Average Health Score',
        height=400,
        barmode='group',
        legend=dict(x=0.7, y=1.1, orientation='h')
    )
    
    return fig

def create_expansion_funnel(customers_df):
    """Create expansion opportunity funnel"""
    
    total = len(customers_df)
    healthy = len(customers_df[customers_df['health_score'] > 70])
    tenure = len(customers_df[(customers_df['health_score'] > 70) & (customers_df['tenure_months'] > 6)])
    high_adoption = len(customers_df[(customers_df['health_score'] > 75) & (customers_df['tenure_months'] > 6)])
    
    fig = go.Figure(go.Funnel(
        y=['All Customers', 'Healthy (>70)', 'Tenured (>6mo)', 'High Adoption (>75)'],
        x=[total, healthy, tenure, high_adoption],
        textposition='inside',
        textinfo='value+percent initial',
        marker=dict(color=['#90caf9', '#64b5f6', '#42a5f5', '#1e88e5']),
    ))
    
    fig.update_layout(
        title='Expansion Opportunity Funnel',
        height=400
    )
    
    return fig

def create_support_topics_chart(interactions_df):
    """Create support topics breakdown"""
    
    topic_counts = interactions_df['topic'].value_counts().head(10)
    
    fig = go.Figure(data=[
        go.Bar(
            y=topic_counts.index,
            x=topic_counts.values,
            orientation='h',
            marker_color='#1f77b4',
            text=topic_counts.values,
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title='Top 10 Support Topics',
        xaxis_title='Number of Tickets',
        yaxis_title='Topic',
        height=500,
        yaxis={'categoryorder':'total ascending'}
    )
    
    return fig

# Initialize
customers_df, interactions_df, calls_df = load_data()
rag_docs = load_rag_documents()
gemini_model = init_gemini()

# Sidebar
with st.sidebar:
     st.markdown("### 🏥 CS Intelligence")
    
    st.markdown("### 💬 AI Chat Assistant")
    st.write("Ask me anything about your customers!")
    
    st.markdown("---")
    
    # API Status
    if gemini_model:
        st.success("✅ AI Connected")
    else:
        st.error("❌ AI Not Connected")
    
    st.markdown("---")
    
    # Quick stats
    if customers_df is not None:
        st.metric("Customers", f"{len(customers_df)}")
        st.metric("Total MRR", f"${customers_df['mrr'].sum()/1000:.0f}K")
        st.metric("At Risk", f"{len(customers_df[customers_df['health_score'] < 50])}")
    
    st.markdown("---")
    
    # Context selector
    st.markdown("### 🎯 Analysis Scope")
    
    analysis_scope = st.radio(
        "Focus on:",
        ["Portfolio Overview", "Specific Customer"],
    )
    
    if analysis_scope == "Specific Customer" and customers_df is not None:
        customer_list = customers_df.sort_values('health_score')[['customer_id', 'organization_name', 'health_score']]
        
        selected_customer = st.selectbox(
            "Select Customer:",
            options=customer_list['customer_id'].tolist(),
            format_func=lambda x: f"{customer_list[customer_list['customer_id']==x]['organization_name'].values[0]} ({customer_list[customer_list['customer_id']==x]['health_score'].values[0]})"
        )
        
        st.session_state.current_context = selected_customer
        
        cust = customers_df[customers_df['customer_id'] == selected_customer].iloc[0]
        st.info(f"""
**{cust['organization_name']}**
- MRR: ${cust['mrr']:,}
- Health: {cust['health_score']}/100
        """)
    else:
        st.session_state.current_context = "portfolio"
    
    st.markdown("---")
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Main content
st.markdown('<p class="main-header">🏥 Healthcare Customer Insight Engine</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-Powered Customer Intelligence with Visual Analytics</p>', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["💬 AI Chat", "📊 Analytics Dashboard", "🎯 Quick Insights"])

# TAB 1: AI Chat
with tab1:
    st.markdown("---")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about your customers..."):
        
        if not gemini_model:
            st.error("⚠️ AI not configured.")
        elif customers_df is None:
            st.error("⚠️ Data not loaded.")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("🤖 Analyzing..."):
                    try:
                        if st.session_state.current_context == "portfolio":
                            context = get_portfolio_context(customers_df, interactions_df)
                        else:
                            context = get_customer_context(
                                st.session_state.current_context,
                                customers_df,
                                interactions_df,
                                calls_df,
                                rag_docs
                            )
                        
                        full_prompt = f"""{context}

User Question: {prompt}

Provide a detailed, actionable answer."""
                        
                        response = gemini_model.generate_content(full_prompt)
                        response_text = response.text
                        
                        st.markdown(response_text)
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    # Starter questions if no messages
    if len(st.session_state.messages) == 0:
        st.info("""
        👋 **Welcome! Ask me anything about your customers.**
        
        Try:
        - "Which customers need attention today?"
        - "Show me expansion opportunities"
        - "What are the biggest product issues?"
        """)

# TAB 2: Analytics Dashboard
with tab2:
    st.header("📊 Portfolio Analytics Dashboard")
    
    if customers_df is not None:
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Customers", len(customers_df))
        with col2:
            st.metric("Total MRR", f"${customers_df['mrr'].sum()/1000:.0f}K")
        with col3:
            at_risk_count = len(customers_df[customers_df['health_score'] < 50])
            st.metric("At Risk", at_risk_count, f"{at_risk_count/len(customers_df)*100:.1f}%", delta_color="inverse")
        with col4:
            avg_health = customers_df['health_score'].mean()
            st.metric("Avg Health", f"{avg_health:.0f}", "+2 pts")
        
        st.markdown("---")
        
        # Row 1: Health Distribution and MRR at Risk
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_health_distribution_chart(customers_df), use_container_width=True)
        
        with col2:
            st.plotly_chart(create_mrr_at_risk_chart(customers_df), use_container_width=True)
        
        # Row 2: Segment Analysis and Churn Trend
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_segment_health_chart(customers_df), use_container_width=True)
        
        with col2:
            st.plotly_chart(create_churn_risk_timeline(customers_df), use_container_width=True)
        
        # Row 3: EHR Integration and Expansion Funnel
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_ehr_integration_chart(customers_df), use_container_width=True)
        
        with col2:
            st.plotly_chart(create_expansion_funnel(customers_df), use_container_width=True)
        
        # Row 4: Support Topics
        st.plotly_chart(create_support_topics_chart(interactions_df), use_container_width=True)

# TAB 3: Quick Insights
with tab3:
    st.header("🎯 Quick Insights & Actions")
    
    if customers_df is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🚨 Critical Attention Needed")
            
            critical = customers_df[customers_df['health_score'] < 40].nsmallest(5, 'health_score')
            
            for idx, cust in critical.iterrows():
                with st.expander(f"🔴 {cust['organization_name']} - ${cust['mrr']:,}"):
                    st.write(f"**Health:** {cust['health_score']}/100")
                    st.write(f"**Segment:** {cust['segment']}")
                    st.write(f"**EHR:** {cust['ehr_system']} ({'Integrated' if cust['ehr_integrated'] else 'Not Integrated'})")
                    st.write(f"**Tenure:** {cust['tenure_months']} months")
                    
                    if st.button(f"💬 Ask AI About This Customer", key=f"ask_{cust['customer_id']}"):
                        st.session_state.current_context = cust['customer_id']
                        st.session_state.messages.append({
                            "role": "user",
                            "content": f"What's the churn risk analysis for {cust['organization_name']}?"
                        })
                        st.switch_page("pages/chat.py") if "pages/chat.py" in st.session_state else st.rerun()
        
        with col2:
            st.subheader("💰 Top Expansion Opportunities")
            
            expansion = customers_df[
                (customers_df['health_score'] > 70) & 
                (customers_df['tenure_months'] > 6)
            ].nlargest(5, 'mrr')
            
            for idx, cust in expansion.iterrows():
                expansion_potential = cust['mrr'] * 0.4
                with st.expander(f"💡 {cust['organization_name']} - ${expansion_potential:,.0f} potential"):
                    st.write(f"**Current MRR:** ${cust['mrr']:,}")
                    st.write(f"**Health:** {cust['health_score']}/100")
                    st.write(f"**Segment:** {cust['segment']}")
                    st.write(f"**Providers:** {cust['num_providers']}")
                    
                    if st.button(f"💬 Get Expansion Strategy", key=f"expand_{cust['customer_id']}"):
                        st.session_state.current_context = cust['customer_id']
                        st.session_state.messages.append({
                            "role": "user",
                            "content": f"What's the expansion strategy for {cust['organization_name']}?"
                        })
                        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>Healthcare Customer Insight Engine</strong></p>
    <p>Conversational AI + Visual Analytics powered by Gemini & Plotly</p>
</div>
""", unsafe_allow_html=True)
