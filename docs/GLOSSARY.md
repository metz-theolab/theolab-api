# Glossary

## Stemmatology terminology

- **Tradition**: ??
- **Manuscript**: ??
- **Folio**: ??
- **Chapter** ??
- **Verse** ??
- **Line** ??

And what's the relations between those things ?


## Software Development terminology

- **Version control**: A system that records changes to a file or set of files over time so that you can recall specific versions later. It allows you to revert files back to a previous state, revert the entire project back to a previous state, compare changes over time, see who last modified something that might be causing a problem, who introduced an issue and when, and more. The VCS (version control system) used in the project is [git](https://git-scm.com/).

- **Repository**: A repository is a central file storage location. It is used by version control systems to store multiple versions of files. While a repository can be configured on a local machine for a single user, it is often stored on a server, which can be accessed by multiple users. The canonical repository for the project is hosted on [GitHub](https://github.com) at the address <https://github.com/metz-theolab/theolab-api>

- **Branch**: A branch is a parallel version of a repository. It is contained within the repository, but does not affect the primary or "main"" branch, allowing you to work freely without disrupting others works. When you've made the changes you wanted to, you can merge your branch back into the main branch to publish your changes with others.

- **Pull request**: A pull request is a method of submitting contributions from a branch to another. It is often the preferred way to contribute to a project using the Git version control system. It allows you to submit your changes to the main branch for review and approval.

## Python terminology

- **Python**: A popular programming language, used in many academic, commercial, and open-source projects.

- **Module**: A file that contains Python code. A module can be imported and used from another module to avoid code duplication.

- **Package**: A set of files (possibly including modules) that are organized in one or several directories.

- **Library**: A package that contains a set of modules used to perform some specific tasks.

- **Framework**: A set of libraries that provide a way to build applications. A framework is often opinionated and provides a set of rules and guidelines to follow.

- **Application**: A program that is designed to perform a specific task or set of tasks. In practice, an application is often created on top of a framework.

- **Project**: A collection of files and directories that are used to create a package. A project can contain one or several applications. In the context of this repository, the term "project" refers to the whole codebase located under `src/`, as well as the `tests/` directory and the `pyproject.toml` file.

- **Virtual environment**: A self-contained directory tree that contains a Python installation for a particular version of Python, plus a number of additional packages. It is used to avoid conflicts between different projects that use different versions of the same package.
 
## Web development terminology

- **HTTP**: The Hypertext Transfer Protocol is an application protocol for information systems. It is the foundation of any data exchange on the Web and it is a client-server protocol, which means requests are initiated by the recipient, usually the Web browser and are responded to by the sender, the Web server.
  
- **URL**: A Uniform Resource Locator is a reference to a web resource that specifies its location on a computer network and a mechanism for retrieving it. A URL is a specific type of Uniform Resource Identifier (URI), although many people use the two terms interchangeably.

- **Web server**: A web server is server software, or hardware dedicated to running said software, that can satisfy client requests on the World Wide Web. It is a software application that runs on a remote server and is responsible for accepting and fulfilling requests on given URLs from clients, usually web browsers.

- **Rest API**: A RESTful API is an architectural style for an application program interface (API) that uses HTTP requests to access and use data. The endpoint method can be `GET`, `PUT`, `POST`, `DELETE`, which refers respectivelly to the reading, updating, creating and deleting of operations concerning resources (non exhaustive list).

- **Endpoint**: An endpoint is an operation within a Rest API. It is located at a specific URL and can be accessed using a specific method (e.g. `GET`, `PUT`,  `POST`, `DELETE`, ...). Each endpoint has a specific purpose and can be used to perform a specific action concerning a resource.

- **Frontend**: The frontend is the part of a software that is responsible for the user interface and user experience. It is the part of the software that users interact with, and is the the software responsible for interacting with the backend in the name of the user.
