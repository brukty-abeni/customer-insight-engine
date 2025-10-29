import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json

np.random.seed(42)

class CompleteCustomerDataGenerator:
    """
    Generate comprehensive customer data including:
    - Product usage telemetry
    - Conversational transcripts
    - Email threads
    - Survey verbatims
    - Outcomes tracking
    """
    
    def __init__(self, n_customers=200):
        self.n_customers = n_customers
        self.start_date = datetime(2024, 1, 1)
        self.end_date = datetime(2025, 10, 6)
        
        # Conversation templates
        self.conversation_frustration = [
            "Look, I'm going to be honest with you {csm_name}. {pain_point}. This is really impacting our {impact_area}.",
            "We've been patient but {pain_point}. My {stakeholder} is asking tough questions about ROI.",
            "I had a demo from {competitor} last week. {comparison}. I don't want to switch but I need to show leadership we have options.",
            "This is the {ordinal} time we've had this issue. {pain_point}. We're paying ${mrr} per month and this keeps happening.",
        ]
        
        self.conversation_positive = [
            "I wanted to share some good news - {success_metric}. The team is really happy with the results.",
            "Your platform has been a game-changer for us. {success_story}. We're actually interested in {expansion_area}.",
            "Just wanted to say thanks for the quick response on {issue}. That's the kind of support that keeps us as customers.",
        ]
        
        self.pain_points = [
            "the {feature} keeps breaking after {trigger}",
            "we're spending {time_amount} extra hours per day on manual workarounds",
            "our {metric} has gotten worse since implementation",
            "the integration with {system} is unreliable",
            "staff are complaining the workflow doesn't match how they actually work",
        ]
        
        self.email_templates = {
            'escalation': """From: {sender_name} <{sender_email}>
Date: {date}
Subject: URGENT: {issue_summary}

{opening_frustration}

{specific_problem_details}

{business_impact}

{urgency_statement}

Please call me ASAP: {phone}
{sender_title}""",
            
            'followup': """From: {sender_name} <{sender_email}>
Date: {date}
Subject: Re: {issue_summary}

I sent information on ticket #{ticket_id} {days_ago} days ago and haven't heard back.

{frustration_statement}

{consequence_statement}

{sender_title}""",
            
            'positive': """From: {sender_name} <{sender_email}>
Date: {date}
Subject: {positive_subject}

{positive_opening}

{success_details}

{forward_looking}

Thanks,
{sender_title}"""
        }
    
    def generate_usage_telemetry(self, customers_df):
        """Generate detailed product usage data"""
        telemetry = []
        
        for _, customer in customers_df.iterrows():
            # Generate daily usage for last 90 days
            for day in range(90):
                date = self.end_date - timedelta(days=90-day)
                
                # Usage intensity based on health score
                if customer['health_score'] > 75:
                    usage_multiplier = 1.2
                    error_rate = 0.02
                elif customer['health_score'] > 50:
                    usage_multiplier = 1.0
                    error_rate = 0.05
                else:
                    usage_multiplier = 0.6
                    error_rate = 0.12
                
                # Decline pattern for at-risk customers
                if customer['health_score'] < 50:
                    usage_multiplier *= (1 - (90-day) / 180)  # Declining usage
                
                base_sessions = max(1, int(customer['num_providers'] * usage_multiplier * random.uniform(0.8, 1.2)))
                
                telemetry.append({
                    'customer_id': customer['customer_id'],
                    'date': date.strftime('%Y-%m-%d'),
                    
                    # Scheduling metrics
                    'appointments_created': int(base_sessions * random.randint(15, 25)),
                    'appointments_cancelled': int(base_sessions * random.randint(1, 3)),
                    'no_shows': int(base_sessions * random.uniform(0.05, 0.20) * 10),
                    'reminders_sent': int(base_sessions * random.randint(15, 25) * 0.98),
                    'online_bookings': int(base_sessions * random.randint(2, 5)),
                    
                    # Billing metrics
                    'claims_submitted': int(base_sessions * random.randint(10, 20)),
                    'claims_approved': int(base_sessions * random.randint(8, 18)),
                    'claims_denied': int(base_sessions * random.uniform(0.1, 0.25) * 15),
                    'claim_denial_rate': random.uniform(0.08, 0.25) if customer['health_score'] < 60 else random.uniform(0.05, 0.12),
                    
                    # EHR sync metrics
                    'ehr_sync_attempts': int(base_sessions * 4),
                    'ehr_sync_failures': int(base_sessions * 4 * error_rate) if customer['ehr_integrated'] else 0,
                    'ehr_data_synced_mb': int(base_sessions * random.uniform(50, 150)),
                    
                    # Portal metrics
                    'portal_active_patients': int(customer['patients_per_month'] * random.uniform(0.10, 0.45)),
                    'portal_logins': int(customer['patients_per_month'] * random.uniform(0.05, 0.25)),
                    'portal_messages': int(base_sessions * random.randint(2, 8)),
                    'portal_adoption_rate': random.uniform(0.08, 0.50),
                    
                    # User activity
                    'active_users': int(customer['num_providers'] * random.uniform(0.4, 0.95)),
                    'licensed_users': customer['num_providers'],
                    'utilization_rate': random.uniform(0.40, 0.95),
                    'total_sessions': base_sessions,
                    'avg_session_duration_min': random.randint(15, 45),
                    
                    # Errors and issues
                    'total_errors': int(base_sessions * error_rate * 10),
                    'critical_errors': int(base_sessions * error_rate * 2),
                    'workflows_completed': int(base_sessions * random.randint(10, 30)),
                    'workflows_abandoned': int(base_sessions * random.uniform(0.05, 0.15) * 10),
                })
        
        return pd.DataFrame(telemetry)
    
    def generate_call_transcripts(self, customers_df, calls_df):
        """Generate realistic call transcripts"""
        transcripts = []
        
        for _, call in calls_df.iterrows():
            customer = customers_df[customers_df['customer_id'] == call['customer_id']].iloc[0]
            
            if call['sentiment'] in ['frustrated', 'concerned']:
                # Frustrated call
                pain_point = random.choice([
                    f"the Epic integration keeps breaking after their updates",
                    f"we're spending 2+ extra hours per day on manual data entry",
                    f"our claim denial rate has jumped from 10% to 25%",
                    f"the scheduling conflicts are causing patient complaints"
                ])
                
                transcript = f"""CALL TRANSCRIPT
Customer: {customer['organization_name']} ({call['customer_id']})
Date: {call['date']}
Duration: {call['duration_minutes']} minutes
Type: {call['call_type']}
Participants: {call['attendees']} (Customer), CSM Team

[00:02:15]
{call['attendees']}: "Look, I'm going to be honest with you. {pain_point}. This is really impacting our operations and my team's morale."

[00:03:30]
CSM: "I completely understand your frustration. This is not the experience we want you to have. Can you tell me more about when this started?"

[00:04:05]
{call['attendees']}: "It's been about {random.randint(2, 6)} weeks now. And here's the thing - we're paying you ${customer['mrr']:,} per month specifically because you promised {random.choice(['seamless integration', 'workflow efficiency', 'reduced admin burden'])}. That was the whole selling point."

[00:05:20]
{call['attendees']}: "I had a demo from {random.choice(['Athenahealth', 'eClinicalWorks', 'NextGen'])} last week. {random.choice(['They showed me their Epic connector and it looked more stable', 'Their workflow actually matches how specialists work', 'The pricing was competitive and they guarantee uptime'])}. I don't want to switch - we've invested a lot in your platform - but I need to show leadership we have options if this doesn't get fixed soon."

[00:07:45]
CSM: "I hear you. Give me 48 hours. I'm going to escalate this to our VP of Engineering personally. Can we schedule a technical deep-dive on {(datetime.strptime(call['date'], '%Y-%m-%d') + timedelta(days=2)).strftime('%A')}?"

[00:08:30]
{call['attendees']}: "{random.choice(['That works', 'Wednesday works', 'I can do Thursday'])}. But this is urgent. We're {random.randint(30, 90)} days from renewal and I can't recommend renewing if we're still having these issues."

[00:09:15]
CSM: "Understood. I'm going to personally own this until it's resolved. You'll have an update from me by end of day tomorrow with a clear action plan."

Call Sentiment: {'Frustrated but willing to work with us' if customer['health_score'] > 40 else 'Very frustrated, high churn risk'}
"""
            
            elif call['sentiment'] in ['positive', 'enthusiastic']:
                success_story = random.choice([
                    f"we reduced our no-show rate from 18% to 8%",
                    f"our staff is saving about 10 hours per week on scheduling",
                    f"patient satisfaction scores have improved by 15 points",
                    f"we're processing claims 30% faster than before"
                ])
                
                transcript = f"""CALL TRANSCRIPT
Customer: {customer['organization_name']} ({call['customer_id']})
Date: {call['date']}
Duration: {call['duration_minutes']} minutes
Type: {call['call_type']}
Participants: {call['attendees']} (Customer), CSM Team

[00:01:30]
{call['attendees']}: "I wanted to share some good news - {success_story}. The team is really happy with the results."

[00:02:15]
CSM: "That's fantastic to hear! What do you think made the biggest difference?"

[00:03:00]
{call['attendees']}: "Honestly, once we got past the initial learning curve, the {random.choice(['automated reminders', 'integration with Epic', 'reporting dashboard', 'mobile app'])} has been a game-changer. {random.choice(['Our providers are actually using it daily', 'The billing team loves the workflow', 'Patients are commenting on how easy it is'])}."

[00:04:30]
{call['attendees']}: "Actually, I wanted to ask about {random.choice(['the telehealth module', 'advanced analytics', 'the referral management feature', 'multi-location scheduling'])}. We're looking to expand and I've heard good things from other practices about that capability."

[00:05:45]
CSM: "Absolutely! Let me set up a demo for you next week. Given your success with the current setup, I think you'll find a lot of value in those features. Many practices your size see additional {random.choice(['15-20% efficiency gains', '$50K+ in recovered revenue', '25% improvement in coordination'])}."

[00:07:00]
{call['attendees']}: "Perfect. Also, our CFO asked me to be a reference for you if you need one. We're really happy with the ROI we're seeing."

Call Sentiment: Very positive - expansion opportunity + reference potential
"""
            
            else:
                # Neutral check-in
                transcript = f"""CALL TRANSCRIPT
Customer: {customer['organization_name']} ({call['customer_id']})
Date: {call['date']}
Duration: {call['duration_minutes']} minutes
Type: {call['call_type']}
Participants: {call['attendees']} (Customer), CSM Team

[00:01:00]
CSM: "Thanks for making time today. How are things going with the platform?"

[00:01:30]
{call['attendees']}: "Overall it's going well. The team is getting more comfortable with it. We're up to about {int(customer['num_providers'] * random.uniform(0.6, 0.9))} of our {customer['num_providers']} providers using it daily."

[00:02:45]
CSM: "That's great adoption. Any areas where the team is struggling or needs additional training?"

[00:04:30]
CSM: "I can arrange that."

[00:05:00]
{call['attendees']}: "Sounds good. Otherwise no major issues. Talk to you next quarter."

Call Sentiment: Neutral - stable but no strong enthusiasm
"""
            
            transcripts.append({
                'call_id': call['call_id'],
                'customer_id': call['customer_id'],
                'date': call['date'],
                'transcript': transcript,
                'key_quotes': self._extract_key_quotes(transcript),
                'competitor_mentioned': 'Athenahealth' in transcript or 'eClinicalWorks' in transcript or 'NextGen' in transcript,
                'expansion_signals': 'expand' in transcript.lower() or 'interested in' in transcript.lower(),
                'churn_signals': 'renewal' in transcript.lower() and 'concern' in transcript.lower()
            })
        
        return pd.DataFrame(transcripts)
    
    def generate_email_threads(self, customers_df, interactions_df):
        """Generate email conversation threads"""
        emails = []
        
        for _, interaction in interactions_df[interactions_df['channel'] == 'email'].iterrows():
            customer = customers_df[customers_df['customer_id'] == interaction['customer_id']].iloc[0]
            
            if interaction['sentiment'] in ['frustrated', 'urgent']:
                email = self.email_templates['escalation'].format(
                    sender_name=interaction['staff_role'],
                    sender_email=f"{interaction['staff_role'].lower().replace(' ', '.')}@{customer['organization_name'].lower().replace(' ', '')}.com",
                    date=interaction['date'],
                    issue_summary=interaction['topic'].replace('_', ' ').title(),
                    opening_frustration=random.choice([
                        "I need immediate assistance with a critical issue.",
                        "This is urgent and affecting patient care.",
                        "We've been struggling with this for too long."
                    ]),
                    specific_problem_details=interaction['description'],
                    business_impact=random.choice([
                        f"This is costing us thousands in delayed revenue.",
                        f"Staff are spending {random.randint(5, 15)} extra hours per week on workarounds.",
                        f"Patients are complaining and it's affecting our reputation."
                    ]),
                    urgency_statement=random.choice([
                        "We need this resolved by end of week.",
                        "This cannot wait any longer.",
                        "Our leadership is questioning whether we should continue with your platform."
                    ]),
                    phone="555-" + str(random.randint(1000, 9999)),
                    sender_title=interaction['staff_role']
                )              
