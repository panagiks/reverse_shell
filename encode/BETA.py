"""
Original file
	->https://github.com/b3mb4m/PythonVIRUS/blob/master/PyBackdoor/encode/BETA.py
"""


def randomkey( size):
	from random import choice
	from string import ascii_uppercase 
	from string import digits
	return "".join([choice(ascii_uppercase+digits) for x in range(size)])

def AES( TEXT, choice):
	try:
		from Crypto.Cipher import AES
		from Crypto import Random
		from base64 import b64encode,b64decode
	except ImportError:
		return False


	if choice == "encode":
		#With base64 that will be 32bit.
		KEY = randomkey( 22)
	else:
		KEY = TEXT[:16] + TEXT[-16:]
		TEXT = TEXT[16:-16]		


	#AES key must be either 16, 24, or 32 bytes long
	#These configs for 32 bits
	if choice == "encode":
		KEY = b64encode(KEY)
		BS = len(KEY) if len(KEY) % 16 == 0 or len(KEY) % 24 == 0 or len(KEY) % 32 == 0 else False
		pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS) 
		raw = pad(TEXT)
		iv = Random.new().read(AES.block_size)
		cipher = AES.new(KEY, AES.MODE_CBC, iv)
		ret = KEY[:16]+b64encode(iv + cipher.encrypt( raw))+KEY[16:]
		ret = ret.replace(ret[-2:], randomkey( 2))
		return ret
	else:
		KEY = KEY.replace(KEY[-2:], "==")
		unpad = lambda s : s[:-ord(s[len(s)-1:])]
		enc = b64decode(TEXT)
		iv = enc[:16]
		cipher = AES.new(KEY, AES.MODE_CBC, iv)
		return unpad(cipher.decrypt( enc[16:])) 
		
"""
Example

print AES( "B3mB4m", "encode")
print AES( "SE1SMjFUSzk3NVpLHHZgyarH++VdtP2OHfOs/qfpdNO4jySnDjZMmfXEC6YqD5QdkRPk2W8H2/xUMH96UFI5SEJTRk0wNwRI", "decode")

"""
