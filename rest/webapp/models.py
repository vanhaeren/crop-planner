from flask_sqlalchemy import SQLAlchemy
import enum

db = SQLAlchemy()


class CroppingArangement(enum.Enum):
    mono = 'Monocropping',
    row = 'RowIntercropping'
    strip = 'StripIntercropping'
    relay = 'RelayIntercropping'
    mixed = 'MixedIntercropping'

crop_companions =  db.Table('crop_companions',
    db.Column('crop_id', db.Integer(), db.ForeignKey('crop.id')),
    db.Column('companion_id', db.Integer(), db.ForeignKey('crop.id')))

class Crop(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    taxon = db.Column(db.String(255))
    taxon_family = db.Column(db.String(255))
    dose = db.Column(db.Integer())
    spread = db.Column(db.Integer())
    row_spacing = db.Column(db.Integer())
    companions = db.relationship('Crop',
                                 secondary='crop_companions',
                                 primaryjoin=(crop_companions.c.crop_id == id),
                                 secondaryjoin=(crop_companions.c.companion_id == id),
                                 backref=db.backref('crop_companions', lazy='dynamic'),
                                 lazy='dynamic')
    varieties = db.relationship('CropVariety',
                                backref='crop',
                                lazy='dynamic'
                                )
    categories = db.relationship('Category',
                             backref='crop',
                             lazy='dynamic'
                             )

class Category(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    crop_id = db.Column(db.Integer(), db.ForeignKey('crop.id'))
    language_code = db.Column(db.String(2), db.ForeignKey('language.code'))
    name = db.Column(db.String(255))
    language = db.relationship('Language',
                               backref=db.backref('category')
                               )


class CropVariety(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    crop_id = db.Column(db.Integer(), db.ForeignKey('crop.id'))
    language_code = db.Column(db.String(2), db.ForeignKey('language.code'))
    name = db.Column(db.String(255))
    variety = db.Column(db.String(255))
    description = db.Column(db.String(2048))
    language = db.relationship('Language',
                           backref=db.backref('crop_variety')
                           )


class Language(db.Model):
    code = db.Column(db.String(2), primary_key=True)
    name = db.Column(db.String(20))




class Cropbeds(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    field_id = db.Column(db.Integer(), db.ForeignKey('field.id'))
    crop_variety_id = db.Column(db.Integer(), db.ForeignKey('crop_variety.id'))
    # For mixed beds %
    crop_coverage = db.Column(db.Integer())
    cropping_type = db.Column(db.Enum(CroppingArangement))
    bed_id = db.Column(db.Integer)
    crop_variety = db.relationship(
        'CropVariety',
        backref=db.backref('cropbeds')
    )

class Field(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), unique=True)
    area = db.Column(db.Float())
    areable_area = db.Column(db.Float())
    coordinates = db.Column(db.String(255))
    number_of_beds = db.Column(db.Integer())
    lengths = db.Column(db.String(255))
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    beds = db.relationship('Cropbeds',
                           backref='field',
                           lazy='dynamic')


class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(255))
    oauth_client_id = db.Column(db.String(255))
    row_width = db.Column(db.Integer(), default=75)
    row_spacing = db.Column(db.Integer(), default=45)
    row_length = db.Column(db.Integer(), default=3000)
    language_code = db.Column(db.String(2), db.ForeignKey('language.code'))
    fields = db.relationship(
        'Field',
        backref='user',
        lazy='dynamic'
    )
    language = db.relationship('Language',
                               backref=db.backref('user', uselist=False)
                               )

    def __init__(self, username, oauth_client_id):
        self.username = username
        self.oauth_client_id = oauth_client_id

    def __repr__(self):
        return "<User '{}'>".format(self.username)


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


def add_or_update(session, model):
    session.add(model)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        print(str(e))


def safe_delete(session, model):
    session.delete(model)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        print(str(e))


def to_dict(model_instance, query_instance=None):
    if hasattr(model_instance, '__table__'):
        return {c.name: str(getattr(model_instance, c.name)) for c in model_instance.__table__.columns}
    else:
        cols = query_instance.column_descriptions
        return {cols[i]['name']: model_instance[i] for i in range(len(cols))}


def from_dict(dict, model_instance):
    for c in model_instance.__table__.columns:
        setattr(model_instance, c.name, dict[c.name])
