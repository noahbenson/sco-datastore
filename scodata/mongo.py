"""MongoDB client factory - The SCO Engine uses multi-processing to execute
model runs. Thus, it should create a new instance of the mongo client for
each process. The MongoDBFactory is used as a central place to establish
connection to MongoDB for the SCO Data Store and the SCO Engine.
"""

import os
from pymongo import MongoClient


class MongoDBFactory(object):
    """Factory pattern to establish connection to default mongo database used
    by the current implementation of the SCO Web API.
    """
    def __init__(self, db_name='scoserv', db_uri=None):
        """Initialize the database name.

        Parameters
        ----------
        db_name : string, optional
            Name of the database (default: scoserv)
        db_uri : string, optional
            URI of the database (default: None); if None is given then
            either the MONGODB_URI environment name or localhost is used.
        """
        self.db_name = db_name
        if db_uri is None:
            db_uri = os.environ.get('MONGODB_URI', 'localhost')
        self.db_uri = db_uri

    def drop_database(self):
        """Drop the database the factory connects to."""
        MongoClient(self.db_uri).drop_database(self.db_name)

    def get_database(self):
        """Create a new default mongo database object.

        Returns
        -------
        MongoDb.database
            MongoDB database object
        """
        return MongoClient(self.db_uri)[self.db_name]
