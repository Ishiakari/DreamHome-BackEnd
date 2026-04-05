from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('branches', '0001_initial'), # This matches your clean slate!
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE FUNCTION generate_branch_no()
            RETURNS VARCHAR AS $$
            DECLARE
                last_branch_no VARCHAR(3);
                new_seq INT;
            BEGIN
                SELECT branch_no INTO last_branch_no
                FROM branches_branch
                ORDER BY branch_no DESC
                LIMIT 1;

                IF last_branch_no IS NOT NULL THEN
                    new_seq := CAST(SUBSTRING(last_branch_no FROM 2) AS INT) + 1;
                ELSE
                    new_seq := 1;
                END IF;

                RETURN 'B' || LPAD(new_seq::TEXT, 2, '0');
            END;
            $$ LANGUAGE plpgsql;

            CREATE OR REPLACE FUNCTION trigger_set_branch_no()
            RETURNS TRIGGER AS $$
            BEGIN
                IF NEW.branch_no IS NULL OR NEW.branch_no = '' THEN
                    NEW.branch_no := generate_branch_no();
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            DROP TRIGGER IF EXISTS tgr_assign_branch_no ON branches_branch;
            CREATE TRIGGER tgr_assign_branch_no
            BEFORE INSERT ON branches_branch
            FOR EACH ROW
            EXECUTE FUNCTION trigger_set_branch_no();
            """,
            reverse_sql="""
            DROP TRIGGER IF EXISTS tgr_assign_branch_no ON branches_branch;
            DROP FUNCTION IF EXISTS trigger_set_branch_no();
            DROP FUNCTION IF EXISTS generate_branch_no();
            """
        )
    ]