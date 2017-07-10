

class User:
    id = None
    rate = None
    name = None
    surname = None
    kat = None
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

        except:
            pass