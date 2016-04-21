# -*- coding: utf-8 -*-
from rest_framework import routers, serializers, viewsets, generics, filters
from rest_framework import authentication, permissions
from salts.models import (TestResult, GeneratorTypeList,
                          GeneratorType, Shooting, TestIni)


from logging import getLogger
log = getLogger("salts")


class GeneratorTypeSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    class Meta:
        model = GeneratorType
        fields = ('id', 'name')


class GeneratorTypeViewSet(viewsets.ModelViewSet):
    serializer_class = GeneratorTypeSerializer
    queryset = GeneratorType.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id', 'name')


class ShootingSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    class Meta:
        model = Shooting


class ShootingViewSet(viewsets.ModelViewSet):
    serializer_class = ShootingSerializer
    queryset = Shooting.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ("id",)

    def create(self, request, *args, **kwargs):
        log.info("Create Shooting: request_body: %s" % request.body)
        log.info("Create Shooting: request: %s" % request.META)
        return viewsets.ModelViewSet.create(self, request, *args, **kwargs)



class TestIniSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    class Meta:
        model = TestIni


class TestIniViewSet(viewsets.ModelViewSet):
    serializer_class = TestIniSerializer
    queryset = TestIni.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ("id", "scenario_id", "status")

# Serializers define the API representation.
class TestResultSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    generator_types = GeneratorTypeSerializer(many=True)
    updated_fields = ["metrics", "jm_jtl", "phout", "yt_log",
                      "jm_log", "yt_conf", "ph_conf", "modified_jmx",
                      "console_log", "report_txt", "jm_log_2",
                      "test_status"]
    class Meta:
        model = TestResult

    def create(self, validated_data):
        log.info("validated_data: %s" % validated_data)
        gt_data = validated_data.pop("generator_types")
        test_result = TestResult.objects.create(**validated_data)
        test_result.save()
        for gt in gt_data:
            for k in gt:
                gen_type = GeneratorType.objects.get(name=gt[k])
                test_result.generator_types.add(gen_type)
        return test_result

    def update(self, instance, validated_data):
        for k in validated_data:
            if k in self.updated_fields:
                setattr(instance, k,
                        validated_data.get(k, getattr(instance, k)))
        instance.save()
        return instance


# ViewSets define the view behavior.
class TestResultViewSet(viewsets.ModelViewSet):
    serializer_class = TestResultSerializer
    queryset = TestResult.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('test_id',)


class GeneratorTypeListSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    class Meta:
        model = GeneratorTypeList


class GeneratorTypeListViewSet(viewsets.ModelViewSet):
    serializer_class = GeneratorTypeListSerializer
    queryset = GeneratorTypeList.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('name_list',)
