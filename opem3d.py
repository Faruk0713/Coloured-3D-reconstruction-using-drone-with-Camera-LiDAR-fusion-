import open3d as o3d
import numpy as np

pcd = o3d.io.read_point_cloud('/home/hailhydra/colored_map.pcd')
print(f"Points: {len(pcd.points)}")
print(f"Has colors: {pcd.has_colors()}")
o3d.visualization.draw_geometries([pcd])