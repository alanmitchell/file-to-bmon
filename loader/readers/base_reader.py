class BaseReader:
    
    def __init__(self, **kw):
        print(f'In BaseReader: {kw}')
        # create subdirectories under file source to hold completed readings
        # and error readings.
        # file_pattern = Path(src['pattern'])
        # (file_pattern.parent / 'completed').mkdir(exist_ok=True)
        # (file_pattern.parent / 'errors').mkdir(exist_ok=True)
