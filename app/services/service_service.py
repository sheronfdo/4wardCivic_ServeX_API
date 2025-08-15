from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId
import re
from app.models.media import Media
from app.models.service import Service
from app.models.authority import Authority 

DUMMY_DATE = datetime(2025, 1, 1)

def parse_time_to_dummy_datetime(time_str):
    time_obj = datetime.strptime(time_str, "%H:%M").time()
    return datetime.combine(DUMMY_DATE.date(), time_obj)

class ServiceService:
        
    def create_service(self, service_data: Dict[str, Any]) -> Service:
        """
        Create a new service
        """
        # Validate required fields
        required_fields = ['serviceName', 'serviceFeeLRK', 'slotduration', 'authority_id']
        for field in required_fields:
            if field not in service_data or service_data[field] is None or service_data[field] == '':
                raise ValueError(f"Missing required field: {field}")
        
        # Validate and get authority
        authority = None
        try:
            authority = Authority.objects(id=service_data['authority_id']).first()
            if not authority:
                raise ValueError("Authority not found")
        except InvalidId:
            raise ValueError("Invalid authority ID format")

        # Validate service icon exists if provided
        service_icon = None

        if service_data.get('serviceIconId'):
            try:
                service_icon = Media.objects(id=service_data['serviceIconId']).first()
                if not service_icon:
                    raise ValueError("Service icon not found")
            except InvalidId:
                raise ValueError("Invalid service icon ID format")
        
        # Create service instance
        service = Service(
            service_name=service_data['serviceName'].strip(),
            note=service_data.get('note', '').strip() or None,
            service_fee_lrk=float(service_data['serviceFeeLRK']),
            start_time=(service_data['startTime']),
            end_time=(service_data['endTime']),
            slot_duration=int(service_data['slotduration']),
            max_people_per_slot=int(service_data.get('maxPeoplePerSlot', 1)),
            kyc=bool(service_data.get('kyc', False)),
            physicalAttendance=bool(service_data.get('isPhysicalAttendance', False)),
            service_icon=service_icon,
            authority=authority,
            status=service_data.get('status', 'Active')
        )
        
        # Validate business rules
        self._validate_service_data(service)
        
        service.save()
        return service
    
    def get_service_by_id(self, service_id: str) -> Optional[Service]:
        """
        Get a service by ID
        """
        try:
            return Service.objects(id=service_id).first()
        except InvalidId:
            return None
    
    def get_all_services(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        status_filter: Optional[str] = None
    ) -> List[Service]:
        """
        Get all services with optional filtering
        """
        query = Service.objects()
        
        if status_filter:
            query = query.filter(status=status_filter)
        
        return query.skip(skip).limit(limit).order_by('-created_at')
    
    def get_all_authority_services(self, skip=0, limit=100, status_filter=None, authority_id=None):
        query = {}
        if status_filter:
            query["status"] = status_filter
        if authority_id:
            query["authority"] = ObjectId(authority_id)  # filter by authority

        return Service.objects(**query).skip(skip).limit(limit)

    def get_services_by_name(self, service_name: str) -> List[Service]:
        """
        Get services by name (partial match, case-insensitive)
        """
        pattern = re.compile(re.escape(service_name), re.IGNORECASE)
        return Service.objects(service_name=pattern)
    
    def update_service(self, service_id: str, update_data: Dict[str, Any]) -> Service:
        """
        Update an existing service
        """
        try:
            service = Service.objects(id=service_id).first()
            if not service:
                raise ValueError("Service not found")
            
            # Validate service icon exists if being updated
            if 'serviceIconId' in update_data:
                if update_data['serviceIconId']:
                    service_icon = Media.objects(id=update_data['serviceIconId']).first()
                    if not service_icon:
                        raise ValueError("Service icon not found")
                    service.service_icon = service_icon
                else:
                    service.service_icon = None
            
            # Update fields with proper mapping
            field_mapping = {
                'serviceName': 'service_name',
                'serviceFeeLRK': 'service_fee_lrk',
                'slotduration': 'slot_duration',
                'maxPeoplePerSlot': 'max_people_per_slot',
                'kyc': 'kyc',
                'note': 'note',
                'status': 'status'
            }
            
            for frontend_field, db_field in field_mapping.items():
                if frontend_field in update_data:
                    value = update_data[frontend_field]
                    
                    # Convert data types for specific fields
                    if db_field == 'service_fee_lrk' and value is not None:
                        value = float(value)
                    elif db_field in ['slot_duration', 'max_people_per_slot'] and value is not None:
                        value = int(value)
                    elif db_field == 'kyc' and value is not None:
                        value = bool(value)
                    elif db_field in ['service_name', 'note'] and value is not None:
                        value = value.strip() if value else None
                    
                    setattr(service, db_field, value)
            
            # Validate updated data
            self._validate_service_data(service)
            
            service.save()
            return service
            
        except InvalidId:
            raise ValueError("Invalid service ID format")
    
    def delete_service(self, service_id: str) -> bool:
        """
        Mark a service as deleted (soft delete)
        """
        try:
            service = Service.objects(id=service_id).first()
            if not service:
                raise ValueError("Service not found")
        
            # Mark as deleted by updating the status field
            service.update(set__status="deleted")  # assuming 'status' is a field in your model
        
            return True
    
        except InvalidId:
            raise ValueError("Invalid service ID format")

    
    def get_active_services(self) -> List[Service]:
        """
        Get all active services
        """
        return Service.objects(status="Active").order_by('-created_at')
    
    def get_services_by_fee_range(self, min_fee: float, max_fee: float) -> List[Service]:
        """
        Get services within a fee range
        """
        return Service.objects(
            service_fee_lrk__gte=min_fee,
            service_fee_lrk__lte=max_fee
        ).order_by('service_fee_lrk')
    
    def get_services_by_slot_duration(self, duration: int) -> List[Service]:
        """
        Get services by slot duration
        """
        return Service.objects(slot_duration=duration)
    
    def get_kyc_mandatory_services(self) -> List[Service]:
        """
        Get all services that require KYC
        """
        return Service.objects(kyc=True)
    
    def search_services(self, search_term: str) -> List[Service]:
        """
        Search services by name or note (case-insensitive)
        """
        pattern = re.compile(re.escape(search_term), re.IGNORECASE)
        return Service.objects(
            __raw__={
                "$or": [
                    {"service_name": pattern},
                    {"note": pattern}
                ]
            }
        ).order_by('-created_at')
    
    def get_services_count(self, status_filter: Optional[str] = None) -> int:
        """
        Get total count of services
        """
        query = Service.objects()
        if status_filter:
            query = query.filter(status=status_filter)
        return query.count()
    
    def _validate_service_data(self, service: Service):
        """
        Validate service data according to business rules
        """
        if not service.service_name or len(service.service_name.strip()) == 0:
            raise ValueError("Service name is required")
        
        if len(service.service_name) > 255:
            raise ValueError("Service name must be less than 255 characters")
        
        if service.service_fee_lrk < 0:
            raise ValueError("Service fee cannot be negative")
        
        if service.slot_duration <= 0:
            raise ValueError("Slot duration must be greater than 0 minutes")
        
        if service.slot_duration > 1440:  # 24 hours in minutes
            raise ValueError("Slot duration cannot exceed 24 hours")
        
        if service.max_people_per_slot <= 0:
            raise ValueError("Max people per slot must be greater than 0")
        
        if service.max_people_per_slot > 100:
            raise ValueError("Max people per slot cannot exceed 100")
        
        if service.status not in ['Active', 'Inactive']:
            raise ValueError("Status must be either 'Active' or 'Inactive'")
        



