"""Pure gameplay state for Splashline Showdown."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from engine.math2d import Vec2


class PlayerId(str, Enum):
    """Logical player ownership identifiers."""

    LEFT = "left"
    RIGHT = "right"

    def opponent(self) -> "PlayerId":
        return PlayerId.RIGHT if self is PlayerId.LEFT else PlayerId.LEFT


class MatchPhase(str, Enum):
    """High-level match lifecycle states."""

    READY = "ready"
    RALLY = "rally"
    POINT_SCORED = "point_scored"
    GAME_OVER = "game_over"


@dataclass(slots=True)
class PlayerState:
    """Runtime state for one local player lane."""

    player_id: PlayerId
    position: Vec2
    movement_min_x: float
    movement_max_x: float
    speed: float
    score: int = 0
    effect_timers: dict[str, float] = field(default_factory=dict)


@dataclass(slots=True)
class TurnState:
    """Turn ownership and shooting budget."""

    active_player: PlayerId
    shots_left: int
    cooldown_remaining: float = 0.0
    awaiting_cross: bool = False
    out_of_ammo_timer: float = 0.0


@dataclass(slots=True)
class MatchState:
    """Whole-match state with two players and a single shared turn."""

    left_player: PlayerState
    right_player: PlayerState
    turn: TurnState
    phase: MatchPhase
    timer_remaining: float
    match_duration: float
    score_cap: int
    shots_per_turn: int
    rally_index: int = 0
    winner: PlayerId | None = None
    sudden_death: bool = False
    last_point_winner: PlayerId | None = None

    def player(self, player_id: PlayerId) -> PlayerState:
        return self.left_player if player_id is PlayerId.LEFT else self.right_player

    def players(self) -> tuple[PlayerState, PlayerState]:
        return self.left_player, self.right_player


def start_match(
    left_player: PlayerState,
    right_player: PlayerState,
    shots_per_turn: int,
    match_duration: float,
    score_cap: int,
    starting_player: PlayerId = PlayerId.LEFT,
) -> MatchState:
    """Create a fresh match state with zeroed scores."""

    left_player.score = 0
    right_player.score = 0
    left_player.effect_timers.clear()
    right_player.effect_timers.clear()
    return MatchState(
        left_player=left_player,
        right_player=right_player,
        turn=TurnState(active_player=starting_player, shots_left=shots_per_turn),
        phase=MatchPhase.READY,
        timer_remaining=match_duration,
        match_duration=match_duration,
        score_cap=score_cap,
        shots_per_turn=shots_per_turn,
    )


def reset_rally(match: MatchState, starting_player: PlayerId | None = None) -> None:
    """Advance to the next rally and refresh turn budget."""

    if match.phase is MatchPhase.GAME_OVER:
        return

    if starting_player is None:
        if match.last_point_winner is not None:
            starting_player = match.last_point_winner.opponent()
        else:
            starting_player = match.turn.active_player

    match.rally_index += 1
    match.phase = MatchPhase.RALLY
    match.turn.active_player = starting_player
    match.turn.shots_left = match.shots_per_turn
    match.turn.cooldown_remaining = 0.0
    match.turn.awaiting_cross = False
    match.turn.out_of_ammo_timer = 0.0


def switch_turn(match: MatchState) -> PlayerId:
    """Hand the rally to the other player and refill shots."""

    match.turn.active_player = match.turn.active_player.opponent()
    match.turn.shots_left = match.shots_per_turn
    match.turn.cooldown_remaining = 0.0
    match.turn.awaiting_cross = False
    match.turn.out_of_ammo_timer = 0.0
    return match.turn.active_player


def award_point(
    match: MatchState,
    water_side: PlayerId | None,
    last_side: PlayerId | None = None,
) -> PlayerId:
    """Award one rally point to the player opposite the water-contact side."""

    resolved_side = water_side or last_side or PlayerId.LEFT
    point_winner = resolved_side.opponent()
    player = match.player(point_winner)
    player.score += 1

    match.phase = MatchPhase.POINT_SCORED
    match.last_point_winner = point_winner
    if player.score >= match.score_cap:
        match.winner = point_winner
        match.phase = MatchPhase.GAME_OVER
        match.sudden_death = False
        return point_winner

    if match.timer_remaining <= 0.0:
        if match.left_player.score != match.right_player.score:
            match.winner = (
                PlayerId.LEFT
                if match.left_player.score > match.right_player.score
                else PlayerId.RIGHT
            )
            match.phase = MatchPhase.GAME_OVER
            match.sudden_death = False
        else:
            match.sudden_death = True
    return point_winner


def tick_match_timer(match: MatchState, dt: float) -> None:
    """Advance the countdown timer and resolve timer-based match end."""

    if match.phase is not MatchPhase.RALLY or match.winner is not None or match.sudden_death:
        return

    match.timer_remaining = max(0.0, match.timer_remaining - dt)
    if match.timer_remaining > 0.0:
        return

    if match.left_player.score != match.right_player.score:
        match.winner = (
            PlayerId.LEFT
            if match.left_player.score > match.right_player.score
            else PlayerId.RIGHT
        )
        match.phase = MatchPhase.GAME_OVER
    else:
        match.sudden_death = True
