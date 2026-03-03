# Japońskie napisy do **K-On!**

Instrukcja obsługi dla osób z zacięciem masochistycznym.

## Pliki z napisami

Napisy od [Matchoo95](https://github.com/Matchoo95/JP-Subtitles/tree/master/K-ON!).

Napisy są dostosowane do wersji BR. Ja mam wersję DVD. Dla pierwszego sezonu wystarczyło zmienić framerate z 23.976 na 25. Z wyjątkiem kilku przypadków napisy są idealnie dopasowane, w niektórych odcinkach można dopasować sekundę przód/tył ale bez tego też da się żyć.

Gorzej z drugim sezonem. Tu napisy też są do BR i trzeba zmienić framerate tak samo, jak dla 1 sezonu. I wszystko jest w porządku aż do końca opening song - potem się rozjeżdża. Najczęściej trzeba ustawić 7.5s do przodu, żeby napisy szły szybciej, ale to opóźnienie bywa różne w różnych odcinkach. Najwyraźniej w wersji na BR opening jest dłuższy albo jest tam jakaś reklama ;)

Do edycji napisów: brzydki jak noc październikowa z gradobiciem i skuteczny jak Chuck Norris po amfetaminie *Subtitle Edit*:

```
❯ paru -Qs subtitleedit
local/subtitleedit 4.0.14-1
    An advanced subtitle editor and converter
```

Narzędzie do przesuwania offsetu potrafi pracować na selekcjach więc nie ma problemu z dopasowaniem drugiej części napisów do odcinków w 2 sezonie.

A jak już mamy pliczek z napisami gotowy, to jedziemy dalej:

## Domyślna ścieżka audio

```
Stream #0:1(eng): Audio ... (default)
Stream #0:2(jpn): Audio ...
```

Czyli:

* `track:a1` = angielski (obecnie default)
* `track:a2` = japoński (chcemy zrobić default)

### Komenda

```bash
mkvpropedit "K-On! S01E01 - Disband the Club!.mkv" \
  --edit track:a1 --set flag-default=0 \
  --edit track:a2 --set flag-default=1
```

To:

* zdejmie `default` z angielskiego
* ustawi `default` na japońskim

Operacja jest:
✔️ natychmiastowa
✔️ bez rekompresji
✔️ bez przepisywania całego pliku
✔️ w pełni odwracalna

### Sprawdzenie:

```bash
mkvmerge -i "K-On! S01E01 - Disband the Club!.mkv"
```

Powinieneś zobaczyć coś w stylu:

```
Track ID 1: audio (eng) [not default]
Track ID 2: audio (jpn) [default]
```

albo w `ffprobe` zniknie `(default)` przy angielskim i pojawi się przy japońskim.

## Dołożenie ścieżki z japońskimi napisami

Najczyściej zrobisz to przez `mkvmerge`, bo on po prostu „dopisuje track”.

### 0) Wymóg wstępny: MKVToolNix

Na Archu zwykle:

```bash
sudo pacman -S mkvtoolnix-cli
```

### 1) Remux z dołożeniem `.ass`

```bash
mkvmerge -o "K-On! S01E01 - Disband the Club!.new.mkv" \
  "K-On! S01E01 - Disband the Club!.mkv" \
  --language 0:jpn --track-name 0:"Japanese (ASS)" \
  "K-On! S01E01 - Disband the Club!.ass"
```

* bierze wszystkie istniejące ścieżki z `.mkv`
* dodaje nową ścieżkę z `.ass`
* ustawia:

  * język: `jpn`
  * nazwę: `Japanese (ASS)`

### 2) Szybka weryfikacja

```bash
mkvmerge -i "K-On! S01E01 - Disband the Club!.new.mkv"
```

Powinieneś zobaczyć nowy track typu **subtitles (SubStationAlpha)** (albo ASS).

Możesz też:

```bash
ffprobe "K-On! S01E01 - Disband the Club!.new.mkv" | rg "Subtitle|Stream #0:|ass|ssa"
```

### Ustawienie domyślnych napisów

```bash
mkvpropedit "K-On! S01E01 - Disband the Club!.new.mkv" \
  --edit track:s1 --set flag-default=0 \
  --edit track:s2 --set flag-default=0 \
  --edit track:s3 --set flag-default=1
```

## Edycja metadanych

### Ustawienie tytułu

```bash
mkvpropedit "K-On! S01E01 - Disband the Club!.new.mkv" \
  --edit info --set "title=Disband the Club\!"
```

### Sprawdzenie

```bash
mkvinfo "K-On! S01E01 - Disband the Club!.new.mkv" | rg "Title"
```

albo po prostu:

```bash
ffprobe "K-On! S01E01 - Disband the Club!.new.mkv" | rg title
```

Powinieneś zobaczyć coś w stylu:

```
title           : Disband the Club!
```

### Konwersja do `.srt`

```bash
subtitleedit /convert input.ass subrip
```

Wywala style i zostawia `input.srt` z samymi tekstami dialogów.
