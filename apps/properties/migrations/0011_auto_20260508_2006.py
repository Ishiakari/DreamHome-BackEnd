from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0010_auto_20260508_1711'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE FUNCTION get_properties_by_owner_and_branch(
                p_owner_no  VARCHAR,
                p_branch_no VARCHAR
            )
            RETURNS TABLE (
                property_no   VARCHAR,
                title         VARCHAR,
                property_type VARCHAR,
                monthly_rent  DECIMAL,
                status        VARCHAR,
                staff_no      VARCHAR
            ) AS $$
            DECLARE
                v_count INTEGER;
            BEGIN
                -- Check first if any properties exist
                SELECT COUNT(*) INTO v_count
                FROM property p
                WHERE p.owner_id = p_owner_no
                AND p.branch_id = p_branch_no;

                IF v_count = 0 THEN
                    RAISE NOTICE 'No properties found for owner % in branch %.', p_owner_no, p_branch_no;
                END IF;

                RETURN QUERY
                SELECT
                    p.property_no,
                    p.title,
                    p.property_type,
                    p.monthly_rent,
                    p.status,
                    p.staff_id
                FROM property p
                WHERE p.owner_id = p_owner_no
                AND p.branch_id = p_branch_no
                ORDER BY p.monthly_rent DESC;
            END;
            $$ LANGUAGE plpgsql;
            """,
            reverse_sql="""
            DROP FUNCTION IF EXISTS get_properties_by_owner_and_branch(VARCHAR, VARCHAR);
            """
        )
    ]
