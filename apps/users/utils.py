from django.utils import timezone

# CREATE OR REPLACE FUNCTION generate_client_no()
# RETURNS VARCHAR AS $$
# DECLARE
#     today_str VARCHAR(8);
#     last_client_no VARCHAR(12);
#     new_seq INT;
# BEGIN

    # today_str := to_char(CURRENT_DATE, 'YYYYMMDD');

    # SELECT client_no INTO last_client_no
    # FROM users_client 
    # WHERE client_no LIKE today_str || '%'
    # ORDER BY client_no DESC
    # LIMIT 1;
#    IF last_client_no IS NOT NULL THEN
#        new_seq := CAST(RIGHT(last_client_no, 4) AS INT) + 1;
#    ELSE
#        new_seq := 1;
#    END IF;
#    RETURN today_str || LPAD(new_seq::TEXT, 4, '0');
#END;
#$$ LANGUAGE plpgsql;

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