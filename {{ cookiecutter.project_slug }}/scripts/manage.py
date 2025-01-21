import ast
import os
import re
import shutil
import subprocess
from inspect import cleandoc
from pathlib import Path

import astor
import simple_term_menu
from pygments import formatters, highlight, lexers
from simple_term_menu import TerminalMenu

BASE_DIR = Path(__file__).resolve().parents[1]

os.chdir(BASE_DIR)

APP_PATH = Path("src/api/app.py")
MODELS_REGISTRY_PATH = Path("src/storages/mongo/__init__.py")
TEMPLATES_PATH = Path("scripts/templates")
PY_LEXER = lexers.get_lexer_by_name("python", stripnl=False, stripall=False)
FORMATTER = formatters.TerminalFormatter(bg="dark")  # dark or light
DEFAULT_TERM_MENU = {"preview_size": 1.00, "menu_cursor": "❯ "}
simple_term_menu.MIN_VISIBLE_MENU_ENTRIES_COUNT = 5


def to_camel_case(snake_str):
    return "".join(x.capitalize() for x in snake_str.split("_"))


def to_snake_case(camel_str):
    return re.sub(r"(?<!^)(?=[A-Z ])", "_", camel_str).lower()


def as_identifier(name: str) -> str:
    name = to_snake_case(name)
    if not name.isidentifier():
        print(f"Invalid name: {name}. Please use a valid Python identifier.")
        raise ValueError("Invalid name")
    return name


def ruff_format(code: str) -> str:
    try:
        r = subprocess.run(
            ["ruff", "check", "--fix", "-"],
            input=code,
            text=True,
            capture_output=True,
            check=True,
        )
        code = r.stdout
    except subprocess.CalledProcessError as e:
        h = highlight(e.stderr, PY_LEXER, FORMATTER)
        print(f"Error in ruff format:\n{h}")
    try:
        r = subprocess.run(
            ["ruff", "format", "-"],
            input=code,
            text=True,
            capture_output=True,
            check=True,
        )
        code = r.stdout
    except subprocess.CalledProcessError as e:
        h = highlight(e.stderr, PY_LEXER, FORMATTER)
        print(f"Error in ruff format:\n{h}")
    return code


def list_modules_and_models():
    modules = []
    models = []
    app_py_lines = APP_PATH.read_text().splitlines()
    model__init__ = MODELS_REGISTRY_PATH.read_text()
    model__init_ast = ast.parse(model__init__)
    included_models = []

    class ModelVisitor(ast.NodeVisitor):
        def visit_ImportFrom(self, node):
            if node.module == "src.storages.mongo":
                for alias in node.names:
                    included_models.append(alias.name)

    ModelVisitor().visit(model__init_ast)

    for module in os.listdir("src/modules"):
        if not os.path.isdir(f"src/modules/{module}") or module.startswith("__"):
            continue
        routes_exists = os.path.exists(f"src/modules/{module}/routes.py")
        crud_exists = os.path.exists(f"src/modules/{module}/crud.py")
        router_included = any(
            f"from src.modules.{module}.routes import router as router_{module}" in line for line in app_py_lines
        )
        modules.append(
            {"name": module, "routes": routes_exists, "crud": crud_exists, "router_included": router_included}
        )

    for _ in os.listdir("src/storages/mongo"):
        if not _.endswith(".py") or _.startswith("__"):
            continue
        content = Path(f"src/storages/mongo/{_}").read_text()
        if "Document" not in content:
            continue
        model = _.removesuffix(".py")
        models.append({"name": model, "included": model in included_models})

    modules.sort(key=lambda x: os.path.getctime(f"src/modules/{x['name']}"), reverse=True)
    models.sort(key=lambda x: os.path.getctime(f"src/storages/mongo/{x['name']}.py"), reverse=True)

    return modules, models


