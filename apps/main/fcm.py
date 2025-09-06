from firebase_admin import messaging



def subscribe_to_topic(tokens):
    topic = "all"
    response = messaging.subscribe_to_topic(tokens, topic)
    if response.failure_count > 0:
        print(f"Failed to subscribe to topic {topic} due to {list(map(lambda e: e.reason, response.errors))}")


def send_notification_to_all(title, body, image=""):
    topic = "all"
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
            image=image,
        ),
        topic=topic
    )
    messaging.send(message)


def send_notification_some_users(title, body, image, tokens=[]):
    if image == "":
        image = "fcm_test_photo.png"
    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=body,
            image=image
        ),
        tokens=tokens
    )
    messaging.send_each_for_multicast(message)


def send_notification(title, body, for_all, tokens=[], image=""):
    if tokens:
        send_notification_some_users(title, body, image, tokens)
    else:
        send_notification_to_all(title, body, image)