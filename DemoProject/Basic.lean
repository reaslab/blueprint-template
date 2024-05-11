variable {a b : Nat}

namespace List
/--
this should be a doc string.
-/
theorem aux : a + b = b + a := Nat.add_comm a b

namespace Nat

/--Here is a doc string-/
theorem Ex:a + b = b + a := aux

end Nat

theorem test : 1 + 1 = 2 := sorry



theorem Test : 1 + 1 = 2 := test

end List
