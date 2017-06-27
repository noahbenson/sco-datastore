# Standard Cortical Observer Data Store - Changelog

### 0.1.0 - 2017-03-13

* Initial Version

### 0.2.0 - 2017-03-16

* Create individual API methods for changing the state of a model run

### 0.3.0 - 2017-03-18

* Remove type definitions and type validation for image group options and model run arguments. Type names and definitions may change over time and the data store is now agnostic to value data types.
* Add model reference to model run

### 0.4.0 - 2017-03-20

* Add constraints for funtional data uploads
* Provide access to files in uploaded functional data archives

### 0.4.1 - 2017-03-20

* Bug fix for download experiment fMRI data

### 0.4.2 - 2017-03-21

* Bug fix for download prediction result data

### 0.4.3 - 2017-04-19

* Allow upload of NIfTI-files for functional data

### 0.4.4 - 2017-04-19

* Avoid duplication of uploaded functional data files if they are not tar-archives.

### 0.5.0 - 2017-05-04

* Add property list as parameter at image object creation
* Remove data_files dictionary from FunctionalDataHandle
* Rename module prediction to modelrun
* Add suffix \_id to object properties that contain object references
* Change list of valid functional image file suffixes
* Remove separation between data dir/file and upload dir/file for functional data. Expects a single functional data file.
* Move validation of attribute lists to module attributes
* Add class for attribute definitions
* Add listing of supported image group options definitions
* Add model run data file attachments

### 0.5.1 - 2017-05-04

* Add mime type information to attachment descriptions (for data files only)
* Add Attachment class


### 0.5.2 - 2017-05-19

* Add drop_database to MongoClientFactory to allow database initialization


### 0.6.0 - 2017-06-27

* Add optional Mime-type parameter for prediction attachments
* Add MongoDBStore.clear_collection() to remove all objects in a collection
* Remove attachment types
