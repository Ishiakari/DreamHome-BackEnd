from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0017_alter_payment_payment_no'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE PROCEDURE apply_monthly_late_fees(p_fee NUMERIC DEFAULT 50.00)
            LANGUAGE plpgsql
            AS $$
            DECLARE
                r RECORD;
                v_next_num INTEGER;
                v_payment_no VARCHAR;
            BEGIN
                FOR r IN 
                    SELECT l.lease_no, l.staff_no_id
                    FROM lease_agreement l
                    WHERE CURRENT_DATE <= l.rent_finish
                      AND calculate_outstanding_balance(l.lease_no) > 0
                LOOP
                    -- Find the maximum sequence number currently in the payment table
                    SELECT COALESCE(MAX(CAST(SUBSTRING(payment_no FROM '\\d+') AS INTEGER)), 0)
                    INTO v_next_num
                    FROM payment;
                    
                    v_next_num := v_next_num + 1;
                    v_payment_no := 'PAY' || LPAD(v_next_num::text, 3, '0');
                    
                    INSERT INTO payment (payment_no, lease_no, amount_paid, payment_method, payment_date, status, processed_by_staff_no)
                    VALUES (v_payment_no, r.lease_no, (p_fee * -1), 'Late Fee Penalty', CURRENT_TIMESTAMP, 'Penalty', r.staff_no_id);
                END LOOP;
            END;
            $$;
            """,
            reverse_sql="""
            CREATE OR REPLACE PROCEDURE apply_monthly_late_fees(p_fee NUMERIC DEFAULT 50.00)
            LANGUAGE plpgsql
            AS $$
            BEGIN
                INSERT INTO payment (lease_no, amount_paid, payment_method, payment_date, status, processed_by_staff_no)
                SELECT 
                    l.lease_no, 
                    (p_fee * -1), 
                    'Late Fee Penalty', 
                    CURRENT_TIMESTAMP, 
                    'Penalty',
                    l.staff_no_id
                FROM lease_agreement l
                WHERE CURRENT_DATE <= l.rent_finish
                    AND calculate_outstanding_balance(l.lease_no) > 0; 
            END;
            $$;
            """
        ),
    ]
