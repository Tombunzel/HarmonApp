<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [] instead of parentheses ().
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/Tombunzel/HarmonApp">
    <img src="HarmonApp/harmon_logo.png" alt="Logo" width="130" height="130">
  </a>

<h3 align="center">HarmonApp</h3>

  <p align="center">
    The music streaming app that brings musicians and users together in harmony.
    <br />
    <a href="https://render-harmonapp.onrender.com/docs">Explore the Documentation »</a>
    <br />
    <a href="https://github.com/Tombunzel/HarmonApp/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/Tombunzel/HarmonApp/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
         <li><a href="#authentication">Authentication</a></li>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#try-the-deployed-api">Try the Deployed API</a>
      <ul>
        <li><a href="#deployed-prerequisites">Prerequisites</a></li>
        <li><a href="#getting-started">Getting Started</a></li>
      </ul>
    </li>
    <li><a href="#local-development-setup">Local Development Setup</a></li>
      <ul>
        <li><a href="#local-prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#testing-the-installation">Testing the Installation</a></li>
      </ul>
    <li><a href="#contributing">Contributing</a></li>
      <ul>
        <li><a href="#top-contributors">Top Contributors</a></li>
      </ul>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project
As a personal project, I have created a back-end API for a music streaming platform, allowing for artists to upload their music
and for users to buy and stream tracks and albums.
The database is built to handle playlists, follows and purchases;
however, some of these features don't have an endpoint yet.<br>
I intend to implement these and further features, as well as a front-end in the future. <br>
You could either try out the deployed API as an artist/user by sending requests to the API URL provided below,
or set up the API locally by cloning this repository.  



### Authentication

* The API uses OAuth2 with password flow
* There are two types of authentication available:
  - User authentication
  - Artist authentication
* Users and artists need to obtain an access token by sending credentials to ```/users/token``` or ```/artists/token```
* The access token expires after 30 minutes
* Tokens must be included in requests using Bearer authentication


<!-- BUILT WITH -->
### Built With

* [![SQLAlchemy][SQLAlchemy]][SQLAlchemy-url]
* [![PostgreSQL][PostgreSQL]][PostgreSQL-url]
* [![JWT][JWT]][JWT-url]
* [![FastAPI][FastAPI]][FastAPI-url]
* [![Render][Render]][Render-url]
* [![GoogleCloud][GoogleCloud]][GoogleCloud-url]
* [![Docker][Docker]][Docker-url]


<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- TRY THE DEPLOYED API -->
## Try the Deployed API


<!-- DEPLOYED PREREQUISITES -->
### Prerequisites

- A modern web browser or API client (like Postman, cURL, etc.)
- The base URL of the API: `https://render-harmonapp.onrender.com`


### Getting Started

To get started, a new user would need to:
1. Create an account:
    <br>
    ```POST``` to ```/users``` with:
      ```sh
       {
         "username": "string",
         "email": "example@example.com",
         "password": "string",
         "name": "string",
         "date_of_birth": "YYYY-MM-DD"
       }
      ```

2. Obtain an access token:
    <br>
   ```POST``` to ```/users/token``` with form data:
    * ```username```
    * ```password```
   

3. The response will include your access token:
    ```sh
    {
        "access_token": "<your_token_here>",
        "token_type": "bearer"
    }
    ```

   Include this token in all subsequent requests using the Authorization header:

      ```sh
    Authorization: Bearer <your_access_token>
    ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LOCAL DEVELOPMENT SETUP -->
## Local Development Setup

<!-- LOCAL PREREQUISITES -->
### Prerequisites
- Python 3.8 or higher
- PostgreSQL installed on your machine
- Git

<!-- INSTALLATION -->
### Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/Tombunzel/HarmonApp.git
    cd harmonapp
    ````

2. Create and activate a virtual environment if your IDE doesn't create one for you:
    ```sh
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up PostgreSQL:
   * Install PostgreSQL if you haven't already
   * Create a new database called `harmonapp` using pgAdmin


