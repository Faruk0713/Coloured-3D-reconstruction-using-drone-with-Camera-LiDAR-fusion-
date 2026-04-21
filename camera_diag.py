# Save as ~/cam_debug.py and run: python3 ~/cam_debug.py
import numpy as np

# Your static transform
T_CAM = np.array([
    [ 0.000, -0.259,  0.966,  0.050],
    [-1.000,  0.000,  0.000,  0.000],
    [ 0.000, -0.966, -0.259, -0.038],
    [ 0.000,  0.000,  0.000,  1.000],
], dtype=np.float64)

FX, FY = 1696.8, 1696.8
CX, CY = 960.5, 540.5
IMG_W, IMG_H = 1920, 1080

# Simulate a wall 2m in front of robot at various heights
print("=== Simulated wall points (robot facing +X) ===")
test_points = [
    [2.0,  0.0,  0.0],   # wall dead ahead, ground level
    [2.0,  0.0,  0.3],   # wall ahead, LiDAR height
    [2.0,  0.5,  0.3],   # wall ahead, slightly right
    [2.0, -0.5,  0.3],   # wall ahead, slightly left
    [2.0,  0.0,  0.6],   # wall ahead, higher
    [2.0,  0.0, -0.2],   # wall ahead, lower
    [0.0,  2.0,  0.3],   # wall to the LEFT (+Y)
    [0.0, -2.0,  0.3],   # wall to the RIGHT (-Y)
]

for pt in test_points:
    p = np.array([pt[0], pt[1], pt[2], 1.0])
    pc = T_CAM @ p
    print(f"\nLiDAR pt {pt} -> cam frame {pc[:3].round(3)}")
    if pc[2] <= 0:
        print(f"  BEHIND camera (Z={pc[2]:.3f}) -- will be GREY")
        continue
    u = FX * pc[0] / pc[2] + CX
    v = FY * pc[1] / pc[2] + CY
    in_img = 0 <= u < IMG_W and 0 <= v < IMG_H
    print(f"  u={u:.1f}, v={v:.1f}  in_image={in_img}  "
          f"({'OK' if in_img else 'OUT OF FRAME -- GREY'})")