# -*- coding: utf-8 -*-
from rest_framework import serializers, viewsets, filters
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User, Group
from salts.models import (TestResult, GeneratorTypeList,
                          GeneratorType, Shooting, Scenario,
                          Tank)
from django.db import connection
from tankmanager import tank_manager
from salts_prj.settings import log
import socket


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
    filter_fields = ('host', 'port')
    queryset = Tank.objects.all()

    def get_queryset(self):
        host = self.request.query_params.get('host', None)
        if not host:
            return super(TankViewSet, self).get_queryset()
        try:
            info = socket.gethostbyname_ex(host)
        except:
            info = None
        if not info:
            log.warning("Invalid '%s' host name is given." % host)
            return Tank.objects.none()
        return Tank.objects.filter(host=info[0])


class ScenarioSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    # group = GroupSerializer()
    class Meta:
        model = Scenario

    def create(self, validated_data):
        scenarios = Scenario.objects.all()
        if scenarios:
            s = scenarios.filter(scenario_path=validated_data.get('scenario_path'))
            if s:
                return s[0]
        new_id = 1
        if scenarios:
            scenarios = scenarios.order_by('-id')
            new_id = scenarios[0].id + 1
        new_scenario = Scenario(id=new_id, scenario_path=validated_data.get('scenario_path'),
                                group=validated_data.get('group'))
        new_scenario.save()
        return new_scenario


class ScenarioViewSet(viewsets.ModelViewSet):
    serializer_class = ScenarioSerializer
    queryset = Scenario.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ("id", "scenario_path", "status")


class ShootingHttpIssue(Exception):
    def __init__(self, errno, msg):
        self.args = (errno, msg)
        self.code = errno
        self.message = msg


class ShootingSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    updated_fields = ['status', 'start', 'finish', 'planned_duration']
    class Meta:
        model = Shooting

    def check_permission(self, key, scenario):
        cursor = connection.cursor()
        cursor.execute(
            """
                SELECT usr_gr.id FROM authtoken_token tok
                JOIN auth_user_groups usr_gr USING(user_id)
                JOIN salts_scenario ti USING(group_id)
                WHERE tok.key = '{token}' AND ti.id = {scenario_id}
            """.format(token=key, scenario_id=scenario.id))
        if not cursor.fetchone():
            token = Token.objects.get(key=key)
            raise ShootingHttpIssue(
                    status.HTTP_403_FORBIDDEN,
                    "Test %s disabled for '%s' user." %
                        (scenario.scenario_path, token.user.username))

    def _get_force_run(self, v):
        if not v:
            v = 0
        return int(v)

    def create(self, validated_data):
        log.info("ShootingSerializer.create. "
                 "validated_data: %s" % validated_data)
        scenario = validated_data.get('scenario')
        tank = validated_data.get('tank')
        if not self._get_force_run(validated_data.get('force_run')):
            self.check_permission(validated_data.get('token'), scenario)
            if not tank_manager.book(tank.id):
                raise ShootingHttpIssue(status.HTTP_403_FORBIDDEN,
                                        "Tank is busy on host %s" % tank.host)
        token = Token.objects.get(key=validated_data.get('token'))
        alt_name = validated_data.get('alt_name')
        if not alt_name:
            alt_name = token.user.username
        sh_data = {'scenario_id': scenario.id,
                   'tank_id': tank.id,
                   'user_id': token.user.id,
                   'status': validated_data.get('status'),
                   'session_id': validated_data.get('session_id'),
                   'ticket_id': validated_data.get('ticket_id'),
                   'alt_name': alt_name}
        shooting = Shooting.objects.create(**sh_data)
        tank_manager.save_to_lock(tank.id, 'session_id',
                                  validated_data.get('session_id'))
        return shooting

    def update(self, instance, validated_data):
        log.info("Shooting. Update: validated_data: %s" % validated_data)
        if not self._get_force_run(validated_data.get('force_run')):
            self.check_permission(validated_data.get('token'),
                                  instance.scenario)

        tank_manager.save_to_lock(instance.tank.id, 'web_console_port',
                                  validated_data.get('web_console_port'))
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
    filter_fields = ('id', 'session_id', 'status')

    def _add_ex_data(self, ex_data, req_data, key):
        value = req_data.get(key)
        if value:
            ex_data[key] = value

    def create(self, request, *args, **kwargs):
        ex_data = {}
        if request.META.get('HTTP_AUTHORIZATION'):
            ex_data['token'] = \
                request.META['HTTP_AUTHORIZATION'].replace('Token ', '')
        self._add_ex_data(ex_data, request.data, 'force_run')
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer, **ex_data)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except ShootingHttpIssue, exc:
            msg = "Shooting HTTP Issue: %s" % exc.message
            log.warning(msg)
            return Response(msg, status=exc.code, content_type='text/html')

    def perform_create(self, serializer, **kwargs):
        serializer.save(**kwargs)

    def update(self, request, *args, **kwargs):
        ex_data = {}
        if request.META.get('HTTP_AUTHORIZATION'):
            ex_data['token'] = \
                request.META['HTTP_AUTHORIZATION'].replace('Token ', '')
        self._add_ex_data(ex_data, request.data, 'force_run')
        self._add_ex_data(ex_data, request.data, 'web_console_port')
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer, **ex_data)
            return Response(serializer.data)
        except ShootingHttpIssue, exc:
            msg = "Shooting HTTP Issue: %s" % exc.message
            log.warning(msg)
            return Response(msg, status=exc.code, content_type='text/html')

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


class UserSerializer(serializers.HyperlinkedModelSerializer):
    # id = serializers.ReadOnlyField()
    class Meta:
        model = User
        fields = ('url', 'username', 'id')


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('username',)

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
    filter_fields = ('session_id',)


class GeneratorTypeListSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    class Meta:
        model = GeneratorTypeList


class GeneratorTypeListViewSet(viewsets.ModelViewSet):
    serializer_class = GeneratorTypeListSerializer
    queryset = GeneratorTypeList.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('name_list',)
