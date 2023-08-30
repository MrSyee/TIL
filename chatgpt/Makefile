BASENAME=$(shell basename $(CURDIR))

env:
	conda create -n ${BASENAME} python=3.9 -y

setup:
	pip install -r requirements.txt
