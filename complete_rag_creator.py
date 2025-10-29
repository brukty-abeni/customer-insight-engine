import pandas as pd
import json
from datetime import datetime
import re

class CompleteHealthcareRAGGenerator:
    """
    Generate comprehensive RAG documents including conversational data
    for Healthcare SaaS customer insights
    """
    
    def __init__(self, customers_df, interactions_df, calls_df, feature_requests_df):
        self.customers = customers_df
        self.interactions = interactions_df
        self.calls = calls_df
        self.feature_requests = feature_requests_df
    
    def create_comprehensive_customer_profile(self):
        """Create rich customer profiles combining all data sources"""
        documents = []
        
        for _, customer in self.customers.iterrows():
            cust_id = customer['customer_id']
            
            # Get related data
            cust_interactions = self.interactions[
                self.interactions['customer_id'] == cust_id
            ].sort_values('date', ascending=False)
            
            cust_calls = self.calls[
                self.calls['customer_id'] == cust_id
            ].sort_values('date', ascending=False)
            
            cust_requests = self.feature_requests[
                self.feature_requests['customer_id'] == cust_id
            ].sort_values('date', ascending=False)
            
            # Calculate advanced metrics
            recent_interactions = cust_interactions.head(10)
            negative_sentiment_pct = (
                len(recent_interactions[recent_interactions['sentiment'].isin(['frustrated', 'negative', 'urgent'])]) / 
                len(recent_interactions) * 100 
                if len(recent_interactions) > 0 else 0
            )
            
            high_priority_tickets = len(cust_interactions[cust_interactions['priority'] == 'high'])
            escalated_tickets = len(cust_interactions[cust_interactions['escalated'] == True])
            
            # Identify patterns
            common_topics = cust_interactions['topic'].value_counts().head(3)
            affected_users_total = cust_interactions['affected_users'].sum()
            
            # Recent call insights
            recent_calls = cust_calls.head(3)
            expansion_mentioned = any(cust_calls['expansion_opportunity'] == True)
            churn_risk_mentioned = any(cust_calls['churn_risk_mentioned'] == True)
            
            # Build comprehensive document
            doc = f"""
═══════════════════════════════════════════════════════
COMPREHENSIVE CUSTOMER PROFILE: {cust_id}
═══════════════════════════════════════════════════════

ORGANIZATION OVERVIEW
━━━━━━━━━━━━━━━━━━━━
Organization: {customer['organization_name']}
Type: {customer['org_type']} | Specialty: {customer['specialty']}
Segment: {customer['segment']}

SCALE & SCOPE
━━━━━━━━━━━━━
• {customer['num_providers']} Providers across {customer['num_locations']} location(s)
• {customer['patients_per_month']:,} patients per month
• Monthly Revenue: ${customer['mrr']:,}
• Customer since: {customer['signup_date']} ({customer['tenure_months']} months)

TECHNOLOGY STACK
━━━━━━━━━━━━━━━━
• EHR System: {customer['ehr_system']}
• Integration Status: {"✓ Integrated" if customer['ehr_integrated'] else "✗ Not Integrated - RISK FACTOR"}
• Implementation: {customer['implementation_status'].replace('_', ' ').title()}
• Compliance: {', '.join(customer['compliance_certifications'])}

ACCOUNT HEALTH
━━━━━━━━━━━━━━
• Health Score: {customer['health_score']}/100 {'🟢 Healthy' if customer['health_score'] > 70 else '🟡 At Risk' if customer['health_score'] > 50 else '🔴 Critical'}
• Contract: {customer['contract_type'].title()}
• Payment Status: {customer['payment_status'].title()}
• Champion: {customer['champion_title']} {'✓ Active' if customer['champion_exists'] else '✗ No Active Champion - RISK'}

ENGAGEMENT & SUPPORT ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━
Recent Support Activity (Last 10 interactions):
• Total Tickets: {len(recent_interactions)}
• High Priority: {len(recent_interactions[recent_interactions['priority'] == 'high'])}
• Escalations: {len(recent_interactions[recent_interactions['escalated'] == True])}
• Negative Sentiment: {negative_sentiment_pct:.0f}% {'⚠️ CONCERN' if negative_sentiment_pct > 30 else ''}
• Average Resolution Time: {cust_interactions['resolution_time_hours'].mean():.1f} hours
• Unresolved Tickets: {len(cust_interactions[cust_interactions['resolved'] == False])}

Most Common Support Topics:
"""
            # Add top topics
            for topic, count in common_topics.items():
                doc += f"• {topic.replace('_', ' ').title()}: {count} tickets\n"
            
            # Add recent critical interactions
            critical_interactions = recent_interactions[
                (recent_interactions['priority'] == 'high') | 
                (recent_interactions['sentiment'].isin(['frustrated', 'urgent']))
            ].head(3)
            
            if len(critical_interactions) > 0:
                doc += f"""
⚠️ RECENT CRITICAL ISSUES:
"""
                for _, ticket in critical_interactions.iterrows():
                    doc += f"""
[{ticket['date']}] {ticket['topic'].replace('_', ' ').title()}
Priority: {ticket['priority'].upper()} | Sentiment: {ticket['sentiment'].title()}
Description: {ticket['description'][:200]}...
Status: {'Resolved' if ticket['resolved'] else '❌ OPEN - Action Required'}
Staff Role Affected: {ticket['staff_role']}
Patient Impact: {ticket['patient_impact'] if pd.notna(ticket['patient_impact']) else 'Unknown'}
---
"""
            
            # Add call summaries
            if len(recent_calls) > 0:
                doc += f"""
RECENT CONVERSATIONS & RELATIONSHIP NOTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
                for _, call in recent_calls.iterrows():
                    doc += f"""
