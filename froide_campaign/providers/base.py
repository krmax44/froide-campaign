from urllib.parse import urlencode

from django.urls import reverse

from ..models import InformationObject
from ..api_views import InformationObjectSerializer


LIMIT = 50


class BaseProvider:

    def __init__(self, campaign, **kwargs):
        self.campaign = campaign
        self.kwargs = kwargs

    def limit(self, qs):
        return qs[:self.kwargs('limit', LIMIT)]

    def search(self, *args, **kwargs):
        iobjs = InformationObject.objects.filter(
            campaign=self.campaign
        )
        if kwargs.get('q'):
            iobjs = InformationObject.objects.search(iobjs, kwargs['q'])
        if kwargs.get('requested'):
            iobjs = iobjs.filter(
                foirequests__isnull=False
            )
        # TODO: geo filter
        # FIXME apply paginator instead of limit
        iobjs = self.limit(iobjs)

        serializer = InformationObjectSerializer(
            iobjs, many=True
        )
        return serializer.data

    def detail(self, ident):
        iobj = self._get_iobj()
        serializer = InformationObjectSerializer(iobj)
        return serializer.data

    def _get_iobj(self, ident):
        return InformationObject.objects.get(
            campaign=self.campaign,
            ident=ident
        )

    def get_publicbody(self, ident):
        try:
            self._get_iobj(ident).publicbody
        except InformationObject.DoesNotExist:
            return

    def make_request_url(self, ident, context):
        publicbody = self.get_publicbody(ident)
        pb_slug = publicbody.slug
        url = reverse('foirequest-make_request', kwargs={
            'publicbody_slug': pb_slug
        })
        subject = self.campaign.get_subject_template().render(context)
        if len(subject) > 250:
            subject = subject[:250] + '...'
        body = self.campaign.get_template().render(context).encode('utf-8')
        ref = ('campaign:%s@%s' % (self.campaign.pk, ident)).encode('utf-8')
        query = {
            'subject': subject.encode('utf-8'),
            'body': body,
            'ref': ref
        }
        hide_features = (
            'hide_public', 'hide_full_text', 'hide_similar', 'hide_publicbody',
            'hide_draft', 'hide_editing'
        )
        query.update({f: b'1' for f in hide_features})
        query = urlencode(query)
        return '%s?%s' % (url, query)
