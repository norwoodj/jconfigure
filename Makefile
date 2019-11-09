PYTHON_IMAGE := python:3.7-slim
VERSION_PLACEHOLDER := _VERSION


default:
	@echo "Available Targets:"
	@echo
	@echo "  clean   - Clean up build artifacts and revert version changes"
	@echo "  dist    - Build the distribution archive"
	@echo "  version - Print current version"
	@echo "  release - Release the module to pypi"

version.txt:
	docker run --rm --entrypoint date $(PYTHON_IMAGE) --utc "+%y.%m%d.0" > version.txt

version: version.txt
	cat version.txt

dist: version.txt
	sed -i "" "s|$(VERSION_PLACEHOLDER)|$(shell cat version.txt)|g" setup.py
	python setup.py sdist

release: dist
	pipenv run twine upload dist/*

clean: version.txt
	sed -i "" "s|$(shell cat version.txt)|$(VERSION_PLACEHOLDER)|g" setup.py
	rm -rf dist version.txt