5. Configure environment variables:

    Create a ```.env``` file in the root directory with the following variables:
    ```sh
    CONNECTION_STRING='postgresql://[username]:[password]@localhost/harmonapp'
    SECRET_KEY='[your-secret-key]'
    ```
    Replace `[username]`, `[password]`, and `[your-secret-key]` with your PostgreSQL credentials and a secure secret key.


6. Initialize the database:
    ```sh
    # The tables will be created automatically when you run the application
    python app.py
    ```

7. Run the development server:
    ```sh
    uvicorn app:app --reload
    ```
    The API will be available at http://localhost:8000


8. To create the first admin user, create a new file (ex. `create_first_admin.py`) outside the project directory with the following code,
and then run the file:
   ```shell
   from HarmonApp.datamanager.database import SessionLocal
   from HarmonApp.routes.user import create_admin_user
   from HarmonApp.schemas.user_schemas import UserCreate
   
   # Create the first admin user
   first_admin = UserCreate(
       username="admin",
       email="example@example.com",
       password="string",
       name="string",
       date_of_birth="2024-12-31"
   )
   
   db = SessionLocal()
   create_admin_user(db, first_admin)
   db.close()
   ```

<!-- TESTING THE INSTALLATION -->
### Testing the Installation
1. Visit http://localhost:8000/docs to see the Swagger documentation
2. Create a test user using the ```/users/``` endpoint
3. Obtain an access token from ```/users/token```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- CONTRIBUTING -->
## Contributing

Contributions are what makes the open source community such an amazing place to learn, inspire, and create. Any contributions are **greatly appreciated**.

If you have a suggestion that would make this app better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".<br>
Don't forget to give the project a star!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

**Thanks!**

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- TOP CONTRIBUTORS -->
### Top contributors:

<a href="https://github.com/Tombunzel/HarmonApp/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Tombunzel/HarmonApp" alt="contrib.rocks image" />
</a>

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- CONTACT -->
## Contact

Tom Bunzel - bunzel.tom@gmail.com

Project Link: [https://github.com/Tombunzel/HarmonApp](https://github.com/Tombunzel/HarmonApp)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/Tombunzel/HarmonApp.svg?style=for-the-badge
[contributors-url]: https://github.com/Tombunzel/HarmonApp/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Tombunzel/HarmonApp.svg?style=for-the-badge
[forks-url]: https://github.com/Tombunzel/HarmonApp/forks
[stars-shield]: https://img.shields.io/github/stars/Tombunzel/HarmonApp.svg?style=for-the-badge
[stars-url]: https://github.com/Tombunzel/HarmonApp/stargazers
[issues-shield]: https://img.shields.io/github/issues/Tombunzel/HarmonApp.svg?style=for-the-badge
[issues-url]: https://github.com/Tombunzel/HarmonApp/issues
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/bunzeltom/
[FastAPI]: https://img.shields.io/badge/FastAPI-069486?style=for-the-badge&logo=fastapi&logoColor=white
[FastAPI-url]: https://fastapi.tiangolo.com/
[SQLAlchemy]: https://img.shields.io/badge/SQLAlchemy-D61F00?style=for-the-badge&logo=sqlalchemy&logoColor=white
[SQLAlchemy-url]: https://www.sqlalchemy.org/
[PostgreSQL]: https://img.shields.io/badge/PostgreSQL-336790?style=for-the-badge&logo=postgresql&logoColor=white
[PostgreSQL-url]: https://www.sqlalchemy.org/
[GoogleCloud]: https://img.shields.io/badge/Google%20Cloud-FFFFFF?style=for-the-badge&logo=googlecloud
[GoogleCloud-url]: https://cloud.google.com/
[Docker]: https://img.shields.io/badge/Docker-1C63ED?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com/
[JWT]: https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=FF3E00
[JWT-url]: https://jwt.io/
[Render]: https://img.shields.io/badge/Render-0D0D0D?style=for-the-badge&logo=render&logoColor=white
[Render-url]: https://render.com/
