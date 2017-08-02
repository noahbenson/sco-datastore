import os
import shutil
import unittest

import scodata.mongo as mongo
import scodata.image as images

TMP_DIR = '/tmp/sco/images'
DATA_DIR = './data'

class TestImageManagerMethods(unittest.TestCase):

    def setUp(self):
        """Connect to MongoDB and clear an existing images and image group
        collection. Ensure that data directory exists and is empty. Then create
        object managers."""
        m = mongo.MongoDBFactory(db_name='scotest')
        db = m.get_database()
        db.images.drop()
        db.predimages.drop()
        if os.path.isdir(TMP_DIR):
            shutil.rmtree(TMP_DIR)
        os.makedirs(TMP_DIR)
        self.mngr_images = images.DefaultImageManager(db.images, TMP_DIR)
        self.mngr_predimages = images.DefaultPredictionImageSetManager(db.predimages)

    def test_object_create(self):
        """Test creation and retrieval of a prediction image set."""
        pred_imgs = [
            images.PredictionImageSet('I1', ['O11', 'O12', 'O13']),
            images.PredictionImageSet('I2', ['O21', 'O22', 'O23']),
            images.PredictionImageSet('I3', ['O31', 'O32', 'O33'])
        ]
        obj = self.mngr_predimages.create_object('Name', pred_imgs)
        img_sets = self.mngr_predimages.get_object(obj.identifier)
        self.assertEquals(obj.identifier, img_sets.identifier)
        self.assertEquals(len(img_sets.images), 3)
        for i in range(3):
            self.assertEquals(img_sets.images[i].input_image, 'I' + str(i+1))
            self.assertEquals(len(img_sets.images[i].output_images), 3)

if __name__ == '__main__':
    unittest.main()