def new_router_func(module_name: str | None = None, model_name: str | None = None):
    """
    "New router" Option:
    1. Prompt user to enter the name of module to add router.
    2. Create a new "src/modules/{module_name}/routes.py" file or abort if already exists.
    3. Also, include created router to application in the "src/api/app.py" file.
    """
    ROUTER_TEMPLATE = (TEMPLATES_PATH / "router").read_text()
    ROUTER_WITH_BASIC_ROUTES_TEMPLATE = (TEMPLATES_PATH / "router_with_basic_routes").read_text()

    modules, models = list_modules_and_models()

    if module_name is None:
        module_name = as_identifier(input("Enter the name of the module: "))
    path = Path(f"src/modules/{module_name}/routes.py")

    if path.exists():
        print(f"Router file for {module_name} already exists.")
        return

    def _code(_model_name):
        if _model_name:
            return (
                ROUTER_WITH_BASIC_ROUTES_TEMPLATE.replace("{module_name}", module_name)
                .replace("{ModuleName}", to_camel_case(module_name))
                .replace("{model_name}", _model_name)
                .replace("{ModelName}", to_camel_case(_model_name))
            )
        return ROUTER_TEMPLATE.replace("{module_name}", module_name).replace("{ModuleName}", to_camel_case(module_name))

    def preview1(model_name):
        if model_name == "SKIP":
            content = _code(None)
        else:
            content = _code(model_name)
        highlighted_content = highlight(content, PY_LEXER, FORMATTER)
        return highlighted_content

    if model_name is None:
        # request model_name to also implement CRUD routes
        terminal_menu = TerminalMenu(
            ["SKIP"] + [m["name"] for m in models],
            title="Select a model to implement basic routes or skip:",
            preview_title="Router Implementation",
            preview_command=preview1,
            **DEFAULT_TERM_MENU,
        )
        menu_entry_index = terminal_menu.show()
        model_name = as_identifier(models[menu_entry_index - 1]["name"]) if menu_entry_index > 0 else None

    def preview2(x):
        if x == "Yes":
            content = _code(model_name)
            highlighted_content = highlight(content, PY_LEXER, FORMATTER)
            return highlighted_content

    # request approval to create the module
    terminal_menu = TerminalMenu(
        ["Yes", "No"],
        title=f'Will be created File "{path}" and the router will be included in "{APP_PATH}"',
        preview_title=f'File "{path}"',
        preview_command=preview2,
        **DEFAULT_TERM_MENU,
    )
    menu_entry_index = terminal_menu.show()

    if menu_entry_index == 0:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(ruff_format(_code(model_name)))
        (path.parent / "__init__.py").touch()
        include_router_func(module_name)
        return module_name
    else:
        print("Aborted")
        return


def include_router_func(module_name: str | None = None):
    """
    "Include Router" Option:
    1. Prompt user to choose router from the list of available routers to include.
    2. Include provided router to application in "src/api/app.py" file.
    """
    app_py_lines = APP_PATH.read_text().splitlines()

    try:
        target_comment = "# Import routers above and include them below [do not edit this comment]"
        target_index = app_py_lines.index(target_comment)
    except ValueError:
        print("Cannot find the place to include routers")
        return

    modules, models = list_modules_and_models()

    def new_app_py(_module_name: str):
        # insert new router to the end of the list
        import_router = f"from src.modules.{_module_name}.routes import router as router_{_module_name}  # noqa: E402"
        _include_router = f"app.include_router(router_{_module_name})"

        new_app_py_lines = app_py_lines.copy()
        new_app_py_lines.insert(target_index - 1, import_router)
        target_include_router_index = target_index + 2
        for i, line in enumerate(new_app_py_lines[target_index:], start=target_index):
            if line.startswith("app.include_router("):
                target_include_router_index = i + 1

        new_app_py_lines.insert(target_include_router_index, _include_router)
        return new_app_py_lines

    def preview(_module_name: str):
        new_app_py_lines = new_app_py(_module_name.removesuffix(" (already included)"))
        new_target_comment_index = new_app_py_lines.index(target_comment)
        view_section = new_app_py_lines[new_target_comment_index - 5 : new_target_comment_index + 5]
        preview_content = "\n".join(view_section)
        highlighted_preview_content = highlight(preview_content, PY_LEXER, FORMATTER)
        return highlighted_preview_content

    if module_name is None:
        modules_with_router = [m for m in modules if m["routes"]]
        terminal_menu = TerminalMenu(
            [f"{m['name']} (already included)" if m["router_included"] else m["name"] for m in modules_with_router],
            title="Select an module:",
            preview_title=f'File "{APP_PATH}"',
            preview_command=preview,
            **DEFAULT_TERM_MENU,
        )
        menu_entry_index = terminal_menu.show()
        module_name = modules_with_router[menu_entry_index]["name"]

    new_app_py_content = "\n".join(new_app_py(module_name))

    APP_PATH.write_text(ruff_format(new_app_py_content))
    return module_name


