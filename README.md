# Palette — k-means image painter

Turns a photo into something closer to a painting by reducing it to a small
set of dominant colors (k-means clustering) and optionally adding
edge-preserving smoothing and brush-stroke texture on top.

The project has two independent implementations of the same idea:

| | Script | Runs where | Best for |
|---|---|---|---|
| 1 | [`script.py`](#python-script-scriptpy) | Your machine, via Python | Batch processing, full-resolution output, exact control via flags |
| 2 | [`painter.html`](#web-app-painterhtml) | Any browser, no install | Quick previews, dragging sliders to explore looks interactively |

They're not code-shared — the web version is a from-scratch JS port of the
same three-step pipeline — so results between the two will be similar but
not pixel-identical.

---

## How it works

Both versions run the same three optional/required steps, in this order:

1. **Bilateral smoothing** *(optional, off by default)* — blurs flat,
   noisy areas (like grass or skin texture) while preserving strong edges,
   so the color regions that come out of step 2 are cleaner and less
   speckled.
2. **K-means color quantization** *(the core step)* — treats every pixel as
   a point in RGB space, finds `k` cluster centers, and repaints the image
   using only those `k` colors. Lower `k` = fewer colors = more flattened
   and painting-like. Higher `k` = closer to the original photo.
3. **Brush-stroke texture** *(optional, off by default)* — adds a painted
   texture on top of the flattened color regions so edges look brushed
   rather than vector-cut.

---

## Python script (`script.py`)

### Requirements

```bash
pip install numpy pillow scikit-learn opencv-python-headless
```

### Basic usage

```bash
python3 script.py input.jpg output.jpg 8
```

- `input.jpg` — path to your source image
- `output.jpg` — path to save the result
- `8` — number of colors (`k`); optional, defaults to `8` if omitted

### Adding smoothing and brush texture

```bash
python3 script.py input.jpg output.jpg 8 --smooth --brush
```

### Full flag reference

| Flag | Default | Description |
|---|---|---|
| `k` (positional) | `8` | Number of colors to reduce the image to |
| `--smooth` | off | Enable bilateral smoothing before quantizing |
| `--smooth-strength` | `75` | Smoothing strength — higher = smoother/more painterly, but softer detail. Try 30–150 |
| `--brush` | off | Enable brush-stroke texture after quantizing |
| `--brush-radius` | `6` | Stroke size — higher = bigger, coarser strokes. Try 3–15 |
| `--brush-sigma` | `60` | Color blending within strokes — higher = more blended. Try 20–100 |

Example with custom tuning:

```bash
python3 script.py input.jpg output.jpg 8 \
  --smooth --smooth-strength 120 \
  --brush --brush-radius 10 --brush-sigma 40
```

### Notes

- Processes the image at full resolution — large images (multi-megapixel
  photos) can take up to ~30 seconds, mostly spent in the k-means fit step.
- `--brush` uses OpenCV's `cv2.stylization`, which isn't available in a
  browser — that's why the web version uses a different (oil-paint style)
  algorithm for its brush effect. Expect similar but not identical results
  between the two.

---

## Web app (`painter.html`)

A single self-contained HTML file — no build step, no server, no
dependencies to install. Open it directly in a browser, or host it as a
static file (e.g. on Firebase Hosting, GitHub Pages, etc.). All processing
happens client-side on `<canvas>`; no image data is ever uploaded anywhere.

### Usage

1. Open `painter.html` in a browser.
2. Load an image by dragging it onto the canvas, clicking to browse, or
   pasting (⌘V / Ctrl+V) an image from your clipboard.
3. Adjust sliders — the preview updates automatically (debounced ~220ms
   after you stop dragging a slider).
4. Click **Download painting** to save the result as a PNG.
5. Click the **×** on the image, or **Load a different image**, to start
   over.

### Controls

| Control | Range | Description |
|---|---|---|
| **Color quantization** toggle | on by default | Turns k-means color reduction on/off, so you can preview smoothing/brush effects against the full original color range |
| **Color count (k)** | 2–32 | Number of colors kept when quantization is on |
| **Bilateral smoothing** toggle | off by default | Enables edge-preserving smoothing before quantizing |
| **Strength** | 10–150 | Smoothing intensity |
| **Brush-stroke texture** toggle | off by default | Enables painted texture after quantizing |
| **Stroke size** | 1–10 | Neighborhood radius used by the brush effect — bigger = coarser strokes |
| **Detail** | 4–30 | Number of intensity bins used by the brush effect — lower = blobbier, higher = finer gradients |

### Notes / limitations

- Images are downscaled to a maximum edge of 560px before processing, so
  the sliders stay responsive (all three algorithms are hand-written JS
  running synchronously on the main thread — no GPU acceleration). The
  downloaded PNG reflects this same working resolution, not the original
  file's full size.
- The brush effect is a from-scratch JS implementation of the classic
  "oil painting" filter (most-frequent intensity bin in a local
  neighborhood) — a different algorithm from the Python version's
  `cv2.stylization`, chosen to achieve a similar look without needing
  OpenCV in the browser.
- The palette panel shows the actual k-means cluster colors as paint
  dabs, sorted dark → light, so you can see exactly which colors the
  current image was reduced to.
- The only external network request the page makes is loading Google
  Fonts (Fraunces, Inter, JetBrains Mono). Everything else — including all
  image processing — runs locally in the browser.

---

## File structure

```
script.py      Python CLI script
painter.html     Self-contained web app
README.md        This file
```
