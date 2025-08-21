.PHONY: unit integration test coverage

unit:
	python3 tests/unit/test_faker_generator.py
	python3 tests/unit/test_formatters.py
	python3 tests/unit/test_s3_uploader.py

integration:
	python3 tests/integration/test_local_lambda.py

test: unit integration

coverage:
	coverage run --source=generator tests/unit/test_faker_generator.py
	coverage run -a --source=generator tests/unit/test_formatters.py
	coverage run -a --source=generator tests/unit/test_s3_uploader.py
	coverage report
	coverage html

coverage-check:
	coverage run --source=generator tests/unit/test_faker_generator.py
	coverage run -a --source=generator tests/unit/test_formatters.py
	coverage run -a --source=generator tests/unit/test_s3_uploader.py
	coverage report --fail-under=80 --skip-empty
	@echo "Checking individual file coverage..."
	@coverage report --format=text | awk 'NR>2 && $$1 !~ /^-+$$/ && $$4+0<80 {print "FAIL: " $$1 " has " $$4 " coverage (Below 80%)"; exit 1}'