@echo off
echo "Formatting using black"
black -t py311 -q src
echo "Formating using isort"
isort -q src
echo "################################### PYLINT ########################"
pylint src
echo "################################### PYTEST ########################"
pytest
cd docs
make html
cd..