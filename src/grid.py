"""Bản đồ lưới 2D cho bài toán tìm đường của robot.

Mỗi ô có hai thông tin:
- cells[r, c]: FREE (0) hoặc WALL (1) — robot có đi vào được hay không.
- cost[r, c] : chi phí để đi VÀO ô đó (1 = đường bằng, >1 = địa hình khó như bùn, dốc).

Thuật toán tìm đường chỉ cần gọi grid.neighbors(cell) và grid.move_cost(a, b),
nên có thể đổi kiểu bản đồ (đi chéo, địa hình) mà không phải sửa thuật toán.
"""
import math

import numpy as np

FREE = 0
WALL = 1

# Thứ tự: Đông, Nam, Bắc, Tây
DIRS_4 = [(0, 1), (1, 0), (-1, 0), (0, -1)]
# Thứ tự: Đông-Nam, Tây-Nam, Đông-Bắc, Tây-Bắc
DIRS_DIAG = [(1, 1), (1, -1), (-1, 1), (-1, -1)]


class Grid:
    def __init__(self, rows, cols, diagonal=False):
        self.rows = rows
        self.cols = cols
        self.diagonal = diagonal                              # True: cho phép đi chéo 8 hướng
        self.cells = np.zeros((rows, cols), dtype=int)        # ban đầu toàn ô trống
        self.cost = np.ones((rows, cols), dtype=float)        # ban đầu mọi ô tốn 1

    # ------------------------------------------------------------------ kiểm tra ô
    def in_bounds(self, cell):
        """True nếu cell = (r, c) nằm trong bản đồ."""
        r, c = cell
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_free(self, cell):
        """True nếu cell không phải tường."""
        r, c = cell
        return self.cells[r, c] != WALL

    # ------------------------------------------------------------------ di chuyển
    def neighbors(self, cell):
        """Trả về list các ô kề đi được.

        4 hướng (Đông, Nam, Bắc, Tây), cộng thêm 4 hướng chéo nếu diagonal=True.
        Luôn gọi in_bounds TRƯỚC is_free: numpy hiểu chỉ số -1 là hàng/cột cuối,
        nên đọc ô ngoài bản đồ sẽ không báo lỗi mà lặng lẽ đọc sai ô.
        """
        r, c = cell
        dirs = DIRS_4 + DIRS_DIAG if self.diagonal else DIRS_4
        result = []
        for dr, dc in dirs:
            nb = (r + dr, c + dc)
            if not (self.in_bounds(nb) and self.is_free(nb)):
                continue
            if dr != 0 and dc != 0:
                # Đi chéo: không cho robot "lách" qua kẽ giữa hai bức tường chạm góc
                if not (self.is_free((r + dr, c)) and self.is_free((r, c + dc))):
                    continue
            result.append(nb)
        return result

    def move_cost(self, a, b):
        """Chi phí đi từ ô a sang ô kề b.

        Bước thẳng dài 1, bước chéo dài √2; nhân với chi phí địa hình của ô đích.
        """
        diagonal_step = a[0] != b[0] and a[1] != b[1]
        step = math.sqrt(2) if diagonal_step else 1.0
        return step * float(self.cost[b])

    # ------------------------------------------------------------------ sinh bản đồ
    def add_random_walls(self, density, seed=None):
        """Biến khoảng `density` phần ô thành tường (vd 0.25 = 25%)."""
        rng = np.random.default_rng(seed)
        nums = rng.random((self.rows, self.cols))
        mask = nums < density
        self.cells[mask] = WALL

    def add_random_terrain(self, density, terrain_cost=5.0, seed=None):
        """Biến khoảng `density` phần ô trống thành địa hình khó (bùn) có chi phí `terrain_cost`."""
        rng = np.random.default_rng(seed)
        nums = rng.random((self.rows, self.cols))
        mask = (nums < density) & (self.cells != WALL)
        self.cost[mask] = terrain_cost

    def clear(self, *cells):
        """Đảm bảo các ô cho trước là ô trống, chi phí 1 (dùng cho start và goal)."""
        for r, c in cells:
            self.cells[r, c] = FREE
            self.cost[r, c] = 1.0

    @classmethod
    def random(cls, rows, cols, wall_density=0.25, terrain_density=0.0,
               terrain_cost=5.0, diagonal=False, seed=None):
        """Tạo một bản đồ ngẫu nhiên tái lập được (cùng seed → cùng bản đồ).

        Tường và địa hình dùng hai luồng số ngẫu nhiên tách riêng từ cùng một seed.
        Nếu dùng chung một seed cho cả hai, bảng số ngẫu nhiên sẽ giống hệt nhau,
        khi đó mọi ô "bùn" đều trùng vào ô tường và bị loại → bản đồ không có bùn.
        """
        wall_seed, terrain_seed = np.random.SeedSequence(seed).spawn(2)
        grid = cls(rows, cols, diagonal=diagonal)
        grid.add_random_walls(wall_density, seed=wall_seed)
        if terrain_density > 0:
            grid.add_random_terrain(terrain_density, terrain_cost, seed=terrain_seed)
        return grid


if __name__ == "__main__":
    g = Grid(5, 5)
    g.cells[1, 2] = WALL
    print(g.neighbors((0, 0)))   # mong đợi: [(0, 1), (1, 0)]
    print(g.neighbors((1, 1)))   # mong đợi: [(2, 1), (0, 1), (1, 0)]
    print(g.neighbors((0, 4)))   # mong đợi: [(1, 4), (0, 3)]

    g2 = Grid.random(10, 10, wall_density=0.25, terrain_density=0.2, seed=42)
    print(g2.cells)
    print("Số ô tường:", g2.cells.sum(), "| Số ô bùn:", int((g2.cost > 1).sum()))
