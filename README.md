# Chaindots Test

## Problem

### Description of the task

Design and implement a Django API for a social media platform that allows users to create posts, follow other users, and comment on posts.

The API should include (but may not be limited to) the following models:

**User:** Represents a user on the platform. Include fields for username, email, password, and followers/following relationships.
**Post:** Represents a user's post. Include fields for the author (foreign key to User model), content, and timestamps (date created).
**Comment:** Represents a comment on a post. Include fields for the author (foreign key to User model), post (foreign key to Post model), and content.

##### Implement the following endpoints:

- `GET` **/api/users/**: Retrieve a list of all users.
- `GET` **/api/users/{id}/**: Retrieve details of a specific user. Including number of total posts, number of total comments, followers and following.
- `POST` **/api/users/{id}/follow/{id}**: Set first id user as follower of second id user.
- `POST` **/api/users/**: Create a new user.
- `GET` **/api/posts/**: Retrieve a list of all posts ordered from newest to oldest from all users, with pagination and filters. The filters to implement are: author_id, from_date, to_date. None of the filters is compulsory. The pagination should be achieved with the following parameters: page_size (default = 20), page_number (default = 1)
- `GET` **/api/posts/{id}/**: Retrieve details of a specific post with it's last three comments included and the information of it's creator.
- `POST` **/api/posts/**: Create a new post.
- `GET` **/api/posts/{id}/comments/**: Retrieve all comments for a specific post.
- `POST` **/api/posts/{id}/comments/**: Add a new comment to a post.

Ensure that all endpoints require authentication. Implement token-based authentication using Django's built-in authentication system.
Optimize the ORM queries to minimize the number of database hits and improve performance.
Implement appropriate indexing and constraints on database fields to optimize query performance.
Optimize complex queries involving multiple models and relationships.
Write unit tests to ensure the API endpoints and ORM queries are functioning correctly.
Use Django REST framework for building the API.

##### Submission:

Provide the source code of your Django project, including all necessary files and folders.
Include a README file with instructions on how to set up and run the project.
Briefly explain the optimizations applied to the ORM queries and any challenges faced during the implementation.

##### Evaluation Criteria:

**Correctness:** Verify that the API endpoints are functioning as expected and that the ORM queries are optimized.
**Code Quality:** Assess the overall code organization, adherence to best practices, and proper use of Django REST framework.
**Optimized Queries:** Evaluate the effectiveness of the applied optimizations and their impact on query performance.
**Testing:** Check the presence of unit tests and their coverage of the API endpoints and ORM queries.

## Requirements

You need to have Docker and Docker Compose installed on your system.

Follow the steps for example in:
https://www.digitalocean.com/community/tutorials?q=install+docker

## Clone repository

```sh
$ git clone https://github.com/eemanuel/chaindots
```

## Run docker-compose commands

Build and start containers:

```sh
$ docker-compose up
```

Go to the `chaindots_api_1` container's shell

```sh
$ docker exec -ti chaindots_api_1 bash
```

Inside the container's shell, you can run all the tests with:

```sh
$ pytest
```

Inside the container's shell as well, you can check the test coverage by running:

```sh
$ coverage run -m pytest
$ coverage report
```

## Install pre-commit locally

If you are a developer, you should install on your system (Not inside `chaindots_api_1` container's shell):

```sh
$ pip install pre-commit
```

To install the git hook scripts, at .git folder level execute:

```sh
$ pre-commit install
$ pre-commit install-hooks
```

You can run hooks before commit using:

```sh
$ git commit --allow-empty
```

More info in https://pre-commit.com/ .

## Endpoints

### Admin

`GET` http://localhost:8000/admin/

### Obtain Authentication Token

`POST` http://localhost:8000/api/api-token-auth/

### Users:

**Create:**
`POST` http://localhost:8000/api/users/

**List:**
`GET` http://localhost:8000/api/users/

**Retrieve:**
`GET` http://localhost:8000/api/users/< id >/

**Follow:**
`GET` http://localhost:8000/api/users/< id >/follow/< id >/

### Posts (Publications)

**Create:**
`POST` http://localhost:8000/posts/

**List:**
`GET` http://localhost:8000/posts/

**Retrieve:**
`GET` http://localhost:8000/posts/< id >/

### Comments (PublicationComments)

**Create:**
`POST` http://localhost:8000/posts/< id >/comments/

**List:**
`GET` http://localhost:8000/posts/< id >/comments/

## Quick Start

_(examples using the "requests" library)_

First, create a new user posting like:
```
response = requests.post(
    "http://localhost:8000/api/users/",
    data={"username": "username", "password": "password", "email": "email"}
)
```
You don't need authentication to create a user.

Next, obtain an Authentication Token by posting like:
```
response = requests.post(
    "http://localhost:8000/api/api-token-auth/",
    data={"username": "username", "password": "password"}
)
```
This endpoint returns a response with data like:
_{'token': 'c11c179a214bbc4920bb81beb8a0cbb5be868a82'}_

You can now access all authentication-required endpoints by addingg the obtained token to the request's headers. For example, you can now list all users:
```
response = requests.get(
    "http://localhost:8000/api/users/",
    headers={
        "Authorization": "Token c11c179a214bbc4920bb81beb8a0cbb5be868a82"
    }
)
```
