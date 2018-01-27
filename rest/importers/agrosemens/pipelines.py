# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import agrosemens.database.connection as db
import mongoengine as mongo
from agrosemens.database.models import Agrosemens

mongo.register_connection(db.dbname,name=db.dbname, host=db.dbhost, username = db.dbuser, password = db.dbpass)
class AddTablePipeline(object):
    def process_item(self, item, spider):
        mongo = Agrosemens(taxon=item['taxon'],
                 href = item['href'],
                 category = item['category'],
                 variety = item['variety'],
                 description = item['description']
                 )
        mongo.save()
        return item
