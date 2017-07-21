

class User:
    id = None
    stat = None
    name = None
    surname = None
    kat = None
    link = None
    reason = 'none'
    #data_types = ['id', 'type', 'name', 'company', 'price', 'description', 'url']
    def get_data(self):  # возвращает список , состоящий из структуры данных типа Item.data_types
        args = (self.name,
                self.surname,
                self.rate
                )
        return args

    def set_full_data(self, *args):
        try:
            self.name = args[1]
            self.surname = args[2]
            self.id = args[0]
            self.rate = args[4]
            self.link = args[5]
            self.reason = args[6]

        except:
            pass

    def reset(self):
        self.id = None
        self.stat = None
        self.name = None
        self.surname = None
        self.kat = None
        self.link = None
        self.reason = 'none'


class Request:
    pass
