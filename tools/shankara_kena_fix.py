from shk_fix import *

p, d, U = load("kena_shankara")
b = part(U["4.6"], "bhashya")
tail = "\nThus instructed, the disciple addressed the preceptor in the following manner."
assert b["english"].endswith(tail.strip())
b["english"] = b["english"][: b["english"].rindex("Thus instructed")].rstrip()
rebuild(U["4.6"])
note(d, "Kena 4.6: closing line that translates the opener of 4.7 removed (4.7 translates it itself)")
save(p, d)
