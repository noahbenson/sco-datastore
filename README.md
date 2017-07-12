# Standard Cortical Observer - Data Store

Data store API for primary data objects (i.e. experiments, functional data, predictions, images, and subject anatomies) that are managed and manipulated by the Standard Cortical Observer.

The API is a standalone library that provides access to resources that are used as input to run a predictive model and that are generated as output from model runs. The library can be used in an offline setting to manipulate SCO resources without the need to communicate via a Web service.

The current implementation of the data store uses the file system to store files such as images, MRI data, and prediction results. The meta data for SCO resources is being managed in a MongoDB database.
