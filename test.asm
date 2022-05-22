PrintStr: 0x1234

    NOP
    NOP
    LDBL 0x50 ; toto
    BZ thing
    SUBR PrintStr
    "blah blah blah"


thing:
    NOP
    HLT
