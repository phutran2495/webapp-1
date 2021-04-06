import json
import traceback

from botocore.exceptions import ClientError

class SNSWrapper:
    def __init__(self, sns_resource):
        self.sns_resource = sns_resource
        

    def publish_message(self, topic_arn, message):
        try:
            response = self.sns_resource.publish(TopicArn=topic_arn, Message=json.dumps(message))
            print(response)
            message_id = response['MessageId']
            self.logger.info(
                "Published message to topic %s.",
                topic_arn)
        except ClientError:

            print("error occurred when sending message")
            print(traceback.format_exc())
        else:
            return message_id