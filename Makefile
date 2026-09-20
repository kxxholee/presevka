.PHONY: build build-fast package doctor install clean distclean

build:
	./scripts/build.sh

# Skip hinting for quick iteration on glyph variants; see README.
build-fast:
	PRESEVKA_HINT=none ./scripts/build.sh

package:
	./scripts/package.sh

doctor:
	./scripts/doctor.sh

install:
	./scripts/install-user.sh

clean:
	./scripts/clean.sh

distclean: clean
	rm -rf .cache .venv
