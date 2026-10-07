import lookup


def test_parts_and_whole():
    whole = lookup.get("bsb_madhva:1.1.1")
    assert [p["role"] for p in whole["parts"]] == ["mula", "bhashya"]
    assert lookup.get("bsb_madhva:1.1.1.mula")["sanskrit"].startswith("॥ ॐ ॐ अथातो ब्रह्मजिज्ञासा")
    assert lookup.get("bsb_madhva:1.1.1.bhashya")["sanskrit"].startswith("अथशब्दो")


def test_refs_with_slash_and_names():
    assert lookup.get("bg_madhva:3/4.tatparya")["english"] is None
    assert lookup.get("aitareya_madhva:mangalacharana")["sanskrit"].startswith("नारायणं")


def test_scope_fallbacks_and_errors():
    assert lookup.get("bsb_madhva:1.3.42.bhashya")["sanskrit"]
    for bad in ("bsb_madhva:9.9.9", "nofile:1", "bsb_madhva:mangalacharana.tatparya", "bsb_madhva"):
        try:
            lookup.get(bad)
        except lookup.NotFound:
            continue
        raise AssertionError(bad)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("ok")
