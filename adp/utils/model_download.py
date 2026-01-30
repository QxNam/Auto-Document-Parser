import os
import shutil

import kagglehub

current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))

tmp_path = kagglehub.dataset_download("quachnam/models-docling")

for item in os.listdir(tmp_path):
    s = os.path.join(tmp_path, item)
    d = os.path.join(project_root, item)
    if os.path.isdir(s):
        if os.path.exists(d):
            shutil.rmtree(d)
        shutil.copytree(s, d)
    else:
        shutil.copy2(s, d)

print("✅ Downloaded.")
