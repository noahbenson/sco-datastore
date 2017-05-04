"""Predictions - Collection of methods to store and manipulate SCO model runs
and their outputs (predictions).
"""

import datetime
import os
import shutil
import uuid

import attribute
import datastore


# ------------------------------------------------------------------------------
#
# Constants
#
# ------------------------------------------------------------------------------

"""Types of attachments for successful model runs. We currently support two
types of attachments: DATAFILES are individual files that can be accessed via
the API, IMAGEARCHIVES are colleciton of images that can be browsed via the API.
"""
ATTACHMENT_DATAFILE = 'DATAFILE'
ATTACHMENT_IMAGEARCHIVE = 'IMAGEARCHIVE'

# Timestamp of run creation
RUN_CREATED = 'createdAt'
# Timestamp of run start
RUN_STARTED = 'startedAt'
# Timestamp of run end
RUN_FINISHED = 'finishedAt'

# Run states
STATE_FAILED = 'FAILED'
STATE_IDLE = 'IDLE'
STATE_RUNNING = 'RUNNING'
STATE_SUCCESS = 'SUCCESS'


# ------------------------------------------------------------------------------
#
# Model Run State Objects
#
# ------------------------------------------------------------------------------

class ModelRunState(object):
    """Object containing information about the state and potential results or
    error messages generated by a predictive model run. This is considered an
    abstract class that is extended by three sub-classes for states: RUNNING,
    FAILED, and SUCCESS.
    """
    @staticmethod
    def from_json(json_obj):
        # Decide on type of returned object based on fact that failed states
        # have errors while success states have model output
        if json_obj['type'] == STATE_FAILED and 'errors' in json_obj:
            return ModelRunFailed(json_obj['errors'])
        elif json_obj['type'] == STATE_SUCCESS and 'modelOutput' in json_obj:
            return ModelRunSuccess(json_obj['modelOutput'])
        elif json_obj['type'] == STATE_IDLE:
            return ModelRunIdle()
        elif json_obj['type'] == STATE_RUNNING:
            return ModelRunActive()

    @property
    def is_failed(self):
        """Flag indicating if the model run has exited in a failed state.

        Returns
        -------
        Boolean
            True, if model run is in falied state.
        """
        return False

    @property
    def is_idle(self):
        """Flag indicating if the model run is waiting to start execution.

        Returns
        -------
        Boolean
            True, if model run is in idle state.
        """
        return False

    @property
    def is_running(self):
        """Flag indicating if the model run is in a running state.

        Returns
        -------
        Boolean
            True, if model run is in running state.
        """
        return False

    @property
    def is_success(self):
        """Flag indicating if the model run has finished with success.

        Returns
        -------
        Boolean
            True, if model run is in success state.
        """
        return False

    @staticmethod
    def to_json(obj):
        """Generate a JSON serialization for the run state object.

        Returns
        -------
        Json-like object
            Json serialization of model run state object
        """
        # Have text description of state in Json object (for readability)
        json_obj = {'type' : repr(obj)}
        # Add state-specific elements
        if obj.is_failed:
            json_obj['errors'] = obj.errors
        elif obj.is_success:
            json_obj['modelOutput'] = obj.model_output
        return json_obj


class ModelRunActive(ModelRunState):
    """Object indicating an active model run."""
    def __repr__(self):
        """String representation of the run state object."""
        return STATE_RUNNING

    @property
    def is_running(self):
        """Override is_running flag to indicate that this object represents a
        failed model run.
        """
        return True


class ModelRunFailed(ModelRunState):
    """Object indicating a failed model run. Contains a list of error messages
    that may have been generated as result of an exception during model run
    execution.

    Attributes
    ----------
    errors : list(string), optional
        List of error messages
    """
    def __init__(self, errors=[]):
        """Initialize list of errors. Set as an empty list if no error messages
        are given.

        Parameters
        ----------
        errors : list(string), optional
            List of error messages
        """
        self.errors = errors

    def __repr__(self):
        """String representation of the run state object."""
        return STATE_FAILED

    @property
    def is_failed(self):
        """Override is_failed flag to indicate that this object represents a
        failed model run.
        """
        return True


class ModelRunIdle(ModelRunState):
    """Object indicating an idle model run."""
    def __repr__(self):
        """String representation of the run state object."""
        return STATE_IDLE

    @property
    def is_idle(self):
        """Override is_idle flag to indicate that this object represents an
        idle model run.
        """
        return True


