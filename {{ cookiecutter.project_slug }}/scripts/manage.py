import ast
import os
import re
import readline  # noqa
import shutil
import subprocess
from inspect import cleandoc
from pathlib import Path

import astor
import simple_term_menu
from pygments import formatters, highlight, lexers
from simple_term_menu import TerminalMenu

# ------------------------------------------------------------------------------
# Constants and Global Settings
# ------------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]
os.chdir(BASE_DIR)

APP_PATH = Path("src/api/app.py")
MODELS_REGISTRY_PATH = Path("src/storages/mongo/__init__.py")
TEMPLATES_PATH = Path("scripts/templates")

PY_LEXER = lexers.get_lexer_by_name("python", stripnl=False, stripall=False)
FORMATTER = formatters.TerminalFormatter(bg="dark")  # 'dark' or 'light'

DEFAULT_TERM_MENU = {"preview_size": 1.00, "menu_cursor": "❯ "}
simple_term_menu.MIN_VISIBLE_MENU_ENTRIES_COUNT = 5


# ------------------------------------------------------------------------------
# Utility Functions
# ------------------------------------------------------------------------------
def to_camel_case(snake_str: str) -> str:
    """Convert a snake_case string to CamelCase."""
    return "".join(x.capitalize() for x in snake_str.split("_"))


def to_snake_case(camel_str: str) -> str:
    """Convert a CamelCase string to snake_case."""
    return re.sub(r"(?<!^)(?=[A-Z ])", "_", camel_str).lower()


def as_identifier(name: str) -> str:
    """
    Ensure a string is a valid Python identifier by:
    1. Converting from CamelCase to snake_case (if needed).
    2. Checking `name.isidentifier()`.
    Raises ValueError if not valid.
    """
    snake = to_snake_case(name)
    if not snake.isidentifier():
        print(f"Invalid name: '{name}'. Please use a valid Python identifier.")
        raise ValueError(f"Invalid name: {name}")
    return snake


def ruff_format(code: str) -> str:
    """
    Run Ruff to fix and format the code snippet in-memory.
    Return the resulting (potentially reformatted) string.
    """
    # Step 1: Ruff check --fix
    try:
        result = subprocess.run(
            ["ruff", "check", "--fix", "-"],
            input=code,
            text=True,
            capture_output=True,
            check=True,
        )
        code = result.stdout
    except subprocess.CalledProcessError as e:
        print("Error in Ruff format stage (check --fix):")
        print(highlight(e.stderr, PY_LEXER, FORMATTER))

    # Step 2: Ruff format
    try:
        result = subprocess.run(
            ["ruff", "format", "-"],
            input=code,
            text=True,
            capture_output=True,
            check=True,
        )
        code = result.stdout
    except subprocess.CalledProcessError as e:
        print("Error in Ruff format stage (format):")
        print(highlight(e.stderr, PY_LEXER, FORMATTER))

    return code


def highlight_preview(content: str) -> str:
    """Return a syntax-highlighted preview of Python code."""
    return highlight(content, PY_LEXER, FORMATTER)


def load_template(template_name: str) -> str:
    """Load a text template from the TEMPLATES_PATH directory."""
    return (TEMPLATES_PATH / template_name).read_text()