def new_model_func():
    """
    "New model" Option:
    1. Prompt user to enter the name of the model.
    2. Create a new "src/storages/mongo/{model_name}.py" file or abort if already exists.
    3. Also, include the created model in the "src/storages/mongo/__init__.py" file.
    4. Suggest to "Implement CRUD+" and "New router" for the model.
    """
    MODEL_TEMPLATE = (TEMPLATES_PATH / "model").read_text()

    model_name = as_identifier(input("Enter the name of the model (in singular form): "))
    ModelName = to_camel_case(model_name)
    path = Path(f"src/storages/mongo/{model_name}.py")

    if path.exists():
        print(f"Model file for {model_name} already exists.")
        return

    def preview(x):
        if x == "Yes":
            content = ruff_format(MODEL_TEMPLATE.replace("{ModelName}", ModelName))
            highlighted_content = highlight(content, PY_LEXER, FORMATTER)
            return highlighted_content

    # Request approval
    terminal_menu = TerminalMenu(
        ["Yes", "No"],
        title=f'Will be created File "{path}" and the model will be included in "{MODELS_REGISTRY_PATH}"',
        preview_title=f'File "{path}"',
        preview_command=preview,
        **DEFAULT_TERM_MENU,
    )
    menu_entry_index = terminal_menu.show()

    if menu_entry_index == 0:
        # Create the model file
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(ruff_format(MODEL_TEMPLATE.replace("{ModelName}", ModelName)))

        # Include the model in the registry
        if not MODELS_REGISTRY_PATH.exists():
            print(f'Registry file "{MODELS_REGISTRY_PATH}" not found.')
            return

        code = MODELS_REGISTRY_PATH.read_text()
        code = f"from src.storages.mongo.{model_name} import {ModelName}\n" + code  # just add to the top
        tree = ast.parse(code)

        class Modifier(ast.NodeTransformer):
            def visit_Assign(self, node):
                """Find the assignment to 'document_models' and modify the list."""
                if any(isinstance(target, ast.Name) and target.id == "document_models" for target in node.targets):
                    if isinstance(node.value, ast.Call) and isinstance(node.value.args[1], ast.List):
                        # Append a string to the list
                        node.value.args[1].elts.append(ast.Name(id=ModelName, ctx=ast.Load()))
                return node

        modified_tree = Modifier().visit(tree)
        modified_code = astor.to_source(modified_tree)
        modified_code = ruff_format(modified_code)
        MODELS_REGISTRY_PATH.write_text(modified_code)

        terminal_menu = TerminalMenu(
            ["Yes", "No"],
            title="Do you want to create router with basic routes?",
            **DEFAULT_TERM_MENU,
        )
        menu_entry_index = terminal_menu.show()
        if menu_entry_index == 0:
            module_name = input(f"Enter the name of the module where to add router [`{model_name}` on empty]: ")
            if not module_name:
                module_name = model_name
            module_name = as_identifier(module_name)
            implement_crud_func(model_name=model_name, module_name=module_name)
            new_router_func(model_name=model_name, module_name=module_name)

        return model_name
    else:
        print("Aborted")
        return


