"""Invoke file for CI/CD tasks.
"""

from invoke.tasks import task


@task
def install(c, editable=False, dev=False):
    """Install the Python API package.

    Args:
        editable_mode (bool): Whether the package should be installed in development mode or not.
        dev (bool): Whether the package should be installed in development mode or not.
    """
    editable_mode = "-e" if editable else ""
    dev_mode = "[dev]" if dev else ""
    cmd = f"pip install {editable_mode} .{dev_mode}" 
    c.run(cmd)


@task
def test(c, coverage=False):
    """Run the tests.

    Args:
        coverage (bool): Whether the coverage should be computed or not.
    """
    print("=== Make sure that the package has been installed in dev mode ! ===")
    coverage_mode = "--cov=src/backend" if coverage else ""
    c.run(f"pytest -v tests/integration {coverage_mode}")
