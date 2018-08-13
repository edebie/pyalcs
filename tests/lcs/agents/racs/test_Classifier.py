import pytest
import random

from lcs import Perception
from lcs.agents.racs import Configuration, Condition, Effect, Classifier
from lcs.representations import UBR


class TestClassifier:

    @pytest.fixture
    def cfg(self):
        return Configuration(classifier_length=2,
                             number_of_possible_actions=2,
                             encoder_bits=4)

    def test_should_initialize_without_arguments(self, cfg):
        # when
        c = Classifier(cfg=cfg)

        # then
        assert c.condition == Condition.generic(cfg=cfg)
        assert c.action is None
        assert c.effect == Effect.pass_through(cfg=cfg)
        assert c.exp == 1
        assert c.talp is None
        assert c.tav == 0.0

    @pytest.mark.parametrize("_effect, _p0, _p1, _result", [
        # Classifier with default pass-through effect
        (None, [0.5, 0.5], [0.5, 0.5], True),
        ([UBR(0, 16), UBR(10, 12)], [0.5, 0.5], [0.5, 0.5], False),
        ([UBR(0, 4), UBR(10, 12)], [0.8, 0.8], [0.2, 0.7], True),
    ])
    def test_should_anticipate_change(self, _effect, _p0, _p1, _result, cfg):
        # given
        p0 = Perception(_p0, oktypes=(float,))
        p1 = Perception(_p1, oktypes=(float,))

        c = Classifier(effect=_effect, cfg=cfg)

        # then
        assert c.does_anticipate_correctly(p0, p1) is _result

    def test_should_decrease_quality(self, cfg):
        # given
        cl = Classifier(cfg=cfg)
        assert cl.q == 0.5

        # when
        cl.decrease_quality()

        # then
        assert cl.q == 0.475

    def test_should_create_copy(self, cfg):
        # given
        operation_time = random.randint(0, 100)
        condition = Condition([self._random_ubr(), self._random_ubr()],
                              cfg=cfg)
        action = random.randint(0, 2)
        effect = Effect([self._random_ubr(), self._random_ubr()], cfg=cfg)

        cl = Classifier(condition, action, effect,
                        quality=random.random(),
                        reward=random.random(),
                        intermediate_reward=random.random(),
                        cfg=cfg)
        # when
        copied_cl = Classifier.copy_from(cl, operation_time)

        # then
        assert cl is not copied_cl
        assert cl.condition == copied_cl.condition
        assert cl.condition is not copied_cl.condition
        assert cl.action == copied_cl.action
        assert cl.effect == copied_cl.effect
        assert cl.effect is not copied_cl.effect
        assert copied_cl.is_marked() is False
        assert cl.r == copied_cl.r
        assert cl.q == copied_cl.q
        assert operation_time == copied_cl.tga
        assert operation_time == copied_cl.talp

    def test_should_specialize(self, cfg):
        # given
        p0 = Perception([random.random()] * 2, oktypes=(float,))
        p1 = Perception([random.random()] * 2, oktypes=(float,))
        cl = Classifier(cfg=cfg)

        # when
        cl.specialize(p0, p1)

        # then
        for condition_ubr, effect_ubr in zip(cl.condition, cl.effect):
            assert condition_ubr.lower_bound == condition_ubr.upper_bound
            assert effect_ubr.lower_bound == effect_ubr.upper_bound

    @staticmethod
    def _random_ubr(lower=0, upper=16):
        return UBR(random.randint(lower, upper), random.randint(lower, upper))