class ModelRunSuccess(ModelRunState):
    """Object indicating a succesful completed model run. Contains the result
    of the model run in form of a functional data object (reference).

    Attributes
    ----------
    model_output : string
        Unique identifier of functional data object containing the model run
        output
    """
    def __init__(self, model_output):
        """Initialize reference to model output object.

        Parameters
        ----------
        model_output : string
            Unique identifier of functional data object containing the model run
            output
        """
        self.model_output = model_output

    def __repr__(self):
        """String representation of the run state object."""
        return STATE_SUCCESS

    @property
    def is_success(self):
        """Override is_success flag to indicate that this object represents a
        failed model run.
        """
        return True


# ------------------------------------------------------------------------------
#
# Database Objects
#
# ------------------------------------------------------------------------------


class ModelRunHandle(datastore.DataObjectHandle):
    """Handle to access and manipulate an object representing a model run and
    its state information.

    The status of the model run is maintained as a separate object. A run that
    has completed successfully will have a prediction result associated
    with its state. In case of failure, there will be a list of error
    messages associated with its state.

    The state information is replicated into the properties list to allow
    object listing filters based on run state.

    Attributes
    ----------
    arguments: Dictionary(attribute.Attribute)
        Dictionary of typed attributes defining the image group options
    attachments : dict('id' : 'type')
        Dictionary of post-processing results that are associated with the model
        run. The attachment type (currently DATAFILE or IMAGEARCHIVE) determines
        how to access the attached reource. The attribute value is None if no
        resources have been attached to the model run.
    experiment_id : string
        Unique experiment object identifier
    model_id : string
        Unique model identifier
    schedule : Dictionary(string)
        Timestamps for model run state changes
    state: ModelRunState
        Model run state object
    """
    def __init__(
        self,
        identifier,
        properties,
        directory,
        state,
        experiment_id,
        model_id,
        arguments,
        attachments={},
        schedule=None,
        timestamp=None,
        is_active=True):
        """Initialize the subject handle.

        Parameters
        ----------
        identifier : string
            Unique object identifier
        properties : Dictionary
            Dictionary of experiment specific properties
        directory : string
            Directory on local disk that contains images tar-file file
        state : ModelRunState
            Model run state object
        experiment_id : string
            Unique experiment object identifier
        model_id : string
            Unique model identifier
        arguments: Dictionary(attribute.Attribute)
            Dictionary of typed attributes defining the model run arguments
        attachments : dict('id' : 'type'), optional
            Dictionary of post-processing results that are associated with the
            model run. The attachment type determines how to access the attached
            reource.
        schedule : Dictionary(string), optional
            Timestamps for model run state changes. Only optinal if timestamp is
            missing as well.
        timestamp : datetime, optional
            Time stamp of object creation (UTC).
        is_active : Boolean, optional
            Flag indicating whether the object is active or has been deleted.
        """
        # Initialize super class
        super(ModelRunHandle, self).__init__(
            identifier,
            timestamp,
            properties,
            directory,
            is_active=is_active
        )
        # Initialize class specific Attributes
        self.state = state
        self.experiment_id = experiment_id
        self.model_id = model_id
        self.arguments = arguments
        self.attachments = attachments
        # Set state change information. Only allowed to be missing at run
        # creation, i.e., if timestamp is none.
        if schedule is None:
            if not timestamp is None:
                raise ValueError('missing schedule information')
            self.schedule = {RUN_CREATED : str(self.timestamp.isoformat())}
        else:
            self.schedule = schedule

    @property
    def is_model_run(self):
        """Override the is_model_run property of the base class."""
        return True


# ------------------------------------------------------------------------------
#
# Object Stores
#
# ------------------------------------------------------------------------------

