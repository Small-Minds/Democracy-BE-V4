from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, UpdateView):

    model = User
    fields = ["name"]

    def get_success_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})

    def get_object(self):
        return User.objects.get(username=self.request.user.username)

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.INFO, _("Infos successfully updated")
        )
        return super().form_valid(form)


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()


class ConfirmEmailView(APIView):
    """Allows API users to confirm an email address, then redirects to
    success/failure pages on the frontend."""

    permission_classes = [AllowAny]

    success_redirect_url = f"{settings.FRONTEND_URL}/email-verified"
    already_verified_redirect_url = f"{settings.FRONTEND_URL}/email-already-verified"
    failure_redirect_url = f"{settings.FRONTEND_URL}/email-verification-error"

    def get_queryset(self):
        queryset = EmailConfirmation.objects.all_valid()
        return queryset.select_related("email_address__user")

    def get(self, *args, **kwargs):
        key = kwargs["key"]
        email_confirmation = EmailConfirmationHMAC.from_key(key=key)
        if not email_confirmation:
            queryset = self.get_queryset()
            try:
                email_confirmation = queryset.get(key=key.lower())
            except EmailConfirmation.DoesNotExist:
                return HttpResponseRedirect(self.failure_redirect_url)

        if email_confirmation.email_address.verified:
            return HttpResponseRedirect(self.already_verified_redirect_url)

        email_confirmation.confirm(self.request)
        return HttpResponseRedirect(self.success_redirect_url)

    def post(self, *args, **kwargs):
        return HttpResponseForbidden()


confirm_email_view = ConfirmEmailView.as_view()
