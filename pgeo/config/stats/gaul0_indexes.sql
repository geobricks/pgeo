
-- Create Search Indexes
CREATE UNIQUE INDEX {{table_name}}_idx idx ON stats.{{table_name}} (polygon_id, fromdate, todate);
CREATE UNIQUE INDEX {{table_name}}_idx idx ON stats.{{table_name}} (polygon_id, dekad);