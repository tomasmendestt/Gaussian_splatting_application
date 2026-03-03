import argparse
import os
import subprocess
import sys

DEFAULT_VIEWER = r"D:\Gaussian_splatting\gaussian_splatting_Tomas_1\viewers\bin\SIBR_gaussianViewer_app.exe"

def find_model_root(path: str) -> str:
    """
    Accepts:
      - root output folder (contains cfg_args)
      - point_cloud/iteration_XXXX folder
      - point_cloud.ply file
    Always returns the root output folder (where cfg_args is located).
    """
    cur = os.path.abspath(path)

    # If it is a file, start from its directory
    if os.path.isfile(cur):
        cur = os.path.dirname(cur)

    # If it is a folder, go up the directory tree until cfg_args is found
    while True:
        if os.path.isfile(os.path.join(cur, "cfg_args")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:  # Reached filesystem root
            raise FileNotFoundError(f"'cfg_args' not found above: {path}")
        cur = parent

def main():
    p = argparse.ArgumentParser(description="Launch SIBR Gaussian Viewer")
    p.add_argument("--viewer", type=str, default=DEFAULT_VIEWER,
                   help="Path to the SIBR Gaussian Viewer executable")
    p.add_argument("-m", "--model", required=True,
                   help="Path to model OUTPUT FOLDER (e.g., output/ID) OR a .ply inside it")
    p.add_argument("extra", nargs=argparse.REMAINDER,
                   help="Additional arguments to pass to the viewer (optional)")
    args = p.parse_args()

    viewer = os.path.abspath(args.viewer)
    model_in = args.model

    if not os.path.isfile(viewer):
        print(f"Error: Viewer executable not found at '{viewer}'")
        sys.exit(1)

    try:
        model_root = find_model_root(model_in)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    cmd = [viewer, "-m", model_root] + (args.extra or [])
    print("Running:", " ".join(cmd))
    subprocess.Popen(cmd)

if __name__ == "__main__":
    main()