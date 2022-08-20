.phony: install lint clean

install:
	pip3 install --quiet -r requirements.txt
	streamlit run streamlit_app.py

lint:
	flake8

clean:
	find . -type d -name __pycache__ | xargs rm -rf
