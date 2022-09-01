"""
Created on 06/04/2011

@author: Ritchie
"""

class RBSav:

    def __init__(self, file, repair = False):
        self.version = 'Red/Blue'
        self.ok = repair
        self.repair = repair
        self.maps = [('Main', 53996, 9624, 13602)]
        table = [''] * 256
        etable = [''] * 256
        for x in range(26):
            table[128 + x] = chr(65 + x)
            table[160 + x] = chr(97 + x)

        for x in range(10):
            table[246 + x] = str(x)

        table[154] = '('
        table[155] = ')'
        table[156] = ':'
        table[157] = ';'
        table[158] = '['
        table[159] = ']'
        table[224] = "'"
        table[225] = 'PK'
        table[226] = 'MN'
        table[227] = '-'
        table[228] = "'r"
        table[229] = "'m"
        table[230] = '?'
        table[231] = '!'
        table[232] = '.'
        table[242] = '.'
        table[243] = '/'
        table[244] = ','
        self.dtable = table
        for x in range(256):
            if len(table[x]) == 1:
                etable[ord(table[x])] = chr(x)

        self.etable = etable
        self.file = file
        self.refreshfile()

    def refreshfile(self):
        fb = open(self.file, 'rb')
        self.buffer = fb.read()
        self.obuffer = self.buffer[:]
        fb.close()
        if self.repair == False:
            if len(self.buffer) < 32768 or len(self.buffer) > 65536:
                self.file = None
                self.buffer = ''
                return
        self.refresh()

    def saveas(self, file):
        self.check_sav()
        fb = open(file, 'wb')
        fb.write(self.buffer)
        fb.close()

    def save(self):
        self.saveas(self.file)

    def refresh(self):
        self.check_sav()
        if self.ok == False:
            return False
        self.load_money()
        self.load_names()
        self.load_badges()
        self.load_items()
        self.load_pokedex()
        self.load_options()
        self.load_time()
        self.load_pokemon()
        self.ok = True

    def check_sav(self):
        start = 9624
        size = 3979
        checksum = 255
        self.checksum = self.buffer[13603]
        for x in range(size):
            checksum -= self.buffer[x + start]
            checksum &= 255

        if checksum == self.checksum:
            self.ok = True
        self.checksum = checksum
        self.setbyte(13603, checksum)

    def set(self, var, value):
        if var == 'name':
            value = self.encode(value, 7)
            self.buffer = self.buffer[0:9624] + value + chr(80) + chr(80) + chr(80) + chr(80) + self.buffer[9635:]
        if var == 'rivalname':
            value = self.encode(value, 7)
            self.buffer = self.buffer[0:9718] + value + chr(80) + chr(80) + chr(80) + chr(80) + self.buffer[9729:]
        if var == 'money':
            value = value[-6:].rjust(6, '0')
            self.setbyte(9715, int(value[0:2], 16))
            self.setbyte(9716, int(value[2:4], 16))
            self.setbyte(9717, int(value[4:6], 16))
        if var == 'chips':
            value = value[-4:].rjust(4, '0')
            self.setbyte(10320, int(value[0:2], 16))
            self.setbyte(10321, int(value[2:4], 16))
        if var == 'hours':
            self.setbyte(11501, int(value) & 255)
            self.setbyte(11502, int(value) >> 8)
        if var == 'minutes':
            self.setbyte(11503, int(value))
        if var == 'seconds':
            self.setbyte(11504, int(value))
        if var == 'itemcount':
            self.setbyte(9673, int(value))
        if var == 'pcitemcount':
            self.setbyte(10214, int(value))
        if var == 'pokemoncount':
            self.setbyte(12076, int(value))
        for b in range(12):
            if var == 'box%dpokemoncount' % b:
                self.setbyte(self.boxoffset[b], int(value))

    def setbyte(self, byte, value, string = None):
        if string == None:
            self.buffer[0:byte].decode("latin-1") + chr(value)
            self.buffer[byte + 1:].decode("latin-1")
        else:
            return string[0:byte] + chr(value) + string[byte + 1:]

    def load_time(self):
        self.hours = self.buffer[11501]
        self.hours += self.buffer[11502] * 256
        self.minutes = self.buffer[11503]
        self.seconds = self.buffer[11504]

    def load_options(self):
        options = self.buffer[9729]
        self.animation = not options >> 7
        self.mantain = options >> 6 & 1
        self.textspeed = options & 15

    def setpokedex(self, x, isseen, iscatched):
        pos = 2 ** ((x - 1) % 8)
        seen = self.buffer[9635 + (x - 1) // 8]
        catched = self.buffer[9654 + (x - 1) // 8]
        if self.seen[x] != isseen:
            seen ^= pos
        if self.catched[x] != iscatched:
            catched ^= pos
        self.setbyte(9654 + (x - 1) // 8, seen)
        self.setbyte(9635 + (x - 1) // 8, catched)

    def load_pokedex(self):
        self.seen = [0] * 256
        self.catched = [0] * 256
        for x in range(19):
            catched = self.buffer[9635 + x]
            seen = self.buffer[9654 + x]
            for y in range(8):
                self.catched[x * 8 + y + 1] = catched >> y & 1
                self.seen[x * 8 + y + 1] = seen >> y & 1

    def load_badges(self):
        badgesmap = self.buffer[9730]
        self.badges = [0] * 8
        for x in range(8):
            self.badges[x] = badgesmap >> x & 1

    def load_items(self):
        items = [[0, 0]] * 50
        for x in range(50):
            item = self.buffer[9674 + 2 * x]
            count = self.buffer[9675 + 2 * x]
            items[x] = [item, count]

        self.items = items
        self.itemcount = self.buffer[9673]
        pcitems = [[0, 0]] * 50
        for x in range(50):
            item = self.buffer[10215 + 2 * x]
            count = self.buffer[10216 + 2 * x]
            pcitems[x] = [item, count]

        self.pcitems = pcitems
        self.pcitemcount = self.buffer[10214]

    def load_pokemon(self):
        self.pokemon = [''] * 6
        self.pcpokemon = [''] * 240
        self.pokemoncount = self.buffer[12076]
        self.boxpokemoncount = [0] * 12
        self.boxoffset = [0] * 12
        for p in range(6):
            self.pokemon[p] = self.pkm(12077 + p, 12348 + 11 * p, 12414 + 11 * p, 12084 + 44 * p)

        self.currentbox = self.buffer[10316] & 127
        for b in range(12):
            offset = 16384 + b // 6 * 8192 + 1122 * (b % 6)
            if b == self.currentbox:
                offset = 12480
            self.boxoffset[b] = offset
            for p in range(20):
                self.pcpokemon[20 * b + p] = self.pcpkm(offset + 1 + p, offset + 682 + p * 11, offset + 902 + p * 11, offset + 22 + p * 33)

            self.boxpokemoncount[b] = self.buffer[offset]

    def setpokemon(self, p, pkm):
        self.pkm(12077 + p, 12348 + 11 * p, 12414 + 11 * p, 12084 + 44 * p, pkm)

    def setpcpokemon(self, p, pkm):
        b = p // 20
        p = p % 20
        offset = self.boxoffset[b]
        self.pcpkm(offset + 1 + p, offset + 682 + p * 11, offset + 902 + p * 11, offset + 22 + p * 33, pkm)

    def pkm(self, off_hex, off_otname, off_name, off_data, data = None):
        if data == None:
            pkm = bytes(self.buffer[off_hex])
            pkm += self.buffer[off_otname:off_otname + 11]
            pkm += self.buffer[off_name:off_name + 11]
            pkm += self.buffer[off_data:off_data + 44]
            return pkm
        self.setbyte(off_hex, data[0])
        self.buffer = self.buffer[0:off_otname] + data[1:12] + self.buffer[off_otname + 11:]
        self.buffer = self.buffer[0:off_name] + data[12:23] + self.buffer[off_name + 11:]
        self.buffer = self.buffer[0:off_data] + data[23:67] + self.buffer[off_data + 44:]

    def pcpkm(self, off_hex, off_otname, off_name, off_data, data = None):
        if data == None:
            pkm = bytes(self.buffer[off_hex])
            pkm += self.buffer[off_otname:off_otname + 11]
            pkm += self.buffer[off_name:off_name + 11]
            pkm += self.buffer[off_data:off_data + 33]
            return pkm
        self.setbyte(off_hex, data[0])
        self.buffer = self.buffer[0:off_otname] + data[1:12] + self.buffer[off_otname + 11:]
        self.buffer = self.buffer[0:off_name] + data[12:23] + self.buffer[off_name + 11:]
        self.buffer = self.buffer[0:off_data] + data[23:67] + self.buffer[off_data + 33:]

    def pkm_get(self, pkm, var):
        if var == 'sprite':
            return pkm[0]
        if var == 'num':
            return pkm[23]
        if var == 'otname':
            return self.decode(pkm[1:11])
        if var == 'name':
            return self.decode(pkm[12:22])
        if var == 'hp':
            return pkm[25] + pkm[24] * 256
        if var == 'level':
            return pkm[26]
        if var == 'asleep':
            if pkm[27] & 7:
                return True
            return False
        if var == 'poisoned':
            if pkm[27] & 8:
                return True
            return False
        if var == 'burned':
            if pkm[27] & 16:
                return True
            return False
        if var == 'frozen':
            if pkm[27] & 32:
                return True
            return False
        if var == 'paralyzed':
            if pkm[27] & 64:
                return True
            return False
        if var == 'ok':
            if pkm[27] & 127:
                return False
            return True
        if var == 'type1':
            return pkm[28]
        if var == 'type2':
            return pkm[29]
        if var == 'catchrate':
            return pkm[30]
        if var == 'move1':
            return pkm[31]
        if var == 'move2':
            return pkm[32]
        if var == 'move3':
            return pkm[33]
        if var == 'move4':
            return pkm[34]
        if var == 'otnum':
            return pkm[36] + pkm[35] * 256
        if var == 'exp':
            return pkm[39] + pkm[38] * 256 + pkm[37] * 65536
        if var == 'maxhpev':
            return pkm[41] + pkm[40] * 256
        if var == 'attackev':
            return pkm[43] + pkm[42] * 256
        if var == 'defenseev':
            return pkm[45] + pkm[44] * 256
        if var == 'speedev':
            return pkm[47] + pkm[46] * 256
        if var == 'specialev':
            return pkm[49] + pkm[48] * 256
        if var == 'attackiv':
            return pkm[50] >> 4
        if var == 'defenseiv':
            return pkm[50] & 15
        if var == 'speediv':
            return pkm[51] >> 4
        if var == 'specialiv':
            return pkm[51] & 15
        if var == 'move1pp':
            return pkm[52] & 63
        if var == 'move1ppup':
            return (pkm[52] & 192) >> 6
        if var == 'move2pp':
            return pkm[53] & 63
        if var == 'move2ppup':
            return (pkm[53] & 192) >> 6
        if var == 'move3pp':
            return pkm[54] & 63
        if var == 'move3ppup':
            return (pkm[54] & 192) >> 6
        if var == 'move4pp':
            return pkm[55] & 63
        if var == 'move4ppup':
            return (pkm[55] & 192) >> 6
        if var == 'curlevel':
            return pkm[56]
        if var == 'maxhp':
            return pkm[58] + pkm[57] * 256
        if var == 'attack':
            return pkm[60] + pkm[59] * 256
        if var == 'defense':
            return pkm[62] + pkm[61] * 256
        if var == 'speed':
            return pkm[64] + pkm[63] * 256
        if var == 'special':
            return pkm[66] + pkm[65] * 256

    def pkm_set(self, pkm, var, value):
        if var == 'sprite':
            pkm = self.setbyte(0, value, pkm)
        if var == 'num':
            pkm = self.setbyte(23, value, pkm)
        if var == 'otname':
            if value != self.pkm_get(pkm, var):
                pkm = pkm[0:1] + self.encode(value, 10) + chr(80) + pkm[12:]
        if var == 'name':
            if value != self.pkm_get(pkm, var):
                pkm = pkm[0:12] + self.encode(value, 10) + chr(80) + pkm[23:]
        if var == 'hp':
            pkm = self.setbyte(25, value & 255, pkm)
            pkm = self.setbyte(24, value >> 8, pkm)
        if var == 'level':
            pkm = self.setbyte(26, value, pkm)
        if var == 'asleep':
            status = pkm[27]
            if value:
                status |= 4
            else:
                status &= 248
            pkm = self.setbyte(27, status, pkm)
        if var == 'poisoned':
            status = pkm[27]
            if value:
                status |= 8
            else:
                status &= 247
            pkm = self.setbyte(27, status, pkm)
        if var == 'burned':
            status = pkm[27]
            if value:
                status |= 16
            else:
                status &= 239
            pkm = self.setbyte(27, status, pkm)
        if var == 'frozen':
            status = pkm[27]
            if value:
                status |= 32
            else:
                status &= 223
            pkm = self.setbyte(27, status, pkm)
        if var == 'paralyzed':
            status = pkm[27]
            if value:
                status |= 64
            else:
                status &= 191
            pkm = self.setbyte(27, status, pkm)
        if var == 'type1':
            pkm = self.setbyte(28, value, pkm)
        if var == 'type2':
            pkm = self.setbyte(29, value, pkm)
        if var == 'catchrate':
            pkm = self.setbyte(30, value, pkm)
        if var == 'move1':
            pkm = self.setbyte(31, value, pkm)
        if var == 'move2':
            pkm = self.setbyte(32, value, pkm)
        if var == 'move3':
            pkm = self.setbyte(33, value, pkm)
        if var == 'move4':
            pkm = self.setbyte(34, value, pkm)
        if var == 'otnum':
            pkm = self.setbyte(36, value & 255, pkm)
            pkm = self.setbyte(35, value >> 8, pkm)
        if var == 'exp':
            pkm = self.setbyte(39, value & 255, pkm)
            pkm = self.setbyte(38, value >> 8 & 255, pkm)
            pkm = self.setbyte(37, value >> 16, pkm)
        if var == 'maxhpev':
            pkm = self.setbyte(41, value & 255, pkm)
            pkm = self.setbyte(40, value >> 8, pkm)
        if var == 'attackev':
            pkm = self.setbyte(43, value & 255, pkm)
            pkm = self.setbyte(42, value >> 8, pkm)
        if var == 'defenseev':
            pkm = self.setbyte(45, value & 255, pkm)
            pkm = self.setbyte(44, value >> 8, pkm)
        if var == 'speedev':
            pkm = self.setbyte(47, value & 255, pkm)
            pkm = self.setbyte(46, value >> 8, pkm)
        if var == 'specialev':
            pkm = self.setbyte(49, value & 255, pkm)
            pkm = self.setbyte(48, value >> 8, pkm)
        if var == 'attackiv':
            iv = pkm[50] & 15
            iv += value << 4
            pkm = self.setbyte(50, iv, pkm)
        if var == 'defenseiv':
            iv = pkm[50] & 240
            iv += value & 15
            pkm = self.setbyte(50, iv, pkm)
        if var == 'speediv':
            iv = pkm[51] & 15
            iv += value << 4
            pkm = self.setbyte(51, iv, pkm)
        if var == 'specialiv':
            iv = pkm[51] & 240
            iv += value & 15
            pkm = self.setbyte(51, iv, pkm)
        if var == 'move1pp':
            pp = pkm[52] & 192
            pp += value & 63
            pkm = self.setbyte(52, pp, pkm)
        if var == 'move1ppup':
            pp = pkm[52] & 63
            pp += value << 6
            pkm = self.setbyte(52, pp, pkm)
        if var == 'move2pp':
            pp = pkm[53] & 192
            pp += value & 63
            pkm = self.setbyte(53, pp, pkm)
        if var == 'move2ppup':
            pp = pkm[53] & 63
            pp += value << 6
            pkm = self.setbyte(53, pp, pkm)
        if var == 'move3pp':
            pp = pkm[54] & 192
            pp += value & 63
            pkm = self.setbyte(54, pp, pkm)
        if var == 'move3ppup':
            pp = pkm[54] & 63
            pp += value << 6
            pkm = self.setbyte(54, pp, pkm)
        if var == 'move4pp':
            pp = pkm[55] & 192
            pp += value & 63
            pkm = self.setbyte(55, pp, pkm)
        if var == 'move4ppup':
            pp = pkm[55] & 63
            pp += value << 6
            pkm = self.setbyte(55, pp, pkm)
        if var == 'curlevel':
            pkm = self.setbyte(56, value, pkm)
        if var == 'maxhp':
            pkm = self.setbyte(58, value & 255, pkm)
            pkm = self.setbyte(57, value >> 8, pkm)
        if var == 'attack':
            pkm = self.setbyte(60, value & 255, pkm)
            pkm = self.setbyte(59, value >> 8, pkm)
        if var == 'defense':
            pkm = self.setbyte(62, value & 255, pkm)
            pkm = self.setbyte(61, value >> 8, pkm)
        if var == 'speed':
            pkm = self.setbyte(64, value & 255, pkm)
            pkm = self.setbyte(63, value >> 8, pkm)
        if var == 'special':
            pkm = self.setbyte(66, value & 255, pkm)
            pkm = self.setbyte(65, value >> 8, pkm)
        return pkm

    def setitem(self, x, item, count):
        if x < 20:
            self.setbyte(9674 + 2 * x, item)
            self.setbyte(9675 + 2 * x, count)
        if x >= 20:
            self.setbyte(10215 + 2 * (x - 20), item)
            self.setbyte(10216 + 2 * (x - 20), count)

    def load_money(self):
        money = ''
        money += hex(self.buffer[9715])[2:].rjust(2, '0')
        money += hex(self.buffer[9716])[2:].rjust(2, '0')
        money += hex(self.buffer[9717])[2:].rjust(2, '0')
        chips = hex(self.buffer[10320])[2:].rjust(2, '0')
        chips += hex(self.buffer[10321])[2:].rjust(2, '0')
        self.chips = 0
        if 'f' not in chips:
            self.chips = int(chips)
        self.money = 0
        if 'f' not in money:
            self.money = int(money)

    def load_names(self):
        self.name = self.decode(self.buffer[9624:9634])
        self.rivalname = self.decode(self.buffer[9718:9728])

    def decode(self, string):
        decoded = ''
        for c in range(len(string)):
            dec = string[c]
            if self.dtable[dec] != '':
                decoded += self.dtable[dec]
            elif dec == 80:
                return decoded

        return decoded

    def encode(self, string, fill = 0):
        encoded = ''
        for c in range(len(string)):
            dec = string[c]
            if len(self.etable[dec]):
                encoded += self.etable[dec]

        encoded = encoded.ljust(fill, chr(80))
        encoded = encoded[0:fill]
        return encoded
