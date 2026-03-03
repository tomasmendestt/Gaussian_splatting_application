import argparse
import os
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(description="Extract video frames using FFmpeg")
    
    parser.add_argument("-i", "--input", required=True, help="Video path")
    parser.add_argument("-o", "--output", default="frames", help="Output folder")
    parser.add_argument("--fps", type=int, required=True, help="Desired FPS")
    parser.add_argument("--qscale", type=int, default=1, help="JPEG quality (1 = maximum)")
    parser.add_argument("--ffmpeg", default="ffmpeg", help="Path to ffmpeg.exe if not in PATH")

    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print("[ERROR] Video not found.")
        sys.exit(1)

    os.makedirs(args.output, exist_ok=True)

    output_pattern = os.path.join(args.output, "%04d.jpg")

    cmd = [
        args.ffmpeg,
        "-i", args.input,
        "-qscale:v", str(args.qscale),
        "-qmin", "1",
        "-vf", f"fps={args.fps}",
        output_pattern
    ]

    print("Executing command:")
    print(" ".join(cmd))

    subprocess.run(cmd)

if __name__ == "__main__":
    main()
