"""Interface to s3 for attaskcreator."""
import os
import boto3
import botocore
# from attaskcreator import exceptions


def make_url(filename, bucket):
    """Upload a file to an s3 bucket and return a presigned url for that
    file."""
    s3client = boto3.client('s3')
    basename = 'garbagefiles/' + os.path.basename(filename)
    # logger = daiquiri.getLogger(__name__)
    # try:
    s3client.upload_file(filename, bucket, basename)
    # except OSError:
    #    logger.error(
    #        '{} could not be found. File will not be uploaded.'.format(
    #            filename))
    #    raise exceptions.NoAttachmentError
    # except botocore.exceptions.BotoCoreError as err:
    #     logger.error('{} could not be uploaded to s3. Details: {}'.format(
    #         filename, err))
    #     # raise exceptions.NoAttachmentError

    return s3client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': bucket,
            'Key': basename
        }
    )
