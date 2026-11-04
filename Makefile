# Пересобрать страницу из данных: make
all:
	python3 -I src/build.py data data/data.json
	python3 -I src/assemble.py data .
serve:
	python3 -m http.server 8000
.PHONY: all serve
