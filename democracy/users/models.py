import uuid

from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, DateTimeField, UUIDField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Default user for Democracy."""

    # Use a UUID as primary key.
    id = UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    created = DateTimeField(auto_now_add=True, editable=False)

    #: First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.
        """
        return reverse("users:detail", kwargs={"id": self.id})

    @property
    def email_domain(self) -> str:
        split = self.email.strip().split("@")
        if len(split) != 2:
            # raise Exception("Failed to split email into two parts.")
            return ""

        # Assume that whatever is after the '@' is the domain.
        domain: str = str(split[1])
        return domain
