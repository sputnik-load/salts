# -*- coding: utf-8 -*-
from rest_framework import routers, serializers, viewsets, generics, filters
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Permission
from salts.models import (TestResult, GeneratorTypeList,
                          GeneratorType, Shooting, TestIni, Tank)
from django.db import connection
from logger import Logger
from tankmanager import tank_manager


log = Logger.get_logger()


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


class TankSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    class Meta:
        model = Tank


class TankViewSet(viewsets.ModelViewSet):
    serializer_class = TankSerializer
    queryset = Tank.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ("id",)


class ShootingHttpIssue(Exception):
    def __init__(self, errno, msg):
        self.args = (errno, msg)
        self.code = errno
        self.message = msg


class ShootingSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    class Meta:
        model = Shooting

    def create(self, validated_data):
        if "test_ini" not in validated_data:
            raise ShootingHttpIssue(status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    "TestIni object cannot be obtained.")
        ti = validated_data["test_ini"]
        tank = validated_data["tank"]
        cursor = connection.cursor()
        cursor.execute(
            """
                SELECT perm.id
                FROM auth_permission perm
                JOIN auth_user_user_permissions uup ON perm.id = uup.permission_id
                JOIN authtoken_token tok ON tok.user_id = uup.user_id
                WHERE perm.codename ~ ('can_run_' || '{codename}')
                        AND tok.key = '{token}';
            """.format(codename=ti.group_ini.codename,
                       token=validated_data["token"]))
        if not cursor.fetchone():
            token = Token.objects.get(key=validated_data["token"])
            raise ShootingHttpIssue(
                    status.HTTP_403_FORBIDDEN,
                    "Test %s disabled for '%s' user." % (ti.scenario_id, token.user.username))
        if not tank_manager.book(tank.id):
            raise ShootingHttpIssue(status.HTTP_403_FORBIDDEN,
                                    "Tank is busy on host %s" % tank.host)
        sh_data = {"test_ini_id": ti.id, "tank_id": tank.id}
        shooting = Shooting.objects.create(**sh_data)
        return shooting

    def update(self, instance, validated_data):
        log.info("Shooting. Update: validated_data: %s" % validated_data)
        return serializers.HyperlinkedModelSerializer.update(self, instance, validated_data)

class ShootingViewSet(viewsets.ModelViewSet):
    serializer_class = ShootingSerializer
    queryset = Shooting.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ("id",)

    def create(self, request, *args, **kwargs):
        ex_data = {}
        if "HTTP_AUTHORIZATION" in request.META:
            ex_data["token"] = request.META["HTTP_AUTHORIZATION"].replace("Token ", "")
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer, **ex_data)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except ShootingHttpIssue, exc:
            log.warning("Shooting HTTP Issue: %s" % exc.message)
            return Response(status=exc.code)

    def perform_create(self, serializer, **kwargs):
        serializer.save(**kwargs)

    def update(self, instance, validated_data):
        log.info("Shooting. Update. Validated Data: %s" % validated_data)
        fields = []
        for k in validated_data:
            setattr(instance, k,
                    validated_data.get(k, getattr(instance, k)))
            fields.append(k)
        instance.save(update_fields=fields)
        return instance


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
        log.info("TestResult: validated_data: %s" % validated_data)
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
