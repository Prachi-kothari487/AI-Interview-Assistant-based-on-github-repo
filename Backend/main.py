from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy import text
from database.connection import engine , get_db
from auth.routes import router as auth_router
import uuid
from auth.security import get_current_user_id
from git import Repo
from fastapi import FastAPI, Depends, HTTPException
import os
import shutil
import zipfile
from database.models import Project
from sqlalchemy.orm import Session
from projects.analyzer import analyze_project_structure
from sqlalchemy.orm import Session

from database.connection import engine, get_db

from database.models import (
    Project,
    ProjectFile,
    ProjectTechnology,
    ProjectModule
)

from projects.analyzer import analyze_project_structure
app = FastAPI(
    title="AI Project Interview Assistant",
    version="1.0.0"
)

class GitHubRequest(BaseModel):
    github_url: HttpUrl


@app.get("/")
def root():

    try:

        
        with engine.connect() as connection:

            result = connection.execute(
                text("SELECT 1")
            )

            result = result.scalar()

        return {
            "success": True,
            "message": "FastAPI + MySQL connected successfully",
            "database_test": result
        }

    except Exception as e:

        return {
            "success": False,
            "message": "Database connection failed",
            "error": str(e)
        }

@app.post("/api/projects/github")
def add_github_repository(
    data: GitHubRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):

    github_url = str(data.github_url)

    if "github.com" not in github_url:
        raise HTTPException(
            status_code=400,
            detail="Please provide a valid GitHub URL"
        )

    try:

        # -----------------------------
        # 1. Clone GitHub Repository
        # -----------------------------

        base_dir = "uploaded_projects"

        os.makedirs(base_dir, exist_ok=True)

        project_uuid = str(uuid.uuid4())

        project_dir = os.path.join(
            base_dir,
            project_uuid
        )

        Repo.clone_from(
            github_url,
            project_dir
        )

        # -----------------------------
        # 2. Analyze Repository
        # -----------------------------

        analysis = analyze_project_structure(
            project_dir
        )

        # -----------------------------
        # 3. Create Project
        # -----------------------------

        project_name = os.path.basename(
            github_url.rstrip("/")
        )

        project = Project(
            user_id=current_user_id,
            name=project_name,
            github_url=github_url,
            source_type="github",
            status="analyzing"
        )

        db.add(project)

        db.commit()

        db.refresh(project)

        # -----------------------------
        # 4. Save Project Files
        # -----------------------------

        files = analysis[
            "files_and_folders"
        ]["files"]

        language_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".jsx": "JavaScript",
            ".ts": "TypeScript",
            ".tsx": "TypeScript",
            ".java": "Java",
            ".cpp": "C++",
            ".c": "C",
            ".html": "HTML",
            ".css": "CSS",
            ".scss": "SCSS"
        }

        for file_path in files:

            full_path = os.path.join(
                project_dir,
                file_path
            )

            file_name = os.path.basename(
                file_path
            )

            extension = os.path.splitext(
                file_name
            )[1].lower()

            language = language_map.get(
                extension
            )

            try:
                file_size = os.path.getsize(
                    full_path
                )
            except OSError:
                file_size = None

            project_file = ProjectFile(
                project_id=project.id,
                file_path=file_path,
                file_name=file_name,
                extension=extension,
                language=language,
                size=file_size
            )

            db.add(project_file)

        # -----------------------------
        # 5. Save Programming Languages
        # -----------------------------

        languages = analysis[
            "programming_languages"
        ]["languages"]

        for language, count in languages.items():

            technology = ProjectTechnology(
                project_id=project.id,
                technology=language,
                category="language"
            )

            db.add(technology)

        # -----------------------------
        # 6. Save Dependencies
        # -----------------------------

        dependencies = analysis[
            "dependencies"
        ]["dependencies"]

        for file_name, dependency_data in dependencies.items():

            if isinstance(
                dependency_data,
                dict
            ):

                for dependency_name in dependency_data.keys():

                    technology = ProjectTechnology(
                        project_id=project.id,
                        technology=dependency_name,
                        category="dependency"
                    )

                    db.add(technology)

            elif isinstance(
                dependency_data,
                list
            ):

                for dependency_name in dependency_data:

                    technology = ProjectTechnology(
                        project_id=project.id,
                        technology=dependency_name,
                        category="dependency"
                    )

                    db.add(technology)

        # -----------------------------
        # 7. Save Detected Databases
        # -----------------------------

        databases = analysis[
            "database"
        ]["databases"]

        for database_name in databases.keys():

            technology = ProjectTechnology(
                project_id=project.id,
                technology=database_name,
                category="database"
            )

            db.add(technology)

        # -----------------------------
        # 8. Save Major Modules
        # -----------------------------

        modules = analysis[
            "major_modules"
        ]["modules"]

        for module_name in modules:

            project_module = ProjectModule(
                project_id=project.id,
                module_name=module_name,
                description=None
            )

            db.add(project_module)

        # -----------------------------
        # 9. Mark Project Completed
        # -----------------------------

        project.status = "completed"

        db.commit()

        db.refresh(project)

        # -----------------------------
        # 10. Return Response
        # -----------------------------

        return {
            "success": True,
            "message": "GitHub repository analyzed successfully",
            "github_url": github_url,
            "project_directory": project_dir,
            "project_id": project.id,
            "user_id": current_user_id,
            "status": project.status,
            "analysis": analysis
        }

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=f"GitHub repository processing failed: {str(e)}"
        )
@app.post("/api/projects/upload")
async def upload_project(
    file: UploadFile = File(...)
):

    if not file.filename.lower().endswith(".zip"):
        raise HTTPException(
            status_code=400,
            detail="Only ZIP files are allowed"
        )

    try:

        # Base directory for uploaded projects
        base_dir = "uploaded_projects"

        os.makedirs(base_dir, exist_ok=True)

        # Create project folder using ZIP filename
        project_name = os.path.splitext(file.filename)[0]

        project_dir = os.path.join(
            base_dir,
            project_name
        )

        # Remove previous upload with same name
        if os.path.exists(project_dir):
            shutil.rmtree(project_dir)

        os.makedirs(project_dir)

        # Read uploaded ZIP
        contents = await file.read()

        if len(contents) == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded ZIP file is empty"
            )

        # Temporary ZIP path
        zip_path = os.path.join(
            base_dir,
            file.filename
        )

        with open(zip_path, "wb") as buffer:
            buffer.write(contents)

        # Extract ZIP
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(project_dir)

        # Delete temporary ZIP
        os.remove(zip_path)

        return {
            "success": True,
            "message": "ZIP uploaded and extracted successfully",
            "filename": file.filename,
            "project_directory": project_dir,
            "status": "ready_for_analysis"
        }

    except zipfile.BadZipFile:

        raise HTTPException(
            status_code=400,
            detail="Invalid or corrupted ZIP file"
        )

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"File processing failed: {str(e)}"
        )

app.include_router(auth_router)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):

    return {
        "success": False,
        "message": "Something went wrong",
        "error": str(exc)
    }