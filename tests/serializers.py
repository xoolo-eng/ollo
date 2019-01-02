from ollo import serializers
from models import Object3
import asyncio


class TestSerializer(serializers.ModelSerializer):
    uuid = serializers.IntegerField()

    class Meta:
        model = Object3
        fields = "__all__"

    async def validate(self, data):
        await asyncio.sleep(1)
        self.add_error("guid", "Error")
        raise self.ValidateError("Non field error")
        print("validate")

    async def validate_uuid(self, field):
        await asyncio.sleep(1)
        raise self.ValidateError("uuid error")
        print("validage_uuid")
