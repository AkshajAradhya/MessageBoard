import pygame
import json
import os
import time

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BG_COLOR = (240, 240, 240)
TEXT_COLOR = (50, 50, 50)
FONT_PATH = "assets/fonts/AfacadFlux.ttf"
DATA_FILE = "data/kudoboard.json"
CURSOR_COLOR = (0, 0, 0)
SCROLL_SPEED = 20
BUTTON_COLOR = (200, 200, 200)
BUTTON_HOVER_COLOR = (180, 180, 180)
CONFIRMATION_BG_COLOR = (169, 169, 169)  # Grey background for the confirmation dialog
CONFIRMATION_WIDTH = 400
CONFIRMATION_HEIGHT = 200

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Message Board")
font = pygame.font.Font(FONT_PATH, 24)
button_font = pygame.font.Font(FONT_PATH, 28)

# Load posts from JSON file
def load_posts():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            posts = json.load(f)
            for post in posts:
                post.setdefault("x", 100)
                post.setdefault("y", 100)
                post.setdefault("width", 200)
                post.setdefault("height", 100)
            return posts
    return []

# Save posts to JSON file
def save_posts(posts):
    with open(DATA_FILE, "w") as f:
        json.dump(posts, f, indent=4)

# Draw posts on the board
def draw_posts(posts, scroll_offset):
    for post in posts:
        rect_x = post["x"]
        rect_y = post["y"] - scroll_offset
        if rect_y + post["height"] > 0 and rect_y < SCREEN_HEIGHT:
            pygame.draw.rect(screen, (255, 255, 255), (rect_x, rect_y, post["width"], post["height"]), border_radius=10)
            pygame.draw.rect(screen, (200, 200, 200), (rect_x, rect_y, post["width"], post["height"]), 2)  # Border
            text_surface = font.render(post["content"], True, TEXT_COLOR)
            screen.blit(text_surface, (rect_x + 10, rect_y + 10))

