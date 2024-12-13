import pickle
import sys
import types
from pathlib import Path
from typing import Any


def _fix_pickle_imports() -> None:
    """Add compatibility for old pickle files with different import paths."""

    # Map old module paths to new ones
    class_mappings = {
        "cayley_tables.cayley_table_states": "cayley_tables.tables.cayley_table_states",
        "cayley_tables.cayley_table_actions": "cayley_tables.tables.cayley_table_actions",
        "cayley_tables.equiv_classes": "cayley_tables.utils.equiv_classes",
    }

    class ModuleRedirector(types.ModuleType):
        def __init__(self, module_name: str):
            super().__init__(module_name)
            self.module_name = module_name

        def __getattr__(self, name: str) -> Any:
            real_module = sys.modules.get(class_mappings[self.module_name])
            if real_module is None:
                __import__(class_mappings[self.module_name])
                real_module = sys.modules[class_mappings[self.module_name]]
            return getattr(real_module, name)

    # Add redirectors for old module paths
    for old_path in class_mappings:
        if old_path not in sys.modules:
            sys.modules[old_path] = ModuleRedirector(old_path)


def migrate_pickle_file(file_path: Path) -> None:
    """Load a pickle file, update its imports, and save it back."""
    print(f"Migrating {file_path}")

    # Add compatibility for old imports
    _fix_pickle_imports()

    # Load the old data
    with open(file_path, "rb") as f:
        data = pickle.load(f)

    # Create backup
    backup_path = file_path.with_suffix(".pkl.bak")
    if not backup_path.exists():
        print(f"Creating backup at {backup_path}")
        with open(backup_path, "wb") as f:
            with open(file_path, "rb") as original:
                f.write(original.read())

    # Save with new imports
    print("Saving updated file")
    with open(file_path, "wb") as f:
        pickle.dump(data, f)


def main():
    # Add the project root directory to the Python path
    project_root = Path(__file__).parent.parent
    sys.path.append(str(project_root))

    # Import required modules after adding to path

    # Find all pickle files
    pickle_dir = project_root / "saved" / "algebra"
    pickle_files = list(pickle_dir.glob("*.pkl"))

    if not pickle_files:
        print(f"No pickle files found in {pickle_dir}")
        return

    print(f"Found {len(pickle_files)} pickle files to migrate")

    # Migrate each file
    for file_path in pickle_files:
        try:
            migrate_pickle_file(file_path)
            print(f"Successfully migrated {file_path}")
        except Exception as e:
            print(f"Error migrating {file_path}: {e}")

    print("\nMigration complete!")
    print("Backups of original files were created with .pkl.bak extension")


if __name__ == "__main__":
    main()
