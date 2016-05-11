# -*- coding: utf-8 -*-
from rest_framework import routers, serializers, viewsets, generics, filters
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Group, Permission
from salts.models import (TestResult, GeneratorTypeList,
                          GeneratorType, Shooting, TestIni,
                          Tank)
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
    filter_fields = ('host', 'port')


class ShootingHttpIssue(Exception):
    def __init__(self, errno, msg):
        self.args = (errno, msg)
        self.code = errno
        self.message = msg


class TestIniSerializer(serializers.HyperlinkedModelSerializer):
    # id = serializers.ReadOnlyField()
    # group = GroupSerializer()
    class Meta:
        model = TestIni
    '''
    def create(self, validated_data):
        log.info("TestIniSerializer.create: validated_data: %s" % validated_data)
        test_ini = TestIni.objects.create(**validated_data)
        test_ini.save()
        return test_ini
    '''

class TestIniViewSet(viewsets.ModelViewSet):
    serializer_class = TestIniSerializer
    queryset = TestIni.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ("id", "scenario_id", "status")
    '''
    def create(self, request, *args, **kwargs):
        log.info("TestIniViewSet.create: request.data: %s" % request.data)
        # return viewsets.ModelViewSet.create(self, request, *args, **kwargs)
        serializer = self.get_serializer(data=request.data)
        log.info("TestIniViewSet.create: serializer: %s" % serializer)
        serializer.is_valid(raise_exception=True)
        log.info("TestIniViewSet.create: is_valid")
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    '''


class ShootingSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    updated_fields = ['status', 'dt_start', 'dt_finish']
    class Meta:
        model = Shooting

    def check_permission(self, key, test_ini_id):
        cursor = connection.cursor()
        cursor.execute(
            """
                SELECT usr_gr.id FROM authtoken_token tok
                JOIN auth_user_groups usr_gr USING(user_id)
                JOIN salts_testini ti USING(group_id)
                WHERE tok.key = '{token}' AND ti.id = {test_ini_id}
            """.format(token=key, test_ini_id=test_ini_id))
        if not cursor.fetchone():
            token = Token.objects.get(key=key)
            raise ShootingHttpIssue(
                    status.HTTP_403_FORBIDDEN,
                    "Test %s disabled for '%s' user." %
                        (test_ini.scenario_id, token.user.username))


    def create(self, validated_data):
        log.info("ShootingSerializer.create. validated_data: %s" % validated_data)
        test_ini = validated_data.get('test_ini')
        tank = validated_data.get('tank')
        self.check_permission(validated_data.get('token'), test_ini.id)
        if not tank_manager.book(tank.id):
            raise ShootingHttpIssue(status.HTTP_403_FORBIDDEN,
                                    "Tank is busy on host %s" % tank.host)
        sh_data = {'test_ini_id': test_ini.id,
                   'tank_id': tank.id,
                   'status': validated_data.get('status'),
                   'test_id': validated_data.get('test_id')}
        shooting = Shooting.objects.create(**sh_data)
        return shooting

    def update(self, instance, validated_data):
        log.info("Shooting. Update: validated_data: %s" % validated_data)
        self.check_permission(validated_data.get('token'), instance.test_ini.id)
        fields = []
        for k in validated_data:
            if k in self.updated_fields:
                setattr(instance, k,
                        validated_data.get(k, getattr(instance, k)))
                fields.append(k)
        instance.save(update_fields=fields)
        return instance


class ShootingViewSet(viewsets.ModelViewSet):
    serializer_class = ShootingSerializer
    queryset = Shooting.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id', 'test_id', 'status', 'dt_start')

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

    def update(self, request, *args, **kwargs):
        ex_data = {}
        if "HTTP_AUTHORIZATION" in request.META:
            ex_data["token"] = request.META["HTTP_AUTHORIZATION"].replace("Token ", "")
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer, **ex_data)
            return Response(serializer.data)
        except ShootingHttpIssue, exc:
            log.warning("Shooting HTTP Issue: %s" % exc.message)
            return Response(status=exc.code)

    def perform_update(self, serializer, **kwargs):
        serializer.save(**kwargs)


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    # id = serializers.ReadOnlyField()
    class Meta:
        model = Group
        fields = ('url', 'name', 'id')


class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    queryset = Group.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('name',)


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
