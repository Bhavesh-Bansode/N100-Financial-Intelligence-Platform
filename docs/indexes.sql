CREATE INDEX IF NOT EXISTS idx_financial_ratios_company_year
ON financial_ratios(company_id, year);

CREATE INDEX IF NOT EXISTS idx_profit_loss_company_year
ON profit_loss(company_id, year);

CREATE INDEX IF NOT EXISTS idx_balance_sheet_company_year
ON balance_sheet(company_id, year);

CREATE INDEX IF NOT EXISTS idx_cash_flow_company_year
ON cash_flow(company_id, year);

CREATE INDEX IF NOT EXISTS idx_documents_company
ON documents(company_id);

CREATE INDEX IF NOT EXISTS idx_sectors_company
ON sectors(company_id);