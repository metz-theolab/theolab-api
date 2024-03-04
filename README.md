# Metz Theolab-APIs
![Tests status](https://github.com/metz-theolab/theolab-api/actions/workflows/test.yml/badge.svg)


This repository contains the API to access data from the QWB project.

## Using the API

Requirements: 

    - Python >= 3.10

    - A running installation of Docker
    
    - The Python package `invoke`

You should first launch the SQL database service through docker-compose:
```
cd deploy && docker-compose up -d
```

In the cloned repository, run:
```
invoke install
```

You can then launch the API using:
```
qwb-api
```

and access the documentation on your browser at `localhost:8000/docs`.

## Contributing to the API

## Funding

*Une partie de ce travail a bénéficié́ d'une aide de l’État gérée par l'Agence Nationale de la Recherche au titre du programme d’Investissements d’avenir portant la référence ANR-21-ESRE-0005 (Biblissima+).*

![Biblissima logo](https://github.com/metz-theolab/theolab-api/blob/main/logos/biblissima-logo.png)

*Ce travail a aussi été financé par l'ANR, projet SHERBET*

![ANR logo](https://github.com/metz-theolab/theolab-api/blob/main/logos/anr.png)

