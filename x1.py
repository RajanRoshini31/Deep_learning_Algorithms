import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Constants
GRID_SIZE = 4
CELL_SIZE = 100
SCREEN_WIDTH = GRID_SIZE * CELL_SIZE
SCREEN_HEIGHT = GRID_SIZE * CELL_SIZE
FPS = 60
COLORS = {
    "empty": (255, 255, 255),
    "player": (0, 0, 255),
    "grid": (200, 200, 200),
    "breeze": (173, 216, 230),  # Light blue
    "stench": (139, 69, 19),    # Brown
    "dual_hint": (169, 169, 169),  # Grey
    "visited": (211, 211, 211), # Light gray
    "hidden": (169, 169, 169),  # Dark gray
    "gold": (255, 255, 0),      # Yellow
}

# Initialize pygame screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Wumpus Game with Advanced Hints")
clock = pygame.time.Clock()

# Grid setup
grid = [[' ' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
hints = [[' ' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
visited = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
player_position = [0, 0]


def draw_grid():
    """Draw the grid, objects, and hints."""
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x, y = col * CELL_SIZE, row * CELL_SIZE

            # Determine cell color based on hints and visited status
            if visited[row][col]:
                if hints[row][col] == 'B' and hints[row][col] == 'S':  # Breeze + Stench
                    color = COLORS["dual_hint"]
                elif hints[row][col] == 'B':  # Breeze
                    color = COLORS["breeze"]
                elif hints[row][col] == 'S':  # Stench
                    color = COLORS["stench"]
                elif grid[row][col] == 'G':  # Gold found
                    color = COLORS["gold"]
                else:
                    color = COLORS["visited"]
            else:
                color = COLORS["hidden"]

            pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, COLORS["grid"], (x, y, CELL_SIZE, CELL_SIZE), 1)

            # Draw player
            if grid[row][col] == 'A':
                pygame.draw.circle(screen, COLORS["player"], (x + CELL_SIZE // 2, y + CELL_SIZE // 2), CELL_SIZE // 3)


def place_objects():
    """Place Wumpus, pits, and gold randomly on the grid, ensuring the starting area is safe."""
    objects = {'W': 1, 'G': 1, 'P': 3}  # Wumpus, Gold, Pits
    for obj, count in objects.items():
        for _ in range(count):
            while True:
                x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
                # Ensure the starting position and its direct neighbors are safe
                if grid[x][y] == ' ' and (x, y) not in safe_area:
                    grid[x][y] = obj
                    break


def initialize_player():
    """Place the player at a safe starting position."""
    global player_position, safe_area
    while True:
        x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
        if grid[x][y] == ' ':
            grid[x][y] = 'A'
            player_position = [x, y]
            # Mark vertical and horizontal neighbors as safe
            safe_area = {(x, y)}
            if x > 0:
                safe_area.add((x - 1, y))
            if x < GRID_SIZE - 1:
                safe_area.add((x + 1, y))
            if y > 0:
                safe_area.add((x, y - 1))
            if y < GRID_SIZE - 1:
                safe_area.add((x, y + 1))
            break


def generate_hints():
    """Generate hints for nearby hazards."""
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if grid[row][col] == 'P':  # Pits cause "breeze"
                for dx, dy in directions:
                    nx, ny = row + dx, col + dy
                    if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                        if hints[nx][ny] == 'S':  # Combine hints
                            hints[nx][ny] = 'B+S'
                        elif hints[nx][ny] != 'B+S':  # Ensure no overwriting
                            hints[nx][ny] = 'B'
            elif grid[row][col] == 'W':  # Wumpus causes "stench"
                for dx, dy in directions:
                    nx, ny = row + dx, col + dy
                    if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                        if hints[nx][ny] == 'B':  # Combine hints
                            hints[nx][ny] = 'B+S'
                        elif hints[nx][ny] != 'B+S':  # Ensure no overwriting
                            hints[nx][ny] = 'S'


def move_player(direction):
    """Move the player and mark visited cells."""
    global player_position
    x, y = player_position
    grid[x][y] = ' '  # Clear the current position

    if direction == "up" and x > 0:
        x -= 1
    elif direction == "down" and x < GRID_SIZE - 1:
        x += 1
    elif direction == "left" and y > 0:
        y -= 1
    elif direction == "right" and y < GRID_SIZE - 1:
        y += 1

    # Check for hazards
    if grid[x][y] == 'W':
        print("You were eaten by the Wumpus! Game Over!")
        pygame.quit()
        sys.exit()
    elif grid[x][y] == 'P':
        print("You fell into a pit! Game Over!")
        pygame.quit()
        sys.exit()
    elif grid[x][y] == 'G':
        print("You found the gold! You Win!")
        pygame.quit()
        sys.exit()

    grid[x][y] = 'A'  # Update the new position
    player_position = [x, y]
    visited[x][y] = True  # Mark the cell as visited


def game_loop():
    """Main game loop."""
    running = True
    while running:
        screen.fill(COLORS["empty"])
        draw_grid()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    move_player("up")
                elif event.key == pygame.K_DOWN:
                    move_player("down")
                elif event.key == pygame.K_LEFT:
                    move_player("left")
                elif event.key == pygame.K_RIGHT:
                    move_player("right")

        pygame.display.flip()
        clock.tick(FPS)


# Initialize game objects
safe_area = set()
place_objects()
initialize_player()
generate_hints()

# Run the game
game_loop()
pygame.quit()
