from django.shortcuts import Http404

from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import InformationObject


class InformationObjectSerializer(serializers.HyperlinkedModelSerializer):
    request_url = serializers.CharField(source='make_domain_request_url')
    publicbody_name = serializers.SerializerMethodField(
        source='get_publicbody_name'
    )
    description = serializers.CharField(source='get_description')

    class Meta:

        model = InformationObject
        fields = (
            'title', 'request_url',
            'description', 'publicbody_name'
        )

    def get_publicbody_name(self, obj):
        if obj.publicbody is None:
            return ''
        return obj.publicbody.name


class InformationObjectViewSet(viewsets.ReadOnlyModelViewSet):
    RANDOM_COUNT = 3
    SEARCH_COUNT = 10
    serializer_class = InformationObjectSerializer

    def get_queryset(self):
        return InformationObject.objects.none()

    @action(detail=False, methods=['get'])
    def random(self, request):
        campaign_ids = request.GET.getlist('campaign')
        try:
            campaign_ids = [int(x) for x in campaign_ids]
        except ValueError:
            raise Http404

        qs = InformationObject.objects.filter(
            publicbody__isnull=False,
            campaign_id__in=campaign_ids, foirequest__isnull=True
        ).select_related('campaign', 'publicbody').order_by('?')
        qs = qs[:self.RANDOM_COUNT]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        campaign_ids = request.GET.getlist('campaign')
        try:
            campaign_ids = [int(x) for x in campaign_ids]
        except ValueError:
            raise Http404

        query = request.GET.get('q')
        if not query:
            return Response([])

        filters = {}
        if not request.GET.get('has_request'):
            filters = {
                'foirequest__isnull': True
            }

        qs = InformationObject.objects.filter(
            publicbody__isnull=False,
            campaign_id__in=campaign_ids, **filters
        )
        qs = InformationObject.objects.search(qs, query)
        qs = qs.select_related('campaign', 'publicbody')
        qs = qs[:self.SEARCH_COUNT]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
