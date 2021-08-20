from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from ewayshop import settings
from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def sendCustomMail(message, recepiants, subject,template):  #template= 'filename.html'
    #  send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,[recepiants], fail_silently=False)
    email_html_message = render_to_string(template, message)
    email = EmailMultiAlternatives(subject, email_html_message, settings.DEFAULT_FROM_EMAIL, [recepiants])
    email.attach_alternative(email_html_message, "text/html")
    email.send()