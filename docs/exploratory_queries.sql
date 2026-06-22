SELECT 'companies' AS table_name, COUNT(*) AS row_count FROM companies
UNION ALL
SELECT 'profitandloss', COUNT(*) FROM profitandloss
UNION ALL
SELECT 'balancesheet', COUNT(*) FROM balancesheet
UNION ALL
SELECT 'cashflow', COUNT(*) FROM cashflow
UNION ALL
SELECT 'analysis', COUNT(*) FROM analysis
UNION ALL
SELECT 'documents', COUNT(*) FROM documents
UNION ALL
SELECT 'prosandcons', COUNT(*) FROM prosandcons
UNION ALL
SELECT 'sectors', COUNT(*) FROM sectors
UNION ALL
SELECT 'stock_prices', COUNT(*) FROM stock_prices
UNION ALL
SELECT 'market_cap', COUNT(*) FROM market_cap
UNION ALL
SELECT 'financial_ratios', COUNT(*) FROM financial_ratios
UNION ALL
SELECT 'peer_groups', COUNT(*) FROM peer_groups;


SELECT COUNT(*) AS total_companies
FROM companies;


SELECT
    company_id,
    COUNT(*) AS years_available
FROM profitandloss
GROUP BY company_id
ORDER BY years_available DESC;


SELECT
    company_id,
    COUNT(*) AS years_available
FROM balancesheet
GROUP BY company_id
ORDER BY years_available DESC;


SELECT
    company_id,
    COUNT(*) AS years_available
FROM cashflow
GROUP BY company_id
ORDER BY years_available DESC;


SELECT
    company_id,
    COUNT(*) AS years_available
FROM profitandloss
GROUP BY company_id
HAVING COUNT(*) < 10
ORDER BY years_available;


SELECT c.id
FROM companies c
LEFT JOIN balancesheet b
ON c.id = b.company_id
WHERE b.company_id IS NULL;



SELECT COUNT(*) AS null_websites
FROM companies
WHERE website IS NULL
   OR TRIM(website) = '';



SELECT
    company_id,
    COUNT(*) AS report_count
FROM documents
GROUP BY company_id
ORDER BY report_count ASC;



SELECT
    c.id,
    COALESCE(pl.cnt,0) AS pl_years,
    COALESCE(bs.cnt,0) AS bs_years,
    COALESCE(cf.cnt,0) AS cf_years
FROM companies c
LEFT JOIN (
    SELECT company_id, COUNT(*) cnt
    FROM profitandloss
    GROUP BY company_id
) pl
ON c.id = pl.company_id
LEFT JOIN (
    SELECT company_id, COUNT(*) cnt
    FROM balancesheet
    GROUP BY company_id
) bs
ON c.id = bs.company_id
LEFT JOIN (
    SELECT company_id, COUNT(*) cnt
    FROM cashflow
    GROUP BY company_id
) cf
ON c.id = cf.company_id
ORDER BY c.id;