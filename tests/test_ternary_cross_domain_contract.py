import cmath
import itertools
import math
import unittest


T3 = (-1, 0, 1)


def stella_states():
    return tuple(itertools.product(T3, repeat=3))


def shell_count(states):
    counts = {0: 0, 1: 0, 2: 0, 3: 0}
    for state in states:
        counts[sum(1 for x in state if x != 0)] += 1
    return counts


def incidence_residual_triangle(t):
    # Oriented triangle: 0->1, 1->2, 2->0.
    # B rows = vertices, columns = edges.
    return (
        -t[0] + t[2],
        t[0] - t[1],
        t[1] - t[2],
    )


def wilson_from_sum(phases, t):
    phase = sum(c * p for c, p in zip(t, phases))
    return cmath.exp(1j * phase)


def wilson_from_product(phases, t):
    out = 1.0 + 0.0j
    for phase, coeff in zip(phases, t):
        out *= cmath.exp(1j * phase) ** coeff
    return out


def ring_spectrum_three_site(phi):
    # Unit-hopping 3-cycle with total loop flux phi.
    return sorted(
        2.0 * math.cos((phi + 2.0 * math.pi * k) / 3.0)
        for k in range(3)
    )


def sign_quantizer(x, delta=0.0):
    if delta < 0:
        raise ValueError("delta must be >= 0")
    if x < -delta:
        return -1
    if x > delta:
        return 1
    return 0


class TernaryCrossDomainContractTest(unittest.TestCase):
    def test_stella_has_27_states(self):
        self.assertEqual(len(stella_states()), 27)

    def test_stella_shell_decomposition_is_1_6_12_8(self):
        self.assertEqual(shell_count(stella_states()), {0: 1, 1: 6, 2: 12, 3: 8})

    def test_outer_shell_is_exact_cube_vertex_set(self):
        outer = {state for state in stella_states() if all(x != 0 for x in state)}
        cube = set(itertools.product((-1, 1), repeat=3))
        self.assertEqual(outer, cube)

    def test_oriented_triangle_cycle_is_closed(self):
        self.assertEqual(incidence_residual_triangle((1, 1, 1)), (0, 0, 0))
        self.assertEqual(incidence_residual_triangle((-1, -1, -1)), (0, 0, 0))

    def test_wilson_sum_and_product_forms_agree(self):
        phases = (0.2, -0.4, 0.9)
        for t in ((1, 1, 1), (-1, -1, -1), (1, 0, -1)):
            self.assertAlmostEqual(
                abs(wilson_from_sum(phases, t) - wilson_from_product(phases, t)),
                0.0,
                places=12,
            )

    def test_three_site_pi_over_two_flux_normalizes_to_trit(self):
        spectrum = ring_spectrum_three_site(math.pi / 2.0)
        expected = [-math.sqrt(3.0), 0.0, math.sqrt(3.0)]
        for actual, target in zip(spectrum, expected):
            self.assertAlmostEqual(actual, target, places=12)
        normalized = [round(x / math.sqrt(3.0), 12) for x in spectrum]
        self.assertEqual(normalized, [-1.0, 0.0, 1.0])

    def test_gremlin_exchange_distinct_spectrum_has_trit_quotient(self):
        energy = 2.75
        full = (-energy, 0.0, 0.0, energy)
        quotient = {round(x / energy, 12) for x in full}
        self.assertEqual(quotient, {-1.0, 0.0, 1.0})
        self.assertEqual(full.count(0.0), 2)

    def test_sign_quantizer(self):
        self.assertEqual(sign_quantizer(-2.0), -1)
        self.assertEqual(sign_quantizer(0.0), 0)
        self.assertEqual(sign_quantizer(2.0), 1)
        self.assertEqual(sign_quantizer(0.05, delta=0.1), 0)

    def test_ternary_path_sector_not_closed_under_unrestricted_addition(self):
        a = (1, 0, 0)
        b = (1, 0, 0)
        summed = tuple(x + y for x, y in zip(a, b))
        self.assertEqual(summed, (2, 0, 0))
        self.assertFalse(all(x in T3 for x in summed))


if __name__ == "__main__":
    unittest.main()
