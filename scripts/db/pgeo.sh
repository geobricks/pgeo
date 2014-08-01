#!/bin/bash

# Variables
USER=fenix
DATABASE=pgeo

# Create Exsisting databse
dropdb -U $USER $DATABASE

# Create Database
createdb -U $USER $DATABASE --encoding='utf-8'

# Create Spatial Extension and pg_trgm
psql  -U $USER pgeo -c "CREATE EXTENSION postgis;CREATE EXTENSION pg_trgm;"

# Create Schemas
psql -U $USER $DATABASE -c "CREATE SCHEMA spatial"
#-f pgeo_spatial.sql
psql -U $USER $DATABASE -c "CREATE SCHEMA stats"

# Default Spatial Imports
sh spatial_imports.sh