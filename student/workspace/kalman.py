"""Extended Kalman filter helpers for 6D constant-velocity motion.

Part E supplies prediction and correction for docs/HUONG_DAN_KY_THUAT.md §2.
Read the shared time step and process-noise settings with get_tracking_params().
"""

from __future__ import annotations

from typing import Any
from typing import Optional

import numpy as np

Matrix = np.matrix | np.ndarray

from fusion_lab.workspace_support import get_tracking_params


def build_F(dt: Optional[float] = None) -> Matrix:
    """Build the constant-velocity state transition matrix F.

    Args:
        dt: Time step in seconds; default from tracking params.

    Returns:
        6x6 state transition matrix as ``np.matrix``.
    """
    params = get_tracking_params()
    step = params.dt if dt is None else dt
    transition = np.eye(params.dim_state, dtype=float)
    transition[:3, 3:6] = np.eye(3) * step
    return np.asmatrix(transition)


def build_Q(dt: Optional[float] = None, q: Optional[float] = None) -> Matrix:
    """Build the process noise covariance matrix Q.

    Args:
        dt: Time step; default from tracking params.
        q: Process noise scale; default from tracking params.

    Returns:
        6x6 process noise matrix.
    """
    params = get_tracking_params()
    step = params.dt if dt is None else dt
    scale = params.q if q is None else q
    # The lab uses diagonal process noise rather than an acceleration model.
    return np.asmatrix(np.eye(params.dim_state) * step * scale)


def ekf_predict(
    x: Matrix,
    P: Matrix,
    F: Optional[Matrix] = None,
    Q: Optional[Matrix] = None,
) -> tuple[Matrix, Matrix]:
    """Predict state and covariance one time step forward.

    Args:
        x: State vector (6x1).
        P: State covariance (6x6).
        F: Optional transition matrix; build via ``build_F`` if None.
        Q: Optional process noise; build via ``build_Q`` if None.

    Returns:
        Tuple ``(x_pred, P_pred)``.
    """
    transition = np.asarray(build_F() if F is None else F, dtype=float)
    noise = np.asarray(build_Q() if Q is None else Q, dtype=float)
    state = np.asarray(x, dtype=float).reshape(-1, 1)
    covariance = np.asarray(P, dtype=float)
    predicted = transition @ state
    predicted_covariance = transition @ covariance @ transition.T + noise
    return np.asmatrix(predicted), np.asmatrix(predicted_covariance)


def innovation(x: Matrix, meas: Any) -> Matrix:
    """Compute the measurement residual (innovation) gamma.

    Args:
        x: Predicted state.
        meas: Measurement with ``z`` and ``sensor.get_hx(x)``.

    Returns:
        Innovation vector ``z - h(x)``.
    """
    observed = np.asarray(meas.z, dtype=float).reshape(-1, 1)
    predicted = np.asarray(meas.sensor.get_hx(x), dtype=float).reshape(-1, 1)
    return np.asmatrix(observed - predicted)


def innovation_covariance(P: Matrix, meas: Any, H: Matrix) -> Matrix:
    """Compute the innovation covariance S = H P H' + R.

    Args:
        P: State covariance.
        meas: Measurement with ``R``.
        H: Measurement Jacobian.

    Returns:
        Innovation covariance matrix S.
    """
    jacobian = np.asarray(H, dtype=float)
    covariance = np.asarray(P, dtype=float)
    noise = np.asarray(meas.R, dtype=float)
    return np.asmatrix(jacobian @ covariance @ jacobian.T + noise)


def ekf_update(x: Matrix, P: Matrix, meas: Any) -> tuple[Matrix, Matrix]:
    """Apply an EKF measurement update and return updated state and covariance.

    Args:
        x: Prior state.
        P: Prior covariance.
        meas: Associated measurement.

    Returns:
        Tuple ``(x_upd, P_upd)``.
    """
    state = np.asarray(x, dtype=float).reshape(-1, 1)
    covariance = np.asarray(P, dtype=float)
    jacobian = np.asarray(meas.sensor.get_H(x), dtype=float)
    residual = np.asarray(innovation(x, meas))
    residual_covariance = np.asarray(innovation_covariance(P, meas, jacobian))
    cross_covariance = covariance @ jacobian.T
    # Solve for K rather than explicitly inverting the innovation covariance.
    gain = np.linalg.solve(residual_covariance.T, cross_covariance.T).T
    updated = state + gain @ residual
    updated_covariance = (np.eye(state.shape[0]) - gain @ jacobian) @ covariance
    # Restore symmetry after floating-point roundoff.
    updated_covariance = (updated_covariance + updated_covariance.T) / 2.0
    return np.asmatrix(updated), np.asmatrix(updated_covariance)
