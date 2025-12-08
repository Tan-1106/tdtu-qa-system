from bson import ObjectId
from datetime import datetime, timezone

from app.databases import mongo
from app.utils import serializer
from app.schemas import statistical_schema
from app.utils.api_response import DatabaseException


class StatisticalDao:
    def __init__(self):
        self.qa_collection = mongo.get_qa_collection()
        
    # 
