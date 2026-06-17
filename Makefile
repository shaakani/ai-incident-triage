.PHONY: run test dashboard airflow setup triage

setup:
	bash scripts/setup.sh

run:
	source venv/bin/activate && python main.py --log logs/payment_errors.log

triage:
	source venv/bin/activate && python main.py --log $(LOG)

test:
	source venv/bin/activate && pytest tests/ -v

dashboard:
	source venv/bin/activate && streamlit run dashboard/app.py

airflow:
	export AIRFLOW_HOME=$(PWD)/airflow && source venv/bin/activate && airflow standalone

watch:
	bash scripts/watch_logs.sh