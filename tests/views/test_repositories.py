import json

import base
from crane import config


class TestRepository(base.BaseCraneAPITest):
    def test_images(self):
        response = self.test_client.get('/v1/repositories/redhat/foo/images')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.headers['X-Docker-Registry-Config'], 'common')
        self.assertEqual(response.headers['X-Docker-Registry-Version'], '0.6.6')
        self.assertEqual(response.headers['X-Docker-Endpoints'], 'localhost:5000')

        response_data = json.loads(response.data)
        self.assertTrue({'id': 'abc123'} in response_data)
        self.assertTrue({'id': 'xyz789'} in response_data)

    def test_detect_endpoint(self):
        """
        Set the configured endpoint to None, forcing crane to detect what
        host and port are being accessed by the request.
        """
        self.app.config[config.KEY_ENDPOINT] = ''

        response = self.test_client.get('/v1/repositories/redhat/foo/images')

        self.assertEqual(response.status_code, 200)
        # 'localhost' is apparently what flask's test client produces
        self.assertEqual(response.headers['X-Docker-Endpoints'], 'localhost')

    def test_images_no_namespace(self):
        """
        The "bar" repository ID does not have a namespace
        """
        response = self.test_client.get('/v1/repositories/bar/images')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.headers['X-Docker-Registry-Config'], 'common')
        self.assertEqual(response.headers['X-Docker-Registry-Version'], '0.6.6')
        self.assertEqual(response.headers['X-Docker-Endpoints'], 'localhost:5000')

        response_data = json.loads(response.data)
        self.assertTrue({'id': 'def456'} in response_data)

    def test_images_no_namespace_docker_1_3_plus(self):
        """
        The "bar" repository ID does not have a namespace
        """
        response = self.test_client.get('/v1/repositories/library/bar/images')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.headers['X-Docker-Registry-Config'], 'common')
        self.assertEqual(response.headers['X-Docker-Registry-Version'], '0.6.6')
        self.assertEqual(response.headers['X-Docker-Endpoints'], 'localhost:5000')

        response_data = json.loads(response.data)
        self.assertTrue({'id': 'def456'} in response_data)

    def test_images_404(self):
        response = self.test_client.get('/v1/repositories/idontexist/images')

        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.headers['Content-Type'].startswith('text/html'))

    def test_images_too_many_slashes(self):
        """
        The repo_id may have at most one slash. Here we have 3, which should
        cause a 404
        """
        response = self.test_client.get('/v1/repositories/a/b/c/d/images')

        self.assertEqual(response.status_code, 404)

    def test_tags(self):
        response = self.test_client.get('/v1/repositories/redhat/foo/tags')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.headers['X-Docker-Registry-Config'], 'common')
        self.assertEqual(response.headers['X-Docker-Registry-Version'], '0.6.6')

        self.assertEqual(json.loads(response.data), {'test': 'def234', 'latest': 'abc123'})

    def test_tags_no_namespace(self):
        """
        The "bar" repository ID does not have a namespace
        """
        # the docker client adds "library" as the default namespace in this case.
        response = self.test_client.get('/v1/repositories/library/bar/tags')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.headers['X-Docker-Registry-Config'], 'common')
        self.assertEqual(response.headers['X-Docker-Registry-Version'], '0.6.6')

        self.assertEqual(json.loads(response.data), {'latest': 'def456', 'test': 'ghi789'})

    def test_tags_404(self):
        response = self.test_client.get('/v1/repositories/redhat/idontexist/tags')

        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.headers['Content-Type'].startswith('text/html'))

    def test_tags_too_many_slashes(self):
        """
        The repo_id may have at most one slash. Here we have 3, which should
        cause a 404
        """
        response = self.test_client.get('/v1/repositories/a/b/c/d/tags')

        self.assertEqual(response.status_code, 404)

    def test_tag_get_tag(self):
        response = self.test_client.get('/v1/repositories/redhat/foo/tags/test')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.headers['X-Docker-Registry-Config'], 'common')
        self.assertEqual(response.headers['X-Docker-Registry-Version'], '0.6.6')

        self.assertEqual(json.loads(response.data), 'def234')

    def test_tag_get_tag_no_namespace(self):
        """
        The "bar" repository ID does not have a namespace
        """
        # the docker client adds "library" as the default namespace in this case.
        response = self.test_client.get('/v1/repositories/library/bar/tags/test')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.headers['X-Docker-Registry-Config'], 'common')
        self.assertEqual(response.headers['X-Docker-Registry-Version'], '0.6.6')

    def test_tag_get_tag_404(self):
        response = self.test_client.get('/v1/repositories/redhat/idontexist/tag/test')

        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.headers['Content-Type'].startswith('text/html'))

    def test_tag_get_tag_too_many_slashes(self):
        """
        The repo_id may have at most one slash. Here we have 3, which should
        cause a 404
        """
        response = self.test_client.get('/v1/repositories/a/b/c/d/tags/test')

        self.assertEqual(response.status_code, 404)

    def test_tag_get_tag_not_found(self):
        """
        The tag may not exist. Here, nop repo does not have a test tag, which
        should result in a 404
        """
        response = self.test_client.get('/v1/repositories/library/nop/tags/test')

        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.headers['Content-Type'].startswith('text/html'))

    def test_tag_latest(self):
        response = self.test_client.get('/v1/repositories/redhat/foo/tags/latest')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.headers['X-Docker-Registry-Config'], 'common')
        self.assertEqual(response.headers['X-Docker-Registry-Version'], '0.6.6')

        self.assertEqual(json.loads(response.data), 'abc123')

    def test_tag_latest_no_namespace(self):
        """
        The "bar" repository ID does not have a namespace
        """
        # the docker client adds "library" as the default namespace in this case.
        response = self.test_client.get('/v1/repositories/library/bar/tags/latest')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.headers['X-Docker-Registry-Config'], 'common')
        self.assertEqual(response.headers['X-Docker-Registry-Version'], '0.6.6')

    def test_tag_latest_404(self):
        response = self.test_client.get('/v1/repositories/redhat/idontexist/tag/latest')

        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.headers['Content-Type'].startswith('text/html'))

    def test_tag_latest_too_many_slashes(self):
        """
        The repo_id may have at most one slash. Here we have 3, which should
        cause a 404
        """
        response = self.test_client.get('/v1/repositories/a/b/c/d/tags/latest')

        self.assertEqual(response.status_code, 404)

    def test_tag_latest_not_found(self):
        """
        The latest tag may not exist. Here, nop repo does not have a latest tag, which
        should result in a 404
        """
        response = self.test_client.get('/v1/repositories/library/nop/tags/latest')

        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.headers['Content-Type'].startswith('text/html'))
