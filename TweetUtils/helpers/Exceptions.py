

class LabelNotFound(Exception):
    def __init__(self, msg):
        self.message = msg


class InvalidConfiguration(Exception):
    pass