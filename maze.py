import pygame
import math
from queue import PriorityQueue
from random import randrange

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))

RED = (128, 65, 70)
GREEN = (102, 141, 58)
BLUE = (77, 132, 184)
YELLOW = (209, 198, 92)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (84, 69, 150)
ORANGE = (150, 122, 69)
GREY = (69, 69, 77)
TURQUOISE = (19, 175, 160)


class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbours = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def close(self):
        self.color = RED

    def open(self):
        self.color = GREEN

    def block(self):
        self.color = BLACK

    def start(self):
        self.color = ORANGE

    def end(self):
        self.color = TURQUOISE

    def path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbours(self, grid):
        self.neighbours = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():  # DOWN
            self.neighbours.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # UP
            self.neighbours.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():  # RIGHT
            self.neighbours.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # LEFT
            self.neighbours.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False


def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.path()
        draw()


def algorithm(draw, grid, start, end):
    count = 0
    neighbour_count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = g_score.copy()
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.end()
            start.start()
            print(f'[NEIGHBOURS FUCKED::] {neighbour_count}')
            neighbour_count = 0
            return True

        for neighbour in current.neighbours:
            temp_g_score = g_score[current] + 1
            neighbour_count += 1
            if temp_g_score < g_score[neighbour]:
                came_from[neighbour] = current
                g_score[neighbour] = temp_g_score
                f_score[neighbour] = temp_g_score + h(neighbour.get_pos(), end.get_pos())
                if neighbour not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbour], count, neighbour))
                    open_set_hash.add(neighbour)
                    neighbour.open()

        draw()

        if current != start:
            current.close()

    return False


def make_grid(rows, width):
    grid = []
    # gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, (width // rows), rows)
            grid[i].append(spot)

    return grid


def walls(grid):
    for row in grid:
        for spot in row:
            if spot.row == 0 or spot.row == len(grid) - 1 or spot.col == 0 or spot.col == len(grid) - 1:
                spot.block()
    return grid


def generate(rows, width):
    grid = make_grid(rows, width)

    grid = walls(grid)
    ent = addEntrance(grid)
    addInnerWalls(True, 1, len(grid) - 2, 1, len(grid) - 2, ent, grid)
    return grid


def addEntrance(grid):
    x = randomNumber(1, len(grid) - 1)
    grid[len(grid) - 1][x].start()
    return x


def addInnerWalls(h, minX, maxX, minY, maxY, gate, grid):
    if h:
        if maxX - minX < 2:
            return

        y = math.floor(randomNumber(minY, maxY)/2)*2
        addHWall(minX, maxX, y, grid)

        addInnerWalls(not h, minX, maxX, minY, y - 1, gate, grid)
        addInnerWalls(not h, minX, maxX, y + 1, maxY, gate, grid)
    else:
        if maxY - minY < 2:
            return

        x = math.floor(randomNumber(minX, maxX)/2)*2
        addVWall(minY, maxY, x, grid)

        addInnerWalls(not h, minX, x - 1, minY, maxY, gate, grid)
        addInnerWalls(not h, x + 1, maxX, minY, maxY, gate, grid)


def addHWall(minX, maxX, y, grid):
    hole = math.floor(randomNumber(minX, maxX)/2)*2 + 1

    for i in range(minX, maxX):
        if i == hole:
            grid[y][i].reset()
        else:
            grid[y][i].block()


def addVWall(minY, maxY, x, grid):
    hole = math.floor(randomNumber(minY, maxY)/2)*2 + 1

    for i in range(minY, maxY + 1):
        if i == hole:
            grid[i][x].reset()
        else:
            grid[i][x].block()


def randomNumber(min, max):
    return randrange(min, max)


def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
    # TODO: catch pygame.error display Surface quit
    win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()


def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos
    row = y // gap
    col = x // gap

    return row, col


def main(win, width):
    ROWS = 53
    grid = generate(ROWS, width)
    start = None
    end = None

    run = True
    clock = pygame.time.Clock()

    while run:
        clock.tick(60)
        draw(win, grid, ROWS, width)
        draw_grid(win, ROWS, width)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                if not start and (spot != end or spot.is_barrier()):
                    start = spot
                    start.start()
                elif not end and spot != start:
                    end = spot
                    end.end()
                elif spot != end and spot != start:
                    spot.block()

            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
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
                            spot.update_neighbours(grid)

                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_c:  # key c to reset the board
                    start = None
                    end = None
                    grid = generate(ROWS, width)

                if event.key == pygame.K_ESCAPE:
                    pygame.display.quit()
                    pygame.quit()

    pygame.quit()


main(WIN, WIDTH)
