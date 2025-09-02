
.PHONY: install run test fmt lint hooks

install:
\tpython -m pip install -r requirements.txt

run:
\tstreamlit run streamlit_app.py

test:
\tpytest -q

fmt:
\tblack .
\tisort .

lint:
\tflake8 .

hooks:
\tpre-commit install