# ------------------------------------------------------------------------------
# Data Retrieval / Parsing
# ------------------------------------------------------------------------------
def list_modules_and_models() -> tuple[list[dict], list[dict]]:
    """
    Scan the "src/modules" and "src/storages/mongo" directories to gather
    information about available modules and models. Returns two lists:
        modules: [
            {"name": str, "routes": bool, "crud": bool, "router_included": bool},
            ...
        ],
        models: [
            {"name": str, "included": bool},
            ...
        ]
    """
    modules_info = []
    models_info = []

    app_py_lines = APP_PATH.read_text().splitlines()

    # Parse __init__.py in mongo to see which models are imported
    model__init_content = MODELS_REGISTRY_PATH.read_text()
    model__init_ast = ast.parse(model__init_content)
    included_models = []

    class ModelVisitor(ast.NodeVisitor):
        def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
            if node.module == "src.storages.mongo":
                for alias in node.names:
                    included_models.append(alias.name)

    ModelVisitor().visit(model__init_ast)

    # Collect modules
    for module in os.listdir("src/modules"):
        full_path = Path("src/modules") / module
        if not full_path.is_dir() or module.startswith("__"):
            continue

        routes_exists = (full_path / "routes.py").exists()
        crud_exists = (full_path / "crud.py").exists()
        router_included = any(
            f"from src.modules.{module}.routes import router as router_{module}" in line for line in app_py_lines
        )

        modules_info.append(
            {
                "name": module,
                "routes": routes_exists,
                "crud": crud_exists,
                "router_included": router_included,
            }
        )

    # Collect models
    for file_name in os.listdir("src/storages/mongo"):
        if not file_name.endswith(".py") or file_name.startswith("__"):
            continue
        file_content = Path(f"src/storages/mongo/{file_name}").read_text()
        if "Document" not in file_content:
            continue

        model = file_name.removesuffix(".py")
        models_info.append(
            {
                "name": model,
                "included": model in included_models,
            }
        )

    # Sort them by creation time (newest first)
    modules_info.sort(key=lambda x: os.path.getctime(f"src/modules/{x['name']}"), reverse=True)
    models_info.sort(key=lambda x: os.path.getctime(f"src/storages/mongo/{x['name']}.py"), reverse=True)

    return modules_info, models_info


# ------------------------------------------------------------------------------
# Command Implementations
# ------------------------------------------------------------------------------
def include_router_func(module_name: str | None = None) -> str | None:
    """
    "Include Router" Option:
    1. Prompt user to choose router from the list of available modules to include.
    2. Add the router import + app.include_router(...) to "src/api/app.py".
    """
    app_py_lines = APP_PATH.read_text().splitlines()

    # Locate anchor comment for insertion in app.py
    anchor_comment = "# Import routers above and include them below [do not edit this comment]"
    try:
        anchor_index = app_py_lines.index(anchor_comment)
    except ValueError:
        print("Cannot find the place to include routers in app.py.")
        return None

    modules_info, _models_info = list_modules_and_models()

    def updated_app_py_lines(_module: str) -> list[str]:
        """
        Generate the new content of app.py with router import
        and `app.include_router(...)` appended/inserted.
        """
        # For display, remove the suffix if it was chosen as "(already included)"
        base_module_name = _module.removesuffix(" (already included)")

        import_router_line = (
            f"from src.modules.{base_module_name}.routes import router as router_{base_module_name}  # noqa: E402"
        )
        include_router_line = f"app.include_router(router_{base_module_name})"

        lines_copy = app_py_lines[:]
        # Insert the import line just above the anchor index
        lines_copy.insert(anchor_index - 1, import_router_line)

        # Find a good place to insert the include line
        # (directly after other include_router lines).
        insert_idx_for_include = anchor_index + 2
        for i, line in enumerate(lines_copy[anchor_index:], start=anchor_index):
            if line.startswith("app.include_router("):
                insert_idx_for_include = i + 1

        lines_copy.insert(insert_idx_for_include, include_router_line)
        return lines_copy

    def preview_module_chosen(selected_module: str) -> str:
        """Preview snippet around the anchor in app.py after insertion."""
        new_lines = updated_app_py_lines(selected_module)
        try:
            new_anchor_index = new_lines.index(anchor_comment)
            snippet_start = max(0, new_anchor_index - 5)
            snippet_end = min(len(new_lines), new_anchor_index + 5)
            preview_content = "\n".join(new_lines[snippet_start:snippet_end])
        except ValueError:
            # Fallback snippet if anchor not found
            preview_content = "\n".join(new_lines[-10:])
        return highlight_preview(preview_content)

    if module_name is None:
        # Filter modules that have a router file
        modules_with_routers = [m for m in modules_info if m["routes"]]

        # Build items for the TerminalMenu
        menu_items = [
            f"{m['name']} (already included)" if m["router_included"] else m["name"] for m in modules_with_routers
        ]

        terminal_menu = TerminalMenu(
            menu_items,
            title="Select a module to include its router:",
            preview_title=f'File "{APP_PATH}" preview',
            preview_command=preview_module_chosen,
            **DEFAULT_TERM_MENU,
        )
        menu_index = terminal_menu.show()
        if menu_index is None or menu_index < 0:
            # User pressed ESC, etc.
            return None

        chosen_module_name = modules_with_routers[menu_index]["name"]
        module_name = chosen_module_name
    else:
        # We came here with module_name explicitly
        pass

    # Write the new app.py
    updated_lines = updated_app_py_lines(module_name)
    new_content = ruff_format("\n".join(updated_lines))
    APP_PATH.write_text(new_content)

    return module_name