def implement_crud_func(model_name: str | None = None, module_name: str | None = None):
    """
    "Implement CRUD+ repository" Option:
    1. Choose model from the list to implement operations for that model.
    2. Choose module where to add operations.
    3. Create the "src/modules/{module_name}/crud.py" file or abort if already exists.
    4. Write operations to the crud.py file.
    """
    CRUD_TEMPLATE = (TEMPLATES_PATH / "crud").read_text()

    modules, models = list_modules_and_models()

    def preview1(_model_name: str):
        content = CRUD_TEMPLATE.replace("{ModelName}", to_camel_case(_model_name)).replace("{model_name}", _model_name)
        highlighted_content = highlight(content, PY_LEXER, FORMATTER)
        return highlighted_content

    if model_name is None:
        terminal_menu = TerminalMenu(
            [m["name"] for m in models],
            title="Select a model for which operations will be implemented:",
            preview_title="CRUD+ Implementation",
            preview_command=preview1,
            **DEFAULT_TERM_MENU,
        )
        menu_entry_index = terminal_menu.show()
        model_name = models[menu_entry_index]["name"]

    if module_name is None:
        terminal_menu = TerminalMenu(
            [f"{m['name']} (with crud)" if m["crud"] else m["name"] for m in modules],
            title="Select a module to include crud:",
            **DEFAULT_TERM_MENU,
        )
        menu_entry_index = terminal_menu.show()
        module_name = modules[menu_entry_index]["name"]

    path = Path(f"src/modules/{module_name}/crud.py")

    if path.exists():
        print(f"CRUD file for {module_name} already exists.")
        return

    def preview2(x):
        if x == "Yes":
            content = CRUD_TEMPLATE.replace("{ModelName}", to_camel_case(model_name)).replace(
                "{model_name}", model_name
            )
            highlighted_content = highlight(content, PY_LEXER, FORMATTER)
            return highlighted_content

    terminal_menu = TerminalMenu(
        ["Yes", "No"],
        title=f'Will be created File "{path}"',
        preview_title=f'File "{path}"',
        preview_command=preview2,
        **DEFAULT_TERM_MENU,
    )

    menu_entry_index = terminal_menu.show()

    if menu_entry_index == 0:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            ruff_format(
                CRUD_TEMPLATE.replace("{ModelName}", to_camel_case(model_name)).replace("{model_name}", model_name)
            )
        )
        (path.parent / "__init__.py").touch()
        return module_name
    else:
        print("Aborted")
        return


