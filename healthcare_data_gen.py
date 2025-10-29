import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json

np.random.seed(42)
random.seed(42)

class HealthcareSaaSDataGenerator:
    """Generate industry-specific customer data for Healthcare SaaS"""
    
    def __init__(self, n_customers=300):
        self.n_customers = n_customers
        self.start_date = datetime(2024, 1, 1)
        self.end_date = datetime(2025, 10, 6)
        
        # Healthcare-specific attributes
        self.org_types = ['Hospital System', 'Clinic Network', 'Private Practice', 
                         'Specialty Center', 'Urgent Care', 'Telehealth Provider']
        
        self.specialties = ['Primary Care', 'Cardiology', 'Orthopedics', 'Pediatrics',
                           'Mental Health', 'Oncology', 'Emergency Medicine', 'Multi-specialty']
        
        self.ehr_systems = ['Epic', 'Cerner', 'Allscripts', 'eClinicalWorks', 'Athenahealth', 'NextGen']
        
        self.compliance_focus = ['HIPAA', 'HITECH', 'State Privacy Laws', 'Meaningful Use']
        
        # Healthcare SaaS specific topics
        self.ticket_topics = [
            'ehr_integration', 'hipaa_compliance', 'patient_scheduling', 
            'billing_workflow', 'clinical_documentation', 'telehealth_setup',
            'insurance_verification', 'patient_portal', 'reporting_analytics',
            'claims_management', 'appointment_reminders', 'prescription_workflow'
        ]
        
        self.feature_requests = [
            'Enhanced ePrescribing integration',
            'Insurance eligibility real-time checks',
            'Patient waitlist management',
            'Referral tracking workflow',
            'Clinical decision support alerts',
            'Lab results integration',
            'Prior authorization automation',
            'Patient payment plans',
            'Telemedicine video quality improvements',
            'Multi-location scheduling view'
        ]
        
        self.pain_points = [
            'Staff spending too much time on manual data entry',
            'EHR integration frequently breaks after Epic updates',
            'Insurance verification taking 15+ minutes per patient',
            'No-show rate impacting revenue, need better reminders',
            'Compliance audit preparation is extremely time-consuming',
            'Patient portal adoption is low, too complex for elderly patients',
            'Billing staff overwhelmed with claim rejections',
            'Cannot easily track referrals to specialists',
            'Reporting doesn\'t show metrics leadership needs',
            'Scheduling conflicts between multiple providers'
        ]
        
        self.success_stories = [
            'Reduced no-show rate from 18% to 7% using automated reminders',
            'Staff saves 2 hours per day on insurance verification',
            'Improved patient satisfaction scores by 23 points',
            'Increased collections by 15% with better billing workflow',
            'Achieved HIPAA audit compliance in half the time',
            'Patient portal adoption increased from 12% to 47%',
            'Decreased wait times by 20 minutes on average',
            'Successfully integrated with Epic in under 2 weeks'
        ]
    
    def generate_customers(self):
        """Generate healthcare-specific customer profiles"""
        customers = []
        
        for i in range(self.n_customers):
            org_type = random.choice(self.org_types)
            
            # Size and MRR based on org type
            if org_type == 'Hospital System':
                providers = np.random.randint(50, 500)
                mrr = np.random.randint(15000, 80000)
                segment = 'Enterprise'
            elif org_type in ['Clinic Network', 'Specialty Center']:
                providers = np.random.randint(10, 100)
                mrr = np.random.randint(5000, 25000)
                segment = 'Mid-Market'
            else:
                providers = np.random.randint(2, 20)
                mrr = np.random.randint(500, 8000)
                segment = 'SMB'
            
            patients_per_month = providers * np.random.randint(100, 300)
            
            tenure = np.random.randint(1, 48)
            health_score = np.random.randint(40, 100)
            
            # Adjust health based on factors
            if tenure < 6:
                health_score = max(30, health_score - 20)  # Implementation phase
            
            customers.append({
                'customer_id': f'HC-{i+1000}',
                'organization_name': f'{random.choice(["Regional", "Community", "Advanced", "Integrated", "Premier"])} {random.choice(["Health", "Medical", "Healthcare", "Care"])} {random.choice(["Center", "Group", "Partners", "Associates", "System"])}',
                'org_type': org_type,
                'specialty': random.choice(self.specialties),
                'segment': segment,
                'num_providers': providers,
                'num_locations': np.random.randint(1, 20) if org_type in ['Hospital System', 'Clinic Network'] else np.random.randint(1, 5),
                'patients_per_month': patients_per_month,
                'mrr': mrr,
                'tenure_months': tenure,
                'health_score': health_score,
                'signup_date': (self.start_date + timedelta(days=random.randint(0, 600))).strftime('%Y-%m-%d'),
                'contract_type': np.random.choice(['monthly', 'annual', '3-year'], p=[0.2, 0.6, 0.2]),
                'ehr_system': random.choice(self.ehr_systems),
                'ehr_integrated': np.random.choice([True, False], p=[0.7, 0.3]),
                'compliance_certifications': random.sample(self.compliance_focus, random.randint(1, 3)),
                'payment_status': np.random.choice(['current', 'past_due', 'excellent'], p=[0.75, 0.1, 0.15]),
                'champion_title': random.choice(['Practice Manager', 'Chief Medical Officer', 'Director of Operations', 'IT Director', 'COO']),
                'champion_exists': np.random.choice([True, False], p=[0.65, 0.35]),
                'implementation_status': random.choice(['live', 'training', 'configuration', 'full_adoption']),
                'competing_systems': random.choice(['None', 'Evaluating alternatives', 'Using legacy system alongside', 'Considering switch'])
            })
        
        return pd.DataFrame(customers)
    
    def generate_interactions(self, customers_df):
        """Generate healthcare-specific support interactions"""
        interactions = []
        
        for _, customer in customers_df.iterrows():
            n_interactions = np.random.poisson(4)
            
            for j in range(n_interactions):
                date = self.start_date + timedelta(days=random.randint(0, (self.end_date - self.start_date).days))
                topic = random.choice(self.ticket_topics)
                
                # Sentiment based on health score and topic
                if customer['health_score'] > 70:
                    sentiment = np.random.choice(['positive', 'neutral', 'satisfied'], p=[0.5, 0.3, 0.2])
                elif customer['health_score'] > 50:
                    sentiment = np.random.choice(['neutral', 'concerned', 'frustrated'], p=[0.5, 0.3, 0.2])
                else:
                    sentiment = np.random.choice(['frustrated', 'negative', 'urgent'], p=[0.4, 0.4, 0.2])
                
                # Priority based on topic and sentiment
                if topic in ['ehr_integration', 'hipaa_compliance', 'patient_scheduling'] or sentiment in ['urgent', 'frustrated']:
                    priority = 'high'
                elif sentiment == 'negative':
                    priority = 'medium'
                else:
                    priority = np.random.choice(['low', 'medium'], p=[0.6, 0.4])
                
                # Generate realistic healthcare interaction description
                description = self._generate_healthcare_interaction(topic, sentiment, customer)
                
                interactions.append({
                    'interaction_id': f'TICKET-{len(interactions)+5000}',
                    'customer_id': customer['customer_id'],
                    'date': date.strftime('%Y-%m-%d'),
                    'channel': np.random.choice(['email', 'chat', 'phone', 'ticket'], p=[0.3, 0.3, 0.3, 0.1]),
                    'topic': topic,
                    'priority': priority,
                    'sentiment': sentiment,
                    'resolution_time_hours': np.random.randint(2, 96),
                    'resolved': np.random.choice([True, False], p=[0.85, 0.15]),
                    'escalated': np.random.choice([True, False], p=[0.15, 0.85]) if priority == 'high' else False,
                    'csat_score': np.random.randint(1, 6) if random.random() > 0.4 else None,
                    'description': description,
                    'staff_role': random.choice(['Practice Manager', 'Medical Assistant', 'Billing Specialist', 'Front Desk', 'Provider', 'IT Admin']),
                    'affected_users': np.random.randint(1, min(10, customer['num_providers'])),
                    'patient_impact': np.random.choice(['None', 'Low', 'Medium', 'High']) if random.random() > 0.5 else None
                })
        
        return pd.DataFrame(interactions)
    
    def generate_sales_calls(self, customers_df, calls_per_customer=2):
        """Generate sales and CS call notes"""
        calls = []
        
        for _, customer in customers_df.iterrows():
            for i in range(calls_per_customer):
                call_date = self.start_date + timedelta(days=random.randint(0, (self.end_date - self.start_date).days))
                
                call_type = random.choice(['onboarding', 'check-in', 'renewal', 'expansion', 'support_escalation'])
                
                notes = self._generate_call_notes(call_type, customer)
                
                calls.append({
                    'call_id': f'CALL-{len(calls)+2000}',
                    'customer_id': customer['customer_id'],
                    'date': call_date.strftime('%Y-%m-%d'),
                    'call_type': call_type,
                    'duration_minutes': np.random.randint(15, 90),
                    'attendees': random.choice(['Practice Manager', 'CMO', 'Operations Director', 'Billing Manager', 'Multiple stakeholders']),
                    'call_notes': notes,
                    'action_items': self._generate_action_items(call_type),
                    'sentiment': random.choice(['positive', 'neutral', 'concerned', 'enthusiastic']),
                    'expansion_opportunity': random.choice([True, False]) if call_type in ['check-in', 'renewal'] else False,
                    'churn_risk_mentioned': np.random.choice([True, False], p=[0.15, 0.85]) if customer['health_score'] < 60 else False
                })
        
        return pd.DataFrame(calls)
    
    def generate_feature_requests(self, customers_df):
        """Generate feature request and feedback data"""
        requests = []
        
        for _, customer in customers_df.iterrows():
            if random.random() > 0.4:  # 60% of customers submit requests
                n_requests = np.random.randint(1, 5)
                
                for i in range(n_requests):
                    request_date = self.start_date + timedelta(days=random.randint(0, (self.end_date - self.start_date).days))
                    
                    requests.append({
                        'request_id': f'FR-{len(requests)+1000}',
                        'customer_id': customer['customer_id'],
                        'date': request_date.strftime('%Y-%m-%d'),
                        'feature_requested': random.choice(self.feature_requests),
                        'description': random.choice(self.pain_points),
                        'business_impact': random.choice(['High - blocking workflow', 'Medium - workaround exists', 'Low - nice to have']),
                        'votes': np.random.randint(1, 50),
                        'status': random.choice(['Under review', 'Planned', 'In development', 'Shipped', 'Declined']),
                        'urgency': random.choice(['Critical', 'High', 'Medium', 'Low'])
                    })
        
        return pd.DataFrame(requests)
    
    def _generate_healthcare_interaction(self, topic, sentiment, customer):
        """Generate realistic healthcare-specific ticket descriptions"""
        
        templates = {
            'ehr_integration': [
                f"Epic integration stopped syncing patient appointments after last {customer['ehr_system']} update. Appointments from past 48 hours missing.",
                f"Medication reconciliation data from {customer['ehr_system']} not flowing correctly. Providers seeing outdated medication lists.",
                f"Lab results integration failing for 3 of our {customer['num_locations']} locations. Urgent - providers need results for patient care."
            ],
            'hipaa_compliance': [
                f"Need audit logs for past 6 months for compliance review. Upcoming HIPAA audit in 2 weeks.",
                f"Questions about data encryption standards. Internal audit flagged concerns about patient data security.",
                f"BAA (Business Associate Agreement) needs review before renewal. Legal team has questions."
            ],
            'patient_scheduling': [
                f"Double-booking occurring in Provider schedule - happened 5 times this week. Causing patient wait issues.",
                f"Recurring appointment feature not working properly. Patients with standing weekly appointments getting canceled.",
                f"Need to block off provider time for hospital rounds but system won't allow multi-location blocking."
            ],
            'billing_workflow': [
                f"Insurance claims rejecting at unusually high rate (35%) - normally 10%. Major revenue impact.",
                f"Explanation of Benefits (EOB) posting is 3 weeks behind. Billing team can't reconcile accounts receivable.",
                f"CPT codes not mapping correctly to {customer['ehr_system']} procedures. Causing claim denials."
            ],
            'patient_portal': [
                f"Patients reporting can't access lab results through portal. IT showing error: 'unauthorized access'.",
                f"Portal messaging feature timing out for {customer['patients_per_month']} patient messages. Staff having to call patients back.",
                f"Appointment request form on portal not submitting. Patients calling saying online booking broken."
            ]
        }
        
        base_description = random.choice(templates.get(topic, [f"Issue with {topic.replace('_', ' ')}"]))
        
        if sentiment in ['frustrated', 'urgent']:
            base_description += f" This is causing significant disruption to patient care. {customer['champion_title']} escalating."
        elif sentiment == 'negative':
            base_description += " Staff productivity severely impacted. Need resolution ASAP."
        
        return base_description
    
    def _generate_call_notes(self, call_type, customer):
        """Generate realistic call notes"""
        
        if call_type == 'onboarding':
            return f"""Onboarding call with {customer['organization_name']} - {customer['specialty']}
            
Goals discussed:
- Reduce no-show rate (currently at 22%)
- Streamline insurance verification process
- Improve patient portal adoption (currently only 15% of patients using)
- Better reporting for quality measures

Current pain points:
- {random.choice(self.pain_points)}
- Staff training needed on advanced features
- {customer['ehr_system']} integration setup pending

Success criteria defined: Reduce no-shows by 50% within 6 months, achieve 40% portal adoption
Timeline: Full implementation target is 90 days
"""
        
        elif call_type == 'expansion':
            return f"""Expansion opportunity discussion
            
Currently using: Basic scheduling + billing modules
Expressed interest in: Telehealth module and advanced analytics

Drivers:
- Expanding to telehealth post-COVID, need integrated solution
- Board requesting better operational dashboards
- {customer['num_providers']} providers, growing to {customer['num_providers']+10} next quarter

Budget: ${customer['mrr'] * 1.5}/mo approved for Q4
Competition: Evaluating [competitor name] but prefer staying with us due to EHR integration

Next steps: Demo advanced analytics next week, pricing proposal by Friday
"""
        
        elif call_type == 'renewal':
            satisfaction = 'high' if customer['health_score'] > 70 else 'medium' if customer['health_score'] > 50 else 'at-risk'
            
            return f"""Renewal discussion - {customer['contract_type']} contract expiring in 60 days

Overall satisfaction: {satisfaction}
Renewal likelihood: {'Strong' if satisfaction == 'high' else 'Moderate' if satisfaction == 'medium' else 'At risk'}

What's working:
- {random.choice(self.success_stories)}

Concerns raised:
- {random.choice(self.pain_points) if satisfaction != 'high' else 'None - very satisfied'}

Renewal terms discussed: {'Multi-year discount offered' if customer['health_score'] > 70 else 'Addressing concerns before renewal'}
Action needed: {'Prepare renewal paperwork' if satisfaction == 'high' else 'Executive escalation meeting scheduled'}
"""
        
        else:
            return f"""Check-in call with {customer['champion_title']}

Usage stats reviewed: {customer['num_providers']} providers active
Recent support tickets: {'None - smooth sailing' if customer['health_score'] > 70 else '2-3 tickets this month, mostly questions'}
Training needs: {'Staff fully trained' if customer['tenure_months'] > 12 else 'Additional training requested on reporting'}

Feedback: {random.choice(['Very happy with platform', 'Some workflow improvements needed', 'Meeting expectations', 'Exceeded expectations'])}
"""
    
    def _generate_action_items(self, call_type):
        """Generate action items from calls"""
        
        items = {
            'onboarding': [
                'Schedule EHR integration kickoff',
                'Send training materials for staff',
                'Configure automated appointment reminders'
            ],
            'expansion': [
                'Send proposal for telehealth module',
                'Schedule demo with CMO and Operations',
                'Prepare ROI analysis'
            ],
            'renewal': [
                'Send renewal quote by Friday',
                'Schedule executive review if needed',
                'Prepare case studies for board presentation'
            ],
            'check-in': [
                'Follow up on training request',
                'Share best practices document',
                'Schedule next quarterly review'
            ]
        }
        
        return ' | '.join(items.get(call_type, ['Follow up next month']))
    
    def generate_all_healthcare_data(self):
        """Generate complete healthcare SaaS dataset"""
        print("Generating healthcare customers...")
        customers = self.generate_customers()
        
        print("Generating support interactions...")
        interactions = self.generate_interactions(customers)
        
        print("Generating sales/CS call notes...")
        calls = self.generate_sales_calls(customers)
        
        print("Generating feature requests...")
        feature_requests = self.generate_feature_requests(customers)
        
        # Save all data
        customers.to_csv('healthcare_customers.csv', index=False)
        interactions.to_csv('healthcare_interactions.csv', index=False)
        calls.to_csv('healthcare_calls.csv', index=False)
        feature_requests.to_csv('healthcare_feature_requests.csv', index=False)
        
        print("\n✅ Healthcare SaaS data generation complete!")
        print(f"   - {len(customers)} healthcare organizations")
        print(f"   - {len(interactions)} support interactions")
        print(f"   - {len(calls)} call notes")
        print(f"   - {len(feature_requests)} feature requests")
        
        return {
            'customers': customers,
            'interactions': interactions,
            'calls': calls,
            'feature_requests': feature_requests
        }

# Generate the data
generator = HealthcareSaaSDataGenerator(n_customers=300)
data = generator.generate_all_healthcare_data()

print("\n📊 Sample Healthcare Customer:")
print(data['customers'].head(2))
print("\n📊 Sample Interaction:")
print(data['interactions'].head(2))
