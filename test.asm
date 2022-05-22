printstr = 0x1234
crlf = 0x0D7A

    NOP
    NOP
    LDBL 0x50 ; toto
    BZ thing
    SUBR printstr
    "blah blah blah" crlf


thing:
    NOP
    HLT
