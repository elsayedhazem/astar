import pygame
import math
from queue import PriorityQueue

WINDOW_WIDTH = 400
WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_WIDTH))
pygame.display.set_caption("A* Path Finding Algorithm")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


class Spot():
    def __init__(self, row, col, width, total_rows):
        self.row = row  # ZERO INDEXED
        self.col = col  # ZERO INDEXED
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows  # ROWS == COLS

    @property
    def position(self):
        return self.row, self.col

    @property
    def is_closed(self):
        return self.color == RED

    def make_closed(self):
        self.color = RED

    @property
    def is_open(self):
        return self.color == GREEN

    def make_open(self):
        self.color = GREEN

    @property
    def is_barrier(self):
        return self.color == BLACK

    def make_barrier(self):
        self.color = BLACK

    @property
    def is_start(self):
        return self.color == ORANGE

    def make_start(self):
        self.color = ORANGE

    @property
    def is_end(self):
        return self.color == TURQUOISE

    def make_end(self):
        self.color = TURQUOISE

    def reset(self):
        self.color = WHITE

    def make_path(self):
        self.color = PURPLE

    def draw(self, window):
        pygame.draw.rect(window, self.color,
                         (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []

        # UP
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier:
            spot_above = grid[self.row - 1][self.col]
            self.neighbors.append(spot_above)

        # DOWN
        if (self.row < self.total_rows - 1) and not grid[self.row + 1][self.col].is_barrier:
            spot_below = grid[self.row + 1][self.col]
            self.neighbors.append(spot_below)

        # RIGHT
        if (self.col < self.total_rows - 1) and not grid[self.row][self.col + 1].is_barrier:
            spot_right = grid[self.row][self.col + 1]
            self.neighbors.append(spot_right)

        # LEFT
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier:
            spot_left = grid[self.row][self.col - 1]
            self.neighbors.append(spot_left)

    def __lt__(self, other):
        return False


def h(p1, p2):
    """Get manhattan distance between two points. (Heuristic function for A* algorithm)"""
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()


def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))

    came_from = {}

    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0

    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.position, end.position)

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            start.make_start()
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + \
                    h(neighbor.position, end.position)
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()


def make_spots_grid(rows, window_width):
    """
    Create 2D array of Spot objects which represents the grid of spots to be displayed.
    Example: spot = grid[spot_row][spot_col]
    """

    grid = []
    gap = window_width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):  # cols
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)

    return grid


def draw_grid(window, rows, window_width):
    """Draw grid lines for grid where n_rows == n_cols"""

    gap = window_width // rows
    for i in range(rows):
        pygame.draw.line(window, GREY, (0, i * gap), (window_width, i * gap))
        pygame.draw.line(window, GREY, (i * gap, 0), (i * gap, window_width))


def draw(window, spots_grid, rows, window_width):
    window.fill(WHITE)

    for row in spots_grid:
        for spot in row:
            spot.draw(window)

    draw_grid(window, rows, window_width)
    pygame.display.update()


def get_clicked_pos(pos, rows, window_width):
    """Get row and column for spot on which mouse coordinates lie."""

    gap = window_width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col


def main(window, window_width, rows):
    grid = make_spots_grid(rows, window_width)
    start = None
    end = None

    run = True
    while run:
        draw(window, grid, rows, window_width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if pygame.mouse.get_pressed()[0]:  # LEFT
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, rows, window_width)
                spot = grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.make_start()

                if not end and spot != start:
                    end = spot
                    end.make_end()

                elif spot != end and spot != start:
                    spot.make_barrier()

            elif pygame.mouse.get_pressed()[2]:  # RIGHT
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, rows, window_width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)

                    algorithm(lambda: draw(window, grid, rows,
                                           window_width), grid, start, end)

    pygame.quit()


if __name__ == "__main__":
    main(WINDOW, WINDOW_WIDTH, 25)
