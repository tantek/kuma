from hashlib import md5

import logging
import zipfile
import tarfile

from django import forms

from django.utils.encoding import smart_unicode, smart_str

from django.conf import settings

from django.utils.translation import ugettext_lazy as _

from django.db import models

from django.contrib.auth.models import User, AnonymousUser

from django.core.exceptions import ObjectDoesNotExist
from django.core import validators
from django.core.exceptions import ValidationError
#from uni_form.helpers import FormHelper, Submit, Reset
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile

from . import (scale_image, TAG_DESCRIPTIONS)
from .models import Submission

from captcha.fields import ReCaptchaField

import django.forms.fields
from django.forms.widgets import CheckboxSelectMultiple

import constance.config

from taggit_extras.utils import parse_tags, split_strip


try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    from PIL import Image
except ImportError:
    import Image


SCREENSHOT_MAXW  = getattr(settings, 'DEMO_SCREENSHOT_MAX_WIDTH', 480)
SCREENSHOT_MAXH = getattr(settings, 'DEMO_SCREENSHOT_MAX_HEIGHT', 360)


class MyModelForm(forms.ModelForm):
    def as_ul(self):
        "Returns this form rendered as HTML <li>s -- excluding the <ul></ul>."
        return self._html_output(
            normal_row = u'<li%(html_class_attr)s>%(label)s %(field)s%(help_text)s%(errors)s</li>',
            error_row = u'<li>%s</li>',
            row_ender = '</li>',
            help_text_html = u' <p class="help">%s</p>',
            errors_on_separate_row = False)


class MyForm(forms.Form):
    def as_ul(self):
        "Returns this form rendered as HTML <li>s -- excluding the <ul></ul>."
        return self._html_output(
            normal_row = u'<li%(html_class_attr)s>%(label)s %(field)s%(help_text)s%(errors)s</li>',
            error_row = u'<li>%s</li>',
            row_ender = '</li>',
            help_text_html = u' <p class="help">%s</p>',
            errors_on_separate_row = False)


class SubmissionEditForm(MyModelForm):
    """Form accepting demo submissions"""

    class Meta:
        model = Submission
        widgets = {
            'navbar_optout': forms.Select
        }
        fields = (
            'title', 'summary', 'description', 'hidden',
            'tech_tags', 'challenge_tags',
            'screenshot_1', 'screenshot_2', 'screenshot_3', 
            'screenshot_4', 'screenshot_5', 
            'video_url', 'navbar_optout',
            'demo_package', 'source_code_url', 'license_name',
        )

    # Assemble tech tag choices from TAG_DESCRIPTIONS
    tech_tags = forms.MultipleChoiceField(
        label = "Tech tags",
        widget = CheckboxSelectMultiple,
        required = False,
        choices = ( 
            (x['tag_name'], x['title']) 
            for x in TAG_DESCRIPTIONS.values() 
            if x['tag_name'].startswith('tech:')
        )
    )

    challenge_tags = forms.MultipleChoiceField(
        label = "Dev Derby Challenge tags",
        widget = CheckboxSelectMultiple,
        required = False,
        choices = (
            (TAG_DESCRIPTIONS[x]['tag_name'], TAG_DESCRIPTIONS[x]['title'])
            for x in parse_tags(
                constance.config.DEMOS_DEVDERBY_CHALLENGE_CHOICE_TAGS, 
                sorted=False)
        )
    )

    def __init__(self, *args, **kwargs):

        # Set the request user, for tag namespace permissions
        self.request_user = kwargs.get('request_user', AnonymousUser)
        del kwargs['request_user']

        # Hit up the super class for init
        super(SubmissionEditForm, self).__init__(*args, **kwargs)

        # Initialize form with namespaced tags.
        instance = kwargs.get('instance', None)
        if instance:
            for ns in ('tech', 'challenge'):
                self.initial['%s_tags' % ns] = [t.name 
                    for t in instance.taggit_tags.all_ns('%s:' % ns)]

    def clean(self):
        cleaned_data = super(SubmissionEditForm, self).clean()

        # If we have a demo_package, try validating it.
        if 'demo_package' in self.files:
            try:
                demo_package = self.files['demo_package']
                Submission.validate_demo_zipfile(demo_package)
            except ValidationError, e:
                self._errors['demo_package'] = self.error_class(e.messages)

        return cleaned_data

    def save(self, commit=True):
        rv = super(SubmissionEditForm,self).save(commit)
        
        # HACK: Since django.forms.models does this in a hack, we have to mimic
        # the hack to override it.
        super_save_m2m = hasattr(self, 'save_m2m') and self.save_m2m or None
        def save_m2m():
            if super_save_m2m: super_save_m2m()
            for ns in ('tech', 'challenge'):
                self.instance.taggit_tags.set_ns('%s:' % ns,
                    *self.cleaned_data.get('%s_tags' % ns, []))

        if commit: save_m2m()
        else: self.save_m2m = save_m2m

        return rv


class SubmissionNewForm(SubmissionEditForm):

    class Meta(SubmissionEditForm.Meta):
        fields = SubmissionEditForm.Meta.fields + ( 'captcha', 'accept_terms', )

    captcha = ReCaptchaField(label=_("Show us you're human")) 
    accept_terms = forms.BooleanField(initial=False, required=True)

    def __init__(self, *args, **kwargs):
        super(SubmissionNewForm, self).__init__(*args, **kwargs)
        if not settings.RECAPTCHA_PRIVATE_KEY:
            del self.fields['captcha']
