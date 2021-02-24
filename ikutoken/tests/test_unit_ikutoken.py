from ..ikutoken import IkuToken
from tbears.libs.scoretest.score_test_case import ScoreTestCase


class TestIkuToken(ScoreTestCase):

    def setUp(self):
        super().setUp()
        self.score = self.get_score_instance(IkuToken, self.test_account1)

    def test_hello(self):
        self.assertEqual(self.score.hello(), "Hello")
