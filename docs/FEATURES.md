# Features

> This document is not a technical document, but rather a high-level overview of the features of the project.

At the highes level, the project is a REST API that provides a way to:

- **Create** and **manage** users
- **Create** and **manage** groups
- **Create** and **manage** manuscripts

The topic of users and groups is not directly related to the main purpose of the project, but it is a necessary feature to provide a way to manage the access to the API.

The main purpose of the project is to provide a way to transcribe manuscripts in a collaborative way. The project is designed to be used by scholars who want to transcribe manuscripts in a collaborative fashion through an easy to use interface.

## Manuscripts use cases

The following use cases are the main use cases of the project:

### Resource creation

- **Create a tradition**: A user can create a new tradition. Manuscripts are organized in traditions. A tradition may be created with metadata, according to the requirements of the project.

- **Add a manuscript**: A user can add a manuscript to a tradition. A manuscript is a witness of a tradition. It may be created with metadata, according to the requirements of the project, but is never created with a transcription.

- **Add a folio**: A user can add a folio to a manuscript. A folio is a part of a manuscript. It may be created with metadata, according to the requirements of the project, but is never created with the text itself.

- **Add a column**: A user can add a column to a folio. A column is a part of a folio. It may be created with metadata, according to the requirements of the project, but is never created with a transcription itself.

- **Add a line**: A user can add a line to a folio. A line is added to a column. It may be created with metadata, according to the requirements of the project.

- **Add a reading**: A user can add a transcription of a line, which is an ensemble of readings.  

- **Add a chapter**: A user can add a chapter to a tradition.

- **Add a verse**: A user can add a verse to a chapter.

- **Add readings to a verse**: A user can add a reading to a verse and its position within the verse.

- **Add a translation**: Add a possible translation to a transcription. For now limited to texts divided in chapter and verses.

## Resource update

- **Update a tradition**: A user can update a tradition. Only the tradition metadata may be updated, as other informations can be found in child resources and not in the tradition itself.

- **Update a manuscript**: A user can update a manuscript. Only the manuscript metadata may be updated, as other informations can be found in child resources and not in the manuscript itself.

- **Update a folio**: A user can update a folio. Only the folio metadata may be updated, as other informations can be found in child resources and not in the folio itself.

- **Update a column**: A user can update a column. Only the column metadata may be updated, as other informations can be found in child resources and not in the column itself.

- **Update a line**: A user can update a line. Only the column metadata may be updated, as other informations can be found in child resources and not in the column itself.

- **Update a reading**: A user can modify a reading.

- **Update a line**: A user can update a line. The line metadata and text may be updated.

- **Update a chapter**: A user can update a chapter. Only the chapter metadata may be updated, as other informations can be found in child resources and not in the chapter itself.

- **Update a verse**: A user can update a chapter. Only the chapter metadata may be updated, as other informations can be found in child resources and not in the chapter itself.


## Resource deletion

- **Delete a tradition**: A user can delete a tradition. All the manuscripts, chapters, folios, columns and lines that are part of the tradition will be deleted.

- **Delete a manuscript**: A user can delete a manuscript. All the chapters, folios, columns and lines that are part of the manuscript will be deleted.

- **Delete a folio**: A user can delete a folio. All the columns and lines that are part of the folio will be deleted.

- **Delete a column**: A user can delete a column. All the lines that are part of the column will be deleted.

- **Delete a line**: A user can delete a line. All the readings in this line will be deleted.

- **Delete a line**: A user can delete a reading. The reading will be deleted.

- **Delete a chapter**: A user can delete a chapter. All the verses contained in this chapter will be deleted.

## Resource query

- **Get a tradition**: A user can get a tradition. The tradition metadata and the list of manuscripts that are part of the tradition will be returned.

- **Get a manuscript transcript**: A user can get a manuscript transcript. The manuscript metadata will be returned, as well as the text of the manuscript. 

- **Get a folio**: A user can get a folio transcript. The folio metadata and the transcription that are part of the folio will be returned.

- **Get a chapter**: A user can get a chapter transcript for all available manuscripts within a tradition. The chapter transcript will be returned.

- **Get a verse**: A user can get a verse transcript for all available manuscripts within a tradition.