[{call['date']}] {call['call_type'].replace('_', ' ').title()} Call
Duration: {call['duration_minutes']} minutes | Attendees: {call['attendees']}
Sentiment: {call['sentiment'].title()}

Notes:
{call['call_notes']}

Action Items: {call['action_items']}
{'🎯 EXPANSION OPPORTUNITY IDENTIFIED' if call['expansion_opportunity'] else ''}
{'⚠️ CHURN RISK DISCUSSED' if call['churn_risk_mentioned'] else ''}
─────────────────────────────────────────
"""
            
            # Add feature requests
            if len(cust_requests) > 0:
                doc += f"""
FEATURE REQUESTS & PRODUCT FEEDBACK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
                for _, req in cust_requests.head(5).iterrows():
                    doc += f"""
[{req['date']}] {req['feature_requested']}
Business Impact: {req['business_impact']}
Pain Point: {req['description']}
Urgency: {req['urgency']} | Status: {req['status']}
Community Votes: {req['votes']}
---
"""
            
            # Risk Assessment
            risk_factors = []
            if customer['health_score'] < 50:
                risk_factors.append("🔴 Critical health score (<50)")
            elif customer['health_score'] < 70:
                risk_factors.append("🟡 At-risk health score (<70)")
            
            if not customer['ehr_integrated']:
                risk_factors.append("🔴 EHR not integrated - major friction point")
            
            if not customer['champion_exists']:
                risk_factors.append("🟡 No active champion identified")
            
            if negative_sentiment_pct > 40:
                risk_factors.append("🔴 High negative sentiment in support interactions")
            
            if escalated_tickets > 2:
                risk_factors.append(f"🟡 {escalated_tickets} escalated tickets")
            
            if customer['payment_status'] == 'past_due':
                risk_factors.append("🔴 Payment past due")
            
            if churn_risk_mentioned:
                risk_factors.append("🔴 Churn risk explicitly mentioned in calls")
            
            if customer['competing_systems'] != 'None':
                risk_factors.append(f"🟡 Competitive threat: {customer['competing_systems']}")
            
            if len(risk_factors) > 0:
                doc += f"""
⚠️ RISK ASSESSMENT
━━━━━━━━━━━━━━━━━
{chr(10).join(risk_factors)}

OVERALL RISK LEVEL: {'🔴 HIGH - Immediate Action Required' if len([r for r in risk_factors if '🔴' in r]) > 2 else '🟡 MEDIUM - Monitor Closely' if len(risk_factors) > 2 else '🟢 LOW - Stable'}
"""
            
            # Opportunity Assessment
            opportunities = []
            if customer['health_score'] > 75 and expansion_mentioned:
                opportunities.append("✓ Strong expansion candidate - high health + interest expressed")
            
            if customer['ehr_integrated'] and customer['health_score'] > 70:
                opportunities.append("✓ Good integration success story - reference potential")
            
            if len(cust_requests) > 3:
                opportunities.append(f"✓ Highly engaged - {len(cust_requests)} feature requests submitted")
            
            if customer['num_locations'] > 3 and customer['segment'] != 'Enterprise':
                opportunities.append("✓ Multi-location practice - potential for enterprise upgrade")
            
            if len(opportunities) > 0:
                doc += f"""
💡 GROWTH OPPORTUNITIES
━━━━━━━━━━━━━━━━━━━━━
{chr(10).join(opportunities)}
"""
            
            # Recommended Actions
            doc += f"""
📋 RECOMMENDED ACTIONS
━━━━━━━━━━━━━━━━━━━━━
"""
            if len(risk_factors) > 2:
                doc += """
IMMEDIATE (Next 48 hours):
• Executive touchpoint with champion/decision maker
• Review and address all open high-priority tickets
• Schedule technical review if integration issues present
"""
            
            if not customer['ehr_integrated']:
                doc += """
SHORT-TERM (Next 2 weeks):
• Prioritize EHR integration completion
• Provide dedicated integration support resources
"""
            
            if expansion_mentioned and customer['health_score'] > 70:
                doc += """
EXPANSION PURSUIT:
• Prepare customized expansion proposal
• Schedule demo of requested features
• Share relevant case studies from similar practices
"""
            
            doc += f"""
═══════════════════════════════════════════════════════
Document Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
═══════════════════════════════════════════════════════
"""
            
            documents.append({
                'customer_id': cust_id,
                'doc_type': 'comprehensive_profile',
                'content': doc.strip(),
                'metadata': {
                    'segment': customer['segment'],
                    'health_score': customer['health_score'],
                    'mrr': customer['mrr'],
                    'tenure': customer['tenure_months'],
                    'risk_level': 'high' if len([r for r in risk_factors if '🔴' in r]) > 2 else 'medium' if len(risk_factors) > 2 else 'low',
                    'has_expansion_opportunity': expansion_mentioned,
                    'has_churn_risk': churn_risk_mentioned or len(risk_factors) > 3
                }
            })
        
        return documents
    
    def create_thematic_insight_documents(self):
        """Create documents organized by themes/patterns across customers"""
        documents = []
        
        # 1. EHR Integration Issues Pattern
        ehr_issues = self.interactions[
            self.interactions['topic'] == 'ehr_integration'
        ].sort_values('date', ascending=False)
        
        if len(ehr_issues) > 0:
            # Group by EHR system
            ehr_breakdown = ehr_issues.merge(
                self.customers[['customer_id', 'ehr_system', 'segment']], 
                on='customer_id'
            )
            
            doc = f"""
THEMATIC INSIGHT: EHR INTEGRATION CHALLENGES
═══════════════════════════════════════════════════════

SCOPE OF ISSUE
━━━━━━━━━━━━━━
• Total EHR-related tickets: {len(ehr_issues)}
• Customers affected: {ehr_issues['customer_id'].nunique()}
• High priority: {len(ehr_issues[ehr_issues['priority'] == 'high'])}
• Average resolution time: {ehr_issues['resolution_time_hours'].mean():.1f} hours

BREAKDOWN BY EHR SYSTEM:
"""
            for ehr_system in ehr_breakdown['ehr_system'].value_counts().head(5).index:
                count = len(ehr_breakdown[ehr_breakdown['ehr_system'] == ehr_system])
                doc += f"• {ehr_system}: {count} tickets\n"
            
            doc += f"""
SEGMENT IMPACT:
"""
            for segment in ehr_breakdown['segment'].value_counts().index:
                count = len(ehr_breakdown[ehr_breakdown['segment'] == segment])
                doc += f"• {segment}: {count} tickets\n"
            
            # Recent examples
            doc += f"""
RECENT INCIDENTS (Last 5):
━━━━━━━━━━━━━━━━━━━━━━
"""
            for _, ticket in ehr_issues.head(5).iterrows():
                customer = self.customers[self.customers['customer_id'] == ticket['customer_id']].iloc[0]
                doc += f"""
[{ticket['date']}] {customer['organization_name']} ({customer['ehr_system']})
{ticket['description']}
Status: {'Resolved' if ticket['resolved'] else 'Open'} | Priority: {ticket['priority'].upper()}
─────────────────────────────────────────
"""
            
            doc += f"""
BUSINESS IMPACT
━━━━━━━━━━━━━━━
• Revenue at Risk: ${ehr_breakdown['customer_id'].drop_duplicates().map(lambda x: self.customers[self.customers['customer_id']==x]['mrr'].values[0] if len(self.customers[self.customers['customer_id']==x]) > 0 else 0).sum():,}/month
• Patient Care Impact: Direct impact on appointment scheduling and clinical workflows
• Compliance Risk: Integration failures can cause HIPAA audit concerns

RECOMMENDED ACTIONS
━━━━━━━━━━━━━━━━━━━
1. IMMEDIATE: Create dedicated EHR integration support team
2. SHORT-TERM: Develop automated monitoring for EHR API health
3. MEDIUM-TERM: Proactive communication before EHR vendor updates
4. LONG-TERM: Enhanced integration resilience and error handling

PRODUCT IMPLICATIONS
━━━━━━━━━━━━━━━━━━━
• Consider building EHR update notification system
• Improve error messaging for integration failures
• Develop self-service diagnostic tools for practices
"""
            
            documents.append({
                'doc_type': 'thematic_insight',
                'theme': 'ehr_integration',
                'content': doc.strip(),
                'metadata': {
                    'customers_affected': ehr_issues['customer_id'].nunique(),
                    'total_incidents': len(ehr_issues),
                    'priority': 'critical'
                }
            })
        
        # 2. Expansion Opportunity Pattern
        expansion_calls = self.calls[self.calls['expansion_opportunity'] == True]
        
        if len(expansion_calls) > 0:
            expansion_customers = expansion_calls.merge(
                self.customers, on='customer_id'
            )
            
            doc = f"""
THEMATIC INSIGHT: EXPANSION OPPORTUNITIES
═══════════════════════════════════════════════════════

OPPORTUNITY PIPELINE
━━━━━━━━━━━━━━━━━━━━
• Total opportunities identified: {len(expansion_calls)}
• Unique customers: {expansion_calls['customer_id'].nunique()}
• Total potential ARR: ${expansion_customers['mrr'].sum() * 0.5:,.0f} (estimated 50% increase)
• Average customer health: {expansion_customers['health_score'].mean():.0f}/100

SEGMENT BREAKDOWN:
"""
            for segment in expansion_customers['segment'].value_counts().index:
                count = len(expansion_customers[expansion_customers['segment'] == segment])
                potential_arr = expansion_customers[expansion_customers['segment'] == segment]['mrr'].sum() * 0.5
                doc += f"• {segment}: {count} opportunities (${potential_arr:,.0f} potential ARR)\n"
            
            doc += f"""
TOP OPPORTUNITIES (By Revenue Potential):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            for _, call in expansion_calls.merge(self.customers, on='customer_id').sort_values('mrr', ascending=False).head(5).iterrows():
                doc += f"""
{call['organization_name']} ({call['segment']})
Current MRR: ${call['mrr']:,} | Health Score: {call['health_score']}/100
Call Date: {call['date']} | Type: {call['call_type']}
Notes Summary: {call['call_notes'][:200]}...
Expansion Potential: ${call['mrr'] * 0.5:,.0f}/month
─────────────────────────────────────────
"""
            
            doc += f"""
