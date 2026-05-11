from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_remove_nextofkin_full_name_client_middle_name_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE OR REPLACE FUNCTION auto_update_property_status()
                RETURNS TRIGGER AS $$
                BEGIN
                    -- 1. If a new lease is signed, automatically mark the property as 'Rented'
                    IF TG_OP = 'INSERT' THEN
                        -- Fix: Use property_no_id instead of property_no
                        UPDATE property
                        SET status = 'Rented'
                        WHERE property_no = NEW.property_no_id;
                        
                    -- 2. If a lease is deleted/cancelled, automatically revert it to 'Available'
                    ELSIF TG_OP = 'DELETE' THEN
                        -- Fix: Use property_no_id instead of property_no
                        UPDATE property
                        SET status = 'Available'
                        WHERE property_no = OLD.property_no_id;
                    END IF;

                    RETURN NULL;
                END;
                $$ LANGUAGE plpgsql;
            """,
            reverse_sql="""
                CREATE OR REPLACE FUNCTION auto_update_property_status()
                RETURNS TRIGGER AS $$
                BEGIN
                    IF TG_OP = 'INSERT' THEN
                        UPDATE property
                        SET status = 'Rented'
                        WHERE property_no = NEW.property_no;
                    ELSIF TG_OP = 'DELETE' THEN
                        UPDATE property
                        SET status = 'Available'
                        WHERE property_no = OLD.property_no;
                    END IF;
                    RETURN NULL;
                END;
                $$ LANGUAGE plpgsql;
            """
        ),
    ]
