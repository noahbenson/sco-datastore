import gzip
import os
import shutil
import sys
import unittest

import scodata.mongo as mongo
import scodata.experiment as experiments

class TestExperimentManagerMethods(unittest.TestCase):

    def setUp(self):
        """Connect to MongoDB and clear an existing experiment collection.
        Create experiment manager"""
        m = mongo.MongoDBFactory(db_name='scotest')
        db = m.get_database()
        db.experiments.drop()
        self.mngr = experiments.DefaultExperimentManager(db.experiments)

    def test_experiment_create(self):
        """Test creation of experiment objects."""
        # Create an experiment from fake data
        experiment = self.mngr.create_object('subject-id', 'images-id', {'name':'NAME'})
        # Assert that object is active and is_image property is true
        self.assertTrue(experiment.is_active)
        self.assertEquals(experiment.type, experiments.TYPE_EXPERIMENT)
        # Assert that getting the object will not throw an Exception
        identifier = experiment.identifier
        experiment = self.mngr.get_object(identifier)
        self.assertEqual(identifier, experiment.identifier)
        # Ensure that subject and image objects are referenced properly
        self.assertEqual(experiment.subject_id, 'subject-id')
        self.assertEqual(experiment.image_group_id, 'images-id')
        self.assertIsNone(experiment.fmri_data_id)
        # Update fMRI data
        experiment = self.mngr.update_fmri_data(identifier, 'fmri-id')
        self.assertIsNotNone(experiment)
        self.assertEqual(experiment.fmri_data_id, 'fmri-id')
        experiment = self.mngr.get_object(experiment.identifier)
        # Ensure that subject and image objects are referenced properly
        self.assertEqual(experiment.subject_id, 'subject-id')
        self.assertEqual(experiment.image_group_id, 'images-id')
        self.assertEqual(experiment.fmri_data_id, 'fmri-id')

        # Create an experiment from fake data this time with functional data
        experiment = self.mngr.create_object('subject-id', 'images-id', {'name':'NAME'}, fmri_data_id='fmri-id')
        experiment = self.mngr.get_object(experiment.identifier)
        # Ensure that subject and image objects are referenced properly
        self.assertEqual(experiment.subject_id, 'subject-id')
        self.assertEqual(experiment.image_group_id, 'images-id')
        self.assertEqual(experiment.fmri_data_id, 'fmri-id')


if __name__ == '__main__':
    unittest.main()
type
