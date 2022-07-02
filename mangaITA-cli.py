from bs4 import BeautifulSoup
import requests
import os
import subprocess
import shutil

#FUNZIONI

def filename_extension(link):
    link = list(link)[::-1]
    index = link.index(".")
    ext = "".join(link[:index+1])[::-1]
    return ext

def get_only_number(text):
    number = ""
    for letter in text:
        if letter.isdigit() or letter == "." or letter == "," or letter == ";":
            number += letter

    if number[0] == "0":
        number = number[1:]

    return str(number)

def change_page(link, new_page):
    link = list(link)[::-1]
    index = int(link.index("/"))
    link[0:index] = "".join(list(str(new_page))[::-1])
    link = link[::-1]
    return "".join(link)

def clean():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system('clear')

def open_chap(ext):
    if os.name == "nt":
        print("Non è possibile aprire file da terminale...")
    else:
        subprocess.run(["xdg-open", f"1{first_ext}"])

def manga_scan(referer, capitolo, ultimo_capitolo, nome_manga):
    link = requests.get(referer).text
    soup = BeautifulSoup(link, "html.parser")

    total_pages = soup.find(class_= "page custom-select")
    total_pages = int(total_pages.findChildren("option")[-1]["value"]) +1

    page = 1
    scan_link = soup.find("div", id="reader").find("img", class_="img-fluid")["src"]
    first_ext = filename_extension(scan_link)

    #download pagina corrente
    while page <= total_pages:
        
        #link per la nuova pagina
        scan_link = change_page(scan_link, page)
        referer = change_page(referer, page)

        #link del file e estensione
        link = requests.get(referer).text
        soup = BeautifulSoup(link, "html.parser")
        scan_link = soup.find("div", id="reader").find("img", class_="img-fluid")["src"]
        ext = filename_extension(scan_link)

        #salva file
        with open(f"{page}{ext}", "wb") as handle:
            pic = requests.get(scan_link, stream=True, headers={"referer": f"{referer}"})
            handle.write(pic.content)
        
        clean()
        print(f"[Capitolo {capitolo}/{ultimo_capitolo}] {nome_manga}:")
        print(f"Download immagini in corso... {round((page/total_pages)*100, 2)}%")

        page += 1
    
    return first_ext

#-------------------------
clean()
print(f"""
    MangaITA-cli versione 1.0.0   (https://github.com/giampietrome)
    Python script per leggere da "https://www.mangaworld.in/"
    Ispirato da "https://github.com/7USTIN/manga-cli"
    I file verranno salavti in {os.getcwd()}/nome-manga/numero-capitolo/
""")
SITE = "https://www.mangaworld.in/archive?keyword="

#ricerca manga
try:
    search_input = input("Cerca manga: ")
except KeyboardInterrupt:
    print("")
    exit()

link = f"{SITE}{search_input}"

#scraper risultati
print(f"Cercando '{search_input}'...")
link = requests.get(link).text
soup = BeautifulSoup(link, "html.parser")

results_list = soup.find("div", class_="comics-grid").find_all("div", class_="entry")
results_dict = {}
number = 0

print(f"\n\nTrovati {len(results_list)} risulati/o:")
for entry in results_list:
    results_dict[f"{number}"] = [entry.a['title'], entry.a['href']]
    number += 1

del results_list

for entry in results_dict:
    print(f"[{entry}] {results_dict[entry][0]}")

#selezione manga
while True:
    try:
        manga = input(f"\n\nScegliere titolo [0]-[{list(results_dict)[-1]}]: ")
    except:
        print("Nessun risulato trovato.")
        exit()
    else:
        try:
            link = results_dict[manga][1]
        except KeyboardInterrupt:
            print("")
            exit()
        except:
            print("Il titolo selezionato non esiste.\nDigitare un numero tra i seguenti:")
            [print(f"[{entry}] {results_dict[entry][0]}") for entry in results_dict]
        else:
            break

