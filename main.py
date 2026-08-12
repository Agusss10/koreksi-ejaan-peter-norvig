#IMPORT LIBRARY
import pandas as pd
import numpy as np
import re
import string
from nltk.tokenize import word_tokenize
import streamlit as st

#DEFINISI FUNGSI
global kamus
global totalSeluruhKata

def preprocessing(text):
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    kecil = text.lower()
    tokens = word_tokenize(kecil)
    return tokens

def level_one_edits(kata):
    abjad = string.ascii_lowercase
    split = [(kata[:i], kata[i:]) for i in range(len(kata) + 1)]
    delete = [l + r[1:] for l,r in split if r]
    swap = [l + r[1] + r[0] + r[2:] for l,r in split if len(r)>1]
    replace = [l + c + r[1:] for l,r in split if r for c in abjad]
    insert = [l + c + r for l,r in split for c in abjad]
    return set(delete + swap + replace + insert)

def level_two_edits(kata):
    return set(e2 for e1 in level_one_edits(kata) for e2 in level_one_edits(e1))

def itung(kata, kamus):
    cari = kamus[kamus['kata'] == kata]
    if not cari.empty:
        return cari['jumlah kata'].values[0]
    else:
        return 0
    
def newFilter(kalimat, kamus):
    filterKata = []
    for kata in kalimat:
        if kata not in kamus['kata'].values:
            filterKata.append(kata)
    return filterKata

def checkKandidat(kata):
    librari = set(kamus['kata'])
    kandidat = level_one_edits(kata) or level_two_edits(kata) or [kata]
    validKandidat = [w for w in kandidat if w in librari]
    if not validKandidat:
        return [kata]
    return validKandidat

def hitungProbas(kandidat):
    if kandidat :
        return itung(kandidat, kamus) / totalSeluruhKata
    else:
        return None

def bestKandidat(kandidat, probabilitas):
    if kandidat and probabilitas:
        return kandidat[probabilitas.index(max(probabilitas))]
    else:
        return None

#KORPUS
korpus = 'korpus.csv'
kamus = pd.read_csv(korpus)
totalKataUnik = kamus.shape[0]
totalSeluruhKata = kamus['jumlah kata'].sum()

#INTERFACE
st.title('SPELLING CORRECTION WITH PETER NORVIG')
st.header('Aplikasi Web Untuk Mengkoreksi Ejaan Kata Salah Dalam Bahasa Indonesia')

default = ""
teksInput = st.text_area('Masukkan Kalimat...', value=default)
if st.button('Submit'):
    if teksInput.strip():
        preprocess = preprocessing(teksInput)
        kata_terfilter = newFilter(preprocess, kamus)
        
        if kata_terfilter:
            st.write("Kata Terdeteksi Salah:")
            kata_salah = ', '.join(kata_terfilter)
            st.success(kata_salah)

            kata_benar = []
            for kata in kata_terfilter:
                kandidat = checkKandidat(kata)
                probabilitas = []

                for kata in kandidat:
                    prob = hitungProbas(kata)
                    probabilitas.append(prob)

                kandidat_terbaik = bestKandidat(kandidat, probabilitas)
                kata_benar.append(kandidat_terbaik)

            koreksi = ', '.join(kata_benar)
            st.write("Hasil Koreksi:")
            st.success(koreksi)

            if kata_salah == koreksi:
                st.write("Kata Tidak Terdeteksi Dalam Kamus")
        else:
            st.success("Tidak ada kata terdeteksi salah")
    else:
        st.success("Input Kosong, Silahkan Masukkan Kalimat...")