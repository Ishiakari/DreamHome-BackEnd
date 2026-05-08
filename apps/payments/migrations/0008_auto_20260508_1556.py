from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        # This ensures the lease and payment tables exist first
        ('payments', '0005_auto_20260506_1027'), 
        ('leases', '0001_initial'), 
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE FUNCTION calculate_outstanding_balance(p_lease_no VARCHAR)
            RETURNS NUMERIC AS $$
            DECLARE
                v_total_due  NUMERIC;
                v_total_paid NUMERIC;
            BEGIN
                -- 1. Get total expected rent
                SELECT (monthly_rent * duration)
                    INTO v_total_due
                    FROM lease_agreement
                    WHERE lease_no = p_lease_no;

                -- 2. Sum existing payments
                SELECT COALESCE(SUM(amount_paid), 0)
                    INTO v_total_paid
                    FROM payment
                    WHERE lease_no = p_lease_no;

                -- 3. Calculate balance
                RETURN COALESCE(v_total_due, 0) - v_total_paid;
            END;
            $$ LANGUAGE plpgsql;
            """,
            reverse_sql="DROP FUNCTION IF EXISTS calculate_outstanding_balance(VARCHAR);"
        ),
    ]