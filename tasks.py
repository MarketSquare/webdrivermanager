# flake8: noqa
from pathlib import Path
from invoke import task
from pathlib import Path
import os
import shutil


QUOTE = '"' if os.name == "nt" else "'"

CHANGELOG = "CHANGELOG"
filters = ["poc", "new release", "wip", "cleanup", "!nocl"]


def filter_entries(filename):
    buffer = []
    with open(filename) as old_file:
        buffer = old_file.read().split("\n")

    with open(filename, "w") as new_file:
        for line in buffer:
            if not any(bad_word in line.lower() for bad_word in filters):
                new_file.write(line + "\n")


assert Path.cwd() == Path(__file__).parent


@task()
def build(ctx):
    """Generates dist tar ball"""
    ctx.run("python setup.py sdist")


@task
def flake(ctx):
    """Runs flake8 against whole project"""
    ctx.run("flake8")


@task
def mypy(ctx):
    """Runs mypy against the codebase"""
    ctx.run("mypy --config mypy.ini")


@task
def black(ctx):
    """Reformat code with black"""
    ctx.run("black -l130 -tpy37 src")


@task
def clean(ctx):
    to_be_removed = [
        "report",
        "dist/",
        ".coverage*",
        "output*",
    ]

    for item in to_be_removed:
        fs_entry = Path(item)
        if fs_entry.is_dir:
            shutil.rmtree(item)
        elif fs_entry.is_file():
            fs_entry.unlink()
        else:
            for fs_entry in Path().glob(item):
                fs_entry.unlink()


@task
def changelog(ctx, version=None):
    if version is not None:
        version = f"-c {version}"
    else:
        version = ""
    ctx.run(f"gcg -x -o {CHANGELOG} -O rpm {version}")
    filter_entries(CHANGELOG)


@task
def release(ctx, version=None):
    assert version != None
    changelog(ctx, version)
    ctx.run(f"git add {CHANGELOG}")
    ctx.run(f"git commit -m {QUOTE}New Release {version}{QUOTE}")
    ctx.run(f"git tag {version}")
    build(ctx)
