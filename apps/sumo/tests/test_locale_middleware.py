from django.test import Client, TestCase


class TestLocaleMiddleware(TestCase):
    client = Client()

    def test_default_redirect(self):
        # User wants en-us, we send en-US
        response = self.client.get('/search', follow=True,
                                   HTTP_ACCEPT_LANGUAGE='en-us')
        self.assertRedirects(response, '/en-US/search', status_code=301)

        # User wants fr-FR, we send fr
        response = self.client.get('/search', follow=True,
                                   HTTP_ACCEPT_LANGUAGE='fr-fr')
        self.assertRedirects(response, '/fr/search', status_code=301)

        # User wants xx, we send en-US
        response = self.client.get('/search', follow=True,
                                   HTTP_ACCEPT_LANGUAGE='xx')
        self.assertRedirects(response, '/en-US/search', status_code=301)

        # User doesn't know what they want, we send en-US
        response = self.client.get('/search', follow=True,
                                   HTTP_ACCEPT_LANGUAGE='')
        self.assertRedirects(response, '/en-US/search', status_code=301)

    def test_specificity(self):
        """Requests for /fr-FR/search should end up on /fr/search"""
        reponse = self.client.get('/fr-FR/search', follow=True)
        self.assertRedirects(reponse, '/fr/search', status_code=301)