import os
from pathlib import Path

while True:
    project_name = input("Enter the Src Folder Name (e.g., 'adaptive_microgesture'): ").strip()
    if project_name != '':
        break

list_of_files = [
    ".github/workflows/.gitkeep",
    f"{project_name}/__init__.py",
    f"{project_name}/data/__init__.py",
    f"{project_name}/data/preprocessed/__init__.py",
    f"{project_name}/data/preprocessed/preprocess_data.py",
    f"{project_name}/data/leapgestrecog/.gitkeep",
    f"{project_name}/data/leapgestrecog/__init__.py",
    f"{project_name}/data/synthetic/__init__.py",
    f"{project_name}/data/synthetic/.gitkeep",
    f"{project_name}/data/processed/__init__.py",
    f"{project_name}/data/processed/.gitkeep",
    f"{project_name}/models/__init__.py",
    f"{project_name}/models/lmgt.py",
    f"{project_name}/models/train.py",
    f"{project_name}/models/eval.py",
    f"{project_name}/models/utils.py",
    f"{project_name}/inference/__init__.py",
    f"{project_name}/inference/real_time_inference.py",
    f"{project_name}/inference/whiteboard_control.py",
    f"{project_name}/inference/webcam_stream.py",
    "notebooks/.gitkeep",
    "templates/index.html",
    "static/style.css",
    "requirements.txt",
    "README.md",
    "init_setup.sh",
    "Dockerfile",
    "setup.py"
]

for filepath in list_of_files:
    filepath = Path(filepath)
    filedir, filename = os.path.split(filepath)

    if filedir != "":
        os.makedirs(filedir, exist_ok=True)
    if not filepath.exists():
        with open(filepath, "w") as f:
            pass

print(f"Project structure created with root source folder '{project_name}'.")
