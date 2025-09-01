from bson import ObjectId
from datetime import datetime

from app.models.service import Service
from app.models.process import Process,SubProcess
from app.models.staff_roll import StaffRoll
 # Fixed import name

class ProcessService:
    
    @staticmethod
    def create_process_for_service(service_id, processes_data):
        """Create process workflow for a service"""
        try:
            # Get service
            service = Service.objects(id=ObjectId(service_id)).first()
            if not service:
                return {"success": False, "message": "Service not found"}

            subprocesses = []
            for idx, process_item in enumerate(processes_data, start=1):
                staffrole_obj = StaffRoll.objects(id=ObjectId(process_item['role'])).first()
                if not staffrole_obj:
                    return {"success": False, "message": f"Staff role not found for {process_item['role']}"}

                subprocesses.append(SubProcess(
                    process_name=process_item['process'],
                    assignedRole=staffrole_obj,
                    order=idx,
                    status="ACTIVE"
                ))

            process_doc = Process(
                service=service,
                processes=subprocesses
            )
            process_doc.save()

            return {
                "success": True,
                "message": "Processes added successfully",
                "data": process_doc.to_json()
            }

        except Exception as e:
            return {"success": False, "message": f"Error creating processes: {str(e)}"}

    @staticmethod
    def get_processes_by_service(service_id):
        """Fetch processes linked to a given service ID"""
        try:
            process_doc = Process.objects(service=ObjectId(service_id)).first()
            if not process_doc:
                return {
                    "success": False,
                    "message": "No processes found for this service"
                }
            
            # Convert embedded SubProcesses to dicts
            processes_list = []
            for sub in process_doc.processes:
                # Retrieve the staff role using the assignedRole ID
                staff_roll_obj = StaffRoll.objects(id=sub.assignedRole.id).first()
                if not staff_roll_obj:
                    return {
                        "success": False,
                        "message": f"No Staff Role found for process {sub.process_name}"
                    }

                processes_list.append({
                    "process_name": sub.process_name,
                    "assignedRole": {
                        "id": str(staff_roll_obj.id),
                        "staffroll": staff_roll_obj.staffroll  # You can include any additional fields you want from StaffRoll here
                    },
                    "order": sub.order,
                    "status": sub.status
                })

            return {
                "success": True,
                "service_id": str(process_doc.service.id),
                "processes": processes_list
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error fetching processes: {str(e)}"
            }


