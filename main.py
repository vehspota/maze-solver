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


class Cell:
    def __init__(self, col, row):
        self.col = col
        self.row = row
        self.walls = {"top": True, "right": True, "bottom": True, "left": True}
        self.visited = False

    def draw(self, screen):
        x = self.col * CELL_SIZE
        y = self.row * CELL_SIZE
        if self.visited:
            pygame.draw.rect(screen, VISITED_COLOR, (x, y, CELL_SIZE, CELL_SIZE))
        if self.walls["top"]:
            pygame.draw.line(screen, WALL_COLOR, (x, y), (x + CELL_SIZE, y), 2)
        if self.walls["right"]:
            pygame.draw.line(screen, WALL_COLOR, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE), 2)
        if self.walls["bottom"]:
            pygame.draw.line(screen, WALL_COLOR, (x, y + CELL_SIZE), (x + CELL_SIZE, y + CELL_SIZE), 2)
        if self.walls["left"]:
            pygame.draw.line(screen, WALL_COLOR, (x, y), (x, y + CELL_SIZE), 2)

    def highlight(self, screen, color):
        x = self.col * CELL_SIZE
        y = self.row * CELL_SIZE
        pygame.draw.rect(screen, color, (x + 4, y + 4, CELL_SIZE - 8, CELL_SIZE - 8))


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


def remove_walls(a, b):
    dc = b.col - a.col
    dr = b.row - a.row
    if dc == 1:  # b is to the right of a
        a.walls["right"] = False
        b.walls["left"] = False
    elif dc == -1:  # b is to the left
        a.walls["left"] = False
        b.walls["right"] = False
    elif dr == 1:  # b is below
        a.walls["bottom"] = False
        b.walls["top"] = False
    elif dr == -1:  # b is above
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
        stack.pop()  # dead end: go back


def new_maze():
    grid = create_grid()
    start = grid[0][0]
    start.visited = True
    stack = [start]
    return grid, stack


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH + 1, HEIGHT + 1))
    pygame.display.set_caption("Maze Solver - press R for a new maze")
    clock = pygame.time.Clock()

    grid, stack = new_maze()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                grid, stack = new_maze()

        if stack:
            generation_step(grid, stack)

        screen.fill(BG_COLOR)
        for row in grid:
            for cell in row:
                cell.draw(screen)
        if stack:
            stack[-1].highlight(screen, CURRENT_COLOR)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
