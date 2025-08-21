# streamlit run app.py AVVIO PROGRAMMA
import streamlit as st
import pandas as pd
import fantacalcio  # Assicurati che fantacalcio.py sia nella stessa cartella
def evidenzia_primo(val):
    return "background-color: #1e3a5f; color: #f0f0f0; font-weight: bold;" if pd.notna(val) else ""
# CONFIGURAZIONE
st.set_page_config(page_title="Fantacalcio App", page_icon="⚽", layout="centered")
st.title("⚽ Fantacalcio Analyzer")

# 📁 Nomi dei file
FILE_OUTPUT = "Output_Fantacalcio_Classico.xlsx"

# 🔁 Esegui lo script fantacalcio.py e ricarica i fogli
if st.button("🔁 Esegui Analisi Fantacalcio"):
    try:
        fantacalcio.main()
        st.success("✅ Analisi completata!")
    except Exception as e:
        st.error(f"❌ Errore nell'esecuzione: {e}")

# 📊 Visualizza fogli per ruolo + griglia con filtro squadra
try:
    fogli = pd.read_excel(FILE_OUTPUT, sheet_name=None)
    # Barra di ricerca globale (sopra tutto)
    search_global = st.text_input("🔎 Cerca giocatore (globale):").strip()

# Se viene inserito un nome globale
    if search_global:
        risultati = []
        visti = set()   # per evitare duplicati totali

        for nome_foglio, df in fogli.items():
            if "Nome" in df.columns:
                filtrato = df[df["Nome"].str.contains(search_global, case=False, na=False)]
                if not filtrato.empty:
                    for _, row in filtrato.iterrows():
                        nome_giocatore = row["Nome"]
                        if nome_giocatore not in visti:
                        # usiamo una serie convertita in DataFrame singola riga
                            singola_riga = row.to_frame().T
                            singola_riga["Ruolo_Foglio"] = nome_foglio
                            risultati.append(singola_riga)
                            visti.add(nome_giocatore)

        if risultati:
            risultati_df = pd.concat(risultati)
            st.subheader("🔍 Risultati ricerca globale (senza duplicati)")
            st.dataframe(risultati_df.reset_index(drop=True))
        else:
            st.info("Nessun giocatore trovato.")
        easter_egg_images = {"Floriani Mussolini": "muss.jpg"}

        for nome_intero, img_path in easter_egg_images.items():
            if search_global.lower() in nome_intero.lower():
                st.image(img_path,caption='BRAVISSIMO PRONIPOTE MIO! PORTA IN ALTO IL COGNOME!', use_container_width=True)
                break
        st.stop()

    if fogli:
        st.markdown("### 📂 Seleziona il foglio da visualizzare")
        ruolo_scelto = st.selectbox("Ruolo o griglia", list(fogli.keys()))
        df_selezionato = fogli[ruolo_scelto]
        

        st.subheader(f"📋 Dati: {ruolo_scelto}")

        # 🔍 Filtro per squadra con "TUTTI"
        if "Squadra" in df_selezionato.columns:
            df_selezionato["Squadra"] = df_selezionato["Squadra"].astype(str)
            squadre = sorted(df_selezionato["Squadra"].dropna().unique().tolist())
            opzioni_squadra = ["TUTTI"] + squadre
            squadra_scelta = st.selectbox("🏷️ Filtra per squadra", opzioni_squadra)

            if squadra_scelta != "TUTTI":
                df_selezionato = df_selezionato[df_selezionato["Squadra"] == squadra_scelta]

        # 🎨 Stile per Griglia Portieri
        if ruolo_scelto == "Griglia Portieri":
            def stile_griglia(val):
                try:
                    num = float(val)
                    if num == 0:
                        return "color: green; background-color: rgba(144,238,144,0.3);"
                    elif 1 <= num <= 8:
                        return "color: #00f7ff;"
                except:
                    return ""
                return ""

            st.markdown("### 🧤 Legenda colori")
            st.markdown("""
            - 🟩 **Verde + sfondo trasparente**: numero **0** (portiere non utilizzato)
            - 🔵 **Blu fluo**: numeri da **1 a 8** (presenze o punteggi rilevanti)
            - ⚪️ Nessuna modifica: altri valori
            """)

            styled_df = df_selezionato.style.applymap(stile_griglia)
            st.dataframe(styled_df)
        else:
            st.dataframe(df_selezionato)
    else:
        st.warning("⚠️ Il file Excel non contiene fogli.")
except FileNotFoundError:
    st.warning("⚠️ Il file Excel non è stato trovato. Esegui prima l'analisi.")
except Exception as e:
    st.warning(f"⚠️ Errore nella lettura del file: {e}")

st.markdown("---")


# Sezione Statistiche per Ruolo
st.header("📊 Statistiche per Ruolo")

