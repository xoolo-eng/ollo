from ollo import models


class Object1(models.Model):

    class Meta:
        db = "test"
        collection = "test_coll"
