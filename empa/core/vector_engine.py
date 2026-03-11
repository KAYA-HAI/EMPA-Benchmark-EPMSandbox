"""
Dimension-agnostic vector engine for progress tracking.

Maintains the position vector P_t in an N-dimensional evaluation space,
applies increment vectors v_t from each evaluation cycle, and records
the full trajectory.  All vector operations work with arbitrary dimension
counts — the engine never assumes a specific rubric.
"""

from __future__ import annotations

import math

from typing import Dict, List, Tuple

Vector = Tuple[float, ...]


class TrajectoryPoint(dict):
    """A single point on the evaluation trajectory.

    Behaves as both a dict and an object with attribute access, so
    downstream code can use either ``point['distance']`` or ``point.distance``.
    """

    def __init__(
        self,
        turn: int,
        P_t: Vector,
        v_t: Vector,
        distance: float,
        in_zone: bool,
        epm: Dict | None = None,
        mdep_analysis: Dict | None = None,
    ):
        super().__init__(
            turn=turn, P_t=P_t, v_t=v_t,
            distance=distance, in_zone=in_zone,
        )
        if epm is not None:
            self["epm"] = epm
        if mdep_analysis is not None:
            self["mdep_analysis"] = mdep_analysis

    def __getattr__(self, name: str):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name: str, value):
        self[name] = value


