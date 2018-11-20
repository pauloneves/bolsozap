#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib.request
import re
import pandas as pd

inicioRE = re.compile(r'^(\d\d/\d\d/\d{4} \d\d:\d\d) - (.*)')
foneRE = re.compile('^\u202a' + r'\+(?P<pais>\d\d) (?P<uf>\d\d)[- ](?P<tel>[-\d]+)' + '\u202c'  + r'(?P<tipo>.) (?P<texto>.*)')

whatsAppExported = "Conversa do WhatsApp com BOLSONARO, o Mito ! 😎👉👉.1.txt"
with open(whatsAppExported, encoding='utf8') as f:
    dados = []
    msg = []
    obs = {} # uma única observação
    txt = []
    for line in f:
        m = inicioRE.match(line)
        if m:
            if obs:
                obs['texto'] = '\n'.join(txt)
                dados.append(obs)
                print(obs)
                obs = {}
                txt = []

            obs['data'] = pd.to_datetime(m.group(1), dayfirst=True) #brasil
            line = m.group(2)
            m = foneRE.match(line)
            if m:
                obs.update(m.groupdict())
                txt = [obs['texto']]
            else:
                txt.append(line)
        else:
            txt.append(line)
        date = line[:16]