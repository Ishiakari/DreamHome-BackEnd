from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0017_remove_advertisement_unique_property_advert_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE FUNCTION log_property_changes()
            RETURNS TRIGGER AS $$
            BEGIN
                IF TG_OP = 'INSERT' THEN
                    RAISE NOTICE '[INSERT] Property: %, Branch: %, Staff: %, Title: "%", Status: %, By: %, At: %',
                        NEW.property_no, NEW.branch_no_id, NEW.staff_no_id,
                        NEW.title, NEW.status,
                        current_user, now();
                    RETURN NEW;

                ELSIF TG_OP = 'UPDATE' THEN
                    -- Fix: Removed strict check for staff_no_id to allow owner updates
                    RAISE NOTICE '[UPDATE] Property: %, Branch: %, Staff: %, Title: "% → %", Status: % → %, By: %, At: %',
                        NEW.property_no, NEW.branch_no_id, NEW.staff_no_id,
                        OLD.title, NEW.title,
                        OLD.status, NEW.status,
                        current_user, now();
                    RETURN NEW;

                ELSIF TG_OP = 'DELETE' THEN
                    RAISE NOTICE '[DELETE] Property: %, Branch: %, Staff: %, Title: "%", Status: %, By: %, At: %',
                        OLD.property_no, OLD.branch_no_id, OLD.staff_no_id,
                        OLD.title, OLD.status,
                        current_user, now();
                    RETURN OLD;
                END IF;

                RETURN NULL;
            END;
            $$ LANGUAGE plpgsql;
            """,
            reverse_sql="""
            CREATE OR REPLACE FUNCTION log_property_changes()
            RETURNS TRIGGER AS $$
            BEGIN
                IF TG_OP = 'UPDATE' THEN
                    IF NEW.staff_no_id IS NULL THEN
                        RAISE EXCEPTION 'Property updates must be performed by an assigned staff member.';
                    END IF;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            """
        ),
    ]
