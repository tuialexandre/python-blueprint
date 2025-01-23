from pathlib import Path
from tempfile import NamedTemporaryFile

import nox
from nox import parametrize
from nox_poetry import Session, session

nox.options.error_on_external_run = True
nox.options.reuse_existing_virtualenvs = True
nox.options.sessions = ["lint", "type_check", "test", "docs"]


@session(python=["3.10", "3.11", "3.12", "3.13"])
def test(s: Session) -> None:
    s.install(".", "pytest", "pytest-cov", "pytest-randomly")
    s.run(
        "python",
        "-m",
        "pytest",
        "--cov=fact",
        "--cov-report=html",
        "--cov-report=term",
        "tests",
        *s.posargs,
    )


# For some sessions, set venv_backend="none" to simply execute scripts within the existing Poetry
# environment. This requires that nox is run within `poetry shell` or using `poetry run nox ...`.
@session(venv_backend="none")
@parametrize(
    "command",
    [
        # During formatting, additionally sort imports and remove unused imports.
        [
            "ruff",
            "check",
            ".",
            "--select",
            "I",
            "--select",
            "F401",
            "--extend-fixable",
            "F401",
            "--fix",
        ],
        ["ruff", "format", "."],
    ],
)
def fmt(s: Session, command: list[str]) -> None:
    s.run(*command)


@session(venv_backend="none")
@parametrize(
    "command",
    [
        ["ruff", "check", "."],
        ["ruff", "format", "--check", "."],
    ],
)
def lint(s: Session, command: list[str]) -> None:
    s.run(*command)


@session(venv_backend="none")
def lint_fix(s: Session) -> None:
    s.run("ruff", "check", ".", "--extend-fixable", "F401", "--fix")


@session(venv_backend="none")
def type_check(s: Session) -> None:
    s.run("mypy", "src", "tests", "noxfile.py")


# Environment variable needed for Sphinx to locate source files.
doc_env = {"PYTHONPATH": "src"}


@session(venv_backend="none")
def docs(s: Session) -> None:
    # Build the HTML documentation
    s.run("sphinx-build", "-b", "html", "docs/source", "docs/build/html", env=doc_env)


@session(venv_backend="none")
def docs_check_urls(s: Session) -> None:
    # Check for broken links
    s.run("sphinx-build", "-b", "linkcheck", "docs/source", "docs/build/linkcheck", env=doc_env)


@session(venv_backend="none")
def docs_serve(s: Session) -> None:
    # Serve the documentation using Python's HTTP server
    s.run("python", "-m", "http.server", "8000", "-d", "docs/build/html")


@session(reuse_venv=False)
def licenses(s: Session) -> None:
    # Generate a unique temporary file name. Poetry cannot write to the temp file directly on
    # Windows, so only use the name and allow Poetry to re-create it.
    with NamedTemporaryFile() as t:
        requirements_file = Path(t.name)

    # Install dependencies without installing the package itself:
    #   https://github.com/cjolowicz/nox-poetry/issues/680
    s.run_always(
        "poetry",
        "export",
        "--without-hashes",
        f"--output={requirements_file}",
        external=True,
    )
    s.install("pip-licenses", "-r", str(requirements_file))
    s.run("pip-licenses", *s.posargs)
    requirements_file.unlink()
