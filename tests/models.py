from ollo import models


class Object1(models.Model):

    class Meta:
        db = "test"
        collection = "test_coll"


class Object2(models.Model):

    index = models.IntegerField()
    guid = models.StringField(
        max_length=36
    )
    isActive = models.BooleanField()
    name = models.ObjectField()
    tags = models.ArrayField()

    class Meta:
        db = "test"
        collection = "test_coll"


class Object3(models.Model):

    index = models.StringField()
    guid = models.IntegerField()
    isActive = models.DateField()
    name = models.ArrayField()
    tags = models.ObjectField()

    class Meta:
        db = "test"
        collection = "test_coll"


class Object4(models.Model):

    date1 = models.DateField()
    date2 = models.DataTimeField()

    class Meta:
        db = "test"
        collection = "data_test"


class Object5(models.Model):

    date1 = models.DateField(format="%Y-%m-%d")
    date2 = models.DataTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        db = "test"
        collection = "data_test"
