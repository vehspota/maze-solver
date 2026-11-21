import random

import pygame

CELL_SIZE = 40
COLS = 15
ROWS = 15
WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE

BG_COLOR = (20, 20, 30)
WALL_COLOR = (230, 230, 230)
VISITED_COLOR = (40, 60, 90)
CURRENT_COLOR = (255, 180, 0)
SEARCH_COLOR = (90, 40, 120)
PATH_COLOR = (0, 200, 120)


class Cell:
    def __init__(self, col, row):
        self.col = col
        self.row = row
        self.walls = {"top": True, "right": True, "bottom": True, "left": True}
        self.visited = False

    def fill(self, screen, color, margin=0):
        x = self.col * CELL_SIZE
        y = self.row * CELL_SIZE
        pygame.draw.rect(
            screen,
            color,
            (x + margin, y + margin, CELL_SIZE - 2 * margin, CELL_SIZE - 2 * margin),
        )

    def draw_walls(self, screen):
        x = self.col * CELL_SIZE
        y = self.row * CELL_SIZE
        if self.walls["top"]:
            pygame.draw.line(screen, WALL_COLOR, (x, y), (x + CELL_SIZE, y), 2)
        if self.walls["right"]:
            pygame.draw.line(screen, WALL_COLOR, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE), 2)
        if self.walls["bottom"]:
            pygame.draw.line(screen, WALL_COLOR, (x, y + CELL_SIZE), (x + CELL_SIZE, y + CELL_SIZE), 2)
        if self.walls["left"]:
            pygame.draw.line(screen, WALL_COLOR, (x, y), (x, y + CELL_SIZE), 2)


def create_grid():
    return [[Cell(col, row) for col in range(COLS)] for row in range(ROWS)]


def get_unvisited_neighbors(grid, cell):
    neighbors = []
    directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # up, right, down, left
    for dc, dr in directions:
        col = cell.col + dc
        row = cell.row + dr
        if 0 <= col < COLS and 0 <= row < ROWS:
            neighbor = grid[row][col]
            if not neighbor.visited:
                neighbors.append(neighbor)
    return neighbors


def get_open_neighbors(grid, cell):
    """Neighbors you can walk to (no wall in between)."""
    neighbors = []
    if not cell.walls["top"] and cell.row > 0:
        neighbors.append(grid[cell.row - 1][cell.col])
    if not cell.walls["right"] and cell.col < COLS - 1:
        neighbors.append(grid[cell.row][cell.col + 1])
    if not cell.walls["bottom"] and cell.row < ROWS - 1:
        neighbors.append(grid[cell.row + 1][cell.col])
    if not cell.walls["left"] and cell.col > 0:
        neighbors.append(grid[cell.row][cell.col - 1])
    return neighbors


def remove_walls(a, b):
    dc = b.col - a.col
    dr = b.row - a.row
    if dc == 1:
        a.walls["right"] = False
        b.walls["left"] = False
    elif dc == -1:
        a.walls["left"] = False
        b.walls["right"] = False
    elif dr == 1:
        a.walls["bottom"] = False
        b.walls["top"] = False
    elif dr == -1:
        a.walls["top"] = False
        b.walls["bottom"] = False


def generation_step(grid, stack):
    current = stack[-1]
    neighbors = get_unvisited_neighbors(grid, current)
    if neighbors:
        next_cell = random.choice(neighbors)
        remove_walls(current, next_cell)
        next_cell.visited = True
        stack.append(next_cell)
    else:
        stack.pop()


class DFSSolver:
    name = "DFS"

    def __init__(self, grid, start, end):
        self.grid = grid
        self.end = end
        self.frontier = [start]  # stack: last in, first out
        self.came_from = {start: None}
        self.explored = set()
        self.path = []
        self.done = False

    def step(self):
        if self.done:
            return
        if not self.frontier:
            self.done = True  # no path found
            return

        current = self.frontier.pop()
        if current in self.explored:
            return
        self.explored.add(current)

        if current is self.end:
            self.path = self.build_path()
            self.done = True
            return

        for neighbor in get_open_neighbors(self.grid, current):
            if neighbor not in self.explored:
                self.came_from[neighbor] = current
                self.frontier.append(neighbor)

    def build_path(self):
        path = []
        cell = self.end
        while cell is not None:
            path.append(cell)
            cell = self.came_from[cell]
        path.reverse()
        return path


def new_maze():
    grid = create_grid()
    start = grid[0][0]
    start.visited = True
    grid[0][0].walls["top"] = False  # entrance
    grid[ROWS - 1][COLS - 1].walls["bottom"] = False  # exit
    stack = [start]
    return grid, stack


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH + 1, HEIGHT + 1))
    pygame.display.set_caption("Maze Solver - press R for a new maze")
    clock = pygame.time.Clock()

    grid, stack = new_maze()
    solver = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                grid, stack = new_maze()
                solver = None

        # 1. Generate, then 2. solve
        if stack:
            generation_step(grid, stack)
        elif solver is None:
            solver = DFSSolver(grid, grid[0][0], grid[ROWS - 1][COLS - 1])
        else:
            solver.step()

        # Draw
        screen.fill(BG_COLOR)
        for row in grid:
            for cell in row:
                if cell.visited:
                    cell.fill(screen, VISITED_COLOR)
        if solver:
            for cell in solver.explored:
                cell.fill(screen, SEARCH_COLOR)
            for cell in solver.path:
                cell.fill(screen, PATH_COLOR, margin=10)
        for row in grid:
            for cell in row:
                cell.draw_walls(screen)
        if stack:
            stack[-1].fill(screen, CURRENT_COLOR, margin=4)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
