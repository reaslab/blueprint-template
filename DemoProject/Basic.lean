import Mathlib.Tactic


lemma aux {a b : ℕ} : a + b = b + a := add_comm a b

theorem Ex {a b c : ℕ} : a + b + c = a + (b + c) := add_assoc a b c
