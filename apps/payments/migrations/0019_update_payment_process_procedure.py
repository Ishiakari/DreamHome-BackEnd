from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0018_update_late_fee_procedure'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE PROCEDURE process_rental_payment(
                p_lease_no VARCHAR,
                p_amount NUMERIC,
                p_method VARCHAR,
                p_staff_no VARCHAR
            )
            LANGUAGE plpgsql
            AS $$
            DECLARE
                v_check_lease VARCHAR;
                v_next_num INTEGER;
                v_payment_no VARCHAR;
            BEGIN
                -- 1. CONCURRENCY & TRANSACTION CONTROL
                SELECT lease_no INTO v_check_lease
                FROM lease_agreement
                WHERE lease_no = p_lease_no 
                    AND staff_no_id = p_staff_no
                FOR UPDATE;

                -- 2. VALIDATION
                IF v_check_lease IS NULL THEN
                    RAISE EXCEPTION 'Access Denied: Staff % is not assigned to Lease %', p_staff_no, p_lease_no;
                END IF;

                -- 3. ID GENERATION
                SELECT COALESCE(MAX(CAST(SUBSTRING(payment_no FROM '\\d+') AS INTEGER)), 0)
                INTO v_next_num
                FROM payment;
                
                v_next_num := v_next_num + 1;
                v_payment_no := 'PAY' || LPAD(v_next_num::text, 3, '0');

                -- 4. THE ACTION (INSERT)
                INSERT INTO payment (
                    payment_no,
                    lease_no,
                    amount_paid,
                    payment_method,
                    processed_by_staff_no,
                    payment_date,
                    status
                )
                VALUES (
                    v_payment_no,
                    p_lease_no,
                    p_amount,
                    p_method,
                    p_staff_no,
                    CURRENT_TIMESTAMP,
                    'Completed'
                );
            END;
            $$;
            """,
            reverse_sql="""
            CREATE OR REPLACE PROCEDURE process_rental_payment(
                p_lease_no VARCHAR,
                p_amount NUMERIC,
                p_method VARCHAR,
                p_staff_no VARCHAR
            )
            LANGUAGE plpgsql
            AS $$
            DECLARE
                v_check_lease VARCHAR;
            BEGIN
                SELECT lease_no INTO v_check_lease
                FROM lease_agreement
                WHERE lease_no = p_lease_no 
                    AND staff_no_id = p_staff_no
                FOR UPDATE;

                IF v_check_lease IS NULL THEN
                    RAISE EXCEPTION 'Access Denied: Staff % is not assigned to Lease %', p_staff_no, p_lease_no;
                END IF;

                INSERT INTO payment (
                    lease_no,
                    amount_paid,
                    payment_method,
                    processed_by_staff_no,
                    payment_date
                )
                VALUES (
                    p_lease_no,
                    p_amount,
                    p_method,
                    p_staff_no,
                    CURRENT_TIMESTAMP
                );
            END;
            $$;
            """
        ),
    ]
