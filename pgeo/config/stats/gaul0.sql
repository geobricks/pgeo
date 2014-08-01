-- Create stats TABLE Structure
CREATE TABLE stats.{{table_name}}  (
    polygon_id  char(36),
    label_en  text,
    fromdate  date,
    todate   date,
--  '1_1 (january_1)'
    dekad  char(4),
    hist json,
    mean double,
    min double,
    max double,
    sd double
);