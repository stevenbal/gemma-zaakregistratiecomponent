from unittest.mock import patch

from django.test import override_settings

from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.constants import VertrouwelijkheidsAanduiding
from vng_api_common.tests import JWTScopesMixin, get_validation_errors, reverse
from vng_api_common.validators import ResourceValidator, URLValidator
from zds_client.tests.mocks import mock_client

from zrc.datamodel.constants import BetalingsIndicatie
from zrc.datamodel.tests.factories import ZaakFactory
from zrc.tests.utils import ZAAK_WRITE_KWARGS

from ..scopes import (
    SCOPE_ZAKEN_ALLES_LEZEN, SCOPE_ZAKEN_BIJWERKEN, SCOPE_ZAKEN_CREATE
)


class ZaakValidationTests(JWTScopesMixin, APITestCase):

    scopes = [SCOPE_ZAKEN_CREATE]

    @override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_404')
    def test_validate_zaaktype_invalid(self):
        url = reverse('zaak-list')

        response = self.client.post(url, {
            'zaaktype': 'https://example.com/foo/bar',
            'bronorganisatie': '517439943',
            'verantwoordelijkeOrganisatie': '517439943',
            'registratiedatum': '2018-06-11',
            'startdatum': '2018-06-11',
        }, **ZAAK_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        validation_error = get_validation_errors(response, 'zaaktype')
        self.assertEqual(validation_error['code'], URLValidator.code)
        self.assertEqual(validation_error['name'], 'zaaktype')

    @override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_200')
    def test_validate_zaaktype_valid(self):
        url = reverse('zaak-list')

        response = self.client.post(url, {
            'zaaktype': 'https://example.com/foo/bar',
            'vertrouwelijkheidaanduiding': VertrouwelijkheidsAanduiding.openbaar,
            'bronorganisatie': '517439943',
            'verantwoordelijkeOrganisatie': '517439943',
            'registratiedatum': '2018-06-11',
            'startdatum': '2018-06-11',
        }, **ZAAK_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_validation_camelcase(self):
        url = reverse('zaak-list')

        response = self.client.post(url, {}, **ZAAK_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        bad_casing = get_validation_errors(response, 'verantwoordelijke_organisatie')
        self.assertIsNone(bad_casing)

        good_casing = get_validation_errors(response, 'verantwoordelijkeOrganisatie')
        self.assertIsNotNone(good_casing)

    @patch('vng_api_common.validators.fetcher')
    @patch('vng_api_common.validators.obj_has_shape', return_value=False)
    @override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_200')
    def test_validate_communicatiekanaal_invalid(self, mock_has_shape, mock_fetcher):
        url = reverse('zaak-list')
        body = {'communicatiekanaal': 'https://ref.tst.vng.cloud/referentielijsten/api/v1/'}

        response = self.client.post(url, body, **ZAAK_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, 'communicatiekanaal')
        self.assertEqual(error['code'], ResourceValidator.code)

    @patch('vng_api_common.validators.fetcher')
    def test_validate_communicatiekanaal_valid(self, mock_fetcher):
        url = reverse('zaak-list')
        body = {'communicatiekanaal': 'https://example.com/dummy'}

        with override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_200'):
            with patch('vng_api_common.validators.obj_has_shape', return_value=True):
                response = self.client.post(url, body, **ZAAK_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, 'communicatiekanaal')
        self.assertIsNone(error)

    @override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_404')
    def test_relevante_andere_zaken(self):
        url = reverse('zaak-list')

        response = self.client.post(url, {
            'zaaktype': 'https://example.com/foo/bar',
            'bronorganisatie': '517439943',
            'verantwoordelijkeOrganisatie': '517439943',
            'registratiedatum': '2018-06-11',
            'startdatum': '2018-06-11',
            'relevanteAndereZaken': [
                'https://example.com/andereZaak'
            ]
        }, **ZAAK_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        validation_error = get_validation_errors(response, 'relevanteAndereZaken.0')
        self.assertEqual(validation_error['code'], URLValidator.code)

    @override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_200')
    def test_laatste_betaaldatum_betaalindicatie_nvt(self):
        """
        Assert that the field laatsteBetaaldatum may not be set for the NVT
        indication.
        """
        url = reverse('zaak-list')

        # all valid values
        for value in BetalingsIndicatie.values:
            if value == BetalingsIndicatie.nvt:
                continue
            with self.subTest(betalingsindicatie=value):
                response = self.client.post(url, {
                    'zaaktype': 'https://example.com/foo/bar',
                    'vertrouwelijkheidaanduiding': VertrouwelijkheidsAanduiding.openbaar,
                    'bronorganisatie': '517439943',
                    'verantwoordelijkeOrganisatie': '517439943',
                    'registratiedatum': '2018-06-11',
                    'startdatum': '2018-06-11',
                    'betalingsindicatie': value,
                    'laatsteBetaaldatum': '2019-01-01T14:03:00Z',
                }, **ZAAK_WRITE_KWARGS)

                self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # invalid value
        with self.subTest(betalingsindicatie=BetalingsIndicatie.nvt):
            response = self.client.post(url, {
                'zaaktype': 'https://example.com/foo/bar',
                'vertrouwelijkheidaanduiding': VertrouwelijkheidsAanduiding.openbaar,
                'bronorganisatie': '517439943',
                'verantwoordelijkeOrganisatie': '517439943',
                'registratiedatum': '2018-06-11',
                'startdatum': '2018-06-11',
                'betalingsindicatie': BetalingsIndicatie.nvt,
                'laatsteBetaaldatum': '2019-01-01T14:03:00Z',
            }, **ZAAK_WRITE_KWARGS)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            validation_error = get_validation_errors(response, 'laatsteBetaaldatum')
            self.assertEqual(validation_error['code'], 'betaling-nvt')

    @override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_200')
    def test_invalide_product_of_dienst(self):
        url = reverse('zaak-list')

        responses = {
            'https://example.com/zaaktype/123': {
                'url': 'https://example.com/zaaktype/123',
                'productenOfDiensten': [
                    'https://example.com/product/123',
                ]
            }
        }

        with mock_client(responses):
            response = self.client.post(url, {
                'zaaktype': 'https://example.com/zaaktype/123',
                'vertrouwelijkheidaanduiding': VertrouwelijkheidsAanduiding.openbaar,
                'bronorganisatie': '517439943',
                'verantwoordelijkeOrganisatie': '517439943',
                'registratiedatum': '2018-12-24',
                'startdatum': '2018-12-24',
                'productenOfDiensten': ['https://example.com/product/999'],
            }, **ZAAK_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        validation_error = get_validation_errors(response, 'productenOfDiensten')
        self.assertEqual(validation_error['code'], 'invalid-products-services')


@override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_200')
class DeelZaakValidationTests(JWTScopesMixin, APITestCase):
    scopes = [
        SCOPE_ZAKEN_BIJWERKEN,
        SCOPE_ZAKEN_CREATE
    ]
    zaaktypes = ['*']

    def test_cannot_use_self_as_hoofdzaak(self):
        """
        Hoofdzaak moet een andere zaak zijn dan de deelzaak zelf.
        """
        zaak = ZaakFactory.create()
        detail_url = reverse('zaak-detail', kwargs={'uuid': zaak.uuid})

        response = self.client.patch(
            detail_url,
            {'hoofdzaak': detail_url},
            **ZAAK_WRITE_KWARGS
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, 'hoofdzaak')
        self.assertEqual(error['code'], 'self-forbidden')

    def test_cannot_have_multiple_levels(self):
        """
        Deelzaak kan enkel deelzaak zijn van hoofdzaak en niet andere deelzaken.
        """
        url = reverse('zaak-list')
        hoofdzaak = ZaakFactory.create()
        deelzaak = ZaakFactory.create(hoofdzaak=hoofdzaak)
        deelzaak_url = reverse('zaak-detail', kwargs={'uuid': deelzaak.uuid})

        response = self.client.post(
            url,
            {'hoofdzaak': deelzaak_url},
            **ZAAK_WRITE_KWARGS
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, 'hoofdzaak')
        self.assertEqual(error['code'], 'deelzaak-als-hoofdzaak')


class ZaakInformatieObjectValidationTests(JWTScopesMixin, APITestCase):

    scopes = [SCOPE_ZAKEN_CREATE]

    @override_settings(
        LINK_FETCHER='vng_api_common.mocks.link_fetcher_404',
        ZDS_CLIENT_CLASS='vng_api_common.mocks.ObjectInformatieObjectClient'
    )
    def test_informatieobject_invalid(self):
        zaak = ZaakFactory.create()
        url = reverse('zaakinformatieobject-list', kwargs={'zaak_uuid': zaak.uuid})

        response = self.client.post(url, {'informatieobject': 'https://drc.nl/api/v1'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        validation_error = get_validation_errors(response, 'informatieobject')
        self.assertEqual(validation_error['code'], URLValidator.code)
        self.assertEqual(validation_error['name'], 'informatieobject')


class FilterValidationTests(JWTScopesMixin, APITestCase):
    """
    Test that incorrect filter usage results in HTTP 400.
    """

    scopes = [SCOPE_ZAKEN_ALLES_LEZEN]

    def test_zaak_invalid_filters(self):
        url = reverse('zaak-list')

        invalid_filters = {
            'zaaktype': '123',
            'bronorganisatie': '123',
            'foo': 'bar',
        }

        for key, value in invalid_filters.items():
            with self.subTest(query_param=key, value=value):
                response = self.client.get(url, {key: value}, **ZAAK_WRITE_KWARGS)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rol_invalid_filters(self):
        url = reverse('rol-list')

        invalid_filters = {
            'zaak': '123',  # must be a url
            'betrokkene': '123',  # must be a url
            'betrokkeneType': 'not-a-valid-choice',  # must be a pre-defined choice
            'rolomschrijving': 'not-a-valid-choice',  # must be a pre-defined choice
            'foo': 'bar',
        }

        for key, value in invalid_filters.items():
            with self.subTest(query_param=key, value=value):
                response = self.client.get(url, {key: value})
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_status_invalid_filters(self):
        url = reverse('status-list')

        invalid_filters = {
            'zaak': '123',  # must be a url
            'statusType': '123',  # must be a url
            'foo': 'bar',
        }

        for key, value in invalid_filters.items():
            with self.subTest(query_param=key, value=value):
                response = self.client.get(url, {key: value})
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
