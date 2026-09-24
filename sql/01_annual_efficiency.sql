-- Annual gasoline MPG with year-over-year changes and a trailing 3-year mean.
WITH annual AS (
    SELECT year, AVG(comb08) AS mean_mpg, COUNT(*) AS records
    FROM vehicles WHERE powertrain = 'Gasoline' GROUP BY year
)
SELECT year, records, mean_mpg,
       mean_mpg - LAG(mean_mpg) OVER (ORDER BY year) AS mpg_change_yoy,
       AVG(mean_mpg) OVER (ORDER BY year ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS rolling_3_year_mpg
FROM annual ORDER BY year;
