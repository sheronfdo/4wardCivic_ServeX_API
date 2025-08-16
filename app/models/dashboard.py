from datetime import datetime
from app.models.service import Service
from app.models.activity import Activity
from app.models.service_requested import ServiceRequested  # Assuming you have an Activity model
from bson import ObjectId

class Dashboard:
    def __init__(self):
        """Initialize the Dashboard class"""
        pass
      
    def get_total_services(self, authority_id=None):
        """Get total number of services filtered by authority"""
        try:
            if authority_id:
                # Convert string to ObjectId if needed
                if isinstance(authority_id, str):
                    authority_id = ObjectId(authority_id)
                return Service.objects(authority=authority_id).count()
            else:
                return Service.objects.count()
        except Exception as e:
            print(f"Error getting total services: {e}")
            return 0
    
    def get_active_services(self, authority_id=None):
        """Get active services count filtered by authority"""
        try:
            query_filter = {"status": "Active"}
            if authority_id:
                if isinstance(authority_id, str):
                    authority_id = ObjectId(authority_id)
                query_filter["authority"] = authority_id
                
            return Service.objects(**query_filter).count()
        except Exception as e:
            print(f"Error getting active services: {e}")
            return 0
    
    def get_pending_services(self, authority_id=None):
        """Get inactive services count filtered by authority"""
        try:
            query_filter = {"status": "Inactive"}
            if authority_id:
                if isinstance(authority_id, str):
                    authority_id = ObjectId(authority_id)
                query_filter["authority"] = authority_id
                
            return Service.objects(**query_filter).count()
        except Exception as e:
            print(f"Error getting inactive services: {e}")
            return 0
    
    def get_recent_services(self, authority_id=None):
        """Get services created today filtered by authority"""
        try:
            # Get today's date range
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
            
            query_filter = {
                "created_at__gte": today_start,
                "created_at__lte": today_end
            }
            
            if authority_id:
                if isinstance(authority_id, str):
                    authority_id = ObjectId(authority_id)
                query_filter["authority"] = authority_id
            
            return Service.objects(**query_filter).count()
        except Exception as e:
            print(f"Error getting recent services: {e}")
            return 0
    
    def get_monthly_usage_data(self, authority_id=None):
        """Get monthly service usage data for chart filtered by authority"""
        try:
            # Build match stage for aggregation
            match_stage = {}
            if authority_id:
                if isinstance(authority_id, str):
                    authority_id = ObjectId(authority_id)
                match_stage["authority"] = authority_id
            
            # MongoEngine aggregation pipeline
            pipeline = []
            
            # Add match stage if we have filters
            if match_stage:
                pipeline.append({"$match": match_stage})
            
            pipeline.extend([
                {
                    "$group": {
                        "_id": {"$month": "$created_at"},
                        "service_count": {"$sum": 1}
                    }
                },
                {"$sort": {"_id": 1}}
            ])
            
            result = list(ServiceRequested.objects.aggregate(pipeline))
            
            # Initialize data for all 12 months
            service_data = [0] * 12
            
            for item in result:
                month_index = item["_id"] - 1  # Convert to 0-based index
                service_data[month_index] = item["service_count"]
            
            return {
                "service_usage": service_data,
                "applications": [0] * 12  # You can implement this based on your Application model
            }
        except Exception as e:
            print(f"Error getting monthly usage data: {e}")
            return {
                "service_usage": [0] * 12,
                "applications": [0] * 12
            }
    
    def get_recent_activities(self, limit=5, authority_id=None):
        """Get recent activities using MongoEngine Activity model"""
        try:
            # Build query filter
            query_filter = {}
            if authority_id:
                if isinstance(authority_id, str):
                    authority_id = ObjectId(authority_id)
                query_filter["authority"] = authority_id
            
            # Use MongoEngine query
            activities = Activity.objects(**query_filter).order_by('-timestamp').limit(limit)
            
            formatted_activities = []
            for activity in activities:
                formatted_activities.append({
                    "id": str(activity.id),
                    "description": activity.description if hasattr(activity, 'description') else "",
                    "timestamp": activity.timestamp if hasattr(activity, 'timestamp') else "",
                    "status": activity.status if hasattr(activity, 'status') else "Pending"
                })
            
            return formatted_activities
        except Exception as e:
            print(f"Error getting recent activities: {e}")
            # Return empty list if Activity model doesn't exist or has issues
            return []
    
    def get_dashboard_summary(self, authority_id=None):
        """Get all dashboard data in one call filtered by authority"""
        try:
            return {
                "statistics": {
                    "total_services": self.get_total_services(authority_id),
                    "active_services": self.get_active_services(authority_id),
                    "pending_services": self.get_pending_services(authority_id),
                    "recent_services": self.get_recent_services(authority_id)
                },
                "chart_data": self.get_monthly_usage_data(authority_id),
                "recent_activities": self.get_recent_activities(5, authority_id)
            }
        except Exception as e:
            print(f"Error getting dashboard summary: {e}")
            return {
                "statistics": {
                    "total_services": 0,
                    "active_services": 0,
                    "pending_services": 0,
                    "recent_services": 0
                },
                "chart_data": {
                    "service_usage": [0] * 12,
                    "applications": [0] * 12
                },
                "recent_activities": []
            }