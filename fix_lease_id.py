import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dreamhome_api.settings')
django.setup()

from django.db import connection

def fix_empty_lease_id():
    try:
        with connection.cursor() as cursor:
            # Check if there's a lease with empty string as lease_no
            cursor.execute("SELECT * FROM lease_agreement WHERE lease_no = '' OR lease_no IS NULL")
            if cursor.fetchone():
                cursor.execute("UPDATE lease_agreement SET lease_no = 'L001' WHERE lease_no = '' OR lease_no IS NULL")
                print("Successfully updated empty lease_no to 'L001'")
            else:
                print("No lease found with an empty ID.")
    except Exception as e:
        print(f"Error fixing lease ID: {e}")

if __name__ == "__main__":
    fix_empty_lease_id()
