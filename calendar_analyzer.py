#!/usr/bin/env python3
"""
Google Calendar Analyzer for Calendar Consolidation Project

This script analyzes the current Google Calendar structure to understand:
- Calendar count and names
- Sharing permissions
- Event types and patterns
- Usage statistics
- Current organization system
"""

import os
import json
import pickle
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Calendar API scope - read-only for analysis
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class GoogleCalendarAnalyzer:
    def __init__(self, credentials_file='client_secret_510608642536-rn43nlpin83e7vtksm05ci7u7qkcp7nf.apps.googleusercontent.com.json'):
        self.credentials_file = credentials_file
        self.service = None
        self.analysis_results = {}
        
    def authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        
        # Check if we have stored credentials
        if os.path.exists('calendar_token.pickle'):
            with open('calendar_token.pickle', 'rb') as token:
                creds = pickle.load(token)
                
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
                
            # Save credentials for next run
            with open('calendar_token.pickle', 'wb') as token:
                pickle.dump(creds, token)
                
        self.service = build('calendar', 'v3', credentials=creds)
        print("✅ Successfully authenticated with Google Calendar API")
        
    def get_calendar_list(self):
        """Get all calendars and their metadata"""
        print("\n📅 Analyzing Calendar Structure...")
        
        calendars = []
        page_token = None
        
        while True:
            calendar_list = self.service.calendarList().list(pageToken=page_token).execute()
            
            for calendar in calendar_list['items']:
                calendar_info = {
                    'id': calendar['id'],
                    'summary': calendar.get('summary', 'No Title'),
                    'description': calendar.get('description', ''),
                    'primary': calendar.get('primary', False),
                    'access_role': calendar.get('accessRole', 'unknown'),
                    'background_color': calendar.get('backgroundColor', '#ffffff'),
                    'foreground_color': calendar.get('foregroundColor', '#000000'),
                    'selected': calendar.get('selected', False),
                    'time_zone': calendar.get('timeZone', 'unknown'),
                    'notification_settings': calendar.get('defaultReminders', [])
                }
                calendars.append(calendar_info)
                
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break
                
        self.analysis_results['calendars'] = calendars
        print(f"   Found {len(calendars)} calendars")
        return calendars
        
    def analyze_recent_events(self, days_back=90):
        """Analyze recent events across all calendars"""
        print(f"\n📊 Analyzing Events from Last {days_back} Days...")
        
        # Calculate time range
        now = datetime.utcnow()
        start_time = (now - timedelta(days=days_back)).isoformat() + 'Z'
        end_time = now.isoformat() + 'Z'
        
        all_events = []
        event_patterns = {
            'by_calendar': defaultdict(int),
            'by_day_of_week': defaultdict(int),
            'by_hour': defaultdict(int),
            'recurring_events': 0,
            'all_day_events': 0,
            'multi_day_events': 0,
            'event_titles': Counter(),
            'attendee_counts': [],
            'durations': []
        }
        
        calendars = self.analysis_results.get('calendars', [])
        
        for calendar in calendars:
            calendar_id = calendar['id']
            calendar_name = calendar['summary']
            
            try:
                events_result = self.service.events().list(
                    calendarId=calendar_id,
                    timeMin=start_time,
                    timeMax=end_time,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                
                events = events_result.get('items', [])
                event_patterns['by_calendar'][calendar_name] = len(events)
                
                for event in events:
                    event_info = self.analyze_single_event(event, calendar_name)
                    all_events.append(event_info)
                    
                    # Update patterns
                    if event_info['recurring']:
                        event_patterns['recurring_events'] += 1
                    if event_info['all_day']:
                        event_patterns['all_day_events'] += 1
                    if event_info['multi_day']:
                        event_patterns['multi_day_events'] += 1
                        
                    event_patterns['by_day_of_week'][event_info['day_of_week']] += 1
                    if event_info['start_hour'] is not None:
                        event_patterns['by_hour'][event_info['start_hour']] += 1
                        
                    event_patterns['event_titles'][event_info['title']] += 1
                    event_patterns['attendee_counts'].append(event_info['attendee_count'])
                    
                    if event_info['duration_minutes']:
                        event_patterns['durations'].append(event_info['duration_minutes'])
                        
            except Exception as e:
                print(f"   ⚠️  Error accessing calendar '{calendar_name}': {e}")
                continue
                
        self.analysis_results['events'] = all_events
        self.analysis_results['event_patterns'] = event_patterns
        print(f"   Analyzed {len(all_events)} events")
        return all_events, event_patterns
        
    def analyze_single_event(self, event, calendar_name):
        """Extract detailed information from a single event"""
        start = event.get('start', {})
        end = event.get('end', {})
        
        # Handle all-day vs timed events
        start_datetime = None
        end_datetime = None
        all_day = False
        
        if 'date' in start:  # All-day event
            all_day = True
            start_datetime = datetime.strptime(start['date'], '%Y-%m-%d')
            end_datetime = datetime.strptime(end['date'], '%Y-%m-%d')
        else:  # Timed event
            start_datetime = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
            end_datetime = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))
            
        # Calculate duration
        duration_minutes = None
        if start_datetime and end_datetime:
            duration = end_datetime - start_datetime
            duration_minutes = int(duration.total_seconds() / 60)
            
        # Check if multi-day
        multi_day = False
        if start_datetime and end_datetime:
            multi_day = (end_datetime.date() - start_datetime.date()).days > 0
            
        return {
            'id': event.get('id', ''),
            'title': event.get('summary', 'No Title'),
            'description': event.get('description', ''),
            'calendar': calendar_name,
            'start_datetime': start_datetime,
            'end_datetime': end_datetime,
            'all_day': all_day,
            'multi_day': multi_day,
            'duration_minutes': duration_minutes,
            'recurring': 'recurringEventId' in event,
            'attendees': event.get('attendees', []),
            'attendee_count': len(event.get('attendees', [])),
            'creator': event.get('creator', {}).get('email', ''),
            'organizer': event.get('organizer', {}).get('email', ''),
            'status': event.get('status', ''),
            'transparency': event.get('transparency', 'opaque'),
            'visibility': event.get('visibility', 'default'),
            'location': event.get('location', ''),
            'day_of_week': start_datetime.strftime('%A') if start_datetime else None,
            'start_hour': start_datetime.hour if start_datetime and not all_day else None
        }
        
    def generate_report(self):
        """Generate comprehensive analysis report"""
        print("\n📋 Generating Analysis Report...")
        
        report = {
            'analysis_date': datetime.now().isoformat(),
            'summary': {},
            'calendars': self.analysis_results.get('calendars', []),
            'events': self.analysis_results.get('events', []),
            'patterns': self.analysis_results.get('event_patterns', {}),
            'recommendations': []
        }
        
        # Generate summary statistics
        calendars = report['calendars']
        events = report['events']
        patterns = report['patterns']
        
        report['summary'] = {
            'total_calendars': len(calendars),
            'primary_calendars': len([c for c in calendars if c['primary']]),
            'shared_calendars': len([c for c in calendars if c['access_role'] in ['writer', 'reader']]),
            'owned_calendars': len([c for c in calendars if c['access_role'] == 'owner']),
            'total_events_analyzed': len(events),
            'events_per_day': len(events) / 90 if events else 0,
            'recurring_events_percentage': (patterns.get('recurring_events', 0) / len(events) * 100) if events else 0,
            'all_day_events_percentage': (patterns.get('all_day_events', 0) / len(events) * 100) if events else 0
        }
        
        # Generate recommendations based on analysis
        recommendations = []
        
        if len(calendars) > 5:
            recommendations.append("Consider consolidating calendars - you have many separate calendars which can increase complexity")
            
        if patterns.get('recurring_events', 0) / len(events) < 0.3:
            recommendations.append("Low percentage of recurring events - consider setting up recurring events for regular appointments")
            
        busiest_day = max(patterns.get('by_day_of_week', {}).items(), key=lambda x: x[1], default=(None, 0))
        if busiest_day[0]:
            recommendations.append(f"Your busiest day is {busiest_day[0]} - consider time-blocking strategies for this day")
            
        if patterns.get('by_calendar', {}).get('primary', 0) / len(events) > 0.8:
            recommendations.append("Most events are in your primary calendar - consider using separate calendars for different life areas")
            
        report['recommendations'] = recommendations
        
        # Save report to file
        with open('calendar_analysis_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
            
        return report
        
    def print_summary(self, report):
        """Print human-readable summary"""
        print("\n" + "="*60)
        print("📊 GOOGLE CALENDAR ANALYSIS SUMMARY")
        print("="*60)
        
        summary = report['summary']
        print(f"\n📅 CALENDAR OVERVIEW:")
        print(f"   Total Calendars: {summary['total_calendars']}")
        print(f"   Primary Calendars: {summary['primary_calendars']}")
        print(f"   Owned Calendars: {summary['owned_calendars']}")
        print(f"   Shared Calendars: {summary['shared_calendars']}")
        
        print(f"\n📊 EVENT STATISTICS (Last 90 Days):")
        print(f"   Total Events: {summary['total_events_analyzed']}")
        print(f"   Events per Day: {summary['events_per_day']:.1f}")
        print(f"   Recurring Events: {summary['recurring_events_percentage']:.1f}%")
        print(f"   All-Day Events: {summary['all_day_events_percentage']:.1f}%")
        
        print(f"\n📋 CALENDARS:")
        for calendar in report['calendars']:
            primary_indicator = " (PRIMARY)" if calendar['primary'] else ""
            print(f"   • {calendar['summary']}{primary_indicator}")
            print(f"     Access: {calendar['access_role']} | Color: {calendar['background_color']}")
            
        patterns = report['patterns']
        if patterns.get('by_calendar'):
            print(f"\n📈 EVENTS BY CALENDAR:")
            for cal_name, count in sorted(patterns['by_calendar'].items(), key=lambda x: x[1], reverse=True):
                print(f"   • {cal_name}: {count} events")
                
        if patterns.get('by_day_of_week'):
            print(f"\n📅 EVENTS BY DAY OF WEEK:")
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            for day in days_order:
                count = patterns['by_day_of_week'].get(day, 0)
                print(f"   • {day}: {count} events")
                
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"   {i}. {rec}")
            
        print(f"\n📄 Full report saved to: calendar_analysis_report.json")
        print("="*60)
        
    def run_full_analysis(self):
        """Run complete calendar analysis"""
        print("🔍 Starting Google Calendar Analysis...")
        print("This will analyze your calendar structure and usage patterns.")
        
        try:
            self.authenticate()
            self.get_calendar_list()
            self.analyze_recent_events()
            report = self.generate_report()
            self.print_summary(report)
            
            print("\n✅ Analysis complete! Check calendar_analysis_report.json for detailed results.")
            return report
            
        except Exception as e:
            print(f"\n❌ Error during analysis: {e}")
            return None

if __name__ == "__main__":
    analyzer = GoogleCalendarAnalyzer()
    analyzer.run_full_analysis() 