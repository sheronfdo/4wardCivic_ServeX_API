from app.models.dashboard import Dashboard
from datetime import datetime, timedelta

class DashboardService:
    
    def get_total_services_count(self):
        """Get total services count"""
        return self.dashboard_model.get_total_services()
    
    def get_active_services_count(self):
        """Get active services count"""
        return self.dashboard_model.get_active_services()
    
    def get_pending_services_count(self):
        """Get pending services count"""
        return self.dashboard_model.get_pending_services()
    
    def get_recent_services_count(self):
        """Get recent services count (today)"""
        return self.dashboard_model.get_recent_services()
    
    def get_monthly_chart_data(self):
        """Get formatted chart data for frontend"""
        data = self.dashboard_model.get_monthly_usage_data()
        
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
    
    def get_recent_activities(self, limit=5):
        """Get recent activities with formatted timestamps"""
        activities = self.dashboard_model.get_recent_activities(limit)
        
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
    
    def get_key_statistics(self):
        """Get all key statistics for dashboard cards"""
        total = self.get_total_services_count()
        active = self.get_active_services_count()
        pending = self.get_pending_services_count()
        recent = self.get_recent_services_count()
        
        # Calculate growth/changes (you can implement your own logic)
        return [
            {
                "title": "Total Registered",
                "value": str(total),
                "subtitle": f"Up by {recent} from last month",
                "color": "bg-blue-500"
            },
            {
                "title": "Active",
                "value": str(active),
                "subtitle": "Up by government",
                "color": "bg-blue-600"
            },
            {
                "title": "Pending",
                "value": str(pending),
                "subtitle": "Pending from last month",
                "color": "bg-blue-700"
            },
            {
                "title": "Recent",
                "value": str(recent),
                "subtitle": "New from today",
                "color": "bg-blue-800"
            }
        ]
    
    def get_complete_dashboard_data(self):
        """Get all dashboard data in one service call"""
        try:
            return {
                "key_statistics": self.get_key_statistics(),
                "chart_data": self.get_monthly_chart_data(),
                "recent_activities": self.get_recent_activities(5),
                "summary": {
                    "total_services": self.get_total_services_count(),
                    "active_services": self.get_active_services_count(),
                    "pending_services": self.get_pending_services_count(),
                    "recent_services": self.get_recent_services_count()
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
    
    def get_service_trends(self, days=30):
        """Get service trends for the last N days"""
        try:
            # You can implement trend calculation logic here
            # This is a placeholder for trend analysis
            return {
                "trend": "increasing",
                "percentage": 5.2,
                "period": f"last {days} days"
            }
        except Exception as e:
            raise Exception(f"Error calculating service trends: {str(e)}")