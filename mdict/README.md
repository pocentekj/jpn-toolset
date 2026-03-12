# mdict

CLI tool for offline Japanese/English dictionary.

## Setup

Dictionary file not included in repository. Download it [here](http://ftp.edrdg.org/pub/Nihongo/JMdict.gz) and place `JMdict.xml` in project data directory.

### Database

**mdict** uses Sqlite as database backend. Create empty database:

```bash
touch ~/.local/share/mdict.sqlite
```

Database schema is in `schema.sql`.

### Import data

```bash
mdict-import
```

### Usage

```
mdict 伝統的 | head -n3
```
