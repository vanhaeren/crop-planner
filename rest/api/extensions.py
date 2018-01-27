from flask_restful import Api, output_json

class UnicodeApi(Api):
    def __init__(self, *args, **kwargs):
        super(UnicodeApi, self).__init__(*args, **kwargs)
        self.representations = {
            'application/json; charset=utf-8': output_json,
        }

rest_api = UnicodeApi()

