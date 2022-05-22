from collections import namedtuple
from dataclasses import dataclass
import sys
from typing import Optional
import re


@dataclass
class Opcode:
    instr: int
    params: str


@dataclass
class OpcodeGroup:
    literal: Optional[Opcode]
    direct: Optional[Opcode]
    indirect: Optional[Opcode]
    pc_direct: Optional[Opcode]
    pc_indirect: Optional[Opcode]
    register: Optional[Opcode]


MNEMONICS = {
    "HLT": Opcode(instr=0x0, params=""),
    "NOP": Opcode(instr=0x1, params=""),
    "SF": Opcode(instr=0x2, params=""),
    "RF": Opcode(instr=0x3, params=""),
    "EI": Opcode(instr=0x4, params=""),
    "DI": Opcode(instr=0x5, params=""),
    "SL": Opcode(instr=0x6, params=""),
    "RL": Opcode(instr=0x7, params=""),
    "CL": Opcode(instr=0x8, params=""),
    "RSR": Opcode(instr=0x9, params=""),
    "RI": Opcode(instr=0x0A, params=""),
    "RIM": Opcode(instr=0x0B, params=""),
    "ELO": Opcode(instr=0x0C, params=""),
    "PCX": Opcode(instr=0x0D, params=""),
    "DLY": Opcode(instr=0x0E, params=""),
    "SYSRET": Opcode(instr=0x0F, params=""),
    "BL": Opcode(instr=0x10, params="PC+N"),
    "BNL": Opcode(instr=0x11, params="PC+N"),
    "BF": Opcode(instr=0x12, params="PC+N"),
    "BNF": Opcode(instr=0x13, params="PC+N"),
    "BZ": Opcode(instr=0x14, params="PC+N"),
    "BNZ": Opcode(instr=0x15, params="PC+N"),
    "BM": Opcode(instr=0x16, params="PC+N"),
    "BP": Opcode(instr=0x17, params="PC+N"),
    "BGZ": Opcode(instr=0x18, params="PC+N"),
    "BLE": Opcode(instr=0x19, params="PC+N"),
    "BS1": Opcode(instr=0x1A, params="PC+N"),
    "BS2": Opcode(instr=0x1B, params="PC+N"),
    "BS3": Opcode(instr=0x1C, params="PC+N"),
    "BS4": Opcode(instr=0x1D, params="PC+N"),
    "INR": Opcode(
        instr=0x20,
        params="Byte Register in high nibble, unsigned constant in low nibble",
    ),
    "DCR": Opcode(
        instr=0x21,
        params="Byte Register in high nibble, unsigned constant in low nibble",
    ),
    "CLR": Opcode(
        instr=0x22,
        params="Byte Register in high nibble, unsigned constant in low nibble",
    ),
    "IVR": Opcode(
        instr=0x23,
        params="Byte Register in high nibble, unsigned constant in low nibble",
    ),
    "SRR": Opcode(
        instr=0x24,
        params="Byte Register in high nibble, unsigned constant in low nibble",
    ),
    "SLR": Opcode(
        instr=0x25,
        params="Byte Register in high nibble, unsigned constant in low nibble",
    ),
    "RRR": Opcode(
        instr=0x26,
        params="Byte Register in high nibble, unsigned constant in low nibble",
    ),
    "RLR": Opcode(
        instr=0x27,
        params="Byte Register in high nibble, unsigned constant in low nibble",
    ),
    "INAL": Opcode(instr=0x28, params=""),
    "DCAL": Opcode(instr=0x29, params=""),
    "CLAL": Opcode(instr=0x2A, params=""),
    "IVAL": Opcode(instr=0x2B, params=""),
    "SRAL": Opcode(instr=0x2C, params=""),
    "SLAL": Opcode(instr=0x2D, params=""),
    "INR": Opcode(
        instr=0x30,
        params="Word Register in high nibble, unsigned constant in low nibble",
    ),
    "DCR": Opcode(
        instr=0x31,
        params="Word Register in high nibble, unsigned constant in low nibble",
    ),
    "CLR": Opcode(
        instr=0x32,
        params="Word Register in high nibble, unsigned constant in low nibble",
    ),
    "IVR": Opcode(
        instr=0x33,
        params="Word Register in high nibble, unsigned constant in low nibble",
    ),
    "SRR": Opcode(
        instr=0x34,
        params="Word Register in high nibble, unsigned constant in low nibble",
    ),
    "SLR": Opcode(
        instr=0x35,
        params="Word Register in high nibble, unsigned constant in low nibble",
    ),
    "RRR": Opcode(
        instr=0x36,
        params="Word Register in high nibble, unsigned constant in low nibble",
    ),
    "RLR": Opcode(
        instr=0x37,
        params="Word Register in high nibble, unsigned constant in low nibble",
    ),
    "INAW": Opcode(instr=0x38, params=""),
    "DCAW": Opcode(instr=0x39, params=""),
    "CLAW": Opcode(instr=0x3A, params=""),
    "IVAW": Opcode(instr=0x3B, params=""),
    "SRAW": Opcode(instr=0x3C, params=""),
    "SLAW": Opcode(instr=0x3D, params=""),
    "INX": Opcode(instr=0x3E, params=""),
    "DCX": Opcode(instr=0x3F, params=""),
    "ADD": Opcode(instr=0x40, params="Byte register, Byte register"),
    "SUB": Opcode(instr=0x41, params="Byte register, Byte register"),
    "AND": Opcode(instr=0x42, params="Byte register, Byte register"),
    "ORI": Opcode(instr=0x43, params="Byte register, Byte register"),
    "ORE": Opcode(instr=0x44, params="Byte register, Byte register"),
    "XFR": Opcode(instr=0x45, params="Byte register, Byte register"),
    "AABL": Opcode(instr=0x48, params=""),
    "SABL": Opcode(instr=0x49, params=""),
    "NABL": Opcode(instr=0x4A, params=""),
    "XAXL": Opcode(instr=0x4B, params=""),
    "XAYL": Opcode(instr=0x4C, params=""),
    "XABL": Opcode(instr=0x4D, params=""),
    "XAZL": Opcode(instr=0x4E, params=""),
    "XASL": Opcode(instr=0x4F, params=""),
    "ADD": Opcode(instr=0x50, params="Word Register, Word Register"),
    "SUB": Opcode(instr=0x51, params="Word Register, Word Register"),
    "AND": Opcode(instr=0x52, params="Word Register, Word Register"),
    "ORI": Opcode(instr=0x53, params="Word Register, Word Register"),
    "ORE": Opcode(instr=0x54, params="Word Register, Word Register"),
    "XFR": Opcode(instr=0x55, params="Word Register, Word Register"),
    "AABW": Opcode(instr=0x58, params=""),
    "SABW": Opcode(instr=0x59, params=""),
    "NABW": Opcode(instr=0x5A, params=""),
    "XAXW": Opcode(instr=0x5B, params=""),
    "XAYW": Opcode(instr=0x5C, params=""),
    "XABW": Opcode(instr=0x5D, params=""),
    "XAZW": Opcode(instr=0x5E, params=""),
    "XASW": Opcode(instr=0x5F, params=""),
    "LDXW": OpcodeGroup(
        literal=Opcode(instr=0x60, params="#Literal"),
        direct=Opcode(instr=0x61, params="Direct"),
        indirect=Opcode(instr=0x62, params="[Indirect]"),
        pc_direct=Opcode(instr=0x63, params="PC+N"),
        pc_indirect=Opcode(instr=0x64, params="[PC+N]"),
        register=Opcode(instr=0x65, params="Word Register, Mod."),
    ),
    "STXW": OpcodeGroup(
        literal=Opcode(instr=0x68, params="Store Location"),
        direct=Opcode(instr=0x69, params="Direct"),
        indirect=Opcode(instr=0x6A, params="[Indirect]"),
        pc_direct=Opcode(instr=0x6B, params="PC+N"),
        pc_indirect=Opcode(instr=0x6C, params="[PC+N]"),
        register=Opcode(instr=0x6D, params="Word Register, Mod."),
    ),
    "JMP": OpcodeGroup(
        literal=Opcode(instr=0x70, params="#Literal"),
        direct=Opcode(instr=0x71, params="Direct"),
        indirect=Opcode(instr=0x72, params="[Indirect]"),
        pc_direct=Opcode(instr=0x73, params="PC+N"),
        pc_indirect=Opcode(instr=0x74, params="[PC+N]"),
        register=Opcode(instr=0x75, params="Word Register, Mod."),
    ),
    "SYSCALL": Opcode(instr=0x76, params=""),
    "JSR": OpcodeGroup(
        literal=Opcode(instr=0x78, params="#Literal"),
        direct=Opcode(instr=0x79, params="Direct"),
        indirect=Opcode(instr=0x7A, params="[Indirect]"),
        pc_direct=Opcode(instr=0x7B, params="PC+N"),
        pc_indirect=Opcode(instr=0x7C, params="[PC+N]"),
        register=Opcode(instr=0x7D, params="Word Register, Mod."),
    ),
    "LDAL": OpcodeGroup(
        literal=Opcode(instr=0x80, params="#Literal"),
        direct=Opcode(instr=0x81, params="Direct"),
        indirect=Opcode(instr=0x82, params="[Indirect]"),
        pc_direct=Opcode(instr=0x83, params="PC+N"),
        pc_indirect=Opcode(instr=0x84, params="[PC+N]"),
        register=Opcode(instr=0x85, params="Word Register, Mod."),
    ),
    "LALA": Opcode(instr=0x88, params=""),
    "LALB": Opcode(instr=0x89, params=""),
    "LALX": Opcode(instr=0x8A, params=""),
    "LALY": Opcode(instr=0x8B, params=""),
    "LALZ": Opcode(instr=0x8C, params=""),
    "LALS": Opcode(instr=0x8D, params=""),
    "LALC": Opcode(instr=0x8E, params=""),
    "LALP": Opcode(instr=0x8F, params=""),
    "LDAW": OpcodeGroup(
        literal=Opcode(instr=0x90, params="#Literal"),
        direct=Opcode(instr=0x91, params="Direct"),
        indirect=Opcode(instr=0x92, params="[Indirect]"),
        pc_direct=Opcode(instr=0x93, params="PC+N"),
        pc_indirect=Opcode(instr=0x94, params="[PC+N]"),
        register=Opcode(instr=0x95, params="Word Register, Mod."),
    ),
    "LAWA": Opcode(instr=0x98, params=""),
    "LAWB": Opcode(instr=0x99, params=""),
    "LAWX": Opcode(instr=0x9A, params=""),
    "LAWY": Opcode(instr=0x9B, params=""),
    "LAWZ": Opcode(instr=0x9C, params=""),
    "LAWS": Opcode(instr=0x9D, params=""),
    "LAWC": Opcode(instr=0x9E, params=""),
    "LAWP": Opcode(instr=0x9F, params=""),
    "STAL": OpcodeGroup(
        literal=Opcode(instr=0xA0, params="Store Location"),
        direct=Opcode(instr=0xA1, params="Direct"),
        indirect=Opcode(instr=0xA2, params="[Indirect]"),
        pc_direct=Opcode(instr=0xA3, params="PC+N"),
        pc_indirect=Opcode(instr=0xA4, params="[PC+N]"),
        register=Opcode(instr=0xA5, params="Word Register, Mod."),
    ),
    "SALA": Opcode(instr=0xA8, params=""),
    "SALB": Opcode(instr=0xA9, params=""),
    "SALX": Opcode(instr=0xAA, params=""),
    "SALY": Opcode(instr=0xAB, params=""),
    "SALZ": Opcode(instr=0xAC, params=""),
    "SALS": Opcode(instr=0xAD, params=""),
    "SALC": Opcode(instr=0xAE, params=""),
    "SALP": Opcode(instr=0xAF, params=""),
    "STAW": OpcodeGroup(
        literal=Opcode(instr=0xB0, params="Store Location"),
        direct=Opcode(instr=0xB1, params="Direct"),
        indirect=Opcode(instr=0xB2, params="[Indirect]"),
        pc_direct=Opcode(instr=0xB3, params="PC+N"),
        pc_indirect=Opcode(instr=0xB4, params="[PC+N]"),
        register=Opcode(instr=0xB5, params="Word Register, Mod."),
    ),
    "SAWA": Opcode(instr=0xB8, params=""),
    "SAWB": Opcode(instr=0xB9, params=""),
    "SAWX": Opcode(instr=0xBA, params=""),
    "SAWY": Opcode(instr=0xBB, params=""),
    "SAWZ": Opcode(instr=0xBC, params=""),
    "SAWS": Opcode(instr=0xBD, params=""),
    "SAWC": Opcode(instr=0xBE, params=""),
    "SAWP": Opcode(instr=0xBF, params=""),
    "LDBL": OpcodeGroup(
        literal=Opcode(instr=0xC0, params="#Literal"),
        direct=Opcode(instr=0xC1, params="Direct"),
        indirect=Opcode(instr=0xC2, params="[Indirect]"),
        pc_direct=Opcode(instr=0xC3, params="PC+N"),
        pc_indirect=Opcode(instr=0xC4, params="[PC+N]"),
        register=Opcode(instr=0xC5, params="Word Register, Mod."),
    ),
    "LBLA": Opcode(instr=0xC8, params=""),
    "LBLB": Opcode(instr=0xC9, params=""),
    "LBLX": Opcode(instr=0xCA, params=""),
    "LBLY": Opcode(instr=0xCB, params=""),
    "LBLZ": Opcode(instr=0xCC, params=""),
    "LBLS": Opcode(instr=0xCD, params=""),
    "LBLC": Opcode(instr=0xCE, params=""),
    "LBLP": Opcode(instr=0xCF, params=""),
    "LDBW": OpcodeGroup(
        literal=Opcode(instr=0xD0, params="#Literal"),
        direct=Opcode(instr=0xD1, params="Direct"),
        indirect=Opcode(instr=0xD2, params="[Indirect]"),
        pc_direct=Opcode(instr=0xD3, params="PC+N"),
        pc_indirect=Opcode(instr=0xD4, params="[PC+N]"),
        register=Opcode(instr=0xD5, params="Word Register, Mod."),
    ),
    "LBWA": Opcode(instr=0xD8, params=""),
    "LBWB": Opcode(instr=0xD9, params=""),
    "LBWX": Opcode(instr=0xDA, params=""),
    "LDBW": Opcode(instr=0xDB, params=""),
    "LBWZ": Opcode(instr=0xDC, params=""),
    "LBWS": Opcode(instr=0xDD, params=""),
    "LBWC": Opcode(instr=0xDE, params=""),
    "LBWP": Opcode(instr=0xDF, params=""),
    "STBL": OpcodeGroup(
        literal=Opcode(instr=0xE0, params="Store Location"),
        direct=Opcode(instr=0xE1, params="Direct"),
        indirect=Opcode(instr=0xE2, params="[Indirect]"),
        pc_direct=Opcode(instr=0xE3, params="PC+N"),
        pc_indirect=Opcode(instr=0xE4, params="[PC+N]"),
        register=Opcode(instr=0xE5, params="Word Register, Mod."),
    ),
    "SBLA": Opcode(instr=0xE8, params=""),
    "SBLB": Opcode(instr=0xE9, params=""),
    "SBLX": Opcode(instr=0xEA, params=""),
    "SBLY": Opcode(instr=0xEB, params=""),
    "SBLZ": Opcode(instr=0xEC, params=""),
    "SBLS": Opcode(instr=0xED, params=""),
    "SBLC": Opcode(instr=0xEE, params=""),
    "SBLP": Opcode(instr=0xEF, params=""),
    "STBW": OpcodeGroup(
        literal=Opcode(instr=0xF0, params="Store Location"),
        direct=Opcode(instr=0xF1, params="Direct"),
        indirect=Opcode(instr=0xF2, params="[Indirect]"),
        pc_direct=Opcode(instr=0xF3, params="PC+N"),
        pc_indirect=Opcode(instr=0xF4, params="[PC+N]"),
        register=Opcode(instr=0xF5, params="Word Register, Mod."),
    ),
    "SBWA": Opcode(instr=0xF8, params=""),
    "SBWB": Opcode(instr=0xF9, params=""),
    "SBWX": Opcode(instr=0xFA, params=""),
    "SBWY": Opcode(instr=0xFB, params=""),
    "SBWZ": Opcode(instr=0xFC, params=""),
    "SBWS": Opcode(instr=0xFD, params=""),
    "SBWC": Opcode(instr=0xFE, params=""),
    "SBWP": Opcode(instr=0xFF, params=""),
}


def assemble(file_name):
    line_cleaner = re.compile(r"^(.*?)(?:;.+)?$")
    out_buf = {"_default": []}
    with open(file_name, "r") as source:
        for line in source:
            line = line_cleaner.sub(r"\1", line).strip()
            if line == "":
                continue

            terms = re.split(r"\s+", line)
            operand = terms.pop(-1)

            try:
                mnemonic = MNEMONICS[operand]
            except KeyError:
                # TODO: support labels
                continue

            if isinstance(mnemonic, OpcodeGroup):
                pass
            else:
                pass


if __name__ == "__main__":
    file_name = sys.argv[1]
    assemble(file_name)
