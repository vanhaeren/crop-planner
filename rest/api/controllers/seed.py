from flask import abort
from flask_restful import Resource, fields, marshal_with
from api.models import Agrosemens

class JsonItem(fields.Raw):
    def format(self, value):
        return value

seed_fields = {
    'variety' : fields.String(),
    'category' : fields.String(),
    'href' : fields.String(),
    'taxon' : fields.String(),
    'description' : JsonItem()
}

class SeedApi(Resource):
    @marshal_with(seed_fields)
    def get(self,page=1):
       seeds = Agrosemens.objects.paginate(page,page + 10).items
       if not seeds:
          abort(404)
       return  seeds