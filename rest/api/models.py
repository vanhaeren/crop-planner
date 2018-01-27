from flask_mongoengine import MongoEngine

mongo = MongoEngine()

class Agrosemens(mongo.DynamicDocument):
    meta = {'db_alias': 'flaskapi'}
    variety = mongo.StringField(required=True)
    category = mongo.StringField()
    href = mongo.StringField()
    taxon = mongo.StringField()
    description = mongo.DictField()


    def __repr__(self):
        return "<Agrosemens '{}'>".format(self.variety)