ruolo = st.selectbox("Seleziona il ruolo", ["Portieri", "Difensori", "Centrocampisti", "Attaccanti"])

try:
    df = pd.read_excel("Output_Fantacalcio_Classico.xlsx", sheet_name=None)  # Assicurati che il path sia corretto
    
    if ruolo == "Portieri":
        df = df["Portieri"]
        st.subheader("🧤 Portieri per MV e FM")

        # Slider per numero minimo di partite a voto
        min_pv = st.slider("Numero minimo di partite a voto (Pv)", min_value=1, max_value=38, value=20)

        # Slider per numero di portieri da visualizzare
        num_portieri = st.slider("Quanti portieri vuoi visualizzare?", min_value=1, max_value=20, value=10)

        # Filtra portieri con almeno 'min_pv' partite
        portieri = df[(df['Ruolo'] == 'P') & (df['Pv'] >= min_pv)]

        # Ordina per MV e FM e prendi i primi N
        top_portieri = portieri.sort_values(by=["Mv", "Fm"], ascending=False).head(num_portieri)

        # Seleziona solo le colonne richieste
        colonne_mostrate = ['Nome','Squadra', 'Mv', 'Fm', 'Rp', 'Au', 'Gs', 'Pv']
        st.dataframe(top_portieri[colonne_mostrate].reset_index(drop=True))
    elif ruolo == "Difensori":
        df = df["Difensori"]
        st.subheader("🧤 Difensori per MV e FM")

        # Slider per numero minimo di partite a voto
        min_pv = st.slider("Numero minimo di partite a voto (Pv)", min_value=1, max_value=38, value=20)

        # Slider per numero di difensori da visualizzare
        num_difensori = st.slider("Quanti portieri vuoi visualizzare?", min_value=1, max_value=50, value=10)

        # Filtra portieri con almeno 'min_pv' partite
        difensori = df[(df['Ruolo'] == 'D') & (df['Pv'] >= min_pv)]

        # Ordina per MV e FM e prendi i primi N
        top_difensori = difensori.sort_values(by=["Mv", "Fm"], ascending=False).head(num_difensori)

        # Seleziona solo le colonne richieste
        colonne_mostrate = ['Nome', 'Squadra', 'Mv', 'Fm', 'Gf', 'Amm', 'Esp', 'Pv','Au']
        st.dataframe(top_difensori[colonne_mostrate].reset_index(drop=True))
    elif ruolo == "Centrocampisti":
        df = df["Centrocampisti"]
        st.subheader("🎯 Centrocampisti per MV e FM")

    # Slider per numero minimo di partite a voto
        min_pv = st.slider("Numero minimo di partite a voto (Pv)", min_value=1, max_value=38, value=20)

    # Slider per numero di centrocampisti da visualizzare
        num_centrocampisti = st.slider("Quanti centrocampisti vuoi visualizzare?", min_value=1, max_value=50, value=10)

    # Filtra centrocampisti con almeno 'min_pv' partite
        centrocampisti = df[(df['Ruolo'] == 'C') & (df['Pv'] >= min_pv)]

    # Ordina per MV e FM e prendi i primi N
        top_centrocampisti = centrocampisti.sort_values(by=["Mv", "Fm"], ascending=False).head(num_centrocampisti)

    # Seleziona solo le colonne richieste
        colonne_mostrate = ['Nome', 'Squadra', 'Mv', 'Fm', 'Gf', 'Ass','Rc','R+','R-', 'Amm', 'Esp', 'Pv']
        st.dataframe(top_centrocampisti[colonne_mostrate].reset_index(drop=True))
        
    elif ruolo == "Attaccanti":
        df = df["Attaccanti"]
        st.subheader("⚽ Attaccanti per MV e FM")

    # Slider per numero minimo di partite a voto
        min_pv = st.slider("Numero minimo di partite a voto (Pv)", min_value=1, max_value=38, value=20)

    # Slider per numero di attaccanti da visualizzare
        num_attaccanti = st.slider("Quanti attaccanti vuoi visualizzare?", min_value=1, max_value=50, value=10)

    # Filtra attaccanti con almeno 'min_pv' partite
        attaccanti = df[(df['Ruolo'] == 'A') & (df['Pv'] >= min_pv)]

    # Ordina per MV e FM e prendi i primi N
        top_attaccanti = attaccanti.sort_values(by=["Mv", "Fm"], ascending=False).head(num_attaccanti)

    # Seleziona solo le colonne richieste
        colonne_mostrate = ['Nome', 'Squadra', 'Mv', 'Fm', 'Gf', 'Ass', 'Rc','R+','R-', 'Amm', 'Esp', 'Pv']
        st.dataframe(top_attaccanti[colonne_mostrate].reset_index(drop=True))

except FileNotFoundError:
    st.error("⚠️ Il file 'Output_Fantacalcio_Classico.xlsx' non è stato trovato.")
