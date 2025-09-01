from app.models.authority import Authority
from app.models.media import Media
from mongoengine.errors import ValidationError
import uuid

from app.utils.email import send_verification_email


class AuthorityService:
    """Service class for authority-related business logic"""

    def create_authority(authority_name, email, address, phone_number, hotline, authority_icon_id=None):
        try:
            if Authority.objects(email=email, status="ACTIVE", is_verified=True).first():
                raise ValueError('Email already registered')

            exist_pending_authority = Authority.objects(email = email, status = "PENDING").first()
            if exist_pending_authority:
                exist_pending_authority.delete()

            # Validate authorityIconId if provided
            icon = None
            if authority_icon_id:
                icon = Media.objects(id=authority_icon_id).first()
                if not icon:
                    raise ValueError("Invalid authority icon ID")

            token = str(uuid.uuid4())
            authority = Authority(
                authorityName=authority_name,
                email=email,
                address=address,
                phoneNumber=phone_number,
                hotline=hotline,
                authorityIconId=icon,
                verification_token=token,
                is_verified=False,
                status="PENDING"
            )
            authority.save()
            send_verification_email(email, authority_name, token, is_authority=True)
            return str(authority.id)
        except ValidationError as e:
            raise ValueError(f"Validation error: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to create authority: {str(e)}")

    def activate_authority(authorityId):
        try:
            authority = Authority.objects(id=authorityId).first()
            if not authority:
                raise ValueError('Authority not found')
            authority.status = "ACTIVE"
            authority.save()
            return str(authority.id)
        except ValidationError as e:
            raise ValueError(f"Validation error: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to create authority: {str(e)}")


    def verify_email(token):
        authority = Authority.objects(verification_token=token, is_verified=False).first()
        if not authority:
            raise ValueError('Invalid or expired token')
        authority.is_verified = True
        authority.verification_token = None
        authority.save()
        return str(authority.id)

    def get_authority(authority_id):
        authority = Authority.objects(id=authority_id).first()
        if not authority:
            raise ValueError('Authority not found')
        return authority
    
    def get_all(self, status_filter=None):
        query = Authority.objects()
        if status_filter:
            query = query.filter(status=status_filter)
        return list(query)
    
    def update_authority(self,authority_id, **authority_updates):
        try:
            # Find existing authority
            authority = Authority.objects(id=authority_id, status="ACTIVE").first()
            if not authority:
                raise ValueError("Authority not found or not active")

            # Validate email if provided and changed
            if 'email' in authority_updates and authority_updates['email'] != authority.email:
                if Authority.objects(email=authority_updates['email'], status="ACTIVE", is_verified=True).first():
                    raise ValueError("Email already registered")
                
                # Delete any pending authority with the same email
                exist_pending_authority = Authority.objects(email=authority_updates['email'], status="PENDING").first()
                if exist_pending_authority:
                    exist_pending_authority.delete()

                # Set new verification token and status for email change
                authority.verification_token = str(uuid.uuid4())
                authority.is_verified = False
                authority.status = "PENDING"
                send_verification_email(authority_updates['email'], authority.authorityName, authority.verification_token, is_authority=True)

            # Update fields if provided
            if 'authorityName' in authority_updates:
                authority.authorityName = authority_updates['authorityName']
            if 'email' in authority_updates:
                authority.email = authority_updates['email']
            if 'address' in authority_updates:
                authority.address = authority_updates['address']
            if 'phoneNumber' in authority_updates:
                authority.phoneNumber = authority_updates['phoneNumber']
            if 'hotline' in authority_updates:
                authority.hotline = authority_updates['hotline']
            if 'authorityIconId' in authority_updates:
                if authority_updates['authorityIconId']:
                    icon = Media.objects(id=authority_updates['authorityIconId']).first()
                    if not icon:
                        raise ValueError("Invalid authority icon ID")
                    authority.authorityIconId = icon
                else:
                    authority.authorityIconId = None

            authority.save()
            return str(authority.id)

        except ValidationError as e:
            raise ValueError(f"Validation error: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to update authority: {str(e)}")