class VectorEngine:
    """
    N-dimensional vector calculator for EPJ/EPM progress tracking.

    Tracks P_t = P_{t-1} + v_t across evaluation cycles and maintains
    the full trajectory with optional EPM energy-dynamics annotations.
    """

    def __init__(
        self,
        n_dims: int,
        epsilon: float = 1.0,
        enable_epm: bool = True,
    ):
        self.n_dims = n_dims
        self.epsilon = epsilon
        self.enable_epm = enable_epm

        self.P_0: Vector | None = None
        self.current_P: Vector | None = None
        self.trajectory: List[TrajectoryPoint] = []

        # EPM v2.0 state
        self.v_star_0: Vector | None = None
        self.E_total: float = 0.0
        self.epsilon_distance: float | None = None
        self.epsilon_direction: float | None = None
        self.epsilon_energy: float | None = None

    # ------------------------------------------------------------------
    # Vector math helpers
    # ------------------------------------------------------------------

    @staticmethod
    def norm(v: Vector) -> float:
        return math.sqrt(sum(x * x for x in v))

    @staticmethod
    def dot(a: Vector, b: Vector) -> float:
        return sum(x * y for x, y in zip(a, b))

    @staticmethod
    def normalize(v: Vector) -> Vector:
        n = VectorEngine.norm(v)
        return tuple(x / n for x in v) if n > 0 else tuple(0.0 for _ in v)

    @staticmethod
    def add(a: Vector, b: Vector) -> Vector:
        return tuple(x + y for x, y in zip(a, b))

    # ------------------------------------------------------------------
    # Zone / distance checks (half-space semantics)
    # ------------------------------------------------------------------

    def check_in_zone(self, P_t: Vector) -> bool:
        """All dimensions >= -epsilon means the deficit is resolved."""
        return all(x >= -self.epsilon for x in P_t)

    def distance_to_zone(self, P_t: Vector) -> float:
        """Euclidean distance from P_t to the target half-space."""
        return math.sqrt(
            sum(
                (-self.epsilon - x) ** 2 if x < -self.epsilon else 0.0
                for x in P_t
            )
        )

    # ------------------------------------------------------------------
    # Initialization (T = 0)
    # ------------------------------------------------------------------

    def initialize(
        self,
        P_0: Vector,
        epm_precomputed: Dict | None = None,
    ) -> TrajectoryPoint:
        """Set the initial deficit vector and record T=0.

        If *epm_precomputed* is given (dict with ``v_star_0``,
        ``epsilon_distance``, etc.) those values are used directly
        instead of being recomputed from P_0.
        """
        assert len(P_0) == self.n_dims
        self.P_0 = P_0
        self.current_P = P_0

        point = TrajectoryPoint(
            turn=0,
            P_t=P_0,
            v_t=tuple(0.0 for _ in range(self.n_dims)),
            distance=self.distance_to_zone(P_0),
            in_zone=self.check_in_zone(P_0),
        )

        if self.enable_epm:
            if epm_precomputed:
                point.epm = self._load_precomputed_epm(P_0, epm_precomputed)
            else:
                point.epm = self._init_epm(P_0)

        self.trajectory.append(point)
        return point

    def _load_precomputed_epm(self, P_0: Vector, pre: Dict) -> Dict:
        """Restore EPM state from precomputed parameters."""
        self.v_star_0 = tuple(pre["v_star_0"])
        self.epsilon_distance = pre["epsilon_distance"]
        self.epsilon_direction = pre["epsilon_direction"]
        self.epsilon_energy = pre["epsilon_energy"]
        self.E_total = 0.0
        p0_norm = pre.get("P_0_norm", self.norm(P_0))
        return {
            "P_norm": round(p0_norm, 4),
            "v_star_0": list(self.v_star_0),
            "E_total": 0.0,
            "projection": round(-p0_norm, 4),
            "alignment": 0.0,
        }

    def _init_epm(self, P_0: Vector, alpha: float = 0.05) -> Dict:
        """Initialize EPM energy-dynamics parameters from P_0."""
        p0_norm = self.norm(P_0)
        self.v_star_0 = tuple(-x / p0_norm for x in P_0) if p0_norm > 0 else tuple(0.0 for _ in P_0)
        self.epsilon_distance = alpha * p0_norm
        self.epsilon_direction = alpha * p0_norm
        self.epsilon_energy = p0_norm
        self.E_total = 0.0

        return {
            "P_norm": round(p0_norm, 4),
            "v_star_0": tuple(round(x, 4) for x in self.v_star_0),
            "E_total": 0.0,
            "projection": round(-p0_norm, 4),
            "alignment": 0.0,
        }

    # ------------------------------------------------------------------
    # Update (T > 0)
    # ------------------------------------------------------------------

    def update(self, v_t: Vector, turn: int, mdep_analysis: Dict | None = None) -> TrajectoryPoint:
        """Apply increment v_t, advance to P_t, and record trajectory."""
        assert self.current_P is not None, "Call initialize() first"
        assert len(v_t) == self.n_dims

        P_t = self.add(self.current_P, v_t)
        self.current_P = P_t

        point = TrajectoryPoint(
            turn=turn,
            P_t=P_t,
            v_t=v_t,
            distance=self.distance_to_zone(P_t),
            in_zone=self.check_in_zone(P_t),
            mdep_analysis=mdep_analysis,
        )

        if self.enable_epm and self.v_star_0 is not None:
            point.epm = self._compute_epm_step(v_t, P_t)

        self.trajectory.append(point)
        return point

    def _compute_epm_step(self, v_t: Vector, P_t: Vector) -> Dict:
        """Compute EPM energy-dynamics metrics for one step."""
        v_norm = self.norm(v_t)
        alignment = self.dot(v_t, self.v_star_0) / v_norm if v_norm > 0 else 0.0
        delta_E = v_norm * alignment
        self.E_total += delta_E

        p_norm = self.norm(P_t)
        projection = self.dot(P_t, self.v_star_0)

        return {
            "v_t_norm": round(v_norm, 4),
            "alignment": round(alignment, 4),
            "delta_E": round(delta_E, 4),
            "E_total": round(self.E_total, 4),
            "P_norm": round(p_norm, 4),
            "projection": round(projection, 4),
        }

    # ------------------------------------------------------------------
    # State queries
    # ------------------------------------------------------------------

    def get_position(self) -> Vector:
        return self.current_P or tuple(0.0 for _ in range(self.n_dims))

    def get_initial_deficit(self) -> Vector:
        return self.P_0 or tuple(0.0 for _ in range(self.n_dims))

    def get_trajectory_dicts(self) -> List[Dict]:
        """Serialize trajectory to plain dicts (JSON-safe)."""
        result = []
        for pt in self.trajectory:
            d: Dict = {
                "turn": pt.turn,
                "P_t": pt.P_t,
                "v_t": pt.v_t,
                "distance": round(pt.distance, 4),
                "in_zone": pt.in_zone,
            }
            if pt.epm is not None:
                d["epm"] = pt.epm
            if pt.mdep_analysis is not None:
                d["mdep_analysis"] = pt.mdep_analysis
            result.append(d)
        return result
