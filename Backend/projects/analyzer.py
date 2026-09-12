import os
import json

# Files/folders that should not be analyzed
IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "venv",
    "__pycache__",
    ".idea",
    ".vscode",
    "dist",
    "build"
}


LANGUAGE_EXTENSIONS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".java": "Java",
    ".cpp": "C++",
    ".c": "C",
    ".h": "C/C++ Header",
    ".hpp": "C++",
    ".cs": "C#",
    ".go": "Go",
    ".rs": "Rust",
    ".php": "PHP",
    ".rb": "Ruby",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sql": "SQL"
}


def detect_files_and_folders(repository_path: str):

    files = []
    folders = []

    for root, directories, filenames in os.walk(repository_path):

        # Remove ignored directories from traversal
        directories[:] = [
            directory
            for directory in directories
            if directory not in IGNORED_DIRECTORIES
        ]

        # Get relative folder path
        relative_root = os.path.relpath(
            root,
            repository_path
        )

        # Detect folders
        for directory in directories:

            if relative_root == ".":
                folder_path = directory
            else:
                folder_path = os.path.join(
                    relative_root,
                    directory
                )

            folders.append(
                folder_path.replace("\\", "/")
            )

        # Detect files
        for filename in filenames:

            if relative_root == ".":
                file_path = filename
            else:
                file_path = os.path.join(
                    relative_root,
                    filename
                )

            files.append(
                file_path.replace("\\", "/")
            )

    return {
        "total_files": len(files),
        "total_folders": len(folders),
        "files": files,
        "folders": folders
    }

def detect_programming_languages(repository_path: str):

    language_counts = {}

    for root, directories, filenames in os.walk(repository_path):

        # Ignore unnecessary directories
        directories[:] = [
            directory
            for directory in directories
            if directory not in IGNORED_DIRECTORIES
        ]

        for filename in filenames:

            extension = os.path.splitext(filename)[1].lower()

            language = LANGUAGE_EXTENSIONS.get(extension)

            if language:

                language_counts[language] = (
                    language_counts.get(language, 0) + 1
                )

    return {
        "languages": language_counts
    }

def detect_dependencies(repository_path: str):

    dependencies = {}

    for root, directories, filenames in os.walk(repository_path):

        # Ignore unnecessary directories
        directories[:] = [
            directory
            for directory in directories
            if directory not in IGNORED_DIRECTORIES
        ]

        for filename in filenames:

            file_path = os.path.join(root, filename)

            # -------------------------
            # Node.js - package.json
            # -------------------------

            if filename == "package.json":

                try:

                    with open(
                        file_path,
                        "r",
                        encoding="utf-8"
                    ) as file:

                        package_data = json.load(file)

                    project_dependencies = {}

                    project_dependencies.update(
                        package_data.get("dependencies", {})
                    )

                    project_dependencies.update(
                        package_data.get("devDependencies", {})
                    )

                    dependencies[
                        os.path.relpath(
                            file_path,
                            repository_path
                        ).replace("\\", "/")
                    ] = project_dependencies

                except (json.JSONDecodeError, OSError):

                    continue

            # -------------------------
            # Python - requirements.txt
            # -------------------------

            elif filename == "requirements.txt":

                try:

                    with open(
                        file_path,
                        "r",
                        encoding="utf-8"
                    ) as file:

                        packages = []

                        for line in file:

                            line = line.strip()

                            if (
                                line
                                and not line.startswith("#")
                            ):
                                packages.append(line)

                    dependencies[
                        os.path.relpath(
                            file_path,
                            repository_path
                        ).replace("\\", "/")
                    ] = packages

                except OSError:

                    continue

    return {
        "dependencies": dependencies
    }

def detect_major_modules(repository_path: str):

    module_names = {
        "src",
        "app",
        "components",
        "pages",
        "routes",
        "controllers",
        "models",
        "services",
        "middleware",
        "config",
        "utils",
        "hooks",
        "context",
        "admin",
        "staff",
        "api",
        "database",
        "auth",
        "modules",
        "views",
        "schemas",
        "tests",
        "test",
    }

    detected_modules = []

    for root, directories, filenames in os.walk(repository_path):

        # Ignore unnecessary directories
        directories[:] = [
            directory
            for directory in directories
            if directory not in IGNORED_DIRECTORIES
        ]

        for directory in directories:

            if directory.lower() in module_names:

                relative_path = os.path.relpath(
                    os.path.join(root, directory),
                    repository_path
                )

                detected_modules.append(
                    relative_path.replace("\\", "/")
                )

    return {
        "modules": detected_modules,
        "total_modules": len(detected_modules)
    }

def detect_configuration_files(repository_path: str):

    configuration_files = {
        ".env",
        ".env.example",
        ".env.local",
        ".env.production",
        ".env.development",
        "vite.config.js",
        "vite.config.ts",
        "vite.config.jsx",
        "vite.config.tsx",
        "tailwind.config.js",
        "tailwind.config.ts",
        "postcss.config.js",
        "postcss.config.cjs",
        "eslint.config.js",
        "eslint.config.mjs",
        "vercel.json",
        "next.config.js",
        "next.config.mjs",
        "webpack.config.js",
        "docker-compose.yml",
        "docker-compose.yaml",
        "Dockerfile",
        ".gitignore"
    }

    detected_files = []

    for root, directories, filenames in os.walk(repository_path):

        directories[:] = [
            directory
            for directory in directories
            if directory not in IGNORED_DIRECTORIES
        ]

        for filename in filenames:

            if filename in configuration_files:

                relative_path = os.path.relpath(
                    os.path.join(root, filename),
                    repository_path
                )

                detected_files.append(
                    relative_path.replace("\\", "/")
                )

    return {
        "configuration_files": detected_files,
        "total_configuration_files": len(detected_files)
    }