RECOMMENDED EXPANSION STRATEGY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Prioritize customers with health scores > 75 and existing budget approval
2. Bundle approach: Package complementary features for higher perceived value
3. Timing: Align with budget cycles (Q4 for most healthcare orgs)
4. Proof: Leverage case studies from similar practice types
5. Incentive: Consider implementation discounts for multi-year commits

SUCCESS FACTORS
━━━━━━━━━━━━━
• EHR integration working smoothly
• Active champion in organization
• Demonstrated ROI from current usage
• Growing provider headcount
• Expressed pain points that we can solve
"""
            
            documents.append({
                'doc_type': 'thematic_insight',
                'theme': 'expansion_opportunities',
                'content': doc.strip(),
                'metadata': {
                    'customers_affected': expansion_calls['customer_id'].nunique(),
                    'potential_arr': expansion_customers['mrr'].sum() * 0.5,
                    'priority': 'high'
                }
            })
        
        return documents
    
    def save_all_documents(self, output_path='healthcare_rag_documents.jsonl'):
        """Generate and save all RAG documents"""
        print("Generating comprehensive customer profiles...")
        profile_docs = self.create_comprehensive_customer_profile()
    
        print("Generating thematic insights...")
        thematic_docs = self.create_thematic_insight_documents()
    
        all_docs = profile_docs + thematic_docs
    
        # Save as JSONL with UTF-8 encoding
        with open(output_path, 'w', encoding='utf-8') as f:
            for doc in all_docs:
                f.write(json.dumps(doc, ensure_ascii=False) + '\n')
        
        print(f"\n✅ Generated {len(all_docs)} RAG documents")
        print(f"   - {len(profile_docs)} customer profiles")
        print(f"   - {len(thematic_docs)} thematic insights")
        print(f"   - Saved to: {output_path}")
        
        # Also save a few samples as readable text files with UTF-8 encoding
    # Also save a few samples as readable text files
        # Also save a few samples as readable text files
        print("\nSaving sample documents for review...")
        for i, doc in enumerate(all_docs[:3]):
            with open(f'sample_rag_doc_{i+1}.txt', 'w', encoding='utf-8') as f:
                f.write(doc['content'])
        return all_docs
# Example usage
if __name__ == "__main__":
    # Load the healthcare data
    customers = pd.read_csv('healthcare_customers.csv')
    interactions = pd.read_csv('healthcare_interactions.csv')
    calls = pd.read_csv('healthcare_calls.csv')
    feature_requests = pd.read_csv('healthcare_feature_requests.csv')
    
    # Generate RAG documents
    rag_generator = CompleteHealthcareRAGGenerator(
        customers, interactions, calls, feature_requests
    )
    
    documents = rag_generator.save_all_documents()
    
    print("\n📄 Sample Document Preview:")
    print("="*80)
    print(documents[0]['content'][:1500])
    print("\n... [truncated] ...")
