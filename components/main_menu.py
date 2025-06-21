# components/main_menu.py
from components.text_element import TextElement

class MainMenu:
    def __init__(self, renderer):
        self.renderer = renderer
        self.text_elements = []
        self.active = True
        
        # Create text elements
        start_text = TextElement(
            text="Start Game",
            position=[0, 0.2],
            size=[0.4, 0.1],
            color=(0, 255, 0),  # Green
            font_size=48
        )
        
        quit_text = TextElement(
            text="Quit",
            position=[0, -0.2],
            size=[0.3, 0.08],
            color=(255, 0, 0),  # Red
            font_size=48
        )
        
        self.text_elements.append(start_text)
        self.text_elements.append(quit_text)
        
        # Add text meshes to renderer
        for text_element in self.text_elements:
            self.renderer.add_screen_mesh(text_element.text_mesh)

    def update(self, input):
        if not self.active:
            return
            
        # Convert mouse position to NDC (-1 to 1)
        mouse_x, mouse_y = input.mouse_pos
        mouse_pos_ndc = [
            (mouse_x / self.renderer.screen_width) * 2 - 1,
            -((mouse_y / self.renderer.screen_height) * 2 - 1)
        ]
        
        # Check if left mouse button is pressed (button 0)
        mouse_clicked = input.mouse_buttons[0]
        
        # Check text interactions
        for text_element in self.text_elements:
            if text_element.text == "Start Game" and text_element.check_click(mouse_pos_ndc, mouse_clicked):
                self.active = False
                return "start"
            elif text_element.text == "Quit" and text_element.check_click(mouse_pos_ndc, mouse_clicked):
                return "quit"
        return None