from django.db import models

try:
    from cms.models.pluginmodel import CMSPlugin
    from .campaign import CampaignPage, Campaign
    from .report import Questionaire
    from django.contrib.postgres.fields import JSONField
except ImportError:
    CMSPlugin = None

if CMSPlugin is not None:

    class CampaignRequestsCMSPlugin(CMSPlugin):
        campaign_page = models.ForeignKey(
            CampaignPage, related_name='+',
            on_delete=models.CASCADE
        )

        def __str__(self):
            return str(self.campaign_page)

    class CampaignCMSPlugin(CMSPlugin):
        campaign = models.ForeignKey(
            Campaign, related_name='+',
            on_delete=models.CASCADE
        )

        settings = JSONField(default=dict, blank=True)
        request_extra_text = models.TextField(blank=True)

        def __str__(self):
            return str(self.campaign)

    class CampaignQuestionaireCMSPlugin(CMSPlugin):
        questionaire = models.ForeignKey(
            Questionaire, related_name='+',
            on_delete=models.CASCADE
        )

        def __str__(self):
            return str(self.questionaire)
