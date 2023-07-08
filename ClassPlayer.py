class Player:

    def __init__(self, socket):
        self.name = None
        self.socket = socket
        self.points = 0

    def set_name(self, name):
        """
        get string name and set it in name
        """
        self.name = name

    def get_name(self):
        """
        return the name of player
        """
        return self.name

    def get_socket(self):
        """
        return socket
        """
        return self.socket

    def get_points(self):
        """
        return the points of the client
        """
        return self.points

    def add_point(self):
        """
        add 1 point to points
        """
        self.points += 1
