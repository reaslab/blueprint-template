import Mathlib.Tactic

variable {a b : ℕ}

lemma aux : a + b = b + a := add_comm a b

theorem Ex : a + b = b + a := aux
