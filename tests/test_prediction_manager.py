import gzip
import os
import shutil
import unittest

import scodata.mongo as mongo
import scodata.attribute as attributes
import scodata.datastore as datastore
import scodata.modelrun as predictions

TMP_DIR = '/tmp/sco/runs'
CSV_FILE_1 = './data/csv/attachment1.csv'
CSV_FILE_2 = './data/csv/attachment2.csv'

class TestPredictionManagerMethods(unittest.TestCase):

    def setUp(self):
        """Connect to MongoDB and clear an existing modelruns collection.
        Create the model run manager"""
        m = mongo.MongoDBFactory(db_name='scotest')
        db = m.get_database()
        db.predictions.drop()
        if os.path.isdir(TMP_DIR):
            shutil.rmtree(TMP_DIR)
        os.makedirs(TMP_DIR)
        self.mngr = predictions.DefaultModelRunManager(db.modelruns, TMP_DIR)

    def test_experiment_create(self):
        """Test creation of experiment objects."""
        # Create an model run from fake data
        model_run = self.mngr.create_object('NAME', 'experiment-id', 'model-id', [])
        # Assert that object is active and is_image property is true
        self.assertTrue(model_run.is_active)
        self.assertTrue(model_run.is_model_run)
        # Ensure that other class type properties are false
        self.assertFalse(model_run.is_functional_data)
        self.assertFalse(model_run.is_image_group)
        self.assertFalse(model_run.is_image)
        self.assertFalse(model_run.is_experiment)
        self.assertFalse(model_run.is_subject)
        # Ensure that run state is IDLE
        self.assertTrue(model_run.state.is_idle)
        self.assertEquals(model_run.properties[datastore.PROPERTY_STATE], str(predictions.ModelRunIdle()))
        # Get object and ansure that all properties and state are still correct
        model_run = self.mngr.get_object(model_run.identifier)
        self.assertEqual(model_run.name, 'NAME')
        self.assertEqual(model_run.experiment_id, 'experiment-id')
        self.assertTrue(model_run.state.is_idle)
        self.assertEquals(model_run.properties[datastore.PROPERTY_STATE], str(predictions.ModelRunIdle()))

    def test_run_attachments(self):
        """Test attachments for model runs."""
        # Create an model run from fake data
        model_run = self.mngr.create_object('NAME', 'experiment-id', 'model-id', [])
        # Make sure that files can only be attached to successful model runs
        with self.assertRaises(ValueError):
            self.mngr.create_data_file_attachment(model_run.identifier, 'attachment', CSV_FILE_1)
        # Set state to success
        model_run = self.mngr.update_state(model_run.identifier, predictions.ModelRunActive())
        state = predictions.ModelRunSuccess('preditcion-id')
        model_run = self.mngr.update_state(model_run.identifier, state)
        # Make sure we can attach the file now
        self.mngr.create_data_file_attachment(model_run.identifier, 'attachment', CSV_FILE_1)
        # Read attached file. Content should be '1'
        with open(self.mngr.get_data_file_attachment(model_run.identifier, 'attachment')[0], 'r') as f:
            self.assertEquals(f.read().strip(), '1')
        # Make sure the list of attachments for the model run is 1
        model_run = self.mngr.get_object(model_run.identifier)
        self.assertEqual(len(model_run.attachments), 1)
        # Overwrite the existing attachment
        self.mngr.create_data_file_attachment(model_run.identifier, 'attachment', CSV_FILE_2)
        # Read attached file. Content should be '1'
        with open(self.mngr.get_data_file_attachment(model_run.identifier, 'attachment')[0], 'r') as f:
            self.assertEquals(f.read().strip(), '2')
        # Make sure the list of attachments for the model run is 1
        model_run = self.mngr.get_object(model_run.identifier)
        self.assertEqual(len(model_run.attachments), 1)
        # Delete attached file
        self.assertTrue(self.mngr.delete_data_file_attachment(model_run.identifier, 'attachment'))
        # Ensure that accessing a non-existent attachment returns None
        self.assertIsNone(self.mngr.get_data_file_attachment(model_run.identifier, 'attachment')[0])
        # Ensure that deleting a non-existent attachemnt return False attached file
        self.assertFalse(self.mngr.delete_data_file_attachment(model_run.identifier, 'attachment'))
        # Make sure the list of attachments for the model run is empty
        model_run = self.mngr.get_object(model_run.identifier)
        self.assertEqual(len(model_run.attachments), 0)

    def test_update_run_state(self):
        # Create an model run from fake data
        model_run = self.mngr.create_object('NAME', 'experiment-id', 'model-id', [])
        #
        # Set state to RUNNING
        #
        model_run = self.mngr.update_state(model_run.identifier, predictions.ModelRunActive())
        self.assertIsNotNone(model_run)
        self.assertTrue(model_run.state.is_running)
        self.assertEqual(model_run.properties[datastore.PROPERTY_STATE], str(predictions.ModelRunActive()))
        # Get object and ansure that state is still RUNNING
        model_run = self.mngr.get_object(model_run.identifier)
        self.assertTrue(model_run.state.is_running)
        self.assertEqual(model_run.properties[datastore.PROPERTY_STATE], str(predictions.ModelRunActive()))
        #
        # Set state to error
        #
        state = predictions.ModelRunFailed(['Some error'])
        model_run = self.mngr.update_state(model_run.identifier, state)
        self.assertIsNotNone(model_run)
        self.assertTrue(model_run.state.is_failed)
        self.assertEqual(model_run.properties[datastore.PROPERTY_STATE], str(state))
        self.assertTrue('Some error' in model_run.state.errors)
        # Get object and ansure that state is still FAILED
        model_run = self.mngr.get_object(model_run.identifier)
        self.assertTrue(model_run.state.is_failed)
        self.assertEqual(model_run.properties[datastore.PROPERTY_STATE], str(state))
        self.assertTrue('Some error' in model_run.state.errors)
        #
        # Set state to success. Will raise exception because run is incactive
        #
        state = predictions.ModelRunSuccess('preditcion-id')
        with self.assertRaises(ValueError):
            self.mngr.update_state(model_run.identifier, state)
        # Create an model run and ensure that we can set state to success for
        # active run
        model_run = self.mngr.create_object('NAME', 'experiment-id', 'model-id', [])
        model_run = self.mngr.update_state(model_run.identifier, predictions.ModelRunActive())
        state = predictions.ModelRunSuccess('preditcion-id')
        model_run = self.mngr.update_state(model_run.identifier, state)
        self.assertIsNotNone(model_run)
        self.assertTrue(model_run.state.is_success)
        self.assertEqual(model_run.properties[datastore.PROPERTY_STATE], str(state))
        self.assertEqual(model_run.state.model_output, 'preditcion-id')
        # Get object and ansure that state is still SUCCESS
        model_run = self.mngr.get_object(model_run.identifier)
        self.assertTrue(model_run.state.is_success)
        self.assertEqual(model_run.properties[datastore.PROPERTY_STATE], str(state))
        self.assertEqual(model_run.state.model_output, 'preditcion-id')

if __name__ == '__main__':
    unittest.main()
