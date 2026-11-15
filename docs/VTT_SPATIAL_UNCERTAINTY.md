# Virtual Time Travel Mapping: 2D spatial covariance propagation

## Purpose

The module ssswet_core.vtt_spatial_uncertainty propagates a point's declared
two-dimensional covariance through an already-known rigid rotation and
translation. It supplies a bounded mathematical primitive for the spatial
alignment research programme; it does not estimate a transform, convert a
geographic coordinate reference system, or reconstruct an unrecorded place.

## Model

For a source-frame point x, proper orthonormal rotation R, and target-frame
translation t, the transformed point is:

~~~text
x' = R x + t
~~~

The source point covariance Cx is pushed into the target axes as R Cx Rᵀ.
The function then adds a translation-only covariance Ct:

~~~text
C' = R Cx Rᵀ + Ct
~~~

This addition assumes the point error and translation error are independent
(and therefore have zero cross-covariance). The function does not estimate
or include rotation-parameter uncertainty, correlations between the point and
transform, scale uncertainty, shear, or non-rigid deformation.

## Usage

Run from the core directory:

~~~python
from ssswet_core.vtt_spatial_uncertainty import transform_point_with_covariance

result = transform_point_with_covariance(
    point=[1, 0],
    rotation_matrix=[[0, -1], [1, 0]],
    translation=[10, 20],
    point_covariance=[[4, 0], [0, 1]],
    transform_covariance=[[1, 0], [0, 1]],
    coordinate_unit="m",
)
print(result["transformed_point"])  # [10.0, 21.0]
print(result["covariance"])         # [[2.0, 0.0], [0.0, 5.0]]
~~~

Both covariance matrices are expressed in the square of the same declared
coordinate unit. The coordinate-unit label is metadata only; no unit
conversion is performed.

## Uncertainty ellipse

The output includes eigenvalues and the semi-axis lengths of a nominal
95-percent two-dimensional ellipse. For covariance eigenvalue λ, the
corresponding semi-axis is:

~~~text
a = sqrt(5.991464547107979 × λ)
~~~

The factor is the 95th percentile of a chi-square distribution with two
degrees of freedom. The 95-percent interpretation is conditional on a
bivariate-Gaussian error model and the independence/exact-rotation
assumptions above. It is not an absolute error bound, a guaranteed coverage
rate for arbitrary distributions, or a calibrated GPS accuracy region.

## Validation and limits

- Rotation matrices must be finite, orthonormal, and have determinant +1.
  Reflections and scale/shear matrices are rejected.
- Covariance matrices must be finite, symmetric, and positive semidefinite.
  Tiny negative eigenvalues within a relative floating-point tolerance are
  clipped to zero; materially indefinite matrices are rejected.
- Inputs and outputs are bounded to a finite numeric range.
- Covariance matrices use the same coordinate unit squared. The function
  does not check whether the caller's unit label is truthful.
- The transform is treated as fixed. Translation covariance is the only
  transform uncertainty represented.
- The function operates in a caller-supplied planar coordinate frame. It
  performs no CRS conversion, datum transformation, georeferencing, GPS
  capture, or altitude handling.
- The result does not establish measurement accuracy, landmark independence,
  spatial generalization, or the correctness of the supplied covariance.
- No unrecorded location, historical state, or future state is inferred.

## Privacy and operation

This is a pure Python calculation. It has no browser, IndexedDB, sensor,
filesystem, network, or SSSWET API access. It does not require raw media or
personal identifiers. Callers should keep source observations and any
sensitive coordinate records in their existing local/private storage.

## Regression acceptance criteria

The dedicated tests require:

1. A known 90-degree rotation and translation to produce the expected point
   and covariance exactly within floating-point normalization.
2. An anisotropic covariance to rotate into the target coordinate axes.
3. Zero covariance to produce zero ellipse semi-axes.
4. Reflections, non-orthonormal matrices, asymmetric covariance, and
   materially non-positive-semidefinite covariance to be rejected.
5. Non-finite, malformed, and unsupported numeric inputs to be rejected.
6. Tiny negative eigenvalues attributable to floating-point round-off to be
   clipped without accepting materially indefinite matrices.
7. The output to disclose the Gaussian and independence assumptions and
   explicitly state that geographic conversion and historical recovery were
   not performed.

All acceptance fixtures are synthetic. They validate deterministic
mathematical behaviour, not real-world survey or GPS accuracy.
