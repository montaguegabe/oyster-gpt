from rest_framework import serializers

MAX_MESSAGES = 39
MAX_MESSAGE_LENGTH = 1000


class MessageSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=["user", "assistant"])
    content = serializers.CharField(max_length=MAX_MESSAGE_LENGTH)


class ChatSerializer(serializers.Serializer):
    messages = serializers.ListField(
        child=MessageSerializer(), min_length=1, max_length=MAX_MESSAGES
    )

    def validate_messages(self, messages):
        if messages[0]["role"] != "user" or messages[-1]["role"] != "user":
            raise serializers.ValidationError(
                "The conversation must start and end with a human message."
            )
        return messages
