from django.utils import timezone

def generate_client_no():
    """
    Generates a unique ID in the format YYYYMMDDXXXX.
    Example: 202604030001
    """
    today_str = timezone.now().strftime('%Y%m%d')

    # Keep this import inside the function to prevent circular import errors
    from .models import Client

    last_client = Client.objects.filter(client_no__startswith=today_str).order_by('-client_no').first()

    if last_client:
        last_sequence = int(last_client.client_no[-4:])
        new_sequence = last_sequence + 1
    else:
        new_sequence = 1

    return f"{today_str}{new_sequence:04d}"