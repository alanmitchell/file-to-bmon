from .base_reader import BaseReader

class Reader(BaseReader):
    
    def __init__(self, **kw):
        super().__init__(**kw)
        print(f'In cea.Reader: {kw}')

    def load(self):
        print('loading')
