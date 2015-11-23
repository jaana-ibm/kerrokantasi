import pytest
from django.contrib.auth import get_user_model
from kk.enums import SectionType, Commenting
from kk.factories.hearing import HearingFactory, LabelFactory
from kk.models import Hearing, Section, Label
from kk.tests.utils import create_default_images, assert_ascending_sequence
from rest_framework.test import APIClient


@pytest.fixture()
def default_hearing():
    """
    Fixture for a "default" hearing with three sections (one introduction, two sections).
    All objects will have the 3 default images attached.
    All objects will allow open commenting.
    """
    hearing = Hearing.objects.create(abstract='Default test hearing One', commenting=Commenting.OPEN)
    create_default_images(hearing)
    for x in range(1, 4):
        section = Section.objects.create(
            abstract='Section %d abstract' % x,
            hearing=hearing,
            type=(SectionType.INTRODUCTION if x == 1 else SectionType.SCENARIO),
            commenting=Commenting.OPEN
        )
        create_default_images(section)
    assert_ascending_sequence([s.ordering for s in hearing.sections.all()])
    return hearing


@pytest.fixture()
def random_hearing():
    if not Label.objects.exists():
        LabelFactory()
    return HearingFactory()


@pytest.fixture()
def random_label():
    return LabelFactory()


@pytest.fixture()
def john_doe():
    user = get_user_model().objects.filter(username="john_doe").first()
    if not user:
        user = get_user_model().objects.create_user("john_doe", "john@example.com", password="password")
    return user


@pytest.fixture()
def john_doe_api_client(john_doe):
    api_client = APIClient()
    api_client.login(username=john_doe.username, password="password")
    return api_client


@pytest.fixture()
def admin_api_client(admin_user):
    api_client = APIClient()
    api_client.login(username=admin_user.username, password="password")
    return api_client