def detect_readme(repository_path: str):

    readme_names = {
        "README.md",
        "README.txt",
        "README"
    }

    readme_files = []

    for root, directories, filenames in os.walk(repository_path):

        directories[:] = [
            directory
            for directory in directories
            if directory not in IGNORED_DIRECTORIES
        ]

        for filename in filenames:

            if filename.upper() in {
                name.upper()
                for name in readme_names
            }:

                file_path = os.path.join(
                    root,
                    filename
                )

                relative_path = os.path.relpath(
                    file_path,
                    repository_path
                )

                try:

                    with open(
                        file_path,
                        "r",
                        encoding="utf-8"
                    ) as file:

                        content = file.read()

                    readme_files.append({
                        "path": relative_path.replace("\\", "/"),
                        "size": len(content),
                        "content": content
                    })

                except (OSError, UnicodeDecodeError):

                    continue

    return {
        "readme_found": len(readme_files) > 0,
        "total_readme_files": len(readme_files),
        "readme_files": readme_files
    }

def detect_databases(repository_path: str):

    database_indicators = {
        "MongoDB": {
            "dependencies": {
                "mongoose",
                "mongodb"
            },
            "keywords": [
                "mongoose.connect",
                "MongoClient",
                "mongodb://",
                "mongodb+srv://"
            ]
        },

        "MySQL": {
            "dependencies": {
                "mysql",
                "mysql2",
                "pymysql",
                "mysql-connector-python"
            },
            "keywords": [
                "mysql://",
                "mysql+pymysql://"
            ]
        },

        "PostgreSQL": {
            "dependencies": {
                "pg",
                "psycopg2",
                "psycopg2-binary",
                "asyncpg"
            },
            "keywords": [
                "postgresql://",
                "postgres://"
            ]
        },

        "SQLite": {
            "dependencies": {
                "sqlite3"
            },
            "keywords": [
                "sqlite://",
                ".db"
            ]
        }
    }

    detected_databases = {}

    # ------------------------------------------------
    # Step 1: Check dependencies
    # ------------------------------------------------

    dependencies_result = detect_dependencies(
        repository_path
    )

    for _, dependency_data in dependencies_result[
        "dependencies"
    ].items():

        # package.json returns dictionary
        if isinstance(dependency_data, dict):

            dependency_names = {
                name.lower()
                for name in dependency_data.keys()
            }

        # requirements.txt returns list
        elif isinstance(dependency_data, list):

            dependency_names = {
                package.split("==")[0]
                .split(">=")[0]
                .split("<=")[0]
                .strip()
                .lower()
                for package in dependency_data
            }

        else:
            continue

        for database, indicators in database_indicators.items():

            for dependency in indicators["dependencies"]:

                if dependency.lower() in dependency_names:

                    detected_databases[database] = {
                        "detected_by": "dependency",
                        "indicator": dependency
                    }

    # ------------------------------------------------
    # Step 2: Check source-code keywords
    # ------------------------------------------------

    for root, directories, filenames in os.walk(repository_path):

        directories[:] = [
            directory
            for directory in directories
            if directory not in IGNORED_DIRECTORIES
        ]

        for filename in filenames:

            extension = os.path.splitext(filename)[1].lower()

            # Only inspect source/config files
            allowed_extensions = {
                ".js",
                ".jsx",
                ".ts",
                ".tsx",
                ".py",
                ".java",
                ".go",
                ".php",
                ".rb",
                ".env",
                ".json"
            }

            if extension not in allowed_extensions:
                continue

            file_path = os.path.join(
                root,
                filename
            )

            try:

                with open(
                    file_path,
                    "r",
                    encoding="utf-8"
                ) as file:

                    content = file.read()

            except (OSError, UnicodeDecodeError):

                continue

            for database, indicators in database_indicators.items():

                for keyword in indicators["keywords"]:

                    if keyword.lower() in content.lower():

                        if database not in detected_databases:

                            detected_databases[database] = {
                                "detected_by": "source_code",
                                "indicator": keyword
                            }

                        break

    return {
        "database_detected": len(detected_databases) > 0,
        "databases": detected_databases
    }
def analyze_project_structure(repository_path: str):

    files_result = detect_files_and_folders(
        repository_path
    )

    languages_result = detect_programming_languages(
        repository_path
    )

    dependencies_result = detect_dependencies(
        repository_path
    )

    modules_result = detect_major_modules(
        repository_path
    )

    configuration_result = detect_configuration_files(
        repository_path
    )

    readme_result = detect_readme(
        repository_path
    )

    database_result = detect_databases(
    repository_path
    )

    return {
        "files_and_folders": files_result,
        "programming_languages": languages_result,
        "dependencies": dependencies_result,
        "major_modules": modules_result,
        "configuration_files": configuration_result,
        "readme": readme_result,
        "database": database_result
    }



if __name__ == "__main__":

    repository_path = "uploaded_projects"

    project_analysis = analyze_project_structure(
        repository_path
    )

    print("\nPROJECT ANALYSIS:")
    print(project_analysis)