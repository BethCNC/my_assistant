-- Function to get table definition
CREATE OR REPLACE FUNCTION public.get_table_definition(table_name text)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  result jsonb;
BEGIN
  -- Get column information
  WITH columns_info AS (
    SELECT 
      c.column_name, 
      c.data_type, 
      c.is_nullable,
      c.column_default,
      (
        SELECT pg_catalog.obj_description(
          ('public.' || c.table_name)::regclass::oid, 'pg_class'
        )
      ) AS table_description,
      (
        SELECT pg_catalog.col_description(
          ('public.' || c.table_name)::regclass::oid, 
          c.ordinal_position
        )
      ) AS column_description
    FROM 
      information_schema.columns c
    WHERE 
      c.table_schema = 'public' 
      AND c.table_name = table_name
    ORDER BY 
      c.ordinal_position
  ),
  
  -- Get primary key information
  pk_info AS (
    SELECT 
      tc.constraint_name,
      kcu.column_name
    FROM 
      information_schema.table_constraints tc
      JOIN information_schema.key_column_usage kcu 
        ON tc.constraint_name = kcu.constraint_name
    WHERE 
      tc.constraint_type = 'PRIMARY KEY' 
      AND tc.table_name = table_name
      AND tc.table_schema = 'public'
  ),
  
  -- Get foreign key information
  fk_info AS (
    SELECT 
      tc.constraint_name,
      kcu.column_name AS fk_column,
      ccu.table_name AS references_table,
      ccu.column_name AS references_column
    FROM 
      information_schema.table_constraints tc
      JOIN information_schema.key_column_usage kcu
        ON tc.constraint_name = kcu.constraint_name
      JOIN information_schema.constraint_column_usage ccu 
        ON ccu.constraint_name = tc.constraint_name
    WHERE 
      tc.constraint_type = 'FOREIGN KEY' 
      AND tc.table_name = table_name
      AND tc.table_schema = 'public'
  )
  
  -- Combine all information and construct result
  SELECT 
    jsonb_build_object(
      'table_name', table_name,
      'columns', (
        SELECT 
          jsonb_agg(
            jsonb_build_object(
              'name', column_name,
              'type', data_type,
              'nullable', is_nullable,
              'default', column_default,
              'description', column_description,
              'is_primary_key', (
                SELECT 
                  EXISTS (
                    SELECT 1 FROM pk_info pk WHERE pk.column_name = columns_info.column_name
                  )
              ),
              'foreign_key', (
                SELECT 
                  CASE WHEN EXISTS (
                    SELECT 1 FROM fk_info fk WHERE fk.fk_column = columns_info.column_name
                  )
                  THEN (
                    SELECT 
                      jsonb_build_object(
                        'references_table', references_table,
                        'references_column', references_column
                      )
                    FROM 
                      fk_info
                    WHERE 
                      fk_column = columns_info.column_name
                    LIMIT 1
                  )
                  ELSE NULL
                  END
              )
            )
          )
        FROM 
          columns_info
      ),
      'table_description', (SELECT table_description FROM columns_info LIMIT 1)
    ) INTO result;
  
  RETURN result;
END;
$$;

-- Set permissions
REVOKE ALL ON FUNCTION public.get_table_definition(text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.get_table_definition(text) TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_table_definition(text) TO service_role; 