import os
import pathlib


def rm_tree(path: pathlib.Path):
    """
    Stolen shamelessly from:
    https://stackoverflow.com/a/57892171/642511
    """
    for child in path.iterdir():
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)
    path.rmdir()


def cleanup():
    for match in pathlib.Path().glob("**/OBSCURATA_LAMINA_INTERRASILIS--*"):
        if match.is_dir():
            rm_tree(match)


def rename_jinja_tmps(directory):
    """
    Traverse the given directory and rename files with double extensions like `.py.jinja`
    to remove the `.jinja` part, while keeping single `.jinja` files untouched.
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Check if the file has a double extension (e.g., .py.jinja)
            if file.endswith(".jinja") and "." in file[:-6]:
                old_path = os.path.join(root, file)
                # Remove only the last ".jinja" part
                new_path = os.path.join(root, file[:-6])
                os.rename(old_path, new_path)


cleanup()
rename_jinja_tmps(os.getcwd())
