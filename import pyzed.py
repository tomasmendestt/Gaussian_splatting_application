import pyzed.sl as sl
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import time


def open_zed():
    zed = sl.Camera()
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD1080
    init_params.camera_fps = 30
    err = zed.open(init_params)
    if err > sl.ERROR_CODE.SUCCESS:
        raise RuntimeError(f"Camera Open: {repr(err)}")
    return zed


def grab_frames(num_frames, save_dir):
    zed = open_zed()
    os.makedirs(save_dir, exist_ok=True)

    image = sl.Mat()
    runtime = sl.RuntimeParameters()

    i = 0
    while i < num_frames:
        if zed.grab(runtime) <= sl.ERROR_CODE.SUCCESS:
            zed.retrieve_image(image, sl.VIEW.LEFT)
            cv_image = image.get_data()

            # Se colori strani, prova:
            # cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGRA2BGR)

            out_path = os.path.join(save_dir, f"ZED_Image_{i}.png")
            ok = cv2.imwrite(out_path, cv_image)
            if not ok:
                print(f"Errore salvataggio: {out_path}")
                break
            i += 1

    zed.close()


def record_svo(duration_s, save_dir, filename="recording.svo2"):
    """
    Registra un video in formato ZED (.svo / .svo2).
    """
    zed = open_zed()
    os.makedirs(save_dir, exist_ok=True)

    svo_path = os.path.join(save_dir, filename)

    rec_params = sl.RecordingParameters(svo_path)
    # opzionale: scegli compressione
    # rec_params.compression_mode = sl.SVO_COMPRESSION_MODE.H264
    # oppure: sl.SVO_COMPRESSION_MODE.H265 / LOSSLESS

    err = zed.enable_recording(rec_params)
    if err != sl.ERROR_CODE.SUCCESS:
        zed.close()
        raise RuntimeError(f"enable_recording: {repr(err)}")

    runtime = sl.RuntimeParameters()
    t0 = time.time()
    frames = 0

    while (time.time() - t0) < duration_s:
        if zed.grab(runtime) <= sl.ERROR_CODE.SUCCESS:
            # Scrittura nel file SVO avviene automaticamente quando grab() ha successo
            frames += 1

    zed.disable_recording()
    zed.close()
    print(f"Registrazione SVO salvata in: {svo_path} (frames: {frames})")


def record_avi(duration_s, save_dir, filename="recording.avi", fps=30):
    """
    Registra un video standard AVI usando OpenCV VideoWriter.
    Nota: MP4 spesso richiede codec specifici, AVI è più semplice.
    """
    zed = open_zed()
    os.makedirs(save_dir, exist_ok=True)

    image = sl.Mat()
    runtime = sl.RuntimeParameters()

    # Prendiamo un frame per sapere la dimensione
    if zed.grab(runtime) > sl.ERROR_CODE.SUCCESS:
        zed.close()
        raise RuntimeError("Impossibile grab iniziale per dimensioni video.")

    zed.retrieve_image(image, sl.VIEW.LEFT)
    frame0 = image.get_data()

    # Converti BGRA -> BGR per VideoWriter (di solito serve)
    if frame0.shape[2] == 4:
        frame0_bgr = cv2.cvtColor(frame0, cv2.COLOR_BGRA2BGR)
    else:
        frame0_bgr = frame0

    h, w = frame0_bgr.shape[:2]
    out_path = os.path.join(save_dir, filename)

    # Codec: XVID è comune su Windows, altrimenti MJPG
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    writer = cv2.VideoWriter(out_path, fourcc, fps, (w, h))
    if not writer.isOpened():
        zed.close()
        raise RuntimeError("VideoWriter non si è aperto. Prova codec MJPG o installa codec.")

    writer.write(frame0_bgr)

    t0 = time.time()
    frames = 1
    while (time.time() - t0) < duration_s:
        if zed.grab(runtime) <= sl.ERROR_CODE.SUCCESS:
            zed.retrieve_image(image, sl.VIEW.LEFT)
            frame = image.get_data()
            if frame.shape[2] == 4:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            writer.write(frame)
            frames += 1

    writer.release()
    zed.close()
    print(f"Registrazione AVI salvata in: {out_path} (frames: {frames})")


if __name__ == "__main__":
    app = tk.Tk()
    app.title("ZED Capture")
    app.geometry("720x480")

    mode_var = tk.StringVar(value="photo")      # photo / video
    video_type_var = tk.StringVar(value="svo")  # svo / avi
    frames_var = tk.StringVar(value="50")
    duration_var = tk.StringVar(value="5")      # seconds
    save_dir_var = tk.StringVar(value=r"D:\Images")

    # Save folder
    tk.Label(app, text="Save folder:").pack(pady=(10, 0))
    row = tk.Frame(app)
    row.pack(fill="x", padx=10, pady=6)
    tk.Entry(row, textvariable=save_dir_var).pack(side="left", fill="x", expand=True)

    def browse():
        chosen = filedialog.askdirectory(title="Select folder to save output")
        if chosen:
            save_dir_var.set(chosen)

    tk.Button(row, text="Browse...", command=browse).pack(side="left", padx=8)

    # Mode selection
    tk.Label(app, text="Mode:").pack(pady=(10, 0))
    tk.Radiobutton(app, text="Photo mode", variable=mode_var, value="photo").pack(anchor="w", padx=20)
    tk.Radiobutton(app, text="Video mode", variable=mode_var, value="video").pack(anchor="w", padx=20)

    # Photo params
    photo_box = tk.LabelFrame(app, text="Photo settings")
    photo_box.pack(fill="x", padx=10, pady=10)
    tk.Label(photo_box, text="Number of frames:").pack(side="left", padx=10, pady=8)
    tk.Entry(photo_box, textvariable=frames_var, width=10).pack(side="left", pady=8)

    # Video params
    video_box = tk.LabelFrame(app, text="Video settings")
    video_box.pack(fill="x", padx=10, pady=10)

    tk.Label(video_box, text="Type:").grid(row=0, column=0, padx=10, pady=8, sticky="w")
    tk.Radiobutton(video_box, text="ZED SVO (.svo2)", variable=video_type_var, value="svo").grid(row=0, column=1, sticky="w")
    tk.Radiobutton(video_box, text="OpenCV AVI (.avi)", variable=video_type_var, value="avi").grid(row=0, column=2, sticky="w")

    tk.Label(video_box, text="Duration (seconds):").grid(row=1, column=0, padx=10, pady=8, sticky="w")
    tk.Entry(video_box, textvariable=duration_var, width=10).grid(row=1, column=1, sticky="w")

    # Start button
    def start():
        save_dir = save_dir_var.get().strip() or r"D:\Images"

        try:
            if mode_var.get() == "photo":
                txt = frames_var.get().strip()
                n = int(txt) if txt.isdigit() else 50
                grab_frames(n, save_dir)
                messagebox.showinfo("Done", f"Saved {n} images in:\n{save_dir}")
            else:
                d_txt = duration_var.get().strip()
                d = float(d_txt) if d_txt else 5.0

                if video_type_var.get() == "svo":
                    record_svo(d, save_dir, filename="zed_recording.svo2")
                    messagebox.showinfo("Done", f"Saved SVO in:\n{save_dir}")
                else:
                    record_avi(d, save_dir, filename="zed_recording.avi", fps=30)
                    messagebox.showinfo("Done", f"Saved AVI in:\n{save_dir}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(app, text="START", command=start, height=2, width=12).pack(pady=10)

    app.mainloop()