def new_router_func(module_name: str | None = None, model_name: str | None = None) -> str | None:
    """
    "New router" Option:
    1. Prompt user for a module name if not provided.
    2. Create "src/modules/{module_name}/routes.py" (or abort if file exists).
    3. If user chooses a model, generate basic CRUD route scaffolding.
    4. Include the created router in "src/api/app.py".
    """
    ROUTER_TEMPLATE = load_template("router")
    ROUTER_WITH_CRUD_TEMPLATE = load_template("router_with_basic_routes")

    modules_info, models_info = list_modules_and_models()

    if module_name is None:
        module_name = as_identifier(input("Enter the name of the module: ").strip())

    path = Path(f"src/modules/{module_name}/routes.py")
    if path.exists():
        print(f"Router file for module '{module_name}' already exists.")
        return None

    def build_router_code(_model_name: str | None) -> str:
        """Return the router code based on user choice to skip or include CRUD."""
        if _model_name is None:
            return ROUTER_TEMPLATE.replace("{module_name}", module_name).replace(
                "{ModuleName}", to_camel_case(module_name)
            )
        return (
            ROUTER_WITH_CRUD_TEMPLATE.replace("{module_name}", module_name)
            .replace("{ModuleName}", to_camel_case(module_name))
            .replace("{model_name}", _model_name)
            .replace("{ModelName}", to_camel_case(_model_name))
        )

    def preview_model_choice(m: str) -> str:
        """Preview the router file if a certain model is selected."""
        selected_model = None if m == "SKIP" else m
        content = build_router_code(selected_model)
        return highlight_preview(content)

    # If model_name was not given, ask the user (optionally skip)
    if model_name is None:
        terminal_menu = TerminalMenu(
            ["SKIP"] + [m["name"] for m in models_info],
            title="Select a model to implement basic routes or skip:",
            preview_title="Router Implementation Preview",
            preview_command=preview_model_choice,
            **DEFAULT_TERM_MENU,
        )
        menu_index = terminal_menu.show()
        if menu_index is None or menu_index < 0:
            print("Aborted creating router.")
            return None

        if menu_index == 0:
            chosen_model = None
        else:
            chosen_model = as_identifier(models_info[menu_index - 1]["name"])
        model_name = chosen_model

    def final_preview_decision(_: str) -> str:
        """Preview content that will be written if user says 'Yes'."""
        return highlight_preview(build_router_code(model_name))

    # Final approval
    confirm_menu = TerminalMenu(
        ["Yes", "No"],
        title=f'Create router file "{path}" and include it in "{APP_PATH}"?',
        preview_title=f'File "{path}" preview',
        preview_command=final_preview_decision,
        **DEFAULT_TERM_MENU,
    )
    confirm_idx = confirm_menu.show()

    if confirm_idx == 0:  # Yes
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(ruff_format(build_router_code(model_name)))
        (path.parent / "__init__.py").touch()

        # Include this router in app.py
        include_router_func(module_name)
        return module_name
    else:
        print("Aborted creating new router.")
        return None


