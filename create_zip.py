import os
import zipfile

def create_project_zip():
    base_dir = r"c:\Users\Theja\Downloads\files"
    zip_path = os.path.join(base_dir, "SupportPilot_Project_Updated.zip")

    exclude_folders = {
        'node_modules', 'venv', '.venv', '__pycache__', '.git', 
        '.pytest_cache', 'dist', '.rolldown', '.vite', '.idea', '.vscode', 'temp_zips'
    }

    exclude_extensions = {
        '.pyc', '.pyo', '.pyd', '.zip', '.tar.gz', '.log', '.sqlite', '.db'
    }

    exclude_files = {
        'create_zip.py'
    }

    print("Compressing project workspace...")
    count = 0

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(base_dir):
            # Exclude folders in-place to prevent os.walk from entering them
            dirs[:] = [d for d in dirs if d not in exclude_folders]
            
            for file in files:
                if file in exclude_files:
                    continue
                _, ext = os.path.splitext(file.lower())
                if ext in exclude_extensions:
                    continue
                
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_dir)
                
                zipf.write(full_path, rel_path)
                count += 1

    print(f"Compressed {count} files successfully into {zip_path}")

if __name__ == "__main__":
    create_project_zip()