except Exception as e:
    st.error(f"❌ Errore nel caricamento dei dati: {e}")
# 📌 Sezione Rigoristi

st.header("🎯 Rigoristi delle Squadre")

try:
    rigoristi_df = pd.read_excel("Rigoristi.xlsx")

    # 🔍 Filtro per squadra
    squadre_rigoristi = sorted(rigoristi_df["Squadra"].dropna().unique().tolist())
    squadra_rig_scelta = st.selectbox("Seleziona una squadra", ["TUTTI"] + squadre_rigoristi)

    if squadra_rig_scelta != "TUTTI":
        rigoristi_df = rigoristi_df[rigoristi_df["Squadra"] == squadra_rig_scelta]

    # 🎨 Stile per evidenziare il primo rigorista
    def evidenzia_primo(val):
        return "background-color: #ffe599; font-weight: bold;" if pd.notna(val) else ""

    styled_df = rigoristi_df.style.applymap(evidenzia_primo, subset=["Rigorista 1"])
    st.write("🎯 Tabella Rigoristi con evidenziazione del primo:")
    st.write(styled_df)
    giocatori_possibili = pd.concat([
        rigoristi_df["Rigorista 1"],
        rigoristi_df["Rigorista 2"],
        rigoristi_df["Rigorista 3"]
    ]).dropna().unique().tolist()

    if giocatori_possibili:
        giocatore_scelto = st.selectbox("Seleziona un rigorista per vedere statistiche Rc / R+ / R-", giocatori_possibili)

        # Carichiamo il file Output generale
        df_stats_all = pd.read_excel("Output_Fantacalcio_Classico.xlsx", sheet_name=None)
        df_unico = pd.concat(df_stats_all.values(), ignore_index=True)

        # Cerchiamo il giocatore
        dati_players = df_unico[df_unico["Nome"] == giocatore_scelto]

        if not dati_players.empty:
            # Estrazione valori (se non ci sono le colonne mette 0)
            Rc = dati_players["Rc"].iloc[0] if "Rc" in dati_players.columns else 0
            R_plus = dati_players["R+"].iloc[0] if "R+" in dati_players.columns else 0
            R_minus = dati_players["R-"].iloc[0] if "R-" in dati_players.columns else 0

            st.markdown(f"**{giocatore_scelto}** — Rc: {Rc}, R+: {R_plus}, R-: {R_minus}")

            # GRAFICO
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots()
            categorie = ["Rig. Calciati", "Rig. Segnati", "Rig. Sbagliati"]
            valori = [Rc, R_plus, R_minus]
            colori = ["#1f77b4", "green", "red"]

            ax.bar(categorie, valori, color=colori)
            ax.set_title(f"Statistiche rigori: {giocatore_scelto}")
            st.pyplot(fig)

        else:
            st.info("Giocatore non trovato nelle statistiche dell'Output.")
    else:
        st.info("Nessun rigorista presente nella squadra selezionata.")
except FileNotFoundError:
    st.warning("⚠️ Il file 'Rigoristi.xlsx' non è stato trovato.")
except Exception as e:
    st.error(f"❌ Errore nel caricamento dei rigoristi: {e}")
    


#FORMAZIONI SQUADRE.
import os

st.header("Formazioni Squadre")
st.markdown("### 🏷️ Seleziona la squadra")

# Percorso assoluto alla cartella 'formazioni'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARTELLA_FORMAZIONI = os.path.join(BASE_DIR, "formazioni")

try:
    if "Squadra" in df.columns:
        # Pulizia valori e preparazione lista
        df["Squadra"] = df["Squadra"].astype(str).str.strip()
        squadre = sorted(df["Squadra"].dropna().unique().tolist())

        opzioni_squadra = ["TUTTI"] + squadre
        squadra_scelta = st.selectbox("Filtra per squadra", opzioni_squadra)

        # Filtra dati
        if squadra_scelta != "TUTTI":
            df_filtrato = df[df["Squadra"] == squadra_scelta]
        else:
            df_filtrato = df

        # --- Funzione per mostrare immagine ---
        def mostra_img(nome_squadra):
            nome_file = nome_squadra.strip().lower().replace(" ", "_") + ".png"
            percorso = os.path.join(CARTELLA_FORMAZIONI, nome_file)
            if os.path.exists(percorso):
                st.image(percorso, caption=nome_squadra)
            else:
                st.warning(f"Immagine non trovata per: {nome_squadra}")

        # --- Mostra immagini ---
        if squadra_scelta == "TUTTI":
            for sq in squadre:
                mostra_img(sq)
        else:
            mostra_img(squadra_scelta)

    else:
        st.info("ℹ️ Colonna 'Squadra' non presente nei dati correnti")

except Exception as e:
    st.error(f"❌ Errore nel filtro per squadra: {e}")
