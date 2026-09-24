-- Compare manufacturer MPG to the same year/segment benchmark.
WITH benchmark AS (
 SELECT year, segment, AVG(comb08) AS segment_mpg FROM vehicles
 WHERE powertrain = 'Gasoline' GROUP BY year, segment
), makers AS (
 SELECT year, segment, make, COUNT(*) AS records, AVG(comb08) AS make_mpg
 FROM vehicles WHERE powertrain = 'Gasoline' GROUP BY year, segment, make HAVING COUNT(*) >= 5
)
SELECT m.*, b.segment_mpg, m.make_mpg - b.segment_mpg AS mpg_above_segment,
       DENSE_RANK() OVER (PARTITION BY m.year, m.segment ORDER BY m.make_mpg DESC) AS efficiency_rank
FROM makers m JOIN benchmark b ON m.year = b.year AND m.segment = b.segment
ORDER BY m.year DESC, m.segment, efficiency_rank;
