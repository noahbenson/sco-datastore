import gzip
import os
import shutil
import sys
import unittest

import scodata.mongo as mongo
import scodata.funcdata as funcdata

FMRIS_DIR = '/tmp/sco/funcdata'
DATA_DIR = './data'
FMRI_ARCHIVE = 'fmris/data.mgz'
INVALID_FMRI_ARCHIVE = 'fmris/invalid-fmri.tar'

class TestFuncDataManagerMethods(unittest.TestCase):

    def setUp(self):
        """Connect to MongoDB and clear an existing funcdata collection. Ensure
        that data directory exists and is empty. Create functional data
        manager."""
        m = mongo.MongoDBFactory(db_name='scotest')
        db = m.get_database()
        db.fmris.drop()
        if os.path.isdir(FMRIS_DIR):
            shutil.rmtree(FMRIS_DIR)
        os.makedirs(FMRIS_DIR)
        self.mngr = funcdata.DefaultFunctionalDataManager(db.fmris, FMRIS_DIR)

    def test_funcdata_create(self):
        """Test creation of functional data objects from files."""
        # Create a functional data object from an archive file
        tmp_file = os.path.join(FMRIS_DIR, os.path.basename(FMRI_ARCHIVE))
        shutil.copyfile(os.path.join(DATA_DIR, FMRI_ARCHIVE), tmp_file)
        fmri = self.mngr.create_object(tmp_file)
        # Assert that object is active and is_functional property is true
        self.assertTrue(fmri.is_active)
        self.assertEquals(fmri.type, funcdata.TYPE_FUNCDATA)
        # Assert that getting the object will not throw an Exception
        self.assertEqual(self.mngr.get_object(fmri.identifier).identifier, fmri.identifier)

    def test_invalid_create(self):
        """Test creation of functional data objects from invalid fMRI files."""
        tmp_file = os.path.join(FMRIS_DIR, os.path.basename(INVALID_FMRI_ARCHIVE))
        shutil.copyfile(os.path.join(DATA_DIR, INVALID_FMRI_ARCHIVE), tmp_file)
        with self.assertRaises(ValueError):
            fmri = self.mngr.create_object(tmp_file)
        os.remove(tmp_file)

if __name__ == '__main__':
    # Pass data directory as optional parameter
    if len(sys.argv) == 2:
        DATA_DIR = sys.argv[1]
    sys.argv = sys.argv[:1]
    unittest.main()
