import lazy_import
import binascii
import base64
import codecs
import html
import base58
import json
import struct
from random import randint

yaml = lazy_import.lazy_module("yaml")
import regex as re
import hexdump
from ast import literal_eval
from typing import TypeVar, Union
from urllib.parse import quote_plus as _urllib_quote_plus
from urllib.parse import unquote_plus as _urllib_unquote_plus

from ..core import ChepyCore, ChepyDecorators
from chepy.modules.internal.constants import Encoding

DataFormatT = TypeVar("DataFormatT", bound="DataFormat")


class DataFormat(ChepyCore):
    def __init__(self, *data):
        super().__init__(*data)

    @ChepyDecorators.call_stack
    def eval_state(self) -> DataFormatT:
        """Eval state as python.
        Handy when converting string representation
        of objects.

        Returns:
            Chepy: The Chepy object
        """
        self.state = literal_eval(self.state)
        return self

    @ChepyDecorators.call_stack
    def bytes_to_ascii(self) -> DataFormatT:
        """Convert bytes (array of bytes) to ascii

        Returns:
            Chepy: The Chepy object.
        """
        assert isinstance(self.state, list), "Data in state is not a list"
        self.state = bytearray(self.state).decode()
        return self

    @ChepyDecorators.call_stack
    def list_to_str(self, join_by: Union[str, bytes] = " ") -> DataFormatT:
        """Join an array by `join_by`

        Args:
            join_by (Union[str, bytes], optional): String character to join by, by default ' '

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy(["a", "b", "c"]).list_to_str(",").o
            "a,b,c"
        """
        assert isinstance(self.state, list), "Data in state not a list"
        # convert the list of items in state appropiately
        if isinstance(join_by, str):
            self.state = [str(x) for x in self.state]
        elif isinstance(join_by, bytes):
            self.state = [bytes(x) for x in self.state]
        self.state = join_by.join(self.state)
        return self

    @ChepyDecorators.call_stack
    def str_list_to_list(self) -> DataFormatT:
        """Convert a string list to a list

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy("[1,2,'lol', true]").str_list_to_list().o
            [1, 2, "lol", True]
        """
        self.state = json.loads(re.sub(r"'", '"', self._convert_to_str()))
        return self

    @ChepyDecorators.call_stack
    def join(self, by: Union[str, bytes] = "") -> DataFormatT:
        """Join a list with specified character

        Args:
            by (Union[str, bytes], optional): What to join with. Defaults to ""

        Returns:
            Chepy: The Chepy object.
        Examples:
            >>> Chepy(["a", "b", "c"]).join_list(":").o
            "a:b:c"
        """
        self.state = by.join(self.state)
        return self

    @ChepyDecorators.call_stack
    def join_list(self, by: Union[str, bytes] = "") -> DataFormatT:
        """Join a list with specified character

        Args:
            by (Union[str, bytes], optional): What to join with. Defaults to ""

        Returns:
            Chepy: The Chepy object.
        Examples:
            >>> Chepy(["a", "b", "c"]).join_list(":").o
            "a:b:c"
        """
        self.state = by.join(self.state)
        return self

    @ChepyDecorators.call_stack
    def json_to_dict(self) -> DataFormatT:
        """Convert a JSON string to a dict object

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy('{"some": "data", "a": ["list", 1, true]}').json_to_dict().o
            {
                "some": "data",
                "a": ["list", 1, True],
            }
        """
        self.state = json.loads(self._convert_to_str())
        return self

    @ChepyDecorators.call_stack
    def dict_to_json(self) -> DataFormatT:
        """Convert a dict object to a JSON string

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy({"some": "data", "a": ["list", 1, True]}).dict_to_json().o
            '{"some":"data","a":["list",1,true]}'
        """
        assert isinstance(self.state, dict), "Not a dict object"
        self.state = json.dumps(self.state)
        return self

    @ChepyDecorators.call_stack
    def dict_get_items(self, *keys) -> DataFormatT:
        """Get items from a dict

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> o = Chepy({"a": 1, "b": 2}).dict_get_items("a", "b", "c").o
            [1, 2]
        """
        assert isinstance(self.state, dict), "Not a dict object"
        assert len(keys) > 0, "No keys provided"
        o = list()
        for k in keys:
            if self.state.get(k):
                o.append(self.state.get(k))
        self.state = o
        return self

    @ChepyDecorators.call_stack
    def yaml_to_json(self) -> DataFormatT:
        """Convert yaml to a json string

        Returns:
            Chepy: The Chepy object.
        """
        self.state = json.dumps(yaml.safe_load(self.state))
        return self

    @ChepyDecorators.call_stack
    def json_to_yaml(self) -> DataFormatT:
        """Convert a json string to yaml structure

        Returns:
            Chepy: The Chepy object.
        """

        class ChepyYamlDumper(yaml.Dumper):
            def increase_indent(self, flow=False, indentless=False):
                return super(ChepyYamlDumper, self).increase_indent(flow, False)

        self.state = yaml.dump(
            json.loads(self.state),
            Dumper=ChepyYamlDumper,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )
        return self

    @ChepyDecorators.call_stack
    def base58_encode(self) -> DataFormatT:
        """Encode as Base58

        Base58 is a notation for encoding arbitrary byte data using a
        restricted set of symbols that can be conveniently used by humans
        and processed by computers.This property encodes raw data
        into an ASCII Base58 string.

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy("some data").base58_encode().out.decode()
            "2UDrs31qcWSPi"
        """
        self.state = base58.b58encode(self._convert_to_bytes())
        return self

    @ChepyDecorators.call_stack
    def base58_decode(self) -> DataFormatT:
        """Decode as Base58

        Base58 is a notation for encoding arbitrary byte data using a
        restricted set of symbols that can be conveniently used by humans
        and processed by computers.This property decodes raw data
        into an ASCII Base58 string.

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy("2UDrs31qcWSPi").base58_decode().out.decode()
            "some data"
        """
        self.state = base58.b58decode(self.state)
        return self

    @ChepyDecorators.call_stack
    def base85_encode(self) -> DataFormatT:
        """Encode as Base58

        Base85 is a notation for encoding arbitrary byte data using a
        restricted set of symbols that can be conveniently used by humans
        and processed by computers.This property decodes raw data
        into an ASCII Base58 string.

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy("some data").base85_encode().out.decode()
            "F)Po,+Cno&@/"
        """
        self.state = base64.a85encode(self._convert_to_bytes())
        return self

    @ChepyDecorators.call_stack
    def base85_decode(self) -> DataFormatT:
        """Decode as Base85

        Base85 is a notation for encoding arbitrary byte data using a
        restricted set of symbols that can be conveniently used by humans
        and processed by computers.This property decodes raw data
        into an ASCII Base58 string.

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy("F)Po,+Cno&@/").base85_decode().out.decode()
            "some data"
        """
        self.state = base64.a85decode(self._convert_to_bytes())
        return self

    @ChepyDecorators.call_stack
    def base16_encode(self) -> DataFormatT:
        """Encode state in base16

        Returns:
            Chepy: The Chepy object.
        """
        self.state = base64.b16encode(self._convert_to_bytes())
        return self

    @ChepyDecorators.call_stack
    def base16_decode(self) -> DataFormatT:
        """Decode state in base16

        Returns:
            Chepy: The Chepy object.
        """
        self.state = base64.b16decode(self._convert_to_bytes())
        return self

    @ChepyDecorators.call_stack
    def base32_encode(self) -> DataFormatT:
        """Encode as Base32

        Base32 is a notation for encoding arbitrary byte data using a
        restricted set of symbols that can be conveniently used by humans
        and processed by computers. It uses a smaller set of characters than
        Base64, usually the uppercase alphabet and the numbers 2 to 7.

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy("some data").base32_encode().out.decode()
            "ONXW2ZJAMRQXIYI="
        """
        self.state = base64.b32encode(self._convert_to_bytes())
        return self

    @ChepyDecorators.call_stack
    def base32_decode(self) -> DataFormatT:
        """Decode as Base32

        Base32 is a notation for encoding arbitrary byte data using a
        restricted set of symbols that can be conveniently used by humans
        and processed by computers. It uses a smaller set of characters than
        Base64, usually the uppercase alphabet and the numbers 2 to 7.

        Returns:
            Chepy: The Chepy object.
        """
        self.state = base64.b32decode(self.state)
        return self

    @ChepyDecorators.call_stack
    def base91_encode(self) -> DataFormatT:  # pragma: no cover
        """Base91 encode
        Reference: https://github.com/aberaud/base91-python/blob/master/base91.py#L69

        Returns:
            Chepy: The Chepy object.
        """
        bindata = self._convert_to_bytes()
        b = 0
        n = 0
        out = ""
        for count in range(len(bindata)):
            byte = bindata[count : count + 1]
            b |= struct.unpack("B", byte)[0] << n
            n += 8
            if n > 13:
                v = b & 8191
                if v > 88:
                    b >>= 13
                    n -= 13
                else:
                    v = b & 16383
                    b >>= 14
                    n -= 14
                out += (
                    Encoding.BASE91_ALPHABET[v % 91] + Encoding.BASE91_ALPHABET[v // 91]
                )
        if n:
            out += Encoding.BASE91_ALPHABET[b % 91]
            if n > 7 or b > 90:
                out += Encoding.BASE91_ALPHABET[b // 91]
        self.state = out
        return self

    @ChepyDecorators.call_stack
    def base91_decode(self) -> DataFormatT:  # pragma: no cover
        """Decode as Base91
        Reference: https://github.com/aberaud/base91-python/blob/master/base91.py#L42

        Returns:
            Chepy: The Chepy object.
        """
        encoded_str = self._convert_to_str()
        decode_table = dict((v, k) for k, v in enumerate(Encoding.BASE91_ALPHABET))
        v = -1
        b = 0
        n = 0
        out = bytearray()
        for strletter in encoded_str:
            if not strletter in decode_table:
                continue
            c = decode_table[strletter]
            if v < 0:
                v = c
            else:
                v += c * 91
                b |= v << n
                n += 13 if (v & 8191) > 88 else 14
                while True:
                    out += struct.pack("B", b & 255)
                    b >>= 8
                    n -= 8
                    if not n > 7:
                        break
                v = -1
        if v + 1:
            out += struct.pack("B", (b | v << n) & 255)
        self.state = out
        return self

    @ChepyDecorators.call_stack
    def to_int(self) -> DataFormatT:
        """Converts the string representation of a number into an int

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy("1").to_int().o
            1
        """
        self.state = int(self.state)
        return self

    @ChepyDecorators.call_stack
    def to_bytes(self) -> DataFormatT:
        """Converts the data in state to bytes

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy({'some': 'val', 'kl': 1}).to_bytes().o
            b"{'some': 'val', 'kl': 1}"
        """
        self.state = self._convert_to_str().encode()
        return self

    @ChepyDecorators.call_stack
    def from_bytes(self) -> DataFormatT:
        """Decodes bytes to string.

        Returns:
            Chepy: The Chepy object.
        """
        self.state = self._convert_to_bytes().decode()
        return self

    @ChepyDecorators.call_stack
    def base64_encode(self, custom: str = None, url_safe: bool = False) -> DataFormatT:
        """Encode as Base64

        Base64 is a notation for encoding arbitrary byte data using a
        restricted set of symbols that can be conveniently used by humans
        and processed by computers.This property encodes raw data
        into an ASCII Base64 string.

        Args:
            custom (str, optional): Provide a custom charset to base64 with
            url_safe (bool, optional): Encode with url safe charset.

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> # To use a custom character set, use:
            >>> custom = "./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
            >>> Chepy("Some data").base64_encode(custom=custom).o
            b'IqxhNG/YMLFV'
        """
        if url_safe:
            self.state = base64.urlsafe_b64encode(self._convert_to_bytes()).replace(
                b"=", b""
            )
            return self
        if custom is not None:
            x = base64.b64encode(self._convert_to_bytes())
            std_base64chars = (
                "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
            )
            self.state = bytes(
                str(x)[2:-1].translate(str(x)[2:-1].maketrans(std_base64chars, custom)),
                "utf-8",
            )
        else:
            self.state = base64.b64encode(self._convert_to_bytes())
        return self

    @ChepyDecorators.call_stack
    def base64_decode(self, custom: str = None, url_safe: bool = False) -> DataFormatT:
        """Decode as Base64

        Base64 is a notation for encoding arbitrary byte data using a
        restricted set of symbols that can be conveniently used by humans
        and processed by computers.This property decodes raw data
        into an ASCII Base64 string.

        Args:
            custom (str, optional): Provide a custom charset to base64 with
            url_safe (bool, optional): If true, decode url safe. Defaults to False

        Returns:
            Chepy: The Chepy object.

        Examples:
            Base64 decode using a custom string
            >>> c = Chepy("QqxhNG/mMKtYPqoz64FVR42=")
            >>> c.base64_decode(custom="./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
            >>> c.out
            b"some random? data"
        """
        data = self._convert_to_str()
        if custom is not None:
            std_base64chars = (
                "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
            )
            data = data.translate(str.maketrans(custom, std_base64chars))
        data += "=="
        if url_safe:
            self.state = base64.urlsafe_b64decode(data)
        else:
            self.state = base64.b64decode(data)
        return self

    @ChepyDecorators.call_stack
    def decode_bytes(self, errors: str = "ignore") -> DataFormatT:
        """Decode bytes to string

        Args:
            errors (str, optional): Ignore or replace error chars. Defaults to 'ignore'.

        Returns:
            Chepy: The Chepy object.
        """
        self.state = self._convert_to_bytes().decode(errors=errors)
        return self

    @ChepyDecorators.call_stack
    def to_hex(self, delimiter: str = "") -> DataFormatT:
        """Converts a string to its hex representation

        Args:
            delimiter (str, optional): Delimiter. Defaults to None.

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy("AAA").to_hex().out.decode()
            "414141"
        """
        if delimiter == "":
            self.state = binascii.hexlify(self._convert_to_bytes())
        else:
            self.state = binascii.hexlify(self._convert_to_bytes(), sep=delimiter)
        return self

    @ChepyDecorators.call_stack
    def from_hex(self, delimiter: str = None, join_by: str = " ") -> DataFormatT:
        """Convert a non delimited hex string to string

        Args:
            delimiter (str, optional): Delimiter. Defaults to None.
            join_by (str, optional): Join by. Defaults to ' '.

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy("414141").from_hex().out
            b"AAA"
        """
        if delimiter is not None:
            self.state = join_by.encode().join(
                list(
                    binascii.unhexlify(x)
                    for x in self._convert_to_str().split(delimiter)
                )
            )
        else:
            self.state = binascii.unhexlify(self._convert_to_str())
        return self

    @ChepyDecorators.call_stack
    def hex_to_int(self) -> DataFormatT:
        """Converts hex into its intiger represantation

        Returns:
            Chepy: The Chepy object.

        Examples:
            Chepy works with hex characters that start with a 0x

            >>> Chepy("0x123").hex_to_int().out
            291

            Without 0x in the hex

            >>> Chepy("123").hex_to_int().out
            291
        """
        if self._convert_to_str().startswith("0x"):
            self.state = int(self.state, 0)
        else:
            self.state = int(self.state, 16)
        return self

    @ChepyDecorators.call_stack
    def hex_to_binary(self) -> DataFormatT:
        """Hex to binary hex

        Converts a hex string to its binary form. Example:
        41 becomes \\x41

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy("ab00").hex_to_binary().o
            b"\\xab\\x00"
        """
        self.state = binascii.unhexlify(self._convert_to_bytes())
        return self

    @ChepyDecorators.call_stack
    def hex_to_str(self, ignore: bool = False) -> DataFormatT:
        """Decodes a hex string to ascii ignoring any decoding errors

        Args:
            ignore (bool, optional): Ignore errors, by default False

        Returns:
            Chepy: The Chepy object.

        Examples:
            To ignore UnicodeDecode errors, set ignore to True
            >>> Chepy("4100").hex_to_str(ignore=True).o
            "A\x00"
        """
        if ignore:
            self.state = binascii.unhexlify(self._convert_to_bytes()).decode(
                errors="ignore"
            )
        else:
            self.state = binascii.unhexlify(self._convert_to_bytes())
        return self

    @ChepyDecorators.call_stack
    def str_to_hex(self) -> DataFormatT:
        """Converts a string to a hex string

        Returns:
            Chepy: The Chepy object.
        """
        self.state = binascii.hexlify(self._convert_to_bytes())
        return self

    @ChepyDecorators.call_stack
    def int_to_hex(self) -> DataFormatT:
        """Converts an integer into its hex equivalent

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy(101).int_to_hex().o
            "65"
        """
        self.state = format(self._convert_to_int(), "x")
        return self

    @ChepyDecorators.call_stack
    def int_to_str(self) -> DataFormatT:
        """Converts an integer into a string

        Returns:
            Chepy: The Chepy object.
        """
        self.state = self._convert_to_str()
        return self

    @ChepyDecorators.call_stack
    def binary_to_hex(self) -> DataFormatT:
        """Converts binary data into a hex string

        Returns:
            Chepy: The Chepy object.
        """
        self.state = binascii.hexlify(self._convert_to_bytes())
        return self

    @ChepyDecorators.call_stack
    def normalize_hex(self, is_bytearray=False) -> DataFormatT:
        """Normalize a hex string

        Removes special encoding characters from a hex string like %,
        0x, , :, ;, \\n and \\r\\n

        Args:
            is_bytearray (bool, optional): Set to True if state is a bytearray

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy("41:42:CE").normalize_hex().o
            "4142CE"
            >>> Chepy("0x410x420xce").normalize_hex().o
            "4142ce"
        """
        if is_bytearray:
            self.state = binascii.hexlify(bytearray(self.state))
            return self
        else:
            delimiters = [" ", "0x", "%", ",", ";", ":", r"\\n", "\\r\\n"]
            string = re.sub("|".join(delimiters), "", self.state)
            self.state = string
            return self

    @ChepyDecorators.call_stack
    def str_from_hexdump(self) -> DataFormatT:
        """Extract a string from a hexdump

        Returns:
            Chepy: The Chepy object.
        """
        # TODO make new line aware \n \r\n \0a etc
        self.state = "".join(re.findall(r"\|(.+)\|", self._convert_to_str()))
        return self

    @ChepyDecorators.call_stack
    def to_hexdump(self) -> DataFormatT:
        """Convert the state to hexdump

        Returns:
            Chepy: The Chepy object.
        """
        self.state = hexdump.hexdump(self._convert_to_bytes(), result="return")
        return self

    @ChepyDecorators.call_stack
    def from_hexdump(self) -> DataFormatT:
        """Convert hexdump back to str

        Returns:
            Chepy: The Chepy object.
        """
        self.state = hexdump.restore(self._convert_to_str())
        return self

    @ChepyDecorators.call_stack
    def url_encode(self, safe: str = "") -> DataFormatT:
        """URL encode

        Encodes problematic characters into percent-encoding,
        a format supported by URIs/URLs.

        Args:
            safe (str, optional): String of characters that will not be encoded, by default ""

        Returns:
            Chepy: The Chepy object.

        Examples:
            Url encode while specifying save characters

            >>> Chepy("https://google.com/?lol=some data&a=1").url_encode(safe="/:").o
            "https://google.com/%3Flol%3Dsome+data%26a%3D1"
        """
        self.state = _urllib_quote_plus(self._convert_to_str(), safe=safe)
        return self

    @ChepyDecorators.call_stack
    def url_decode(self) -> DataFormatT:
        """Converts URI/URL percent-encoded characters back to their raw values.

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy("https://google.com/%3Flol%3Dsome+data%26a%3D1").url_decode().o
            "https://google.com/?lol=some data&a=1"
        """
        self.state = _urllib_unquote_plus(self._convert_to_str())
        return self

    @ChepyDecorators.call_stack
    def bytearray_to_str(
        self, encoding: str = "utf8", errors: str = "replace"
    ) -> DataFormatT:
        """Convert a python bytearray to string

        Args:
            encoding (str, optional): String encoding. Defaults to 'utf8'.
            errors (str, optional): How errors should be handled. Defaults to replace.

        Raises:
            TypeError: If state is not a bytearray

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy(bytearray("lolol", "utf")).bytearray_to_str().o
            "lolol"
        """
        if isinstance(self.state, bytearray):
            self.state = self.state.decode(encoding, errors=errors)
            return self
        else:  # pragma: no cover
            raise TypeError("State is not a bytearray")

    @ChepyDecorators.call_stack
    def str_to_list(self) -> DataFormatT:
        """Convert string to list

        Converts the string in state to an array of individual characyers

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy("abc").str_to_list().o
            ["a", "b", "c"]
        """
        self.state = list(self._convert_to_str())
        return self

    @ChepyDecorators.call_stack
    def str_to_dict(self) -> DataFormatT:
        """Convert string to a dictionary

        Returns:
            Chepy: The Chepy object.
        """
        self.state = yaml.safe_load(self._convert_to_str())
        return self

    @ChepyDecorators.call_stack
    def to_charcode(self, join_by: str = " ", base: int = 16) -> DataFormatT:
        """Convert a string to a list of unicode charcode

        Converts text to its unicode character code equivalent.
        e.g. Γειά σου becomes 0393 03b5 03b9 03ac 20 03c3 03bf 03c5

        Args:
            join_by (str, optional): String to join the charcodes by. Defaults to ' '.
            base (int, optional): Base to use for the charcodes. Defaults to 16.

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy("aㅎ").to_charcode()
            "61 314e"
        """
        hold = []
        for c in self._convert_to_str():
            hold.append(str(int(hex(ord(c))[2:], base)))
        self.state = join_by.join(hold)
        return self

    @ChepyDecorators.call_stack
    def from_charcode(
        self, delimiter: str = " ", join_by: str = "", base: int = 16
    ) -> DataFormatT:
        """Convert array of unicode chars to string

        Args:
            delimiter (str, optional): Delimiter. Defaults to " ".
            join_by (str, optional): Join by. Defaults to "".
            base (int, optional): Base. Defaults to 16.

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy("314e 61 20 41"]).from_charcode().o
            "ㅎa A"
        """
        out = []
        for c in self._convert_to_str().split(delimiter):
            out.append(chr(int(c, base)))
        self.state = join_by.join(out)
        return self

    @ChepyDecorators.call_stack
    def to_decimal(self, join_by: str = " ") -> DataFormatT:
        """Convert charactes to decimal

        Args:
            join_by (str, optional): Join the decimal values by this. Defaults to ' '.

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy("aㅎ").to_decimal().o
            '97 12622'
        """
        self.state = join_by.join(
            str(x) for x in list(ord(s) for s in list(self._convert_to_str()))
        )
        return self

    @ChepyDecorators.call_stack
    def from_decimal(self, delimiter: str = " ", join_by: str = "") -> DataFormatT:
        """Convert a list of decimal numbers to string

        Args:
            delimiter (str, optional): Delimiter. Defaults to " ".
            join_by (str, optional): Join by. Defaults to "".

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy(12622).from_decimal().o
            "ㅎ"
        """
        self.state = join_by.join(
            list(chr(int(s)) for s in self._convert_to_str().strip().split(delimiter))
        )
        return self

    @ChepyDecorators.call_stack
    def to_binary(self, join_by: str = " ") -> DataFormatT:
        """Convert string characters to binary

        Args:
            join_by (str, optional): join_by. Defaults to " ".

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy("abc").to_binary().o
            "01100001 01100010 01100011"
        """
        self.state = join_by.join(
            list(format(ord(s), "08b") for s in list(self._convert_to_str()))
        )
        return self

    @ChepyDecorators.call_stack
    def from_binary(self, delimiter: str = " ") -> DataFormatT:
        """Convert a list of binary numbers to string

        Args:
            delimiter (str, optional): Delimiter. Defaults to " ".

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy(["01100001", "01100010", "01100011"]).from_binary().o
            "abc"
        """
        n = int("".join(self._convert_to_str().split(delimiter)), 2)
        self.state = n.to_bytes((n.bit_length() + 7) // 8, "big")
        return self

    @ChepyDecorators.call_stack
    def to_octal(self, join_by: str = " ") -> DataFormatT:
        """Convert string characters to octal

        Args:
            join_by (str, optional): Join by. Defaults to "".

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy("abㅎ").to_octal().o
            "141 142 30516"
        """
        self.state = join_by.join(
            list(format(ord(s), "0o") for s in list(self._convert_to_str()))
        )
        return self

    @ChepyDecorators.call_stack
    def from_octal(self, delimiter: str = None, join_by: str = "") -> DataFormatT:
        """Convert a list of octal numbers to string

        Args:
            delimiter (str, optional): Delimiter. Defaults to None.
            join_by (str, optional): Join by. Defaults to "".

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy("141 142").from_octal().o
            "ab"
        """
        self.state = join_by.join(
            list(chr(int(str(x), 8)) for x in self._convert_to_str().split(delimiter))
        )
        return self

    @ChepyDecorators.call_stack
    def to_html_entity(self) -> DataFormatT:
        """Encode html entities

        Encode special html characters like & > < etc

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy('https://google.com&a="lol"').to_html_entity().o
            "https://google.com&amp;a=&quot;lol&quot;"
        """
        self.state = html.escape(self._convert_to_str())
        return self

    @ChepyDecorators.call_stack
    def from_html_entity(self) -> DataFormatT:
        """Decode html entities

        Decode special html characters like & > < etc

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy("https://google.com&amp;a=&quot;lol&quot;").from_html_entity().o
            'https://google.com&a="lol"'
        """
        self.state = html.unescape(self._convert_to_str())
        return self

    @ChepyDecorators.call_stack
    def to_punycode(self) -> DataFormatT:
        """Encode to punycode

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy("münchen").to_punycode().o
            b"mnchen-3ya"
        """
        self.state = self._convert_to_str().encode("punycode")
        return self

    @ChepyDecorators.call_stack
    def from_punycode(self) -> DataFormatT:
        """Decode to punycode

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy(b"mnchen-3ya").from_punycode().o
            "münchen"
        """
        self.state = self._convert_to_bytes().decode("punycode")
        return self

    @ChepyDecorators.call_stack
    def encode_bruteforce(self) -> DataFormatT:
        """Bruteforce the various encoding for a string

        Enumerates all supported text encodings for the input,
        allowing you to quickly spot the correct one.
        `Reference <https://docs.python.org/2.4/lib/standard-encodings.html>`__

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy("münchen한").encode_bruteforce()
            {
                'ascii': b'm\\xfcnchen\\ud55c',
                'base64_codec': b'bcO8bmNoZW7tlZw=\\n',
                'big5': b'm\\xfcnchen\\ud55c',
                'big5hkscs': b'm\\x88\\xa2nchen\\ud55c',
                ...
            }
        """
        data = self._convert_to_str()
        final = dict()
        for enc in Encoding.py_encodings:
            final[enc] = data.encode(enc, errors="backslashreplace")

        for text_enc in Encoding.py_text_encodings:
            try:
                final[text_enc] = codecs.encode(data, text_enc)
            except TypeError:
                final[text_enc] = codecs.encode(data.encode(), text_enc)
            except UnicodeEncodeError:
                try:
                    final[text_enc] = codecs.encode(
                        data, text_enc, errors="backslashreplace"
                    )
                except TypeError:  # pragma: no cover
                    final[text_enc] = codecs.encode(
                        data.encode(), text_enc, errors="backslashreplace"
                    )
        self.state = final
        return self

    @ChepyDecorators.call_stack
    def decode_bruteforce(self) -> DataFormatT:
        """Bruteforce the various decoding for a string

        Enumerates all supported text encodings for the input,
        allowing you to quickly spot the correct one.
        `Reference <https://docs.python.org/2.4/lib/standard-encodings.html>`__

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy("m\\xfcnchen\\ud55c").decode_bruteforce()
            {
                ...
                'unicode_escape': 'münchen한',
                'utf_16': '屭晸湣档湥畜㕤挵',
                'utf_16_be': '浜硦据捨敮屵搵㕣',
                ...
            }
        """
        data = self._convert_to_bytes()
        final = dict()
        for enc in Encoding.py_encodings:
            final[enc] = data.decode(enc, errors="backslashreplace")

        for text_enc in Encoding.py_text_encodings:
            try:
                final[text_enc] = codecs.decode(
                    data, text_enc, errors="backslashreplace"
                )
            except UnicodeDecodeError:  # pragma: no cover
                final[text_enc] = codecs.decode(
                    data.decode(), text_enc, errors="backslashreplace"
                )
            except AssertionError:
                final[text_enc] = ""
                continue
            except UnicodeError:
                final[text_enc] = ""
                continue
            except TypeError:
                final[text_enc] = ""
                continue
        self.state = final
        return self

    @ChepyDecorators.call_stack
    def to_braille(self) -> DataFormatT:
        """Convery text to six-dot braille symbols

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy("secret message").to_braille().o
            "⠎⠑⠉⠗⠑⠞⠀⠍⠑⠎⠎⠁⠛⠑"
        """
        chars = dict(zip(Encoding.asciichars, Encoding.brailles))
        self.state = "".join(list(chars.get(c.lower()) for c in self.state))
        return self

    @ChepyDecorators.call_stack
    def from_braille(self) -> DataFormatT:
        """Convery text to six-dot braille symbols

        Returns:
            Chepy: The Chepy object.

        Examples:
            >>> Chepy("⠎⠑⠉⠗⠑⠞⠀⠍⠑⠎⠎⠁⠛⠑").from_braille().o
            "secret message"
        """
        chars = dict(zip(Encoding.brailles, Encoding.asciichars))
        self.state = "".join(list(chars.get(c.lower()) for c in self.state))
        return self

    @ChepyDecorators.call_stack
    def trim(self) -> DataFormatT:
        """Trim string. Removes whitespaces

        Returns:
            Chepy: The Chepy object.
        """
        self.state = self._convert_to_str().strip()
        return self

    @ChepyDecorators.call_stack
    def to_nato(self, join_by: str = " ") -> DataFormatT:
        """Convert string to NATO phonetic format.

        Example: abc = Alpha Bravo Charlie

        Args:
            join_by (str, optional): [description]. Defaults to " ".

        Returns:
            Chepy: The Chepy object
        """
        nato_chars = Encoding.NATO_CONSTANTS_DICT
        hold = []
        data: str = self._convert_to_str()
        for d in data:
            if d.isalpha():
                hold.append(nato_chars[d.upper()])
            else:
                hold.append(d)
        self.state = join_by.join(hold)
        return self

    @ChepyDecorators.call_stack
    def from_nato(self, delimiter: str = " ", join_by: str = "") -> DataFormatT:
        """Translate NATO phoentic to words

        Args:
            delimiter (str, optional): Delimiter to split on. Defaults to ' '.
            join_by (str, optional): Join result by. Defaults to ''.

        Returns:
            Chepy: The Chepy object
        """
        data = self._convert_to_str().split(delimiter)
        d = {v: k for k, v in Encoding.NATO_CONSTANTS_DICT.items()}
        self.state = join_by.join([d.get(p, "") for p in data])
        return self

    @ChepyDecorators.call_stack
    def swap_strings(self, by: int) -> DataFormatT:
        """Swap characters in string

        Args:
            by (int): Number of bytes to swap

        Returns:
            Chepy: The Chepy object
        """
        t = list(self.state)
        t[::by], t[1::by] = t[1::by], t[::by]
        self.state = "".join(t)
        return self

    @ChepyDecorators.call_stack
    def to_string(self) -> DataFormatT:
        """Convert to string

        Returns:
            Chepy: The Chepy object
        """
        self.state = self._convert_to_str()
        return self

    @ChepyDecorators.call_stack
    def select(self, start: int, end: int = None) -> DataFormatT:
        """Get an item by specifying an index

        Args:
            start (int): Starting index number to get
            end (int, optional): Ending index number to get. If none specified, will be end of item. Defaults to None.

        Returns:
            Chepy: The Chepy object.
        """
        if end is None:
            self.state = self.state[start:]
        else:
            self.state = self.state[start:end]
        return self

    @ChepyDecorators.call_stack
    def length(self) -> DataFormatT:
        """Get the length of the current state as string

        Returns:
            Chepy: The Chepy object.
        """
        self.state = len(self.state)
        return self

    @ChepyDecorators.call_stack
    def to_leetcode(self, replace_space: str = "") -> DataFormatT:
        """Convert to leetcode. Reference
        Reference github.com/ss8651twtw/CTF-flag-generator

        Args:
            replace_space (str, optional): Replace spaces with specified char. Defaults to ''.

        Returns:
            Chepy: The Chepy object.
        """

        def change(c):
            if replace_space and c == " ":
                return replace_space
            if c.isalpha():
                c = c.upper()
                char_set = Encoding.LEETCODE[ord(c) - ord("A")]
                new_c = char_set[randint(0, len(char_set) - 1)]
                return new_c
            else:
                return c

        hold = ""
        string = self._convert_to_str()
        for s in string:
            hold += change(s)
        self.state = hold
        return self

    @ChepyDecorators.call_stack
    def substitute(self, x: str, y: str) -> DataFormatT:
        """Replace a subset of specified characters in the state.

        Args:
            x (str): Chars to replace
            y (str): Chars to replace with

        Returns:
            Chepy: The Chepy object.
        """
        assert len(x) == len(y), "x and y chars are not of equal length"
        s = self._convert_to_str()
        o = s.maketrans(x, y)
        self.state = s.translate(o)
        return self

    @ChepyDecorators.call_stack
    def remove_nonprintable(self, replace_with: bytes = b"") -> DataFormatT:
        """Remove non-printable characters from string.

        Args:
            replace_with (bytes, optional): Replace non-printable characters with this. Defaults to ''.

        Returns:
            Chepy: The Chepy object.
        """
        if isinstance(replace_with, str):
            replace_with = replace_with.encode()
        data = self._convert_to_bytes()
        self.state = re.sub(b"[^[:print:]]", replace_with, data)
        return self

    @ChepyDecorators.call_stack
    def swap_endianness(self) -> DataFormatT:
        # TODO make this better. this is not inline with cyberchef
        """Swap endianness of a hex string.

        Returns:
            Chepy: The Chepy object.
        """
        data = self._convert_to_bytes()
        # check if hex
        if not re.match(b"^[0-9a-fA-F]+$", data):  # pragma: no cover
            raise ValueError("Data is not hex")
        self.state = hex(struct.unpack("<I", struct.pack(">I", int(data, 16)))[0])[2:]
        return self
