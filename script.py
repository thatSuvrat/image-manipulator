import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
import cv2
import argparse

def bilateral_smooth(arr, d=9, sigma_color=75, sigma_space=75):
    """Smooth flat areas while preserving strong edges (pre-quantize step)."""
    return cv2.bilateralFilter(arr, d, sigma_color, sigma_space)

def add_brush_strokes(arr, radius=6, sigma=60):
    """Give quantized color regions a painted/stroked texture (post-quantize step)."""
    # cv2.stylization softens + adds a painterly stroke feel while respecting edges
    return cv2.stylization(arr, sigma_s=radius * 10, sigma_r=sigma / 100.0)

def quantize_image(input_path, output_path, k=8, smooth=True, brush=False,
                    smooth_strength=75, brush_radius=6, brush_sigma=60):
    img = Image.open(input_path).convert("RGB")
    arr = np.array(img)
    h, w, c = arr.shape

    if smooth:
        print(f"Applying bilateral smoothing (strength={smooth_strength})...")
        arr = bilateral_smooth(arr, sigma_color=smooth_strength, sigma_space=smooth_strength)

    pixels = arr.reshape(-1, 3).astype(np.float32)

    print(f"Running k-means with k={k} on {pixels.shape[0]} pixels...")
    kmeans = KMeans(n_clusters=k, n_init=4, random_state=42)
    labels = kmeans.fit_predict(pixels)
    centers = kmeans.cluster_centers_.astype(np.uint8)

    new_pixels = centers[labels]
    new_arr = new_pixels.reshape(h, w, 3)

    if brush:
        print(f"Adding brush-stroke texture (radius={brush_radius}, sigma={brush_sigma})...")
        new_arr = add_brush_strokes(new_arr, radius=brush_radius, sigma=brush_sigma)

    out_img = Image.fromarray(new_arr, mode="RGB")
    out_img.save(output_path)
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="K-means color quantization with optional painterly effects.")
    parser.add_argument("input_path", help="Path to input image")
    parser.add_argument("output_path", help="Path to save output image")
    parser.add_argument("k", type=int, nargs="?", default=8, help="Number of colors (default: 8)")
    parser.add_argument("--smooth", action="store_true", help="Apply bilateral smoothing before quantizing")
    parser.add_argument("--smooth-strength", type=int, default=75,
                         help="Bilateral smoothing strength, higher = smoother/more painterly (default: 75)")
    parser.add_argument("--brush", action="store_true", help="Apply brush-stroke texture after quantizing")
    parser.add_argument("--brush-radius", type=int, default=6,
                         help="Brush stroke size, higher = coarser strokes (default: 6)")
    parser.add_argument("--brush-sigma", type=int, default=60,
                         help="Brush stroke color blending, higher = more blended (default: 60)")
    args = parser.parse_args()

    quantize_image(
        args.input_path, args.output_path, args.k,
        smooth=args.smooth, brush=args.brush,
        smooth_strength=args.smooth_strength,
        brush_radius=args.brush_radius, brush_sigma=args.brush_sigma,
    )