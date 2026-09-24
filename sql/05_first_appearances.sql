-- First appearance in this snapshot, not a global product launch date.
SELECT make, powertrain, MIN(year) AS first_recorded_year, COUNT(*) AS records
FROM vehicles WHERE powertrain IN ('HEV', 'PHEV', 'BEV')
GROUP BY make, powertrain ORDER BY first_recorded_year, make, powertrain;
