import argparse
import os
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(description="Extrair frames de vídeo usando FFmpeg")
    
    parser.add_argument("-i", "--input", required=True, help="Caminho para o vídeo")
    parser.add_argument("-o", "--output", default="frames", help="Pasta de saída")
    parser.add_argument("--fps", type=int, required=True, help="FPS desejado")
    parser.add_argument("--qscale", type=int, default=1, help="Qualidade JPEG (1 = máxima)")
    parser.add_argument("--ffmpeg", default="ffmpeg", help="Path do ffmpeg.exe se não estiver no PATH")

    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print("[ERRO] Vídeo não encontrado.")
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

    print("Executando comando:")
    print(" ".join(cmd))

    subprocess.run(cmd)

if __name__ == "__main__":
    main()