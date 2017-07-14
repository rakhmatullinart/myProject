from base import is_editor
objects = []

class Choice:
    def __init__(self, user_id):
        self.step = 'kat_choose'
        self.kat = None
        self.name = None
        self.surname = None
        self.callback = {}
        self.user_id = user_id
        self.editor = is_editor(user_id)
        objects.append(self)