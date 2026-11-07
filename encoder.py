"""
=============================================================================
URL SHORTENER - CORE MATH ENGINE: Base62 Encoder & Decoder
=============================================================================

What is Base62 and why is it used in URL Shorteners?
---------------------------------------------------
1. In a relational database, every saved URL gets an auto-incrementing integer ID:
      ID 1, ID 2, ..., ID 100000, ID 10000000.
   Because these IDs are generated sequentially by the database, they are
   100% GUARANTEED to be unique. No two links will ever share the same ID.

2. However, a raw number like "10000000" is long (8 characters) and looks like
   a database record rather than a clean short link.

3. We convert that Base10 (decimal) number into Base62.
   - Base 10 uses 10 characters: 0 to 9
   - Base 62 uses 62 characters: 0-9 (10) + a-z (26) + A-Z (26) = 62 characters.

4. With 62 characters:
   - A 1-character code can represent 62 URLs (0 to 61).
   - A 2-character code can represent 62^2 = 3,844 URLs.
   - A 4-character code can represent 62^4 = 14,776,336 URLs (over 14 million!).
   - A 6-character code can represent 62^6 = 56,800,235,584 URLs (over 56 billion!).

This allows us to create ultra-short, collision-free short codes without
needing random string collision-checks against the database.
=============================================================================
"""

# The 62-character alphabet used for encoding and decoding.
# Characters 0-9 are at indices 0-9.
# Characters a-z are at indices 10-35.
# Characters A-Z are at indices 36-61.
BASE62_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = len(BASE62_ALPHABET)  # 62


def encode_base62(num: int) -> str:
    """
    Converts a positive decimal integer (e.g. database row ID) into a Base62 string.

    How the Math Works (Step-by-Step):
    ----------------------------------
    Think of how Base 10 works with % 10 and // 10 to extract digits from right to left.
    Base 62 uses the exact same logic with % 62 and // 62:

    1. We take remainder: (num % 62).
       This remainder gives us the index of the character in our BASE62_ALPHABET.
    2. We shrink the number: (num // 62).
       This cuts off the digit we just extracted.
    3. We repeat steps 1 & 2 until num becomes 0.
    4. Because remainders peel off digits from smallest place-value to largest
       (right-to-left), we REVERSE the collected characters at the end.

    Example with num = 125:
    - Round 1: 125 % 62 = 1  -> Alphabet[1] = '1'
               125 // 62 = 2
    - Round 2: 2 % 62   = 2  -> Alphabet[2] = '2'
               2 // 62   = 0  -> Stop!
    - Collected: ['1', '2']
    - Reversed:  "21"
    So, 125 in Base62 is "21".
    """
    if num < 0:
        raise ValueError("Number must be a non-negative integer")

    # Edge case: if ID is 0, return the first character '0'
    if num == 0:
        return BASE62_ALPHABET[0]

    result_chars = []
    while num > 0:
        remainder = num % BASE
        result_chars.append(BASE62_ALPHABET[remainder])
        num //= BASE  # Integer division (discards remainder)

    # Reverse because the first remainder extracted was the lowest place value
    return "".join(reversed(result_chars))


def decode_base62(code: str) -> int:
    """
    Converts a Base62 string back into its original decimal integer ID.

    How the Math Works (Step-by-Step):
    ----------------------------------
    Think of reading a normal decimal number like "352" from left to right:
    - Start total = 0
    - Read '3': total = (0 * 10) + 3 = 3
    - Read '5': total = (3 * 10) + 5 = 35  (the 3 shifted left into tens place!)
    - Read '2': total = (35 * 10) + 2 = 352 (the 35 shifted left into hundreds/tens!)

    In Base 62, each place value is a power of 62 (1, 62, 3844, etc.).
    So instead of multiplying by 10, we multiply the existing total by 62!

    Example with code = "21":
    - Start total = 0
    - Read '2' (index 2): total = (0 * 62) + 2 = 2
    - Read '1' (index 1): total = (2 * 62) + 1 = 124 + 1 = 125
    We get back our original ID 125!
    """
    if not code:
        raise ValueError("Code string cannot be empty")

    num = 0
    for char in code:
        index = BASE62_ALPHABET.find(char)
        if index == -1:
            raise ValueError(f"Invalid Base62 character: '{char}'")

        # Shift the previous total left by one Base62 place value and add new digit
        num = (num * BASE) + index

    return num


# =============================================================================
# Quick Test / Verification when running: python encoder.py
# =============================================================================
if __name__ == "__main__":
    print("=" * 65)
    print(" BASE62 ENCODER / DECODER TEST RUN")
    print("=" * 65)

    test_ids = [0, 1, 5, 61, 62, 125, 200, 9999, 100000, 10000000]

    for test_id in test_ids:
        encoded = encode_base62(test_id)
        decoded = decode_base62(encoded)
        is_match = (test_id == decoded)
        print(f"Decimal ID: {test_id:<10} -> Base62: {encoded:<8} -> Decoded: {decoded:<10} [Match: {is_match}]")

    print("=" * 65)
    print("All tests passed! Base62 encoding and decoding is working accurately.")
