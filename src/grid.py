
import numpy as np

FREE = 0
WALL = 1


class Grid:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.cells = np.zeros((rows, cols), dtype=int)  # ban đầu toàn ô trống

    def in_bounds(self, cell):
        r,c = cell 
        if( (r < self.rows and r >= 0 ) and (c <= self.cols and c >= 0 )):
            return True
        else: 
            return False

    def is_free(self, cell):
        """True nếu cell không phải tường."""
        r,c = cell 
        if self.cells[r,c] == WALL :
            return False 
        else:
            return True

    def neighbors(self, cell):
        """Trả về list các ô kề đi được, theo thứ tự Đông, Nam, Bắc, Tây.
        Ô kề phải nằm trong bản đồ VÀ không phải tường."""
        r,c = cell
        result = []
        for dr , dc in [(0,1),(1,0),(-1,0),(0,-1)]: 
            nb = (r+dr, c +dc)
            if self.in_bounds(nb) == True : 
                if self.is_free(nb) == True : 
                    result.append(nb) 
        return result 
       


    def add_random_walls(self, density, seed=None):
        """Biến khoảng `density` phần ô thành tường (vd 0.25 = 25%)."""
        rng = np.random.default_rng(seed)         # tạo bộ sinh số ngẫu nhiên với seed
        nums = rng.random((self.rows, self.cols)) 
        mask = nums < density 
        self.cells[mask] = WALL


if __name__ == "__main__":
    g = Grid(5, 5)
    g.cells[1, 2] = WALL
    print(g.neighbors((0, 0)))   # mong đợi: [(0, 1), (1, 0)]
    print(g.neighbors((1, 1)))   # mong đợi: [(2, 1), (0, 1), (1, 0)]
    g2 = Grid(10, 10)
    g2.add_random_walls(0.25, seed=42)
    print(g2.cells) 

