# Features

> This document is not a technical document, but rather a high-level overview of the features of the project.

At the highes level, the project is a REST API that provides a way to:

- **Create** and **manage** users
- **Create** and **manage** groups
- **Create** and **manage** manuscripts

The topic of users and groups is not directly related to the main purpose of the project, but it is a necessary feature to provide a way to manage the access to the API.

The main purpose of the project is to provide a way to manage manuscripts in a collaborative way. The project is designed to be used by scholars who want to work on the same manuscript, and who want to keep track of the changes made to the manuscript over time.

## Manuscripts use cases

The following use cases are the main use cases of the project:

### Resource creation

- **Create a tradition**: A user can create a new tradition. Manuscripts are organized in traditions. A tradition may be created with metadata, according to the requirements of the project.

- **Add a manuscript**: A user can add a manuscript to a tradition. A manuscript is a version of a text. It may be created with metadata, according to the requirements of the project, but is never created with the text itself.

- **Add a chapter**: A user can add a chapter to a manuscript. A chapter is a part of a manuscript. It may be created with metadata, according to the requirements of the project, but is never created with the text itself.

- **Add a folio**: A user can add a folio to a chapter. A folio is a part of a chapter. It may be created with metadata, according to the requirements of the project, but is never created with the text itself.

- **Add a column**: A user can add a column to a folio. A column is a part of a folio. It may be created with metadata, according to the requirements of the project, but is never created with the text itself.

- **Add a line**: A user can add a line to a folio. A line is a part of a folio. It may be created with metadata, according to the requirements of the project, and MUST be created with the text itself.


## Resource update

- **Update a tradition**: A user can update a tradition. Only the tradition metadata may be updated, as other informations can be found in child resources and not in the tradition itself.

- **Update a manuscript**: A user can update a manuscript. Only the manuscript metadata may be updated, as other informations can be found in child resources and not in the manuscript itself.

- **Update a chapter**: A user can update a chapter. Only the chapter metadata may be updated, as other informations can be found in child resources and not in the chapter itself.

- **Update a folio**: A user can update a folio. Only the folio metadata may be updated, as other informations can be found in child resources and not in the folio itself.

- **Update a column**: A user can update a column. Only the column metadata may be updated, as other informations can be found in child resources and not in the column itself.

- **Update a line**: A user can update a line. The line metadata and text may be updated.

## Resource deletion

- **Delete a tradition**: A user can delete a tradition. All the manuscripts, chapters, folios, columns and lines that are part of the tradition will be deleted.

- **Delete a manuscript**: A user can delete a manuscript. All the chapters, folios, columns and lines that are part of the manuscript will be deleted.

- **Delete a chapter**: A user can delete a chapter. All the folios, columns and lines that are part of the chapter will be deleted.

- **Delete a folio**: A user can delete a folio. All the columns and lines that are part of the folio will be deleted.

- **Delete a column**: A user can delete a column. All the lines that are part of the column will be deleted.

- **Delete a line**: A user can delete a line. The line will be deleted.

## Resource query

- **Get a tradition**: A user can get a tradition. The tradition metadata and the list of manuscripts that are part of the tradition will be returned.

- **Get a manuscript**: A user can get a manuscript. The manuscript metadata and the list of chapters that are part of the manuscript will be returned.

- **Get a manuscript transcript**: A user can get a manuscript transcript. The manuscript metadata will be returned, as well as the text of the manuscript. 

- **Get a chapter**: A user can get a chapter. The chapter metadata and the list of folios that are part of the chapter will be returned.

- **Get a folio**: A user can get a folio. The folio metadata and the list of columns that are part of the folio will be returned.

- **Get a column**: A user can get a column. The column metadata and the list of lines that are part of the column will be returned.

- **Get a line**: A user can get a line. The line metadata and the text will be returned.
