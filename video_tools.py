import cv2
import imagehash
from PIL import Image
import numpy as np
import subprocess
import argparse

def video_perceptual_hash(video_path, hash_size=8, frames_sample=10):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_indices = np.linspace(0, total_frames-1, frames_sample, dtype=int)
    frame_hashes = []

    for frame_index in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = cap.read()

        if not ret:
            continue

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        pil_img = Image.fromarray(gray_frame)
        h = imagehash.phash(pil_img, hash_size=hash_size)
        frame_hashes.append(h)

    cap.release()
    video_hash = ''.join(map(str, frame_hashes))
    return video_hash

def compare_hashes(hash1, hash2):
    return sum(1 for a, b in zip(hash1, hash2) if a != b)

def reencode_video(input_file, output_file, resolution):
    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-vf', f"scale={resolution}",
        '-c:a', 'copy',
        output_file
    ]
    subprocess.run(cmd)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Video tools for fingerprinting and re-encoding.")
    parser.add_argument('action', choices=['hash', 'compare', 'reencode'], help="Action to perform.")
    parser.add_argument('-i', '--input', required=True, help="Input video file.")
    parser.add_argument('-o', '--output', help="Output video file (used for re-encoding).")
    parser.add_argument('-s', '--second_input', help="Second input video file (used for comparison).")
    parser.add_argument('-r', '--resolution', default="640x360", help="Resolution for re-encoding (default: 640x360).")

    args = parser.parse_args()

    if args.action == 'hash':
        print(video_perceptual_hash(args.input))

    elif args.action == 'compare':
        if not args.second_input:
            print("Please provide a second video for comparison using the -s or --second_input option.")
        else:
            hash1 = video_perceptual_hash(args.input)
            hash2 = video_perceptual_hash(args.second_input)
            difference = compare_hashes(hash1, hash2)
            print(f"Difference between video hashes: {difference}")

    elif args.action == 'reencode':
        if not args.output:
            print("Please provide an output file name using the -o or --output option.")
        else:
            reencode_video(args.input, args.output, args.resolution)
