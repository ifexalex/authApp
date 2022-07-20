from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives


def send_mail(subject, body, sender, recipient, context):
    """
    It takes a subject, body, sender, recipient, and context, and sends an email with the subject, body,
    and sender to the recipient
    
    :param subject: The subject of the email
    :param body: The template to use for the email body
    :param sender: The email address that the email is being sent from
    :param recipient: The email address of the recipient
    :param context: A dictionary of values to be passed to the template
    """
    html_content = render_to_string(body, context)
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(subject, text_content, sender, recipient)
    email.attach_alternative(html_content, "text/html")
    email.send()
