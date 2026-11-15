# Virtual Time Travel Mapping: 2D spatial covariance propagation

## Purpose

The module `ssswet_core.vtt_spatial_uncertainty` propagates a declared
two-dimensional point covariance through an already-known rigid rotation
and translation. It supplies a bounded mathematical primitive for the
spatial-alignment research programme; it does not estimate a transform,
convert a geographic coordinate reference system, or reconstruct an
unrecorded place.

The legacy call remains schema version 1 and treats rotation as exact. An
opt-in schema-version-2 call can additionally propagate a caller-declared
scalar rotation-angle variance using a first-order delta-method approximation.

## Model

For a source-frame point x, proper orthonormal rotation R, and target-frame
translation t:

~~~text
x' = R x + t
~~~

The source point covariance Cx is pushed into the target axes as R Cx Rᵀ.
The translation-only covariance Ct is then added:

~~~text
Cbase = R Cx Rᵀ + Ct
~~~

This assumes point and translation errors are independent.

### Optional rotation-parameter uncertainty

When `rotation_variance_radians2` is supplied, it represents the declared
variance of a zero-mean scalar angular perturbation around the nominal
rotation matrix. It is expressed in radians squared. The first-order
Jacobian of the transformed point with respect to that angle is:

~~~text
Jθ = d(R(θ)x)/dθ
~~~

For R = [[cos θ, -sin θ], [sin θ, cos θ]]:

~~~text
Jθ = [-sin θ · x - cos θ · y, cos θ · x - sin θ · y]ᵀ
~~~

The added rotation contribution is:

~~~text
Crotation = Jθ · Var(θ) · Jθᵀ
C' = R Cx Rᵀ + Ct + Crotation
~~~

The implementation evaluates the Jacobian from the supplied rotation matrix.
This is a first-order small-angle approximation. It assumes zero-mean
Gaussian angle error independent of point and translation errors. It omits
higher-order terms, correlations and cross-covariances. The standard
deviation is limited to 0.25 radians; this is a conservative implementation
guard for the linearized model, not an empirically calibrated accuracy
threshold. A caller must not supply an arbitrary value merely to enlarge an
uncertainty ellipse.

If the optional argument is omitted, the function preserves the schema-v1
result and exact-rotation assumption. If it is explicitly supplied as zero,
the function returns schema version 2 and records that zero variance was
declared. Missing rotation uncertainty is never silently converted into a
measured zero.

## Usage

Run from the core directory:

~~~python
from ssswet_core.vtt_spatial_uncertainty import transform_point_with_covariance

result = transform_point_with_covariance(
    point=[2, 0],
    rotation_matrix=[[1, 0], [0, 1]],
    translation=[0, 0],
    point_covariance=[[0, 0], [0, 0]],
    transform_covariance=[[0, 0], [0, 0]],
    coordinate_unit="m",
    rotation_variance_radians2=0.01,
)
print(result["schema_version"])  # 2
print(result["rotation_uncertainty_covariance"])  # [[0, 0], [0, 0.04]]
print(result["covariance"])  # [[0, 0], [0, 0.04]]
~~~

Both input covariance matrices are expressed in the square of the same
declared coordinate unit. The coordinate-unit label is metadata only; no
unit conversion is performed. The angular variance must be in radians².

## Uncertainty ellipse

The output includes eigenvalues and semi-axis lengths of a nominal
95-percent two-dimensional ellipse. For covariance eigenvalue λ, the
corresponding semi-axis is:

~~~text
a = sqrt(5.991464547107979 × λ)
~~~

The factor is the 95th percentile of a chi-square distribution with two
degrees of freedom. The 95-percent interpretation is conditional on a
bivariate-Gaussian error model and the applicable independence and
linearization assumptions. It is not an absolute error bound, guaranteed
coverage for arbitrary distributions, or calibrated GPS accuracy region.

## Validation and limits

- Rotation matrices must be finite, orthonormal, and have determinant +1.
  Reflections and scale/shear matrices are rejected.
- Covariance matrices must be finite, symmetric, and positive semidefinite.
  Tiny negative eigenvalues within a relative floating-point tolerance are
  clipped to zero; materially indefinite matrices are rejected.
- Inputs and outputs are bounded to a finite numeric range.
- The optional angle variance must be finite, non-negative and no greater
  than 0.0625 radians² (standard deviation 0.25 radians).
- The optional rotation contribution is a first-order delta-method result.
  It is not suitable as a general model for large-angle uncertainty,
  multimodal orientation distributions or correlated transform parameters.
- The point and translation covariance matrices use the same coordinate
  unit squared. The function does not check whether the caller's unit label
  is truthful.
- Translation covariance remains translation-only. Rotation/translation
  cross-covariance, point/transform cross-covariance, scale uncertainty,
  shear and non-rigid deformation are not represented.
- The function operates in a caller-supplied planar coordinate frame. It
  performs no CRS conversion, datum transformation, georeferencing, GPS
  capture or altitude handling.
- The result does not establish measurement accuracy, landmark independence,
  spatial generalization or correctness of the supplied covariance.
- No unrecorded location, historical state or future state is inferred.

## Privacy and operation

This is a pure Python calculation. It has no browser, IndexedDB, sensor,
filesystem, network or SSSWET API access. It does not require raw media or
personal identifiers. Callers should keep source observations and any
sensitive coordinate records in their existing local/private storage.

## Regression acceptance criteria

The dedicated tests require:

1. All seven existing schema-v1 behaviours to remain unchanged.
2. An analytic identity-rotation fixture to produce the exact expected
   first-order angular covariance.
3. Rotation uncertainty to combine additively with declared point and
   translation covariance under the stated independence assumptions.
4. Explicit zero angular variance to be distinguished from an omitted
   variance while leaving the numerical covariance unchanged.
5. Negative, boolean, non-finite and over-limit angular variances to be
   rejected; the documented 0.25-radian standard-deviation boundary is
   accepted.
6. A seeded 40,000-sample Monte Carlo fixture with 0.01-radian standard
   deviation to agree with the first-order angular covariance within 4%
   relative tolerance (and 1e-7 absolute tolerance).
7. The output to disclose the Gaussian, independence and first-order
   assumptions and explicitly state that geographic conversion and
   historical recovery were not performed.

The Monte Carlo test is a reproducible synthetic simulation of the declared
small-angle model. It is not measured device performance, a real survey,
empirical calibration or evidence of spatial reconstruction accuracy.
