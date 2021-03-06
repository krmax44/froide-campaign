import json
import logging

from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from froide.foirequest.models.request import Resolution
from froide.foirequest.views import MakeRequestView

from .models import (CampaignRequestsCMSPlugin,
                     InformationObject,
                     CampaignSubscription,
                     CampaignCMSPlugin,
                     CampaignQuestionaireCMSPlugin)

from .serializers import InformationObjectSerializer
from .providers import BaseProvider

try:
    from django.contrib.gis.geoip2 import GeoIP2
except ImportError:
    GeoIP2 = None

from froide.helper.utils import get_client_ip

logger = logging.getLogger(__name__)


@plugin_pool.register_plugin
class CampaignRequestsPlugin(CMSPluginBase):
    module = _("Campaign")
    name = _("Campaign Requests")
    render_template = "froide_campaign/plugins/campaign_requests.html"
    model = CampaignRequestsCMSPlugin

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        campaigns = instance.campaign_page.campaigns.all()
        iobjs = InformationObject.objects.filter(
            campaign__in=campaigns,
            foirequest__isnull=False
        ).select_related('foirequest')
        context.update({
            'iobjs': iobjs
        })
        return context

@plugin_pool.register_plugin
class CampaignPlugin(CMSPluginBase):
    module = _("Campaign")
    name = _("Campaign Map")
    render_template = "froide_campaign/plugins/campaign_map.html"
    model = CampaignCMSPlugin
    cache = False

    def get_city_from_request(self, request):
        if GeoIP2 is None:
            return

        ip = get_client_ip(request)
        if not ip:
            logger.warning('No IP found on request: %s', request)
            return
        if ip == '127.0.0.1':
            # Access via localhost
            return

        try:
            g = GeoIP2()
        except Exception as e:
            logger.exception(e)
            return
        try:
            result = g.city(ip)
        except Exception as e:
            logger.exception(e)
            return
        if result and result.get('latitude'):
            return result

    def get_map_config(self, request, instance):
        city = self.get_city_from_request(request)
        campaign_id = instance.campaign.id
        law_type = None

        try:
            law_type = instance.campaign.provider_kwargs.get('law_type')
        except AttributeError:
            pass
        add_location_allowed = instance.campaign.get_provider().CREATE_ALLOWED
        plugin_settings = instance.settings
        request_extra_text = instance.request_extra_text

        has_subscription = False
        if request.user.is_authenticated:
            email = request.user.email
            has_subscription = CampaignSubscription.objects.filter(
                email=email, campaign=instance.campaign).exists()

        plugin_settings.update({
            'city': city or {},
            'campaignId': campaign_id,
            'lawType': law_type,
            'addLocationAllowed': add_location_allowed,
            'requestExtraText': request_extra_text,
            'hasSubscription': has_subscription
        })
        return plugin_settings

    def render(self, context, instance, placeholder):

        context = super().render(context, instance, placeholder)
        request = context.get('request')
        fake_make_request_view = MakeRequestView(request=request)

        context.update({
            'config': json.dumps(self.get_map_config(request, instance)),
            'request_config': json.dumps(
                fake_make_request_view.get_js_context()),
            'request_form': fake_make_request_view.get_form(),
            'user_form': fake_make_request_view.get_user_form()
        })
        return context


@plugin_pool.register_plugin
class CampaignQuestionairePlugin(CMSPluginBase):
    module = _("Campaign")
    name = _("Campaign Questionaire")
    render_template = "froide_campaign/plugins/campaign_questionaire.html"
    model = CampaignQuestionaireCMSPlugin
    cache = False

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        iobjs = instance.questionaire.campaign.informationobject_set.all()

        iobjs_success = iobjs.filter(
            report__isnull=True,
            foirequests__resolution=Resolution.SUCCESSFUL)

        provider = BaseProvider(campaign=instance.questionaire.campaign)
        mapping = provider.get_foirequests_mapping(iobjs_success)
        data = [provider.get_provider_item_data(obj, foirequests=mapping)
                for obj in iobjs_success]

        questions = [{'text': question.text,
                      'id': question.id,
                      'options': question.options.split(','),
                      'required': question.is_required,
                      'helptext': question.help_text
                      }
                     for question in instance.questionaire.question_set.all()]

        config = {
            'viewerUrl': static('filingcabinet/viewer/web/viewer.html')
        }

        context.update({
            'questionaire': instance.questionaire.id,
            'informationobjects': json.dumps(data),
            'questions': json.dumps(questions),
            'config': json.dumps(config)
        })
        return context


@plugin_pool.register_plugin
class CampaignListPlugin(CMSPluginBase):
    module = _("Campaign")
    name = _("Campaign List")
    render_template = "froide_campaign/plugins/campaign_list.html"
    model = CampaignCMSPlugin
    cache = False

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        campaign = instance.campaign.id
        config = {
            'campaignId': campaign,
        }
        context.update({
            'config': json.dumps(config)
        })
        return context

