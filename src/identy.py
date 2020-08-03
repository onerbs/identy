"""Generate grayscale identity icons."""

from xu import integer

BORDER = 1  # must be less than radius
COLOR = True  # true means white background else black
RADIUS = 4  # the size of a tile (with border)
VARIANT = 0  # [0-63]; 0 means random

PALETTE = (
	(0x00, '  '),
	(0x3f, '░░'),
	(0x7e, '▒▒'),
	(0xbd, '▓▓'),
	(0xff, '██')
)


def assure(condition: bool, reason: str):
	"""Assures the compliance with the condition, otherwise raises an exception.

	:param condition: The condition to be verified.
	:param reason: The reason why the condition is false.
	"""
	if condition is not True:
		raise Exception('Invalid argument: %s.' % reason)


def warning(message: str):
	"""Print a warning message."""
	print(f'\033[33m warning \033[m{message}')


class png:
	"""The PNG class."""

	def __init__(self, matrix: list):
		"""Encode the source matrix into PNG bytes."""
		from struct import pack
		from zlib import compress, crc32

		size = len(matrix)
		hdr = pack(">2LBBBBB", size, size, 0o10, 0, 0, 0, 0)
		data = bytearray()
		for row in matrix:
			data.append(0)
			data.extend(row)

		bs = bytearray(b'\x89PNG\r\n\x1a\n')
		for row in [
			(bytes(b'IHDR'), hdr),
			(bytes(b'IDAT'), compress(data)),
			(bytes(b'IEND'), bytes()),
		]:
			bs.extend(pack(">L", len(row[1])))
			bs.extend(row[0])
			bs.extend(row[1])
			bs.extend(pack(">L", crc32(row[1], crc32(row[0]))))

		self._bytes = bytes(bs)

	def base64str(self) -> str:
		"""Encode to a base64 string."""
		from base64 import b64encode
		return b64encode(self._bytes).decode()

	def save(self, path: str):
		"""Save to a `.png` file."""
		with open(path, 'wb') as file:
			file.write(self._bytes)


class icon:
	"""Square matrix of int values [0-255]."""

	def __init__(self, matrix: list, *, border=BORDER, color=COLOR):
		"""Initialize a new icon.

		:param border: The size of the border.
		:param color: The color of the border.
		"""
		self._border = border
		self._color = color * PALETTE[-1][0]
		self._matrix = matrix

	def __getitem__(self, item):
		"""Get an item of this icon by the index."""
		return self._matrix[item]

	def __len__(self):
		"""Get the size of a side of this icon."""
		return (len(self._matrix) + self._border) * 2

	def __str__(self) -> str:
		"""Create a str representation of this icon."""
		return '\n'.join(''.join(PALETTE[item // 0x3f][1] for item in row) for row in self.border().unfold())

	def copy(self):
		"""Create a copy of this icon."""
		return icon(self._matrix.copy(), border=self._border, color=self._color)

	def border(self, /, color=None, size=None):
		"""Add border to this icon."""
		color = color or self._color
		size = size or self._border
		if not size:
			return self.copy()
		r = [[color for _ in range(len(self._matrix) + size)] for _ in range(size)]
		for row in self:
			r.append([color for _ in range(size)] + row)
		return icon(r)

	def invert(self):
		"""Invert the values of this.

		255 becomes 0 and vice versa"""
		return icon([[int(item + (127.5 - item) * 2) for item in row] for row in self])

	def scale(self, factor=1):
		"""Scale this icon by the specified factor.

		:param factor: Must be a positive integer.
		"""
		assure(factor > 0, 'the factor (%d) must be a positive integer' % factor)
		if factor == 1:
			return self.copy()
		scaled = []
		for row in self:
			scaled_row = []
			for item in row:
				scaled_row.extend([item] * factor)
			for _ in range(factor):
				scaled.append(scaled_row)
		return icon(scaled)

	def unfold(self):
		"""Mirror vertically, then horizontally."""
		h = [row + row[::-1] for row in self]
		return h + h[::-1]

	def png(self, size=0, *, scale=1) -> png:
		"""Convert this icon to png format.

		:param size: The size in pixels for the resulting image.
		:param scale: The factor to scale this icon.

		It is not supposed to provide `size` and `scale` at the same time.
		If so, then the specified size will determine the scale.
		"""
		if size:
			side = len(self)
			if not size >= side:
				warning('The requested size is too small (%d). Using minimum (%d).' % (size, side))
				size = side
			ratio = size / side
			scale = int(ratio)
			if not ratio == scale:
				size = side * scale
				warning('Loose scale (1:%.1f), fixed to 1:%d. Output size %d*%d px.' % (ratio, scale, size, size))
		return png(self.border().scale(scale).unfold())


def from_array(source: list, rows: int, *, border=BORDER, color=COLOR) -> icon:
	"""Generate an icon from an array.

	:param source: The source array
	:param rows: The number of parts to split the source array into
	:param border: The thickness of the border
	:param color: The color of the border
	"""
	size = len(source)
	assure(size % rows == 0, "%d items doesn't fit in %d rows" % (size, rows))
	chunks = size // rows
	matrix = [source[i * rows:i * rows + rows] for i in range(chunks)]
	return icon(matrix, border=border, color=color)


def from_string(
		string: str, radius=RADIUS, *,
		border=BORDER, color=COLOR, v=VARIANT) -> icon:
	"""Generate an icon from a string.

	:param string: The source string
	:param radius: Half the size of the icon
	:param border: The thickness of the border
	:param color: The color of the border
	:param v: The variant number
	"""
	assure(border < radius, 'too much border (%d), max (%d)' % (border, radius - 1))

	rd = radius - border
	if not 0 < rd < 0o11:
		warning('Radius (%d) is not between interval [1-8]. Using default (%d).' % (rd, RADIUS))
		rd = RADIUS

	from hashlib import md5
	v = integer(0x3f, 1).next() if v < 1 or v >= 0x40 else v

	digest = md5(string.encode()).hexdigest()  # len: 32
	digest = digest[::-1] + digest  # len: 64
	__digs = digest * 2
	digest = ''.join(__digs[i::v] for i in range(v))  # len: 64

	digest = [digest[i:i + 2] for i in range(0, len(digest), 2)][:rd * rd]
	digest = [int(pair, 0x10) for pair in digest]

	return from_array(digest, rd, border=border, color=color)


def random(radius=RADIUS, *, border=BORDER, color=COLOR) -> icon:
	"""Generate a random icon.

	:param radius: Half the size of the icon
	:param border: The thickness of the border
	:param color: The color of the border
	"""
	return icon(integer(0xff) ** (radius - border), border=border, color=color)
