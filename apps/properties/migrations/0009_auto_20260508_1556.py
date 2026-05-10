from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0008_alter_advertisement_table_alter_property_table_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DROP TRIGGER IF EXISTS trigger_property_audit ON property;
            DROP FUNCTION IF EXISTS log_property_changes();

            CREATE FUNCTION log_property_changes()
            RETURNS TRIGGER AS $$
            BEGIN
                IF TG_OP = 'INSERT' THEN
                    RAISE NOTICE '[INSERT] Property: %, Branch: %, Staff: %, Title: "%", Status: %, By: %, At: %',
                        NEW.property_no, NEW.branch_id, NEW.staff_id,
                        NEW.title, NEW.status,
                        current_user, now();
                    RETURN NEW;
                ELSIF TG_OP = 'UPDATE' THEN
                    IF NEW.staff_id IS NULL THEN
                        RAISE EXCEPTION 'Property updates must be performed by an assigned staff member.';
                    END IF;
                    RAISE NOTICE '[UPDATE] Property: %, Branch: %, Staff: %, Title: "% → %", Status: % → %, By: %, At: %',
                        NEW.property_no, NEW.branch_id, NEW.staff_id,
                        OLD.title, NEW.title,
                        OLD.status, NEW.status,
                        current_user, now();
                    RETURN NEW;
                ELSIF TG_OP = 'DELETE' THEN
                    RAISE NOTICE '[DELETE] Property: %, Branch: %, Staff: %, Title: "%", Status: %, By: %, At: %',
                        OLD.property_no, OLD.branch_id, OLD.staff_id,
                        OLD.title, OLD.status,
                        current_user, now();
                    RETURN OLD;
                END IF;
                RETURN NULL;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER trigger_property_audit
            BEFORE INSERT OR UPDATE OR DELETE ON property
            FOR EACH ROW EXECUTE FUNCTION log_property_changes();
            """,
            reverse_sql="""
            DROP TRIGGER IF EXISTS trigger_property_audit ON property;
            DROP FUNCTION IF EXISTS log_property_changes();
            """
        ),
    ]