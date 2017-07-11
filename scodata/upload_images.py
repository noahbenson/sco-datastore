import os
import shutil
import sys
import tarfile
import tempfile

from image import DefaultImageManager, DefaultImageGroupManager, GroupImage, get_image_files
from mongo import MongoDBFactory

args = sys.argv[1:]
if len(args) != 5:
    print 'Usage: <mongo-db> <data-dir> <image-group-id> <name> <image-group-tar-file>'
    sys.exit(1)

db = MongoDBFactory(db_name=args[0]).get_database()

abs_base_dir = os.path.abspath(args[1])
images_dir =os.path.join(abs_base_dir, 'images')
image_files_dir = os.path.join(images_dir, 'files')
image_groups_dir = os.path.join(images_dir, 'groups')

images = DefaultImageManager(db.images, image_files_dir)
image_groups = DefaultImageGroupManager(db.imagegroups, image_groups_dir,images)

name = args[3]
filename = args[4]

# Unpack the file to a temporary folder .
temp_dir = tempfile.mkdtemp()
try:
    tf = tarfile.open(name=filename, mode='r')
    tf.extractall(path=temp_dir)
except (tarfile.ReadError, IOError) as err:
    # Clean up in case there is an error during extraction
    shutil.rmtree(temp_dir)
    raise ValueError(str(err))
# Get names of all files with valid image suffixes and create an
# object for each image object
group = []
for img_file in get_image_files(temp_dir, []):
    img_obj = images.create_object(img_file)
    folder = img_file[len(temp_dir):-len(img_obj.name)]
    group.append(GroupImage(
        img_obj.identifier,
        folder,
        img_obj.name,
        img_obj.image_file
    ))
# Create image group
img_grp = image_groups.create_object(
    name,
    group,
    filename,
    object_identifier=args[2],
    read_only=True
)
# Delete the temporary folder
shutil.rmtree(temp_dir)