def new_model_func() -> str | None:
    """
    "New model" Option:
    1. Ask user for the model name.
    2. Create "src/storages/mongo/{model_name}.py".
    3. Include the created model in "src/storages/mongo/__init__.py".
    4. Optionally implement CRUD and create a new router for this model.
    """
    MODEL_TEMPLATE = load_template("model")

    model_input = input("Enter the name of the model (in singular form): ").strip()
    model_name = as_identifier(model_input)
    ModelName = to_camel_case(model_name)
    path = Path(f"src/storages/mongo/{model_name}.py")

    if path.exists():
        print(f"Model file for '{model_name}' already exists.")
        return None

    def preview_model_creation(_: str) -> str:
        """Show a preview of the new model file."""
        content = MODEL_TEMPLATE.replace("{ModelName}", ModelName)
        return highlight_preview(ruff_format(content))

    # Confirm creation
    confirm_menu = TerminalMenu(
        ["Yes", "No"],
        title=f'Create new model file "{path}" and update registry "{MODELS_REGISTRY_PATH}"?',
        preview_title=f'File "{path}" preview',
        preview_command=preview_model_creation,
        **DEFAULT_TERM_MENU,
    )
    choice_idx = confirm_menu.show()

    if choice_idx == 0:  # Yes
        # Create the model file
        path.parent.mkdir(parents=True, exist_ok=True)
        content = MODEL_TEMPLATE.replace("{ModelName}", ModelName)
        path.write_text(ruff_format(content))

        # Insert import into models registry
        if not MODELS_REGISTRY_PATH.exists():
            print(f'Registry file "{MODELS_REGISTRY_PATH}" not found. Skipping registry update.')
            return model_name

        registry_code = MODELS_REGISTRY_PATH.read_text()
        registry_code = f"from src.storages.mongo.{model_name} import {ModelName}\n" + registry_code
        tree = ast.parse(registry_code)

        class RegistryModifier(ast.NodeTransformer):
            """Append the model to the `document_models` list if it exists."""

            def visit_Assign(self, node: ast.Assign) -> ast.Assign:
                if any(isinstance(target, ast.Name) and target.id == "document_models" for target in node.targets):
                    if (
                        isinstance(node.value, ast.Call)
                        and len(node.value.args) >= 2
                        and isinstance(node.value.args[1], ast.List)
                    ):
                        node.value.args[1].elts.append(ast.Name(id=ModelName, ctx=ast.Load()))
                return node

        modified_tree = RegistryModifier().visit(tree)
        modified_code = astor.to_source(modified_tree)
        modified_code = ruff_format(modified_code)
        MODELS_REGISTRY_PATH.write_text(modified_code)

        # Ask if user wants to create a router with basic routes
        router_menu = TerminalMenu(
            ["Yes", "No"],
            title="Do you want to create a router with basic routes for this model?",
            **DEFAULT_TERM_MENU,
        )
        router_choice = router_menu.show()

        if router_choice == 0:  # Yes
            mod_name = input(
                f"Enter the name of the module to place the router [Press Enter to use '{model_name}']: "
            ).strip()
            if not mod_name:
                mod_name = model_name
            mod_name = as_identifier(mod_name)

            # Also ask if user wants to implement a crud.py
            implement_crud_func(model_name=model_name, module_name=mod_name)
            new_router_func(module_name=mod_name, model_name=model_name)

        return model_name
    else:
        print("Aborted model creation.")
        return None


