"""Regression tests for Splashline Showdown match rules."""

from __future__ import annotations

import unittest

from engine.math2d import Vec2

from game.state import MatchPhase, PlayerId, PlayerState, award_point, reset_rally, start_match, switch_turn, tick_match_timer


def _build_match():
    left = PlayerState(PlayerId.LEFT, Vec2(150.0, 200.0), 80.0, 420.0, 300.0)
    right = PlayerState(PlayerId.RIGHT, Vec2(850.0, 200.0), 680.0, 1020.0, 300.0)
    match = start_match(left, right, shots_per_turn=2, match_duration=10.0, score_cap=3)
    reset_rally(match, starting_player=PlayerId.LEFT)
    return match


class MatchStateTests(unittest.TestCase):
    def test_award_point_goes_to_opposite_side(self) -> None:
        match = _build_match()

        winner = award_point(match, water_side=PlayerId.LEFT)

        self.assertEqual(winner, PlayerId.RIGHT)
        self.assertEqual(match.right_player.score, 1)
        self.assertEqual(match.phase, MatchPhase.POINT_SCORED)

    def test_switch_turn_refills_shots(self) -> None:
        match = _build_match()
        match.turn.shots_left = 0
        match.turn.cooldown_remaining = 1.0

        active = switch_turn(match)

        self.assertEqual(active, PlayerId.RIGHT)
        self.assertEqual(match.turn.shots_left, 2)
        self.assertEqual(match.turn.cooldown_remaining, 0.0)

    def test_reset_rally_hands_next_turn_to_point_loser(self) -> None:
        match = _build_match()
        award_point(match, water_side=PlayerId.LEFT)

        reset_rally(match)

        self.assertEqual(match.turn.active_player, PlayerId.LEFT)
        self.assertEqual(match.phase, MatchPhase.RALLY)
        self.assertEqual(match.rally_index, 2)

    def test_timer_expiry_with_lead_ends_match(self) -> None:
        match = _build_match()
        match.left_player.score = 2
        match.right_player.score = 1

        tick_match_timer(match, 10.0)

        self.assertEqual(match.winner, PlayerId.LEFT)
        self.assertEqual(match.phase, MatchPhase.GAME_OVER)
        self.assertEqual(match.timer_remaining, 0.0)

    def test_tied_timer_enters_sudden_death(self) -> None:
        match = _build_match()
        match.left_player.score = 1
        match.right_player.score = 1

        tick_match_timer(match, 10.0)

        self.assertTrue(match.sudden_death)
        self.assertIsNone(match.winner)
        self.assertEqual(match.phase, MatchPhase.RALLY)

    def test_sudden_death_point_sets_winner(self) -> None:
        match = _build_match()
        match.left_player.score = 2
        match.right_player.score = 2
        match.timer_remaining = 0.0
        match.sudden_death = True

        winner = award_point(match, water_side=PlayerId.RIGHT)

        self.assertEqual(winner, PlayerId.LEFT)
        self.assertEqual(match.winner, PlayerId.LEFT)
        self.assertEqual(match.phase, MatchPhase.GAME_OVER)


if __name__ == "__main__":
    unittest.main()
