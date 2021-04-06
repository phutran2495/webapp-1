import json


class SNSWrapper:
    def __init__(self, sns_resource):
        self.sns_resource = sns_resource
        

    def publish_message(self, topic_arn, message):
        try:
            response = self.sns_resource.publish(TopicArn=topic_arn, Message=json.dumps(message))
           
        except:
            print("error occurred when sending message")
            