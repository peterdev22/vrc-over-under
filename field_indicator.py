import pygame
import math

# Initialize Pygame
pygame.init()

# Field settings
field_size = (600, 600)
tile_size = field_size[0] // 6
origin = (field_size[0] // 2, field_size[1] // 2)

# Block settings
block_size = (45, 45)
block_color = pygame.Color('blue')
block_speed = 1
block_rotation_speed = 5

# Create the window
screen = pygame.display.set_mode(field_size)
pygame.display.set_caption('Field Position Indicator')

# Font settings
font = pygame.font.SysFont(None, 18)
text_color = pygame.Color('white')

# Initialize block position, direction, and arrow rotation
block_pos = pygame.Vector2(origin)
block_dir = pygame.Vector2(0, -1)
arrow_rotation = 0

# Track pressed keys
pressed_keys = set()

def draw_field():
    imp = pygame.image.load("C:\\Users\\EricGu\\Desktop\\VEX\\over under\\field diagram.png").convert()
    screen.blit(imp, (0, 0))
def draw_block():
    rotated_block = pygame.transform.rotate(pygame.Surface(block_size), -arrow_rotation)
    block_rect = rotated_block.get_rect(center=block_pos)
    pygame.draw.rect(screen, block_color, block_rect)

def draw_text_box(text):
    pygame.draw.rect(screen, pygame.Color('gray'), (10, 10, 200, 20))
    text_surface = font.render(text, True, text_color)
    screen.blit(text_surface, (15, 15))

def move_block():
    global block_pos
    direction = pygame.Vector2(0, 0)
    if pygame.K_w in pressed_keys:
        direction += block_dir
    if pygame.K_s in pressed_keys:
        direction -= block_dir
    if pygame.K_a in pressed_keys:
        direction -= pygame.Vector2(-block_dir.y, block_dir.x)
    if pygame.K_d in pressed_keys:
        direction -= pygame.Vector2(block_dir.y, -block_dir.x)
    if direction.length() != 0:
        direction.scale_to_length(block_speed)
    block_pos += direction


# Game loop
running = True
textbox_text = ""

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            pressed_keys.add(event.key)
            if event.key == pygame.K_RETURN:
                try:
                    x, y = map(float, textbox_text.split(','))
                    block_pos = pygame.Vector2(round(x, 2), round(y, 2))
                except ValueError:
                    pass
        elif event.type == pygame.KEYUP:
            pressed_keys.discard(event.key)

    # Update the block position
    move_block()
    
    # Update the screen
    draw_field()
    draw_block()
    draw_text_box(f"Current Position: {round(block_pos.x*6-1800, 2)}, {round(block_pos.y*6-1800, 2)}")
    pygame.display.flip()

# Quit the game
pygame.quit()