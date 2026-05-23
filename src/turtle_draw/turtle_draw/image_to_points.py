from pathlib import Path
import cv2
import numpy as np
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent
IMAGE_PATH = BASE_DIR / "images" / "dog.png"
POINTS_PATH = BASE_DIR / "points.txt"

image = cv2.imread(str(IMAGE_PATH))

if image is None:
    print("Erro ao carregar imagem")
    exit()

image = image[:, :, ::-1]

height, width, _ = image.shape

# =====================================
# GRAYSCALE MANUAL

gray = np.zeros((height, width), dtype=np.float32)

for y in range(height):
    for x in range(width):

        r = image[y, x, 0]
        g = image[y, x, 1]
        b = image[y, x, 2]

        gray[y, x] = (
            0.299 * r +
            0.587 * g +
            0.114 * b
        )

# =====================================
# BLUR MANUAL 

kernel = np.array([
    [1, 2, 1],
    [2, 4, 2],
    [1, 2, 1]
], dtype=np.float32) / 16

blur = np.zeros_like(gray)

for y in range(1, height - 1):
    for x in range(1, width - 1):

        region = gray[y-1:y+2, x-1:x+2]

        blur[y, x] = np.sum(region * kernel)

# =====================================
# SOBEL

sobel_x = np.array([
    [-1, 0, 1],
    [-2, 0, 2],
    [-1, 0, 1]
], dtype=np.float32)

sobel_y = np.array([
    [-1, -2, -1],
    [0, 0, 0],
    [1, 2, 1]
], dtype=np.float32)

edges = np.zeros_like(blur)

for y in range(1, height - 1):
    for x in range(1, width - 1):

        region = blur[y-1:y+2, x-1:x+2]

        gx = np.sum(region * sobel_x)
        gy = np.sum(region * sobel_y)

        magnitude = np.sqrt(gx**2 + gy**2)

        edges[y, x] = magnitude

# =====================================
# THRESHOLD

threshold = 120

binary = np.zeros_like(edges, dtype=np.uint8)

binary[edges > threshold] = 255

# =====================================
# REMOVER BORDA EXTERNA

margin = 15

binary[:margin, :] = 0
binary[-margin:, :] = 0
binary[:, :margin] = 0
binary[:, -margin:] = 0

# =====================================
# DFS CONTÍNUO

visited = np.zeros_like(binary, dtype=bool)

paths = []

step = 2

# mantém proporção original
scale = 10.0 / max(width, height)

draw_width = width * scale
draw_height = height * scale

offset_x = (11 - draw_width) / 2
offset_y = (11 - draw_height) / 2

def to_turtle(px, py):

    tx = offset_x + px * scale

    ty = 11 - (offset_y + py * scale)

    return tx, ty


def dfs(start_x, start_y):

    stack = [(start_x, start_y)]

    component = []

    visited[start_y, start_x] = True

    while stack:

        cx, cy = stack.pop()

        component.append((cx, cy))

        for dy in [-step, 0, step]:
            for dx in [-step, 0, step]:

                if dx == 0 and dy == 0:
                    continue

                nx = cx + dx
                ny = cy + dy

                if 0 <= nx < width and 0 <= ny < height:

                    if (
                        binary[ny, nx] == 255
                        and not visited[ny, nx]
                    ):

                        visited[ny, nx] = True
                        stack.append((nx, ny))

    return component


for y in range(0, height, step):
    for x in range(0, width, step):

        if binary[y, x] != 255:
            continue

        if visited[y, x]:
            continue

        component = dfs(x, y)

        if len(component) < 30:
            continue

        first = True

        for px, py in component:

            tx, ty = to_turtle(px, py)

            if first:
                paths.append((tx, ty, 0))
                first = False
            else:
                paths.append((tx, ty, 1))

# =====================================
# SALVAR
# =====================================

with open(POINTS_PATH, "w") as f:

    for x, y, pen in paths:

        f.write(f"{x},{y},{pen}\n")

print(f"{len(paths)} pontos salvos")

# =====================================
# MOSTRAR
# =====================================

plt.imshow(binary, cmap="gray")
plt.title("Bordas Detectadas")
plt.show()