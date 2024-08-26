import re
from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from dmaps.models import Collaborator
from rest_framework import status
from rest_framework.response import Response


@receiver(post_save, sender=Collaborator)
def send_thank_you_email(sender, instance, created, raw, **kwargs):
    if created:
        current_site = settings.BACKEND_URL
        email_subject = "Thank You from DMAPS Team"
        template = "collaborator_message_received.html"

        email_data = {
            "user_title": instance.name.title()
            if instance.name
            else re.split(r"[@.]", instance.email)[0].title(),
            "user": instance,
            "domain": current_site,
        }
        mail_to = str(instance.email)
        html_message = render_to_string(template, email_data)
        email_message = strip_tags(html_message)
        try:
            email_res = send_mail(
                email_subject,
                email_message,
                settings.EMAIL_HOST_USER,
                [
                    instance.email,
                ],
                html_message=html_message,
                fail_silently=False,
            )
            email_response = (
                ", Confirm your email address.".format(mail_to)
                if email_res
                else "Email verification could not be done."
            )
        except Exception as e:
            return Response(
                {"message": f"Error sending email to partner."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@receiver(post_save, sender=Collaborator)
def send_team_notification_email(sender, instance, **kwargs):
    team_email = "info.dmaps@gmail.com"
    email_subject = "New message from a partner at DMAPS"
    template = "organization_message_received.html"

    role = dict(Collaborator.COLLABORATORS_CHOICES).get(
        instance.collaborator, "collaborator"
    )

    email_data = {
        "role": role,
        "message": instance.message,
    }
    html_message = render_to_string(template, email_data)
    email_message = strip_tags(html_message)

    try:
        send_mail(
            email_subject,
            email_message,
            settings.EMAIL_HOST_USER,
            [team_email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        return Response(
            {"message": f"Error sending email to team."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
