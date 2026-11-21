import heapq
import itertools
import random
from collections import deque

import pygame

CELL_SIZE = 30
COLS = 15
ROWS = 15
MAZE_WIDTH = COLS * CELL_SIZE
MAZE_HEIGHT = ROWS * CELL_SIZE
GAP = 40
PANELS = 3
INFO_HEIGHT = 90
WIDTH = MAZE_WIDTH * PANELS + GAP * (PANELS - 1)
HEIGHT = MAZE_HEIGHT + INFO_HEIGHT

BG_COLOR = (20, 20, 30)
WALL_COLOR = (230, 230, 230)
VISITED_COLOR = (40, 60, 90)
CURRENT_COLOR = (255, 180, 0)
SEARCH_COLOR = (90, 40, 120)
PATH_COLOR = (0, 200, 120)
TEXT_COLOR = (230, 230, 230)
WIN_COLOR = (255, 215, 0)


class Cell:
    def __init__(self, col, row):
        self.col = col
        self.row = row
        self.walls = {"top": True, "right": True, "bottom": True, "left": True}
        self.visited = False

    def fill(self, screen, color, offset_x=0, margin=0):
        x = offset_x + self.col * CELL_SIZE
        y = self.row * CELL_SIZE
        pygame.draw.rect(
            screen,
            color,
            (x + margin, y + margin, CELL_SIZE - 2 * margin, CELL_SIZE - 2 * margin),
        )

    def draw_walls(self, screen, offset_x=0):
        x = offset_x + self.col * CELL_SIZE
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


class Solver:
    name = "Solver"

    def __init__(self, grid, start, end):
        self.grid = grid
        self.start = start
        self.end = end
        self.frontier = deque([start])
        self.came_from = {start: None}
        self.explored = set()
        self.path = []
        self.steps = 0
        self.done = False

    def take(self):
        raise NotImplementedError

    def consider(self, neighbor, current):
        if neighbor not in self.came_from:
            self.came_from[neighbor] = current
            self.frontier.append(neighbor)

    def step(self):
        if self.done:
            return
        if not self.frontier:
            self.done = True  # no path found
            return

        current = self.take()
        if current is None:
            self.done = True
            return
        self.steps += 1
        self.explored.add(current)

        if current is self.end:
            self.path = self.build_path()
            self.done = True
            return

        for neighbor in get_open_neighbors(self.grid, current):
            if neighbor not in self.explored:
                self.consider(neighbor, current)

    def build_path(self):
        path = []
        cell = self.end
        while cell is not None:
            path.append(cell)
            cell = self.came_from[cell]
        path.reverse()
        return path


class DFSSolver(Solver):
    name = "DFS"

    def take(self):
        return self.frontier.pop()  # newest cell (stack)


class BFSSolver(Solver):
    name = "BFS"

    def take(self):
        return self.frontier.popleft()  # oldest cell (queue)


class AStarSolver(Solver):
    name = "A*"

    def __init__(self, grid, start, end):
        super().__init__(grid, start, end)
        self.counter = itertools.count()  # tie-breaker so cells are never compared
        self.g = {start: 0}
        self.frontier = [(self.heuristic(start), next(self.counter), start)]

    def heuristic(self, cell):
        return abs(cell.col - self.end.col) + abs(cell.row - self.end.row)

    def take(self):
        while self.frontier:
            _, _, cell = heapq.heappop(self.frontier)
            if cell not in self.explored:
                return cell
        return None

    def consider(self, neighbor, current):
        new_g = self.g[current] + 1
        if new_g < self.g.get(neighbor, float("inf")):
            self.g[neighbor] = new_g
            self.came_from[neighbor] = current
            f = new_g + self.heuristic(neighbor)
            heapq.heappush(self.frontier, (f, next(self.counter), neighbor))


def new_maze():
    grid = create_grid()
    start = grid[0][0]
    start.visited = True
    grid[0][0].walls["top"] = False  # entrance
    grid[ROWS - 1][COLS - 1].walls["bottom"] = False  # exit
    stack = [start]
    return grid, stack


def draw_maze(screen, grid, solver, stack, offset_x):
    for row in grid:
        for cell in row:
            if cell.visited:
                cell.fill(screen, VISITED_COLOR, offset_x)
    if solver:
        for cell in solver.explored:
            cell.fill(screen, SEARCH_COLOR, offset_x)
        for cell in solver.path:
            cell.fill(screen, PATH_COLOR, offset_x, margin=8)
    for row in grid:
        for cell in row:
            cell.draw_walls(screen, offset_x)
    if stack:
        stack[-1].fill(screen, CURRENT_COLOR, offset_x, margin=4)


def draw_stats(screen, font, solver, offset_x, winner):
    if solver is None:
        lines = ["Generating maze..."]
        color = TEXT_COLOR
    else:
        status = "done" if solver.done else "searching..."
        lines = [
            f"{solver.name} - {status}",
            f"Cells explored: {len(solver.explored)}",
            f"Path length: {len(solver.path) if solver.path else '-'}",
        ]
        color = WIN_COLOR if solver is winner else TEXT_COLOR
        if solver is winner:
            lines[0] += "  - finished first!"

    y = MAZE_HEIGHT + 10
    for line in lines:
        screen.blit(font.render(line, True, color), (offset_x + 5, y))
        y += 24


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH + 1, HEIGHT + 1))
    pygame.display.set_caption("Maze Solver Race - press R for a new maze")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 26)

    solver_classes = [DFSSolver, BFSSolver, AStarSolver]
    offsets = [i * (MAZE_WIDTH + GAP) for i in range(PANELS)]

    grid, stack = new_maze()
    solvers = []
    winner = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                grid, stack = new_maze()
                solvers = []
                winner = None

        # 1. Generate, then 2. race the solvers
        if stack:
            generation_step(grid, stack)
        elif not solvers:
            start = grid[0][0]
            end = grid[ROWS - 1][COLS - 1]
            solvers = [cls(grid, start, end) for cls in solver_classes]
        else:
            for solver in solvers:
                solver.step()
                if solver.done and solver.path and winner is None:
                    winner = solver

        # Draw
        screen.fill(BG_COLOR)
        for i, offset_x in enumerate(offsets):
            solver = solvers[i] if solvers else None
            draw_maze(screen, grid, solver, stack, offset_x)
            draw_stats(screen, font, solver, offset_x, winner)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
