import pygame


class textbox:

    def __init__(self, x, y, background_color):
        self.x = x      # set x coordinate of textbox
        self.y = y      # set y coordinate of textbox
        self.font = pygame.font.Font(None, 32)  # set font of text
        self.input_box = pygame.Rect(x, y, 140, 32)     # create rect
        self.color = pygame.Color('dodgerblue2')        # set color of box
        self.background_color = background_color        # set background color
        self.text = ""                                  # text that the user insert(set to "")
        self.text_surface = self.font.render(self.text, True, self.color)   # serface of textbox
        self.change = False         # var that say if user press on keyboard
        self.first = True
        self.width = 350            # width of box
        self.input_box.w = self.width

    def get_x(self):
        """
        return the x coordinates of box
        """
        return self.x

    def get_y(self):
        """
        return the y coordinates of box
        """
        return self.y

    def get_background(self):
        """
        return the background color
        """
        return self.background_color

    def update(self, text):
        """
        update the text
        """
        self.text = text
        self.text_surface = self.font.render(self.text, True, self.color)

    def get_rect(self):
        """
        return the rect
        """
        return self.input_box

    """def get(self):
        return self.text_surface"""

    def get_text(self):
        """
        return the text
        """
        return self.text

    def add_char(self, char):
        """
        func get char and add it to text
        """
        self.text += char
        self.text_surface = self.font.render(self.text, True, self.color)

    def remove_char(self):
        """
        func remove char from the text
        """
        self.text = self.text[:-1]
        self.text_surface = self.font.render(self.text, True, self.color)

    def clear(self):
        """
        func put "" in text
        """
        self.text = ""
        self.text_surface = self.font.render(self.text, True, self.color)

    def is_empty(self):
        """
        func return true if the text is empty
        else return false
        """
        if self.text == "":
            return True
        return False

    def print_box(self, screen):
        """
        func get screen
        func print to screen the textbox
        """
        font = pygame.font.Font(r"fonts\secret_word_2.ttf", 30)
        # Blit the text.
        screen.blit(self.text_surface, (self.input_box.x+5, self.input_box.y+5))
        # Blit the input_box rect.
        #pygame.display.flip()
        pygame.draw.rect(screen, self.color, self.input_box, 2)
        pygame.display.flip()