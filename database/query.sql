CREATE OR REPLACE FUNCTION generate_dreamhome_id()
RETURNS TRIGGER AS $$
DECLARE
    prefix TEXT;
    next_num INT;
    id_column TEXT;
BEGIN
    -- 1. Identify the Table, the correct Case Study Prefix, and the Primary Key Column
    IF TG_TABLE_NAME = 'branch' THEN
        prefix := 'B';
        id_column := 'branch_no';
        
    ELSIF TG_TABLE_NAME = 'staff' THEN
        prefix := 'SL'; 
        id_column := 'staff_no';
        
    ELSIF TG_TABLE_NAME = 'client' THEN
        -- Conditional logic: Renters get CR, Owners get CO
        IF NEW.role = 'Renter' THEN
            prefix := 'CR';
        ELSE
            prefix := 'CO';
        END IF;
        id_column := 'client_no';
        
    ELSIF TG_TABLE_NAME = 'property' THEN
        prefix := 'PG'; 
        id_column := 'property_no';
        
    ELSIF TG_TABLE_NAME = 'lease_agreement' THEN
        prefix := 'LS';
        id_column := 'lease_no';
        
    ELSIF TG_TABLE_NAME = 'payment' THEN
        prefix := 'PAY-';
        id_column := 'payment_no';
        
    ELSE
        -- If the trigger fires on an unmapped table, just proceed normally
        RETURN NEW; 
    END IF;

    -- 2. Dynamically find the highest existing number for this specific prefix
    -- It strips the letters, converts the rest to an integer, and adds 1
    EXECUTE format('SELECT COALESCE(MAX(CAST(SUBSTRING(%I FROM %L) AS INT)), 0) + 1 
                    FROM %I WHERE %I LIKE %L', 
                    id_column, length(prefix) + 1, TG_TABLE_NAME, id_column, prefix || '%')
    INTO next_num;

    -- 3. Assign the newly generated ID directly to the incoming record
    -- Result examples: B3, SL21, CR74, PG4, LS100
    IF id_column = 'branch_no' THEN
        NEW.branch_no := prefix || next_num::TEXT;
    ELSIF id_column = 'staff_no' THEN
        NEW.staff_no := prefix || next_num::TEXT;
    ELSIF id_column = 'client_no' THEN
        NEW.client_no := prefix || next_num::TEXT;
    ELSIF id_column = 'property_no' THEN
        NEW.property_no := prefix || next_num::TEXT;
    ELSIF id_column = 'lease_no' THEN
        NEW.lease_no := prefix || next_num::TEXT;
    ELSIF id_column = 'payment_no' THEN
        NEW.payment_no := prefix || LPAD(next_num::TEXT, 3, '0');
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;



-- 1. Branch Trigger
DROP TRIGGER IF EXISTS trigger_generate_branch_id ON branch;
CREATE TRIGGER trigger_generate_branch_id
BEFORE INSERT ON branch
FOR EACH ROW EXECUTE FUNCTION generate_dreamhome_id();

-- 2. Staff Trigger
DROP TRIGGER IF EXISTS trigger_generate_staff_id ON staff;
CREATE TRIGGER trigger_generate_staff_id
BEFORE INSERT ON staff
FOR EACH ROW EXECUTE FUNCTION generate_dreamhome_id();

-- 3. Client Trigger (Handles both Renters and Owners)
DROP TRIGGER IF EXISTS trigger_generate_client_id ON client;
CREATE TRIGGER trigger_generate_client_id
BEFORE INSERT ON client
FOR EACH ROW EXECUTE FUNCTION generate_dreamhome_id();

-- 4. Property Trigger
DROP TRIGGER IF EXISTS trigger_generate_property_id ON property;
CREATE TRIGGER trigger_generate_property_id
BEFORE INSERT ON property
FOR EACH ROW EXECUTE FUNCTION generate_dreamhome_id();

-- 5. Lease Trigger
DROP TRIGGER IF EXISTS trigger_generate_lease_id ON lease_agreement;
CREATE TRIGGER trigger_generate_lease_id
BEFORE INSERT ON lease_agreement
FOR EACH ROW EXECUTE FUNCTION generate_dreamhome_id();

-- 6. Payment Trigger
DROP TRIGGER IF EXISTS trigger_generate_payment_id ON payment;
CREATE TRIGGER trigger_generate_payment_id
BEFORE INSERT ON payment
FOR EACH ROW EXECUTE FUNCTION generate_dreamhome_id();