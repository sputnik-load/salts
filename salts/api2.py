# -*- coding: utf-8 -*-
from rest_framework import routers, serializers, viewsets, generics, filters
from salts.models import TestResult

# Serializers define the API representation.
class TestResultSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    class Meta:
        model = TestResult
        # fields = ('url', 'username', 'email', 'is_staff')

# ViewSets define the view behavior.
class TestResultViewSet(viewsets.ModelViewSet ):
    serializer_class = TestResultSerializer
    queryset = TestResult.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('test_id',)
