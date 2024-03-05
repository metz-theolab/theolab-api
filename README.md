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

## Running the API in SCRIBES only mode

If you only want to access SCRIBES related endpoints, :
```
qwb-api --scribes-only
```



