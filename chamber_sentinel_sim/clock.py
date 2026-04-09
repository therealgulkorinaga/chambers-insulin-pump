"""Virtual clock controller for time-accelerated simulation."""

from __future__ import annotations


class SimulationClock:
    """Deterministic virtual clock decoupled from wall-clock time.

    All simulation components MUST use this clock for timestamps.
    Supports pause, resume, step, and arbitrary acceleration.
    """

    def __init__(self, start_time: float = 0.0, tick_minutes: float = 5.0):
        self._time = start_time          # current sim time in minutes from epoch
        self._tick = tick_minutes         # minutes per tick
        self._paused = False
        self._total_ticks = 0

    @property
    def now(self) -> float:
        """Current simulation time in minutes."""
        return self._time

    @property
    def now_hours(self) -> float:
        return self._time / 60.0

    @property
    def now_days(self) -> float:
        return self._time / (60.0 * 24.0)

    @property
    def tick_minutes(self) -> float:
        return self._tick

    @property
    def total_ticks(self) -> int:
        return self._total_ticks

    @property
    def paused(self) -> bool:
        return self._paused

    def advance(self, ticks: int = 1) -> float:
        """Advance the clock by N ticks. Returns new time."""
        if self._paused:
            return self._time
        self._time += self._tick * ticks
        self._total_ticks += ticks
        return self._time

    def pause(self) -> None:
        self._paused = True

    def resume(self) -> None:
        self._paused = False

    def jump_to(self, target_minutes: float) -> None:
        """Jump to a specific time (must be in the future)."""
        if target_minutes > self._time:
            diff_ticks = int((target_minutes - self._time) / self._tick)
            self._time = target_minutes
            self._total_ticks += diff_ticks

    def minutes_to_ticks(self, minutes: float) -> int:
        return max(1, int(minutes / self._tick))

    def days_to_ticks(self, days: float) -> int:
        return self.minutes_to_ticks(days * 24 * 60)

    def __repr__(self) -> str:
        d = self.now_days
        return f"SimClock(day={d:.1f}, tick={self._total_ticks}, paused={self._paused})"
