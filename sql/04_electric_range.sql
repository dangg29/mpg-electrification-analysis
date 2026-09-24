-- Electricity range uses range for BEVs and rangeA for PHEVs.
SELECT year, powertrain, COUNT(*) AS records,
       COUNT(CASE WHEN powertrain = 'BEV' THEN range ELSE rangeA END) AS usable_range_records,
       AVG(CASE WHEN powertrain = 'BEV' THEN range ELSE rangeA END) AS mean_electricity_range_miles
FROM vehicles
WHERE powertrain = 'BEV' OR (powertrain = 'PHEV' AND fuelType2 = 'Electricity')
GROUP BY year, powertrain ORDER BY year, powertrain;