# Add follow-up email if unresolved
                if not interaction['resolved']:
                    followup_email = self.email_templates['followup'].format(
                        sender_name=interaction['staff_role'],
                        sender_email=f"{interaction['staff_role'].lower().replace(' ', '.')}@{customer['organization_name'].lower().replace(' ', '')}.com",
                        date=(datetime.strptime(interaction['date'], '%Y-%m-%d') + timedelta(days=3)).strftime('%Y-%m-%d'),
                        issue_summary=interaction['topic'].replace('_', ' ').title(),
                        ticket_id=interaction['interaction_id'].split('-')[1],
                        days_ago=3,
                        frustration_statement="This is the second time this month I've had to repeat myself. I'm spending more time explaining our problems than getting them fixed.",
                        consequence_statement=f"Our {random.choice(['CFO', 'CMO', 'Board'])} just asked me if we should look at other platforms. I don't know what to tell them.",
                        sender_title=interaction['staff_role']
                    )
                    
                    email += f"\n\n{'='*60}\nFOLLOW-UP EMAIL:\n{'='*60}\n\n{followup_email}"
            
            else:
                email = self.email_templates['positive'].format(
                    sender_name=interaction['staff_role'],
                    sender_email=f"{interaction['staff_role'].lower().replace(' ', '.')}@{customer['organization_name'].lower().replace(' ', '')}.com",
                    date=interaction['date'],
                    positive_subject=random.choice([
                        "Thank you for the quick response",
                        "Positive feedback to share",
                        "Great support experience"
                    ]),
                    positive_opening="I wanted to reach out with some positive feedback.",
                    success_details=random.choice([
                        "Your team was incredibly responsive on our recent issue.",
                        "The new feature you rolled out is exactly what we needed.",
                        "Our providers are really happy with the improvements you've made."
                    ]),
                    forward_looking=random.choice([
                        "Looking forward to continuing our partnership.",
                        "Interested in learning about upcoming features.",
                        "Would be happy to be a reference if you need one."
                    ]),
                    sender_title=interaction['staff_role']
                )
            
            emails.append({
                'email_id': f"EMAIL-{len(emails)+1000}",
                'customer_id': interaction['customer_id'],
                'interaction_id': interaction['interaction_id'],
                'date': interaction['date'],
                'thread_content': email,
                'sentiment': interaction['sentiment'],
                'escalation_level': 'high' if interaction['priority'] == 'high' else 'normal'
            })
        
        return pd.DataFrame(emails)
    
    def generate_survey_verbatims(self, customers_df):
        """Generate detailed survey responses with verbatim feedback"""
        surveys = []
        
        for _, customer in customers_df.iterrows():
            if random.random() > 0.4:  # 60% response rate
                
                # NPS based on health score
                if customer['health_score'] > 80:
                    nps = random.randint(9, 10)
                    sentiment_type = 'promoter'
                elif customer['health_score'] > 60:
                    nps = random.randint(7, 9)
                    sentiment_type = 'passive'
                else:
                    nps = random.randint(0, 6)
                    sentiment_type = 'detractor'
                
                # Generate verbatim based on sentiment
                if sentiment_type == 'promoter':
                    primary_reason = random.choice([
                        f"The platform has transformed our workflow. We're saving {random.randint(5, 15)} hours per week on administrative tasks.",
                        f"Integration with {customer['ehr_system']} works flawlessly. Our providers love how seamless it is.",
                        f"Best investment we've made. ROI was evident within {random.randint(2, 4)} months.",
                        f"Support team is exceptional. They truly understand healthcare workflows and respond quickly.",
                        f"The reporting capabilities give us insights we never had before. Making much better operational decisions."
                    ])
                    
                    improvement = random.choice([
                        "Honestly, very satisfied. Maybe add more mobile functionality for providers on the go.",
                        "Would love to see integration with a few more specialty-specific tools.",
                        "Everything is great. Keep up the good work.",
                        "More customization options for reports would be nice, but this is minor."
                    ])
                    
                    considering_alternatives = "No, very happy with the platform."
                    
                elif sentiment_type == 'passive':
                    primary_reason = random.choice([
                        "It works well overall, but some features are more complex than they need to be.",
                        f"Good platform but the learning curve was steep. Took us {random.randint(3, 6)} months to get fully comfortable.",
                        "Meets our needs but doesn't exceed expectations. Feels like we're paying for features we don't use.",
                        f"Integration with {customer['ehr_system']} works most of the time, but occasional hiccups are frustrating.",
                        "Support is responsive but sometimes it feels like they don't fully understand our workflow."
                    ])
                    
                    improvement = random.choice([
                        "Simplify the UI. Too many clicks to do basic tasks.",
                        "Better training materials. More specialty-specific examples.",
                        "More competitive pricing. We're a small practice and it's a stretch for our budget.",
                        "Faster resolution on technical issues. When something breaks, we can't wait days for a fix."
                    ])
                    
                    considering_alternatives = random.choice([
                        "Not actively looking, but we review options annually.",
                        "We've had a few demos from competitors but nothing compelling yet.",
                        "Considering it. Depends on whether issues get resolved."
                    ])
                    
                else:  # detractor
                    primary_reason = random.choice([
                        f"The implementation was a disaster. We were promised {random.randint(60, 90)} days but it took {random.randint(4, 7)} months and still isn't working properly.",
                        f"Integration with {customer['ehr_system']} breaks constantly. We're doing manual data entry that should be automatic.",
                        "The sales demo was not representative of reality. What we were shown doesn't match what we actually got.",
                        f"Our {random.choice(['claim denial rate', 'no-show rate', 'administrative burden'])} has actually INCREASED since implementation. This is the opposite of what was promised.",
                        "Support is slow and often gives us generic answers that don't solve our specific problems. We feel like we're troubleshooting your product for you."
                    ])
                    
                    improvement = random.choice([
                        "Either fix the core functionality or be honest in sales that it doesn't work for our type of practice.",
                        "Stop telling us to 'adapt our workflow to the software.' We're running a medical practice - the software should adapt to us.",
                        "Assign us a dedicated support person who actually understands our specialty and can solve problems quickly.",
                        "Massive improvement needed in reliability and integration stability. We can't run a practice on a platform that breaks every few weeks."
                    ])
                    
                    considering_alternatives = random.choice([
                        f"Yes, we have demos scheduled with {random.choice(['Athenahealth', 'eClinicalWorks', 'NextGen'])} next week.",
                        "Actively evaluating alternatives. This isn't working for us.",
                        "Already put in a budget request to switch platforms. Just waiting for board approval.",
                        "We're stuck until our contract is up but we won't be renewing unless major improvements happen."
                    ])
                
                surveys.append({
                    'survey_id': f"SURVEY-{len(surveys)+1000}",
                    'customer_id': customer['customer_id'],
                    'survey_date': (self.end_date - timedelta(days=random.randint(0, 60))).strftime('%Y-%m-%d'),
                    'nps_score': nps,
                    'nps_category': sentiment_type,
                    'ease_of_use': random.randint(3, 5) if sentiment_type == 'promoter' else random.randint(2, 4) if sentiment_type == 'passive' else random.randint(1, 3),
                    'feature_satisfaction': random.randint(3, 5) if sentiment_type == 'promoter' else random.randint(2, 4) if sentiment_type == 'passive' else random.randint(1, 3),
                    'support_satisfaction': random.randint(4, 5) if sentiment_type == 'promoter' else random.randint(2, 4) if sentiment_type == 'passive' else random.randint(1, 3),
                    'value_for_money': random.randint(3, 5) if sentiment_type == 'promoter' else random.randint(2, 4) if sentiment_type == 'passive' else random.randint(1, 3),
                    'primary_reason_verbatim': primary_reason,
                    'improvement_suggestion_verbatim': improvement,
                    'considering_alternatives_verbatim': considering_alternatives,
                    'would_recommend_verbatim': f"Score: {nps}/10 - {sentiment_type.title()}"
                })
        
        return pd.DataFrame(surveys)
    
    def generate_outcomes_tracking(self, customers_df, interactions_df):
        """Generate outcomes data for insights generated"""
        outcomes = []
        
        # Identify customers that had issues and track resolution
        at_risk_customers = customers_df[customers_df['health_score'] < 60]
        
        for _, customer in at_risk_customers.iterrows():
            # Generate insight
            cust_interactions = interactions_df[interactions_df['customer_id'] == customer['customer_id']]
            
            if len(cust_interactions) > 0:
                primary_issue = cust_interactions['topic'].mode()[0] if len(cust_interactions['topic'].mode()) > 0 else 'general'
                
                # Simulate intervention
                intervention_success = random.random() > 0.4  # 60% success rate
                
                if intervention_success:
                    health_improvement = random.randint(20, 50)
                    new_health = min(100, customer['health_score'] + health_improvement)
                    outcome_status = 'resolved'
                    expansion_chance = random.random() > 0.7
                else:
                    health_improvement = random.randint(-10, 10)
                    new_health = max(0, customer['health_score'] + health_improvement)
                    outcome_status = 'unresolved' if new_health > 30 else 'churned'
                    expansion_chance = False
                
                outcomes.append({
                    'insight_id': f"INS-{len(outcomes)+5000}",
                    'customer_id': customer['customer_id'],
                    'generated_date': (self.end_date - timedelta(days=random.randint(30, 90))).strftime('%Y-%m-%d'),
                    'insight_type': 'churn_risk',
                    'risk_score': 100 - customer['health_score'],
                    'primary_issue': primary_issue,
                    'recommended_actions': json.dumps([
                        "Executive escalation call",
                        f"Resolve {primary_issue.replace('_', ' ')} issues",
                        "Offer service credit",
                        "Weekly check-ins until stable"
                    ]),
                    'actions_taken': json.dumps([
                        {"action": "Executive escalation", "completed": True, "date": (self.end_date - timedelta(days=random.randint(25, 85))).strftime('%Y-%m-%d')},
                        {"action": "Technical fix deployed", "completed": intervention_success, "date": (self.end_date - timedelta(days=random.randint(20, 80))).strftime('%Y-%m-%d') if intervention_success else None},
                        {"action": "Service credit applied", "completed": True, "date": (self.end_date - timedelta(days=random.randint(20, 80))).strftime('%Y-%m-%d')}
                    ]),
                    'outcome_status': outcome_status,
                    'health_score_before': customer['health_score'],
                    'health_score_after': new_health,
                    'health_score_change': health_improvement,
                    'churn_prevented': outcome_status == 'resolved',
                    'expansion_occurred': expansion_chance,
                    'expansion_arr': customer['mrr'] * random.uniform(0.3, 0.6) * 12 if expansion_chance else 0,
                    'mrr_retained': customer['mrr'] if outcome_status != 'churned' else 0,
                    'customer_feedback': random.choice([
                        "Very satisfied with response. Issues resolved quickly.",
                        "Appreciate the attention. Staying with platform.",
                        "Good progress but still monitoring closely.",
                        "Too little, too late. Already committed to alternative."
                    ]) if outcome_status == 'resolved' else "Unfortunately decided to move to competitor",
                    'learnings': json.dumps([
                        f"Fast response critical for {primary_issue.replace('_', ' ')} issues",
                        "Executive engagement makes difference",
                        "Service credits effective goodwill gesture" if intervention_success else "Need faster technical resolution"
                    ])
                })
        
        return pd.DataFrame(outcomes)
    
    def _extract_key_quotes(self, transcript):
        """Extract key quotes from transcript"""
        lines = [l for l in transcript.split('\n') if ']:' in l and 'CSM:' not in l]
        return ' | '.join([l.split(']: ')[1][:100] + '...' if len(l.split(']: ')[1]) > 100 else l.split(']: ')[1] for l in lines[:3]])
    
    def generate_complete_dataset(self, customers_df, interactions_df, calls_df):
        """Generate all enhanced data types"""
        print("\n🔄 Generating complete customer intelligence dataset...")
        
        print("📊 Generating usage telemetry...")
        telemetry = self.generate_usage_telemetry(customers_df)
        
        print("💬 Generating call transcripts...")
        transcripts = self.generate_call_transcripts(customers_df, calls_df)
        
        print("📧 Generating email threads...")
        emails = self.generate_email_threads(customers_df, interactions_df)
        
        print("📝 Generating survey verbatims...")
        surveys = self.generate_survey_verbatims(customers_df)
        
        print("🎯 Generating outcomes tracking...")
        outcomes = self.generate_outcomes_tracking(customers_df, interactions_df)
        
        # Save all data
        telemetry.to_csv('complete_usage_telemetry.csv', index=False)
        transcripts.to_csv('complete_call_transcripts.csv', index=False)
        emails.to_csv('complete_email_threads.csv', index=False)
        surveys.to_csv('complete_survey_verbatims.csv', index=False)
        outcomes.to_csv('complete_outcomes_tracking.csv', index=False)
        
        # Also save sample transcripts and emails as text files
        with open('sample_transcript.txt', 'w') as f:
            f.write(transcripts.iloc[0]['transcript'])
        
        with open('sample_email_thread.txt', 'w') as f:
            f.write(emails.iloc[0]['thread_content'])
        
        print("\n✅ Complete dataset generated!")
        print(f"   📊 {len(telemetry)} usage telemetry records")
        print(f"   💬 {len(transcripts)} call transcripts")
        print(f"   📧 {len(emails)} email threads")
        print(f"   📝 {len(surveys)} survey responses")
        print(f"   🎯 {len(outcomes)} outcome records")
        
        return {
            'telemetry': telemetry,
            'transcripts': transcripts,
            'emails': emails,
            'surveys': surveys,
            'outcomes': outcomes
        }

# Example usage
if __name__ == "__main__":
    # First load the base healthcare data
    print("Loading base healthcare data...")
    customers = pd.read_csv('healthcare_customers.csv')
    interactions = pd.read_csv('healthcare_interactions.csv')
    calls = pd.read_csv('healthcare_calls.csv')
    
    # Generate complete enhanced dataset
    generator = CompleteCustomerDataGenerator(n_customers=len(customers))
    complete_data = generator.generate_complete_dataset(customers, interactions, calls)
    
    print("\n" + "="*60)
    print("SAMPLE CALL TRANSCRIPT:")
    print("="*60)
    print(complete_data['transcripts'].iloc[0]['transcript'][:800])
    
    print("\n" + "="*60)
    print("SAMPLE SURVEY VERBATIM:")
    print("="*60)
    sample_survey = complete_data['surveys'].iloc[0]
    print(f"NPS: {sample_survey['nps_score']} ({sample_survey['nps_category']})")
    print(f"\nPrimary Reason: {sample_survey['primary_reason_verbatim']}")
    print(f"\nImprovement Needed: {sample_survey['improvement_suggestion_verbatim']}")
    print(f"\nConsidering Alternatives: {sample_survey['considering_alternatives_verbatim']}")