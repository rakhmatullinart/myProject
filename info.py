from base import is_editor
objects = []

class Choice:
    def __init__(self, user_id):
        self.step = 'menu'
        self.kat = None
        self.name = None
        self.surname = None
        self.callback = {}
        self.user_id = user_id
        self.editor = is_editor(user_id)
        self.edit = None
        self.queue = []
        self.prev_r = None
        self.offline = False
        self.forward = None
        objects.append(self)