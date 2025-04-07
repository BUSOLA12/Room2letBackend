from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.timezone import now, timedelta
from .models import Interest

def password_reset_email(uidb64, token, email):
    subject = "Password Reset Token"
    reset_url = f"{settings.FRONTEND_URL}/password-reset-confirm/{uidb64}/{token}"
    
    # Context for the template
    context = {
        'reset_url': reset_url,
        'site_name': settings.SITE_NAME if hasattr(settings, 'SITE_NAME') else 'Our Website',
        'support_email': settings.SUPPORT_EMAIL if hasattr(settings, 'SUPPORT_EMAIL') else settings.DEFAULT_FROM_EMAIL,
    }
    
    # Render HTML content
    html_message = render_to_string('app/password_reset.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject, 
        plain_message, 
        settings.DEFAULT_FROM_EMAIL, 
        [email], 
        fail_silently=False,
        html_message=html_message
    )

def property_create_email(title, emails):
    subject = "New Property Needs Review"
    
    # Context for the template
    context = {
        'property_title': title,
        'admin_url': f"{settings.ADMIN_URL}/properties/" if hasattr(settings, 'ADMIN_URL') else "/admin/properties/",
        'site_name': settings.SITE_NAME if hasattr(settings, 'SITE_NAME') else 'Our Website',
    }
    
    # Render HTML content
    html_message = render_to_string('app/property_create.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject, 
        plain_message, 
        settings.DEFAULT_FROM_EMAIL, 
        emails, 
        fail_silently=True,
        html_message=html_message
    )

def property_status_change_email(title, status, email):
    subject = "Your Property Status Changed"
    
    # Context for the template
    context = {
        'property_title': title,
        'property_status': status.upper(),
        'dashboard_url': f"{settings.FRONTEND_URL}/dashboard" if hasattr(settings, 'FRONTEND_URL') else "/dashboard",
        'site_name': settings.SITE_NAME if hasattr(settings, 'SITE_NAME') else 'Our Website',
        'support_email': settings.SUPPORT_EMAIL if hasattr(settings, 'SUPPORT_EMAIL') else settings.DEFAULT_FROM_EMAIL,
    }
    
    # Render HTML content
    html_message = render_to_string('app/property_status_change.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject, 
        plain_message, 
        settings.DEFAULT_FROM_EMAIL, 
        [email], 
        fail_silently=True,
        html_message=html_message
    )




def email_interested_users(property_obj):
    local_govt = property_obj.local_Govt
    state = property_obj.state
    title = property_obj.title
    

    property_url = f"{settings.FRONTEND_URL}/properties/{property_obj.id}" if hasattr(settings, 'FRONTEND_URL') else f"/properties/{property_obj.id}"
    
    # Filter interests within the same local govt and created in the last 30 days
    one_month_ago = now() - timedelta(days=30)
    recent_interests = Interest.objects.filter(
        local_Govt__iexact=local_govt,
        created_at__gte=one_month_ago
    ).select_related('user').distinct()

    emails = set(i.user.email for i in recent_interests if i.user.email)
    
    subject = "New Property Match in Your Area"
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@yourdomain.com")
    
    # Create common context for all emails
    context = {
        'property_title': title,
        'local_govt': local_govt,
        'state': state,
        'property_url': property_url,
        'site_name': getattr(settings, 'SITE_NAME', 'Our Website'),
        'support_email': getattr(settings, 'SUPPORT_EMAIL', from_email)
    }
    
    # Add optional property details if available
    if hasattr(property_obj, 'price'):
        context['property_price'] = property_obj.price
    
    if hasattr(property_obj, 'property_type'):
        context['property_type'] = property_obj.property_type
    
    # Render HTML content
    html_message = render_to_string('app/property_match.html', context)
    # Create plain text version for email clients that don't support HTML
    plain_message = strip_tags(html_message)
    
    # Send emails individually to each interested user
    for email in emails:
        send_mail(
            subject, 
            plain_message, 
            from_email, 
            [email], 
            fail_silently=True,
            html_message=html_message
        )