# Function to display the confirmation dialog with buttons
def show_confirmation_dialog():
    # Create the confirmation dialog background (grey)
    confirmation_rect = pygame.Rect((SCREEN_WIDTH - CONFIRMATION_WIDTH) // 2, (SCREEN_HEIGHT - CONFIRMATION_HEIGHT) // 2, CONFIRMATION_WIDTH, CONFIRMATION_HEIGHT)
    pygame.draw.rect(screen, CONFIRMATION_BG_COLOR, confirmation_rect)

    # Create the confirmation text (black)
    confirmation_text = "Are you sure you want to delete this post?"
    confirmation_surface = font.render(confirmation_text, True, (0, 0, 0))  # Black text
    text_x = (confirmation_rect.width - confirmation_surface.get_width()) // 2 + confirmation_rect.x
    text_y = 40 + confirmation_rect.y
    screen.blit(confirmation_surface, (text_x, text_y))

    # Create the buttons
    button_width = 120
    button_height = 40
    confirm_button_rect = pygame.Rect((SCREEN_WIDTH - CONFIRMATION_WIDTH) // 2 + 30, SCREEN_HEIGHT // 2 + 40, button_width, button_height)
    cancel_button_rect = pygame.Rect((SCREEN_WIDTH - CONFIRMATION_WIDTH) // 2 + 250, SCREEN_HEIGHT // 2 + 40, button_width, button_height)

    pygame.draw.rect(screen, BUTTON_COLOR, confirm_button_rect, border_radius=5)
    pygame.draw.rect(screen, BUTTON_COLOR, cancel_button_rect, border_radius=5)

    confirm_text = button_font.render("Yes", True, (0, 0, 0))  # Black text on button
    cancel_text = button_font.render("No", True, (0, 0, 0))  # Black text on button
    screen.blit(confirm_text, (confirm_button_rect.centerx - confirm_text.get_width() // 2, confirm_button_rect.centery - confirm_text.get_height() // 2))
    screen.blit(cancel_text, (cancel_button_rect.centerx - cancel_text.get_width() // 2, cancel_button_rect.centery - cancel_text.get_height() // 2))

    return confirm_button_rect, cancel_button_rect

# Modify the main function in your existing code
def main():
    clock = pygame.time.Clock()
    running = True
    posts = load_posts()
    creating_post = False
    editing_post = None
    resizing_post = None
    resize_anchor = None
    user_input = ""
    cursor_pos = 0
    cursor_visible = True
    cursor_time = time.time()
    last_click_time = 0
    scroll_offset = 0
    backspace_held = False
    backspace_time = 0  # Tracks when Backspace was first pressed
    BACKSPACE_DELAY = 0.5  # Initial delay before repeating
    BACKSPACE_REPEAT = 0.05  # Repeat interval when holding Backspace
    dragging_post = None  # Track the post being dragged
    drag_offset = (0, 0)  # Track the offset from the mouse click
    confirmation_popup_active = False
    deleting_post = None

    while running:
        screen.fill(BG_COLOR)

        # Event handling
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if creating_post or editing_post is not None:
                        creating_post = False
                        editing_post = None
                        user_input = ""
                    elif confirmation_popup_active:
                        confirmation_popup_active = False
                        deleting_post = None
                    else:
                        running = False
                elif creating_post or editing_post is not None:
                    if event.key == pygame.K_RETURN:
                        if creating_post:
                            posts.append({"content": user_input, "x": 100, "y": scroll_offset + 100, "width": 200, "height": 100})
                        elif editing_post is not None:
                            posts[editing_post]["content"] = user_input
                        save_posts(posts)
                        user_input = ""
                        creating_post = False
                        editing_post = None
                        cursor_pos = 0
                    elif event.key == pygame.K_BACKSPACE:
                        backspace_held = True
                        backspace_time = time.time()
                        if cursor_pos > 0:
                            user_input = user_input[:cursor_pos - 1] + user_input[cursor_pos:]
                            cursor_pos -= 1
                    elif event.key == pygame.K_DELETE:
                        if cursor_pos < len(user_input):
                            user_input = user_input[:cursor_pos] + user_input[cursor_pos + 1:]
                    elif event.key == pygame.K_LEFT:
                        if cursor_pos > 0:
                            cursor_pos -= 1
                    elif event.key == pygame.K_RIGHT:
                        if cursor_pos < len(user_input):
                            cursor_pos += 1
                    else:
                        user_input = user_input[:cursor_pos] + event.unicode + user_input[cursor_pos:]
                        cursor_pos += 1
                elif event.key == pygame.K_c:  # Press 'C' to create a new post
                    creating_post = True
                    user_input = ""
                    cursor_pos = 0
                elif event.key == pygame.K_UP:
                    scroll_offset = max(scroll_offset - SCROLL_SPEED, 0)
                elif event.key == pygame.K_DOWN:
                    scroll_offset += SCROLL_SPEED
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    click_time = time.time()
                    for i, post in enumerate(posts):
                        post_rect = pygame.Rect(post["x"], post["y"] - scroll_offset, post["width"], post["height"])
                        resize_zone = pygame.Rect(post["x"] + post["width"] - 10, post["y"] + post["height"] - 10 - scroll_offset, 10, 10)
                        if resize_zone.collidepoint(event.pos):
                            resizing_post = i
                            resize_anchor = (post["width"], post["height"], event.pos[0], event.pos[1])
                            break
                        elif post_rect.collidepoint(event.pos):
                            if click_time - last_click_time < 0.3:  # Double-click detected
                                editing_post = i
                                user_input = posts[editing_post]["content"]
                                cursor_pos = len(user_input)
                                break
                            # Start dragging the post
                            dragging_post = i
                            drag_offset = (event.pos[0] - post["x"], event.pos[1] - post["y"])
                            last_click_time = click_time
                elif event.button == 3:  # Right mouse button
                    if confirmation_popup_active:
                        continue
                    for i, post in enumerate(posts):
                        post_rect = pygame.Rect(post["x"], post["y"] - scroll_offset, post["width"], post["height"])
                        if post_rect.collidepoint(event.pos):
                            deleting_post = i
                            confirmation_popup_active = True
                            break
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    resizing_post = None
                    resize_anchor = None
                    # Stop dragging the post
                    dragging_post = None

        # Handle dragging of the post
        if dragging_post is not None:
            post = posts[dragging_post]
            # Update the post's position based on the mouse position and the drag offset
            post["x"] = mouse_pos[0] - drag_offset[0]
            post["y"] = mouse_pos[1] - drag_offset[1]

        # Draw posts or input form
        if creating_post or editing_post is not None:
            input_text = user_input
            text_surface = font.render(input_text, True, TEXT_COLOR)
            text_x = 50 if creating_post else posts[editing_post]["x"] + 10
            text_y = SCREEN_HEIGHT // 2 if creating_post else posts[editing_post]["y"] + 10 - scroll_offset
            screen.blit(text_surface, (text_x, text_y))

            # Blinking cursor
            if time.time() - cursor_time > 0.5:
                cursor_visible = not cursor_visible
                cursor_time = time.time()
            if cursor_visible:
                cursor_x = text_x + font.size(input_text[:cursor_pos])[0]
                cursor_y = text_y
                pygame.draw.line(screen, CURSOR_COLOR, (cursor_x, cursor_y), (cursor_x, cursor_y + font.get_height()), 2)

        # Draw the delete confirmation UI if active
        if confirmation_popup_active:
            confirm_button_rect, cancel_button_rect = show_confirmation_dialog()

            # Handle button clicks
            if confirm_button_rect.collidepoint(mouse_pos) and mouse_pressed[0]:
                posts.pop(deleting_post)
                save_posts(posts)
                confirmation_popup_active = False
                deleting_post = None
            elif cancel_button_rect.collidepoint(mouse_pos) and mouse_pressed[0]:
                confirmation_popup_active = False
                deleting_post = None

        # Draw posts and scrolling
        draw_posts(posts, scroll_offset)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
