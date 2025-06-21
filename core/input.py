import pygame


class Input(object):
    def __init__(self) -> None:
        self.quit = False
        self.key_down_list = []
        self.key_pressed_list = []
        self.key_up_list = []
        
        # Mouse state
        self.mouse_pos = (0, 0)
        self.mouse_rel = (0, 0)
        self.mouse_buttons = [False, False, False]  # Left, Middle, Right
    
    def is_key_down(self, keyCode):
        return keyCode in self.key_down_list
    def is_key_pressed(self, keyCode):
        return keyCode in self.key_pressed_list
    def is_key_up(self, keyCode):
        return keyCode in self.key_up_list

    def update(self):
        self.key_down_list = []
        self.key_up_list = []
        self.mouse_rel = (0, 0)  # Reset relative motion each frame

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True
            elif event.type == pygame.KEYDOWN:
                key_char = event.unicode.lower()
                if key_char:
                    if key_char not in self.key_pressed_list:
                        self.key_down_list.append(key_char)
                        self.key_pressed_list.append(key_char)
            elif event.type == pygame.KEYUP:
                key_char = event.unicode.lower() if event.unicode else pygame.key.name(event.key).lower()
                if key_char in self.key_pressed_list:
                    self.key_pressed_list.remove(key_char)
                self.key_up_list.append(key_char)
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_rel = event.rel
                self.mouse_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button <= 3: 
                    self.mouse_buttons[event.button - 1] = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button <= 3:
                    self.mouse_buttons[event.button - 1] = False