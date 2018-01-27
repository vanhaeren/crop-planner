from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, IntegerField, SubmitField, SelectField, FieldList, FormField
from wtforms.validators import DataRequired, Length


class FieldForm(FlaskForm):
    fieldname = StringField(validators=[DataRequired(), Length(max=255)],render_kw=dict(size = 8), label="Field Name")
    area = StringField(validators=[DataRequired(), Length(max=255)],render_kw=dict(size = 8), label="Field Area (m2)")
    coordinates = HiddenField()
    lengths = HiddenField()

class AddFieldForm(FlaskForm):
    fieldform = FormField(FieldForm)
    submit_add = SubmitField(label="Add Field",render_kw=dict(class_="btn btn-primary"))

class CropBedDetail(FlaskForm):
    crop_type = SelectField(label=("Distribution type"), choices=[("mono", "Bed Monoculture"),
                                                                  ("row", 'Alternating rows'),
                                                                  ("strip", "Trapcrop at edges"),
                                                                  ("relay", "Covercrop with relayharvesting"),
                                                                  ("mixed", "Random alternating crops")],
                            render_kw=dict(class_="selectpicker"))
    crop_coverage = IntegerField(label="Crop coverage in %", default=100,render_kw=dict(size = 4))
    submit_update = SubmitField(label="Save",render_kw=dict(class_="btn btn-primary"))
    submit_delete = SubmitField(label="Delete",render_kw=dict(class_="btn btn-primary"))


class FieldFormDetail(FlaskForm):
    fieldform = FormField(FieldForm)
    areable_area = HiddenField()
    number_of_beds = HiddenField()
    field_id = HiddenField()
    cropbedform = FormField(CropBedDetail)
    submit_add = SubmitField(label="Add Field")
    submit_addcrop = SubmitField(label="Add crop",render_kw=dict(class_="btn btn-primary"))


class SettingsForm(FlaskForm):
    row_width = IntegerField(validators=[DataRequired()], default=75)
    row_spacing = IntegerField(validators=[DataRequired()], default=45)
    row_length = IntegerField(validators=[DataRequired()], default=3000)
    submit_save = SubmitField(label="Save",render_kw=dict(class_="btn btn-primary"))