class DefaultModelRunManager(datastore.DefaultObjectStore):
    """Manager for model runs and their outputs.

    This is a default implentation that uses MongoDB as storage backend.
    """
    def __init__(self, mongo_collection, base_directory):
        """Initialize the MongoDB collection and set immutable and mandatory
        properties.

        Parameters
        ----------
        mongo_collection : Collection
            Collection in MongoDB storing model run information
        base_directory : string
            Base directory on local disk for model run resources.
        """
        # Initialize the super class
        super(DefaultModelRunManager, self).__init__(
            mongo_collection,
            base_directory,
            [datastore.PROPERTY_STATE, datastore.PROPERTY_MODEL])

    def create_data_file_attachment(self, identifier, resource_id, filename):
        """Attach a given data file with a model run. The attached file is
        identified by the resource identifier. If a resource with the given
        identifier already exists it will be overwritten.

        Parameters
        ----------
        identifier : string
            Unique model run identifier
        resource_id : string
            Unique attachment identifier
        filename : string
            Path to data file that is being attached. A copy of the file will
            be created

        Returns
        -------
        ModelRunHandle
            Modified model run handle or None if no run with given identifier
            exists
        """
        # Get model run to ensure that it exists
        model_run = self.get_object(identifier)
        if model_run is None:
            return None
        # It is only possible to attach files to successful model run
        if not model_run.state.is_success:
            raise ValueError('cannot attach file to model run in state: ' + str(model_run.state))
        # If an attachment with the given identifier exists it can only be
        # Overwritten if the type of the exosting attachment is DATAFILE.
        if resource_id in model_run.attachments:
            if model_run.attachments[resource_id] != ATTACHMENT_DATAFILE:
                raise ValueError("cannot replace attachment: " + resource_id)
        # The attachment will be written to a directory with name resource_id
        # in the data directory for the model_run. If the directory exists it
        # will be overwritten
        directory = os.path.abspath(
            os.path.join(model_run.directory, resource_id)
        )
        # Make sure that the given resource identifier leads to a sub-folder
        # of the model run's data directory
        if not directory.startswith(os.path.abspath(model_run.directory)):
            raise ValueError('invalid resource identifier: ' + resource_id)
        # Delete directory if exists
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.makedirs(directory)
        shutil.copyfile(
            filename,
            os.path.join(directory, os.path.basename(filename))
        )
        # Update model run information in the database
        model_run.attachments[resource_id] = ATTACHMENT_DATAFILE
        self.replace_object(model_run)
        # Return modified model run
        return model_run

    def create_object(self, name, experiment_id, model_id, arguments=None, properties=None):
        """Create a model run object with the given list of arguments. The
        initial state of the object is RUNNING.

        Parameters
        ----------
        name : string
            User-provided name for the model run
        experiment_id : string
            Unique identifier of associated experiment object
        model_id : string
            Unique model identifier
        arguments : list(dict('name':...,'value:...')), optional
            List of attribute instances
        properties : Dictionary, optional
            Set of model run properties.
        Returns
        -------
        PredictionHandle
            Object handle for created model run
        """
        # Create a new object identifier.
        identifier = str(uuid.uuid4())
        # Directory for successful model run resource files. Directories are
        # simply named by object identifier
        directory = os.path.join(self.directory, identifier)
        # Create the directory if it doesn't exists
        if not os.access(directory, os.F_OK):
            os.makedirs(directory)
        # By default all model runs are in IDLE state at creation
        state = ModelRunIdle()
        # Create the initial set of properties.
        run_properties = {
            datastore.PROPERTY_NAME: name,
            datastore.PROPERTY_STATE: str(state),
            datastore.PROPERTY_MODEL: model_id
        }
        if not properties is None:
            for prop in properties:
                if not prop in run_properties:
                    run_properties[prop] = properties[prop]
        # If argument list is not given then the initial set of arguments is
        # empty. Here we do not validate the given arguments. Definitions of
        # valid argument sets are maintained in the model registry and are not
        # accessible by the model run manager at this point.
        run_arguments = {}
        if not arguments is None:
            for attr in arguments:
                run_arguments[attr['name']] = attribute.Attribute(
                    attr['name'],
                    attr['value']
                )
        # Create the image group object and store it in the database before
        # returning it.
        obj = ModelRunHandle(
            identifier,
            run_properties,
            directory,
            state,
            experiment_id,
            model_id,
            run_arguments
        )
        self.insert_object(obj)
        return obj

    def delete_data_file_attachment(self, identifier, resource_id):
        """Delete attached file with given resource identifier from a mode run.

        Raise ValueError if an image archive with the given resource identifier
        is attached to the model run instead of a data file.

        Parameters
        ----------
        identifier : string
            Unique model run identifier
        resource_id : string
            Unique attachment identifier

        Returns
        -------
        boolean
            True, if file was deleted. False, if no attachment with given
            identifier existed.
        """
        # Get model run to ensure that it exists. If not return False
        model_run = self.get_object(identifier)
        if model_run is None:
            return False
        # Ensure that attachment with given resource identifier exists.
        if not resource_id in model_run.attachments:
            return False
        # Raise an exception if the attached resource is not a data file
        if model_run.attachments[resource_id] != ATTACHMENT_DATAFILE:
            raise ValueError("cannot delete attachment: " + resource_id)
        # Delete resource directory if exists
        directory = os.path.join(model_run.directory, resource_id)
        if os.path.exists(directory):
            shutil.rmtree(directory)
        # Update model run information in the database
        del model_run.attachments[resource_id]
        self.replace_object(model_run)
        return True
        
    def from_json(self, document):
        """Create model run object from JSON document retrieved from database.

        Parameters
        ----------
        document : JSON
            Json document in database

        Returns
        -------
        PredictionHandle
            Handle for model run object
        """
        # Get object identifier from Json document
        identifier = str(document['_id'])
        # Directories are simply named by object identifier
        directory = os.path.join(self.directory, identifier)
        # Create model run handle.
        return ModelRunHandle(
            identifier,
            document['properties'],
            directory,
            ModelRunState.from_json(document['state']),
            document['experiment'],
            document['model'],
            attribute.attributes_from_json(document['arguments']),
            attachments=document['attachments'],
            schedule=document['schedule'],
            timestamp=datetime.datetime.strptime(
                document['timestamp'], '%Y-%m-%dT%H:%M:%S.%f'
            ),
            is_active=document['active']
        )

    def get_data_file_attachment(self, identifier, resource_id):
        """Get path to attached data file with given resource identifer. If no
        data file with given id exists the result will be None.

        Raise ValueError if an image archive with the given resource identifier
        is attached to the model run instead of a data file.

        Parameters
        ----------
        identifier : string
            Unique model run identifier
        resource_id : string
            Unique attachment identifier

        Returns
        -------
        string
            Path to attached data file on disk
        """
        # Get model run to ensure that it exists. If not return None
        model_run = self.get_object(identifier)
        if model_run is None:
            return None
        # Ensure that attachment with given resource identifier exists.
        if not resource_id in model_run.attachments:
            return None
        # Raise an exception if the attached resource is not a data file
        if model_run.attachments[resource_id] != ATTACHMENT_DATAFILE:
            raise ValueError("cannot download attachment: " + resource_id)
        # The attached file is expected to be the only entry in the resource
        # directory
        directory = os.path.join(model_run.directory, resource_id)
        for filename in os.listdir(directory):
            return os.path.abspath(os.path.join(directory, filename))

    def to_json(self, model_run):
        """Create a Json-like dictionary for a model run object. Extends the
        basic object with run state, arguments, and optional prediction results
        or error descriptions.

        Parameters
        ----------
        model_run : PredictionHandle

        Returns
        -------
        (JSON)
            Json-like object, i.e., dictionary.
        """
        # Get the basic Json object from the super class
        json_obj = super(DefaultModelRunManager, self).to_json(model_run)
        # Add run state
        json_obj['state'] = ModelRunState.to_json(model_run.state)
        # Add run scheduling Timestamps
        json_obj['schedule'] = model_run.schedule
        # Add experiment information
        json_obj['experiment'] = model_run.experiment_id
        # Add model information
        json_obj['model'] = model_run.model_id
        # Transform dictionary of attributes into list of key-value pairs.
        json_obj['arguments'] = attribute.attributes_to_json(model_run.arguments)
        # Include attachments
        json_obj['attachments'] = model_run.attachments
        return json_obj

    def update_state(self, identifier, state):
        """Update state of identified model run.

        Raises exception if state change results in invalid run life cycle.

        Parameters
        ----------
        identifier : string
            Unique model run identifier
        state : ModelRunState
            Object representing new run state

        Returns
        -------
        ModelRunHandle
            Modified model run handle or None if no run with given identifier
            exists
        """
        # Get model run to ensure that it exists
        model_run = self.get_object(identifier)
        if model_run is None:
            return None
        # Set timestamp of state change. Raise exception if state change results
        # in invalid life cycle
        timestamp = str(datetime.datetime.utcnow().isoformat())
        if state.is_idle:
            raise ValueError('invalid state change: run cannot become idle')
        elif state.is_running:
            # Current state is required to be IDLE
            if not model_run.state.is_idle:
                raise ValueError('invalid state change: finished run cannot start again')
            model_run.schedule[RUN_STARTED] = timestamp
        elif state.is_failed:
            # Current state is required to be RUNNING
            if not (model_run.state.is_running or model_run.state.is_idle):
                raise ValueError('invalid state change: cannot fail finished run')
            model_run.schedule[RUN_FINISHED] = timestamp
        elif state.is_success:
            # Current state is required to be RUNNING
            if not model_run.state.is_running:
                raise ValueError('invalid state change: cannot finish inactive run')
            model_run.schedule[RUN_FINISHED] = timestamp
        # Update model run state and replace object in database
        model_run.state = state
        model_run.properties[datastore.PROPERTY_STATE] = str(state)
        self.replace_object(model_run)
        # Return modified model run
        return model_run