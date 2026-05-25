import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dreamhome_api.settings')
django.setup()

from django.db import connection

def drop_triggers():
    with connection.cursor() as cursor:
        cursor.execute("DROP TRIGGER IF EXISTS trigger_generate_payment_id ON payment;")
        print("Dropped trigger_generate_payment_id")

if __name__ == "__main__":
    drop_triggers()
