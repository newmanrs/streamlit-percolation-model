.phony: install lint clean

install:
	pip3 install --quiet -r requirements.txt
	streamlit run streamlit_app.py

lint:
	flake8

clean:
	rm -rf __pycache__
