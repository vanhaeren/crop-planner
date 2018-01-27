from flask import Blueprint, render_template, session, redirect, url_for, abort
from webapp.models import db, Field, User, add_or_update, safe_delete, Crop, Cropbeds, CropVariety, Language
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from webapp.forms import FieldFormDetail, SettingsForm, AddFieldForm, SelectField, CropBedDetail
from webapp.utils import fieldCalculation
from os import path
from webapp import oauth2
import sys
import json
from urllib.request import unquote

planner_blueprint = Blueprint(
    'planner',
    __name__,
    template_folder=path.join(path.pardir, 'templates', 'planner'),
    url_prefix="/planner",

)


@planner_blueprint.route('/fielddetail/<int:field_id>', methods=['POST'])
@oauth2.required
def fielddetail(field_id):
    user = User.query.filter_by(oauth_client_id=session['profile']['id']).first()
    field = Field.query.filter_by(user_id=user.id,id=field_id).first()
    FieldFormDetail.bed_id = SelectField(coerce=int,label=("Bed Id"), choices=[(i,i) for i in range(0,field.number_of_beds)],
                                         render_kw=dict(class_="selectpicker"))
    CropBedDetail.crops = QuerySelectField(
        query_factory=CropVariety.query.filter_by(language_code=user.language_code).all,
        get_pk=lambda r: r.id,
        get_label=lambda r: r.variety,
        default=CropVariety.query.filter_by(language_code=user.language_code).first(),
        render_kw=dict(class_="selectpicker")
    )
    fieldformdetail = FieldFormDetail()

    if fieldformdetail.validate_on_submit():
        print('fieldformdetail was submitted', file=sys.stderr)
        if fieldformdetail.cropbedform.submit_update.data:
            print('Update clicked', file=sys.stderr)
            update_field = Field.query.filter_by(id=field_id).first()
            update_field.name = fieldformdetail.fieldform.fieldname.data
            update_field.area = fieldformdetail.fieldform.area.data
            add_or_update(db.session, update_field)

        if fieldformdetail.cropbedform.submit_delete.data:
            delete_field = Field.query.filter_by(id=field_id).first()
            safe_delete(db.session, delete_field)

        if fieldformdetail.submit_addcrop.data:
            add_cropbed = Cropbeds(field_id=field_id)
            add_cropbed.crop_variety_id = fieldformdetail.cropbedform.crops.data.id
            add_cropbed.crop_coverage = fieldformdetail.cropbedform.crop_coverage.data
            add_cropbed.cropping_type = fieldformdetail.cropbedform.crop_type.data
            add_cropbed.bed_id = fieldformdetail.bed_id.data
            add_or_update(db.session, add_cropbed)

        return redirect(url_for('planner.field'))
    else:
        print("AddFieldFormDetail errors {}".format(fieldformdetail.errors), file=sys.stderr)
        abort(400)

@planner_blueprint.route('/cropbeddetail/<int:bed_id>', methods=['POST'])
@oauth2.required
def cropbeddetail(bed_id):
    user = User.query.filter_by(oauth_client_id=session['profile']['id']).first()
    cropbed = Cropbeds.query.filter_by(id=bed_id).first()

    CropBedDetail.crops = QuerySelectField(
        query_factory=CropVariety.query.filter_by(language_code=user.language_code).all,
        get_pk=lambda r: r.id,
        get_label=lambda r: r.variety,
        default=CropVariety.query.filter_by(language_code=user.language_code).first(),
        render_kw=dict(class_="selectpicker")
    )
    cropbeddetail = CropBedDetail()

    if cropbeddetail.validate_on_submit():
        print('cropbeddetail was submitted', file=sys.stderr)
        if cropbeddetail.submit_update.data:
            print('Update clicked', file=sys.stderr)
            cropbed.crop_variety_id = cropbeddetail.crops.data
            cropbed.crop_type = cropbeddetail.crop_type.data
            cropbed.crop_coverage = cropbeddetail.crop_coverage.data
            add_or_update(db.session, cropbed)

        if cropbeddetail.submit_delete.data:
            safe_delete(db.session, cropbed)

        return redirect(url_for('planner.field'))
    else:
        print("CropBedDetail errors {}".format(cropbeddetail.errors), file=sys.stderr)
        abort(400)


