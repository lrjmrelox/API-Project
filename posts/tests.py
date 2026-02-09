from django.test import TestCase
from factories.post_factory import PostFactory
from posts.models import Post

class PostFactoryTest(TestCase):
    def test_create_text_post(self):
        post = PostFactory.create_post(post_type='text', title='Test Text Post', content='Hello World')
        self.assertEqual(post.title, 'Test Text Post')
        self.assertEqual(post.post_type, 'text')
        self.assertEqual(post.content, 'Hello World')

    def test_create_image_post_without_file_size_raises_error(self):
        with self.assertRaises(ValueError) as context:
            PostFactory.create_post(post_type='image', title='Image Post', metadata={})
        self.assertIn("Image posts require 'file_size' in metadata", str(context.exception))

    def test_create_image_post_success(self):
        post = PostFactory.create_post(post_type='image', title='Image Post', metadata={'file_size': '2MB'})
        self.assertEqual(post.post_type, 'image')
        self.assertEqual(post.metadata['file_size'], '2MB')
