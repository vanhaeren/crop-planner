from mongoengine import DynamicDocument, StringField, DictField, connect

class Agrosemens(DynamicDocument):
    meta = {'db_alias': 'flaskapi'}
    variety = StringField(required=True)
    category = StringField()
    href = StringField()
    taxon = StringField()
    description = DictField()


