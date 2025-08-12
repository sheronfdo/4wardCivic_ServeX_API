from app.models.authority import Authority
from app.models.media import Media
from mongoengine.errors import ValidationError

class AuthorityService:
    """Service class for authority-related business logic"""

    def create_authority(authority_name, email, address, phone_number, hotline, authority_icon_id=None):
        try:
            # Validate authorityIconId if provided
            icon = None
            if authority_icon_id:
                icon = Media.objects(id=authority_icon_id).first()
                if not icon:
                    raise ValueError("Invalid authority icon ID")

            authority = Authority(
                authorityName=authority_name,
                email=email,
                address=address,
                phoneNumber=phone_number,
                hotline=hotline,
                authorityIconId=icon
            )
            authority.save()
            return str(authority.id)
        except ValidationError as e:
            raise ValueError(f"Validation error: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to create authority: {str(e)}")