def implement_crud_func(model_name: str | None = None, module_name: str | None = None) -> str | None:
    """
    "Implement CRUD+ repository" Option:
    1. Choose model if not specified.
    2. Choose module if not specified (with an option to create a new module).
    3. Create "src/modules/{module_name}/crud.py" with basic CRUD+ functions.
    """
    CRUD_TEMPLATE = load_template("crud")
    modules_info, models_info = list_modules_and_models()

    def preview_model(m: str) -> str:
        """Show CRUD code snippet that will be generated."""
        content = CRUD_TEMPLATE.replace("{ModelName}", to_camel_case(m)).replace("{model_name}", m)
        return highlight_preview(content)

    # Step 1: If model_name is not provided, choose from the models
    if model_name is None:
        terminal_menu = TerminalMenu(
            [m["name"] for m in models_info],
            title="Select a model for CRUD+ implementation:",
            preview_title="CRUD Implementation Preview",
            preview_command=preview_model,
            **DEFAULT_TERM_MENU,
        )
        idx = terminal_menu.show()
        if idx is None:
            print("Aborted CRUD+ implementation.")
            return None
        model_name = models_info[idx]["name"]

    # Step 2: If module_name is not provided, choose from the modules
    if module_name is None:
        # Add a "create new module" option to the existing modules list
        menu_items = [(f"{m['name']} (already has crud.py)" if m["crud"] else m["name"]) for m in modules_info]
        menu_items.append("Create new module")

        terminal_menu = TerminalMenu(
            menu_items,
            title="Select a module to place crud.py:",
            **DEFAULT_TERM_MENU,
        )
        idx = terminal_menu.show()
        if idx is None:
            print("Aborted CRUD+ implementation.")
            return None

        if idx == len(menu_items) - 1:
            # User chose "Create new module"
            new_module_name = input("Enter the new module name: ").strip()
            new_module_name = as_identifier(new_module_name)
            target_dir = Path(f"src/modules/{new_module_name}")
            if target_dir.exists():
                print(f"Module '{new_module_name}' already exists. Aborting.")
                return None

            # Create the new module folder and __init__.py
            target_dir.mkdir(parents=True, exist_ok=True)
            (target_dir / "__init__.py").touch()
            module_name = new_module_name
        else:
            # Chose an existing module
            module_name = modules_info[idx]["name"]

    # Step 3: Create the CRUD file
    path = Path(f"src/modules/{module_name}/crud.py")
    if path.exists():
        print(f"CRUD file for module '{module_name}' already exists.")
        return None

    def preview_final(_: str) -> str:
        """Show final CRUD content to be created."""
        content = CRUD_TEMPLATE.replace("{ModelName}", to_camel_case(model_name)).replace("{model_name}", model_name)
        return highlight_preview(content)

    confirm_menu = TerminalMenu(
        ["Yes", "No"],
        title=f'Create file "{path}" with CRUD+ implementation?',
        preview_title=f'File "{path}" preview',
        preview_command=preview_final,
        **DEFAULT_TERM_MENU,
    )
    choice_idx = confirm_menu.show()

    if choice_idx == 0:
        path.parent.mkdir(parents=True, exist_ok=True)
        content = CRUD_TEMPLATE.replace("{ModelName}", to_camel_case(model_name)).replace("{model_name}", model_name)
        path.write_text(ruff_format(content))
        (path.parent / "__init__.py").touch()
        return module_name
    else:
        print("Aborted CRUD+ creation.")
        return None