def delete_module(module_name: str | None = None):
    """
    "Delete module" Option:
    1. Prompt the user to choose a module to delete (if not given).
    2. Show all references to this module found in the entire codebase.
    3. Ask for confirmation.
    4. Remove references from src/api/app.py (router import + app.include_router).
    5. Delete the module folder.
    6. Warn user that other references may need manual cleanup.
    """
    modules, _ = list_modules_and_models()

    # If there are no modules, just exit
    if not modules:
        print("No modules found to delete.")
        return

    module_names = [m["name"] for m in modules]
    if not module_name:
        # Let user pick from the existing modules
        def preview(m: str):
            # We won't do a fancy multi-file preview here, just docstring or prompt
            return f"Selected module: {m}"

        terminal_menu = TerminalMenu(
            module_names,
            title="Select a module to delete:",
            preview_title="Confirmation",
            preview_command=preview,
            **DEFAULT_TERM_MENU,
        )
        idx = terminal_menu.show()
        module_name = module_names[idx]

    elif module_name not in module_names:
        print(f"Module '{module_name}' not found in src/modules/.")
        return

    # Find references to this module in the entire project
    references = []
    for root, dirs, files in os.walk(BASE_DIR):
        # Optionally skip hidden, venv, etc.:
        # if "venv" in dirs: dirs.remove("venv")
        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                try:
                    lines = file_path.read_text().splitlines()
                except UnicodeDecodeError:
                    continue  # skip non-text or problematic files

                for i, line in enumerate(lines, start=1):
                    # A naive way to check references:
                    if f"src.modules.{module_name}" in line:
                        references.append((file_path, i, line.strip()))

    # Build a preview string of references found
    if references:
        ref_preview = ["References found in project:\n"]
        for ref_file, ref_line_no, ref_line in references:
            ref_preview.append(f"- {ref_file.relative_to(BASE_DIR)} (line {ref_line_no}): {ref_line}")
        ref_preview_str = "\n".join(ref_preview)
    else:
        ref_preview_str = "No direct references found apart from potential router usage in app.py.\n"

    # We'll do a second pass to see if "src/api/app.py" includes a router import
    app_py_lines = APP_PATH.read_text().splitlines()
    import_line_idx = None
    include_line_idx = None
    for i, line in enumerate(app_py_lines):
        if f"from src.modules.{module_name}.routes import router as router_{module_name}" in line:
            import_line_idx = i
        if f"app.include_router(router_{module_name})" in line:
            include_line_idx = i

    def preview_delete(_):
        return (
            f"You are about to delete the module '{module_name}'.\n\n"
            + ref_preview_str
            + "\n\nPress ENTER on 'Yes' to proceed, or 'No' to abort."
        )

    # Ask user for confirmation
    confirm_menu = TerminalMenu(
        ["Yes", "No"],
        title=f"Delete module '{module_name}'?",
        preview_command=preview_delete,
        preview_title="Module Deletion Confirmation",
        **DEFAULT_TERM_MENU,
    )
    choice = confirm_menu.show()

    if choice == 0:  # Yes
        # Remove references in app.py
        changed_app_py = False
        new_app_py_lines = app_py_lines.copy()

        # Remove router import line
        if import_line_idx is not None:
            new_app_py_lines[import_line_idx] = ""

        # Remove app.include_router line
        if include_line_idx is not None:
            new_app_py_lines[include_line_idx] = ""
        if import_line_idx is not None or include_line_idx is not None:
            changed_app_py = True

        if changed_app_py:
            # Filter out empty lines if you want, or leave them as blank
            filtered_app_py_lines = [line for line in new_app_py_lines if line.strip() != ""]
            updated_content = ruff_format("\n".join(filtered_app_py_lines) + "\n")
            APP_PATH.write_text(updated_content)

        # Finally, remove the module folder
        target_dir = Path("src/modules") / module_name
        if target_dir.exists() and target_dir.is_dir():
            shutil.rmtree(target_dir)
            print(f"Module '{module_name}' directory removed.")
        else:
            print(f"Module directory '{target_dir}' does not exist or is not a directory.")

        print(
            "Module deletion completed. If there were other references shown above, "
            "please remove them manually if needed."
        )
    else:
        print("Aborted module deletion.")


def main():
    options = ["New model", "Implement CRUD+ repository", "New router", "Delete module"]

    def preview(x):
        if x == "New router":
            return cleandoc(new_router_func.__doc__)
        elif x == "Include Router":
            return cleandoc(include_router_func.__doc__)
        elif x == "New model":
            return cleandoc(new_model_func.__doc__)
        elif x == "Implement CRUD+ repository":
            return cleandoc(implement_crud_func.__doc__)
        elif x == "Delete module":
            return cleandoc(delete_module.__doc__)

    terminal_menu = TerminalMenu(
        options, title="Select an option:", preview_command=preview, preview_title="Description", **DEFAULT_TERM_MENU
    )
    menu_entry_index = terminal_menu.show()
    choice = options[menu_entry_index]
    if choice == "New model":
        new_model_func()
    elif choice == "Implement CRUD+ repository":
        implement_crud_func()
    elif choice == "New router":
        new_router_func()
    elif choice == "Delete module":
        delete_module()
    else:
        raise ValueError("Unknown option")


if __name__ == "__main__":
    main()
