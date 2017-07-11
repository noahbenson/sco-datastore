import os
import sys

from mongo import MongoDBFactory
from subject import DefaultSubjectManager

args = sys.argv[1:]
if len(args) != 4:
    print 'Usage: <mongo-db> <data-dir> <subject-id> <subject-tar-file>'
    sys.exit(1)

mongo = MongoDBFactory(db_name=args[0])
subjects_dir = os.path.join(os.path.abspath(args[1]), 'subjects')

subjects = DefaultSubjectManager(mongo.get_database()['subjects'], subjects_dir)
subjects.upload_freesurfer_archive(
    args[3],
    object_identifier=args[2],
    read_only=True
)
