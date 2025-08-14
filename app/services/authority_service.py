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