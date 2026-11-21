import pygame

CELL_SIZE = 40
COLS = 15
ROWS = 15
WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE

BG_COLOR = (20, 20, 30)
WALL_COLOR = (230, 230, 230)


class Cell:
    def __init__(self, col, row):
        self.col = col
        self.row = row
        self.walls = {"top": True, "right": True, "bottom": True, "left": True}
        self.visited = False

    def draw(self, screen):
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


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH + 1, HEIGHT + 1))
    pygame.display.set_caption("Maze Solver")
    clock = pygame.time.Clock()

    grid = create_grid()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BG_COLOR)
        for row in grid:
            for cell in row:
                cell.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