@planner_blueprint.route('/settings', methods=['POST'])
@oauth2.required
def settings():
    user = User.query.filter_by(oauth_client_id=session['profile']['id']).first()
    SettingsForm.language = QuerySelectField(query_factory=Language.query.all,
                                             get_pk=lambda a: a.code,
                                             get_label=lambda a: a.name,
                                             default=user.language_code,
                                             render_kw=dict(class_="selectpicker")
                                             )
    settingsform = SettingsForm()

    if settingsform.validate_on_submit():
        user.row_width = settingsform.row_width.data
        user.row_length = settingsform.row_length.data
        user.row_spacing = settingsform.row_spacing.data
        user.language_code = settingsform.language.data.code
        add_or_update(db.session, user)
        return redirect(url_for('planner.field'))
    else:
        print("Settingsform errors {}".format(settingsform.errors), file=sys.stderr)

    pass


@planner_blueprint.route('/field', methods=['POST'])
@oauth2.required
def addfield():
    user = User.query.filter_by(oauth_client_id=session['profile']['id']).first()
    addfieldform = AddFieldForm()
    if addfieldform.validate_on_submit():
        print('fieldform was submitted', file=sys.stderr)
        if addfieldform.submit_add.data:
            fc = fieldCalculation(json.loads(unquote(addfieldform.fieldform.lengths.data)), user)
            new_field = Field(name=addfieldform.fieldform.fieldname.data)
            new_field.area = addfieldform.fieldform.area.data
            new_field.areable_area = fc.areableArea
            new_field.number_of_beds = fc.numberOfBeds
            new_field.user = user
            new_field.coordinates = unquote(addfieldform.fieldform.coordinates.data)
            new_field.lengths = unquote(addfieldform.fieldform.lengths.data)
            add_or_update(db.session, new_field)
            return redirect(url_for('planner.field'))
    else:
        print("AddFieldForm errors {}".format(addfieldform.errors), file=sys.stderr)
        abort(400)


@planner_blueprint.route('/field', methods=['GET'])
@oauth2.required
def field():
    user = User.query.filter_by(oauth_client_id=session['profile']['id']).first()
    fields = Field.query.filter_by(user_id=user.id).all()

    CropBedDetail.crops = QuerySelectField(
        query_factory=CropVariety.query.filter_by(language_code=user.language_code).all,
        get_pk=lambda r: r.id,
        get_label=lambda r: r.variety,
        render_kw=dict(class_="selectpicker")
    )

    SettingsForm.language = QuerySelectField(query_factory=Language.query.all,
                                             get_pk=lambda a: a.code,
                                             get_label=lambda a: a.name,
                                             default=user.language_code,
                                             render_kw=dict(class_="selectpicker")
                                             )
    settingsform = SettingsForm()
    addfieldform = AddFieldForm()
    cropbedform = CropBedDetail()
    fieldformdetails = []
    for field in fields:
        FieldFormDetail.bed_id = SelectField(coerce=int,label=("Bed Id"), choices=[(i,i) for i in range(0,field.number_of_beds)],
                                             render_kw=dict(class_="selectpicker"))
        fieldformdetail = FieldFormDetail()
        fieldformdetail.fieldform.fieldname.data = field.name
        fieldformdetail.fieldform.area.data = field.area
        fieldformdetail.fieldform.coordinates.data = field.coordinates
        fieldformdetail.fieldform.lengths.data = field.lengths
        fieldformdetail.field_id.data = field.id
        fieldformdetail.areable_area.data = field.areable_area
        fieldformdetail.number_of_beds.data = field.number_of_beds
        fieldformdetails.append(fieldformdetail)

    settingsform.row_width.data = user.row_width
    settingsform.row_length.data = user.row_length
    settingsform.row_spacing.data = user.row_spacing

    return render_template(
        'field.html',
        fields=fields,
        addfieldform=addfieldform,
        fieldformdetails=fieldformdetails,
        cropbedform=cropbedform,
        settingsform=settingsform
    )


@planner_blueprint.route('/user', methods=['GET'])
@oauth2.required
def user():
    # return defined fields for logged in user in json
    user = User.query.filter_by(oauth_client_id=session['profile']['id']).first()
    results = Field.query.filter_by(user_id=user.id).all()
    formdata = {}
    for result in results:
        formdata[result.name] = json.loads(result.coordinates)
    return json.dumps(formdata)


@planner_blueprint.route('/companion/<int:crop_id>', methods=['GET'])
@oauth2.required
def companion(crop_id):
    results = Crop.query.filter_by(crop_id=crop_id).all()
    formdata = []
    for result in results.companions:
        formdata.append(result.companion_id)
    return json.dumps(formdata)
