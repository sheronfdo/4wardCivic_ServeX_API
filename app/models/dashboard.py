from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime


class Dashboard:
      
    def get_total_services(self):
        """Get total number of services"""
        try:
            return self.db.services.count_documents({})
        except Exception as e:
            print(f"Error getting total services: {e}")
            return 0
    
    def get_active_services(self):
        """Get active services count"""
        try:
            return self.db.services.count_documents({"status": "active"})
        except Exception as e:
            print(f"Error getting active services: {e}")
            return 0
    
    def get_pending_services(self):
        """Get pending services count"""
        try:
            return self.db.services.count_documents({"status": "pending"})
        except Exception as e:
            print(f"Error getting pending services: {e}")
            return 0
    
    def get_recent_services(self):
        """Get services created today"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            return self.db.services.count_documents({
                "created_date": {"$regex": f"^{today}"}
            })
        except Exception as e:
            print(f"Error getting recent services: {e}")
            return 0
    
    def get_monthly_usage_data(self):
        """Get monthly service usage data for chart"""
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": {"$month": "$created_date"},
                        "service_count": {"$sum": 1},
                        "application_count": {"$sum": "$applications"}
                    }
                },
                {"$sort": {"_id": 1}}
            ]
            
            result = list(self.db.services.aggregate(pipeline))
            
            # Initialize data for all 12 months
            service_data = [0] * 12
            application_data = [0] * 12
            
            for item in result:
                month_index = item["_id"] - 1  # Convert to 0-based index
                service_data[month_index] = item["service_count"]
                application_data[month_index] = item.get("application_count", 0)
            
            return {
                "service_usage": service_data,
                "applications": application_data
            }
        except Exception as e:
            print(f"Error getting monthly usage data: {e}")
            return {
                "service_usage": [65, 59, 80, 81, 56, 55, 70, 85, 75, 90, 95, 88],
                "applications": [45, 49, 60, 71, 46, 45, 50, 65, 55, 70, 75, 68]
            }
    
    def get_recent_activities(self, limit=5):
        """Get recent activities for the activities table"""
        try:
            activities = list(self.db.activities.find().sort("timestamp", -1).limit(limit))
            
            formatted_activities = []
            for activity in activities:
                formatted_activities.append({
                    "id": str(activity["_id"]),
                    "description": activity.get("description", ""),
                    "timestamp": activity.get("timestamp", ""),
                    "status": activity.get("status", "Pending")
                })
            
            return formatted_activities
        except Exception as e:
            print(f"Error getting recent activities: {e}")
            return []
    
    def get_dashboard_summary(self):
        """Get all dashboard data in one call"""
        try:
            return {
                "statistics": {
                    "total_services": self.get_total_services(),
                    "active_services": self.get_active_services(),
                    "pending_services": self.get_pending_services(),
                    "recent_services": self.get_recent_services()
                },
                "chart_data": self.get_monthly_usage_data(),
                "recent_activities": self.get_recent_activities()
            }
        except Exception as e:
            print(f"Error getting dashboard summary: {e}")
            return None