def delete_module(module_name: str | None = None) -> None:
    """
    "Delete module" Option:
    1. Prompt user to choose a module to delete (if not given).
    2. Show references to this module found in entire codebase.
    3. Ask for confirmation.
    4. Remove references from src/api/app.py (router import + app.include_router).
    5. Delete the module folder.
    6. Advise user to remove leftover references manually if needed.
    """
    modules_info, _ = list_modules_and_models()

    if not modules_info:
        print("No modules found to delete.")
        return

    module_names = [m["name"] for m in modules_info]

    if not module_name:
        menu = TerminalMenu(
            module_names,
            title="Select a module to delete:",
            **DEFAULT_TERM_MENU,
        )
        idx = menu.show()
        if idx is None:
            print("Aborted module deletion.")
            return
        module_name = module_names[idx]
    else:
        if module_name not in module_names:
            print(f"Module '{module_name}' not found in 'src/modules/'.")
            return

    # Find references to this module across the project
    references = []
    for root, _dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                try:
                    lines = file_path.read_text().splitlines()
                except UnicodeDecodeError:
                    continue  # skip unreadable files

                for i, line in enumerate(lines, start=1):
                    if f"src.modules.{module_name}" in line:
                        references.append((file_path, i, line.strip()))

    # Build reference preview
    if references:
        ref_lines = ["References found in project:\n"]
        for ref_file, line_no, text in references:
            ref_lines.append(f"- {ref_file.relative_to(BASE_DIR)} (line {line_no}): {text}")
        ref_preview_str = "\n".join(ref_lines)
    else:
        ref_preview_str = "No direct references found, except possibly in app.py.\n"

    # Check for references in app.py specifically (router import, etc.)
    app_py_lines = APP_PATH.read_text().splitlines()
    import_line_idx = None
    include_line_idx = None

    for i, line in enumerate(app_py_lines):
        if f"from src.modules.{module_name}.routes import router as router_{module_name}" in line:
            import_line_idx = i
        if f"app.include_router(router_{module_name})" in line:
            include_line_idx = i

    def preview_deletion(_: str) -> str:
        return (
            f"You are about to delete the module '{module_name}'.\n\n"
            + ref_preview_str
            + "\nPress ENTER on 'Yes' to proceed, or 'No' to abort."
        )

    # Confirm
    confirm_menu = TerminalMenu(
        ["Yes", "No"],
        title=f"Delete module '{module_name}'?",
        preview_command=preview_deletion,
        preview_title="Module Deletion Confirmation",
        **DEFAULT_TERM_MENU,
    )
    choice_idx = confirm_menu.show()

    if choice_idx == 0:
        # Remove references from app.py
        changed_app_py = False
        new_app_py_lines = app_py_lines[:]

        if import_line_idx is not None:
            new_app_py_lines[import_line_idx] = ""
            changed_app_py = True

        if include_line_idx is not None:
            new_app_py_lines[include_line_idx] = ""
            changed_app_py = True

        if changed_app_py:
            filtered = [line for line in new_app_py_lines if line.strip() != ""]
            updated = ruff_format("\n".join(filtered) + "\n")
            APP_PATH.write_text(updated)

        # Remove the module folder
        target_dir = Path("src/modules") / module_name
        if target_dir.exists() and target_dir.is_dir():
            shutil.rmtree(target_dir)
            print(f"Module '{module_name}' directory removed.")
        else:
            print(f"Module directory '{target_dir}' does not exist or is not a directory.")

        print("Module deletion completed. Check references above to remove if needed.")
    else:
        print("Aborted module deletion.")


# ------------------------------------------------------------------------------
# Main CLI
# ------------------------------------------------------------------------------
def main() -> None:
    """Script entry point: Display a menu of available actions."""
    options = ["New model", "Implement CRUD+ repository", "New router", "Delete module"]

    doc_map = {
        "New model": cleandoc(new_model_func.__doc__ or ""),
        "Implement CRUD+ repository": cleandoc(implement_crud_func.__doc__ or ""),
        "New router": cleandoc(new_router_func.__doc__ or ""),
        "Delete module": cleandoc(delete_module.__doc__ or ""),
    }

    def preview(option: str) -> str:
        """Show docstring of the chosen command as a preview."""
        return doc_map.get(option, "No documentation available")

    menu = TerminalMenu(
        options,
        title="Select an option:",
        preview_command=preview,
        preview_title="Description",
        **DEFAULT_TERM_MENU,
    )
    choice_idx = menu.show()
    if choice_idx is None or choice_idx < 0:
        print("No option selected. Exiting.")
        return

    choice = options[choice_idx]

    if choice == "New model":
        new_model_func()
    elif choice == "Implement CRUD+ repository":
        implement_crud_func()
    elif choice == "New router":
        new_router_func()
    elif choice == "Delete module":
        delete_module()
    else:
        raise ValueError(f"Unknown option selected: {choice}")


if __name__ == "__main__":
    main()
