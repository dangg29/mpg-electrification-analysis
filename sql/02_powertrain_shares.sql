-- Powertrain record shares, using a CTE joined to annual totals.
WITH totals AS (SELECT year, COUNT(*) AS total FROM vehicles GROUP BY year),
counts AS (SELECT year, powertrain, COUNT(*) AS records FROM vehicles GROUP BY year, powertrain)
SELECT c.year, c.powertrain, c.records, t.total,
       100.0 * c.records / t.total AS record_share_pct
FROM counts c JOIN totals t ON c.year = t.year ORDER BY c.year, c.powertrain;
