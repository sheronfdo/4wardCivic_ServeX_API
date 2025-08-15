from app.models.dashboard import Dashboard
from datetime import datetime, timedelta

class DashboardService:
    def __init__(self):
        """Initialize the Dashboard instance"""
        self.dashboard = Dashboard()
    
    def get_total_services_count(self, authority_id=None):
        """Get total services count filtered by authority"""
        return self.dashboard.get_total_services(authority_id)
    
    def get_active_services_count(self, authority_id=None):
        """Get active services count filtered by authority"""
        return self.dashboard.get_active_services(authority_id)
    
    def get_pending_services_count(self, authority_id=None):
        """Get pending services count filtered by authority"""
        return self.dashboard.get_pending_services(authority_id)
    
    def get_recent_services_count(self, authority_id=None):
        """Get recent services count (today) filtered by authority"""
        return self.dashboard.get_recent_services(authority_id)
    
    def get_monthly_chart_data(self, authority_id=None):
        """Get formatted chart data for frontend filtered by authority"""
        data = self.dashboard.get_monthly_usage_data(authority_id)
        
        return {
            "labels": [
                "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
            ],
            "datasets": [
                {
                    "label": "Service Usage",
                    "data": data["service_usage"],
                    "backgroundColor": "rgba(59, 130, 246, 0.8)",
                    "borderColor": "rgba(59, 130, 246, 1)",
                    "borderWidth": 1,
                    "borderRadius": 4
                },
                {
                    "label": "Applications",
                    "data": data["applications"],
                    "backgroundColor": "rgba(34, 197, 94, 0.8)",
                    "borderColor": "rgba(34, 197, 94, 1)",
                    "borderWidth": 1,
                    "borderRadius": 4
                }
            ]
        }
    
    def get_recent_activities(self, limit=5, authority_id=None):
        """Get recent activities with formatted timestamps filtered by authority"""
        activities = self.dashboard.get_recent_activities(limit, authority_id)
        
        # Format activities for frontend
        formatted_activities = []
        for activity in activities:
            # Format timestamp if it's a datetime object
            timestamp = activity.get("timestamp", "")
            if isinstance(timestamp, datetime):
                timestamp = timestamp.strftime("%Y-%m-%d %I:%M %p")
            
            formatted_activities.append({
                "id": activity["id"],
                "description": activity["description"],
                "timestamp": timestamp,
                "status": activity["status"]
            })
        
        return formatted_activities
    
    def get_key_statistics(self, authority_id=None):
        """Get all key statistics filtered by authority"""
        try:
            return {
                "total_services": self.get_total_services_count(authority_id),
                "active_services": self.get_active_services_count(authority_id),
                "pending_services": self.get_pending_services_count(authority_id),
                "recent_services": self.get_recent_services_count(authority_id),
                "growth_trends": self.get_service_trends(authority_id=authority_id)
            }
        except Exception as e:
            raise Exception(f"Error getting key statistics: {str(e)}")
    
    def get_complete_dashboard_data(self, authority_id=None):
        """Get all dashboard data in one service call filtered by authority"""
        try:
            return {
                "chart_data": self.get_monthly_chart_data(authority_id),
                "recent_activities": self.get_recent_activities(5, authority_id),
                "summary": {
                    "total_services": self.get_total_services_count(authority_id),
                    "active_services": self.get_active_services_count(authority_id),
                    "pending_services": self.get_pending_services_count(authority_id),
                    "recent_services": self.get_recent_services_count(authority_id)
                }
            }
        except Exception as e:
            raise Exception(f"Error getting complete dashboard data: {str(e)}")
    
    def calculate_growth_percentage(self, current, previous):
        """Calculate percentage growth"""
        if previous == 0:
            return 100 if current > 0 else 0
        
        growth = ((current - previous) / previous) * 100
        return round(growth, 1)
    
    def get_service_trends(self, days=30, authority_id=None):
        """Get service trends for the last N days filtered by authority"""
        try:
            # You can implement trend calculation logic here
            # This is a placeholder for trend analysis
            # You would add authority filtering logic here as well
            return {
                "trend": "increasing",
                "percentage": 5.2,
                "period": f"last {days} days"
            }
        except Exception as e:
            raise Exception(f"Error calculating service trends: {str(e)}")