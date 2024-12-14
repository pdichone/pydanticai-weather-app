import pygame
import numpy as np
import random

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 10

# Compute the number of cells in the grid
cols, rows = WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE

# Initialize the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game of Life with Random Colors")

# Create grid
grid = np.random.choice([0, 1], (rows, cols), p=[0.8, 0.2])

# Colors
def random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Main loop
running = True
while running:
    screen.fill((0, 0, 0))
    new_grid = np.copy(grid)

    for y in range(rows):
        for x in range(cols):
            # Get the number of live neighbors
            neighbors = (
                grid[(y-1) % rows, (x-1) % cols] +
                grid[(y-1) % rows, x] +
                grid[(y-1) % rows, (x+1) % cols] +
                grid[y, (x-1) % cols] +
                grid[y, (x+1) % cols] +
                grid[(y+1) % rows, (x-1) % cols] +
                grid[(y+1) % rows, x] +
                grid[(y+1) % rows, (x+1) % cols]
            )

            # Apply the Game of Life rules
            if grid[y, x] == 1:
                if neighbors < 2 or neighbors > 3:
                    new_grid[y, x] = 0
            else:
                if neighbors == 3:
                    new_grid[y, x] = 1

            # Draw the cell
            if grid[y, x] == 1:
                color = random_color()
                pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1))

    # Update grid
    grid = new_grid
    pygame.display.flip()

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    pygame.time.delay(100)

pygame.quit()