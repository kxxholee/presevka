.PHONY: build doctor install clean distclean

build:
	./scripts/build.sh

doctor:
	./scripts/doctor.sh

install:
	./scripts/install-user.sh

clean:
	./scripts/clean.sh

distclean: clean
	rm -rf .cache .venv
