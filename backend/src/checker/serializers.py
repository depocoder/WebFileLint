from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import File, LintFile


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email"]


class LintFileHyperSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = LintFile
        fields = "__all__"


class LintFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = LintFile
        fields = "__all__"


class DynamicFieldsModelSerializer(serializers.HyperlinkedModelSerializer):
    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop("fields", None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class FileSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = File
        fields = [
            "id",
            "url",
            "file_name",
            "raw_file",
            "status",
            "last_check",
            "user",
            "checks",
        ]

    def validate_raw_file(self, value):
        if value.name.endswith(".py"):
            return value
        raise ValidationError("File must be ending with .py!")


class FileSerializerWithDepth(FileSerializer):
    #  https://stackoverflow.com/questions/58644572/drf-adding-depth-1-to-model-serializer-no-longer-allows-me-to-post
    class Meta:
        model = File
        fields = [
            "id",
            "url",
            "file_name",
            "raw_file",
            "status",
            "last_check",
            "user",
            "checks",
        ]
        depth = 1
