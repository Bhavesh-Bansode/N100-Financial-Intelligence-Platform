load:
	python src/etl/loader.py

ratios:
	python src/analytics/ratios.py

test:
	pytest tests/

dashboard:
	streamlit run src/dashboard/app.py

api:
	uvicorn src.api.main:app --reload

clean:
	find . -name "__pycache__" -type d -exec rm -rf {} +