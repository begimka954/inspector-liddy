import numpy as np
import matplotlib
matplotlib.use("Agg")  # headless -- we are solving a murder, not painting
import matplotlib.pyplot as plt

class LIDARMap:
    """
    Simulated LIDAR built from bounding box centroids accumulated over time.
    Real LIDAR costs thousands of pounds. Matplotlib costs dignity.
    Inspector Liddy accepts this trade without complaint.
    """
    def __init__(self, grid_size=50):
        self.size    = grid_size
        self.grid    = np.zeros((grid_size, grid_size), dtype=np.float32)
        self.history = []

    def update(self, detections, frame_w, frame_h):
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            cx = (x1 + x2) / 2 / frame_w
            cy = (y1 + y2) / 2 / frame_h

            gx = int(np.clip(cx * (self.size - 1), 0, self.size - 1))
            gy = int(np.clip(cy * (self.size - 1), 0, self.size - 1))

            self.grid[gy, gx] += det["confidence"]
            self.history.append({"class": det["class"], "gx": gx, "gy": gy})

        # Evidence fades at 0.97 per scan. Memories fade at their own rate.
        # Carpet stains do not fade. That is a different problem entirely.
        self.grid *= 0.97

    def render(self):
        """Returns an RGB numpy array of the positional heatmap."""
        fig, ax = plt.subplots(figsize=(4, 4), facecolor="#111")
        ax.set_facecolor("#111")

        vmax = max(float(self.grid.max()), 0.1)
        ax.imshow(self.grid, cmap="YlOrRd", origin="upper", vmin=0, vmax=vmax)
        ax.set_title("LIDAR Positional Scan", color="#c8a96e", fontsize=9, pad=4)
        ax.axis("off")

        fig.tight_layout(pad=0.3)
        fig.canvas.draw()
        # tostring_rgb was removed in newer matplotlib. buffer_rgba is its unsentimental replacement.
        rgba = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8)
        w, h = fig.canvas.get_width_height()
        buf  = rgba.reshape(h, w, 4)[:, :, :3]
        plt.close(fig)
        return buf

    def hotspots(self):
        """Grid cells with activity above 70% of peak. Where things keep appearing."""
        threshold = self.grid.max() * 0.7
        return np.argwhere(self.grid >= threshold).tolist()