manga_name = results_dict[manga][0]
del results_dict

#scraper pagina manga
link = requests.get(link).text
soup = BeautifulSoup(link, "html.parser")

#elenca capitoli
chapter_list = soup.find_all("div", class_="chapter")
chapter_dict = {}

for chap in chapter_list:
    chapter_dict[get_only_number(chap.span.get_text())] = [chap.a["title"], chap.a["href"]]

del chapter_list
last_chap = list(chapter_dict)[0]

#selezione capitolo
while True:
    try:
        chapter = input(f"Scegliere capitolo [{list(chapter_dict)[-1]}] - [{last_chap}] ('mostra' per elencarli tutti): ")
    except KeyboardInterrupt:
            print("")
            exit()
    else:
        if chapter == "mostra":
            print("")
            chapter_numbers = [f"[{chap}]" for chap in chapter_dict]
            print(*chapter_numbers[::-1])
            print("")
        else:
            try:
                referer = chapter_dict[str(chapter)][1] + "/"
            except:
                print("Il capitolo selezionato non esiste.\nDigitare un numero tra i seguenti:\n")
                chapter_numbers = [f"[{chap}]" for chap in chapter_dict]
                print(*chapter_numbers[::-1])
                print("")
            else:
                break
    

next_chapter = chapter_dict[list(chapter_dict)[list(chapter_dict).index(f"{chapter}") - 1]][1] + "/"

if float(chapter) >= 2:
    previous_chapter = chapter_dict[list(chapter_dict)[list(chapter_dict).index(f"{chapter}") + 1]][1] + "/"

del chapter_dict
clean()

#crea cartella manga
if manga_name not in os.listdir():
    os.mkdir(manga_name)
    os.chdir(manga_name)
else:
    os.chdir(manga_name)

#crea cartella capitolo
if chapter not in os.listdir():
    os.mkdir(chapter)
    os.chdir(chapter)
else:
    os.chdir(chapter)

#scraper pagina corrente
first_ext = manga_scan(referer, capitolo=chapter,
                        ultimo_capitolo=last_chap, nome_manga=manga_name)

clean()
print("Download completato.")
print(f"Files salvati in {os.getcwd()}\n\n")

#apre file con app di sistema
open_chap(first_ext)

#opzioni
print(f"[a] Capitolo successivo\n[b] Capitolo precedente\n[c] Elimina capitolo appena scaricato '{manga_name}: {chapter}/{last_chap}'")
try:
    letter = input("\nSelezionare opzione [a]-[c] (Ctrl+C per chiudere): ")
except KeyboardInterrupt:
    print("")
    exit()
else:
    if letter == "a":
        chapter = str(float(chapter) + 1)
        os.chdir("..")
        os.mkdir(f"{chapter}")
        os.chdir(f"{chapter}")

        referer = next_chapter
        first_ext = manga_scan(referer, capitolo=chapter,
                        ultimo_capitolo=last_chap, nome_manga=manga_name)

        clean()
        print("Download completato.")
        print(f"Files salvati in {os.getcwd()}\n\n")
        open_chap(first_ext)
        
    
    elif letter == "b":
        try:
            referer = previous_chapter
        except:
            print("\nNon c'è alcun capitolo precedente.")
            
        else:
            chapter = str(float(chapter) - 1)
            os.chdir("..")
            os.mkdir(f"{chapter}")
            os.chdir(f"{chapter}")
            
            first_ext = manga_scan(referer, capitolo=chapter,
                            ultimo_capitolo=last_chap, nome_manga=manga_name)

            clean()
            print("Download completato.")
            print(f"Files salvati in {os.getcwd()}\n\n")
            open_chap(first_ext)

    elif letter == "c":
        os.chdir("..")
        shutil.rmtree(f"{chapter}")

    else:
        print("Selezionare una lettera tra [a] [b] [c].")




    


