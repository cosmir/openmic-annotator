from gcloud import storage
import logging

logger = logging.getLogger(__name__)


class Storage(object):

    def __init__(self, name, project_id, testing=False):
        self.name = name
        self.project_id = project_id
        self._testing = testing

    @property
    def client(self):
        return storage.Client(project=self.project_id)

    def upload(self, fdata, key):
        """Upload a local file to GCS.

        Parameters
        ----------
        fdata : str
            File's bytestream.

        key : str
            Key for writing the file data.

        Returns
        -------
        nothing?
            Not sure what a sane response object is here.
        """
        logger.debug("Uploading to {}: {}".format(key, fdata))
        if self._testing:
            logger.info("In test-mode, skipping upload.")
            return

        bucket = self.client.get_bucket(CLOUD_STORAGE_BUCKET)
        blob = bucket.blob(key)
        blob.upload_from_string(fdata, content_type="application/octet-stream")
        return
