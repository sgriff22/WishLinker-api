# WishLinker API

This repository is a Django API designed to manage wishlists. This project serves as the backend for the WishLinker application, providing RESTful endpoints to handle the core functionalities.

## Notes

The client-side repository for this API can be found [here](https://github.com/sgriff22/WishLinker-client).

## Technologies Used

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Django](	https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white) ![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white) ![Git](https://img.shields.io/badge/git%20-%23F05033.svg?&style=for-the-badge&logo=git&logoColor=white) ![GitHub](https://img.shields.io/badge/github%20-%23121011.svg?&style=for-the-badge&logo=github&logoColor=white) ![Visual Studio Code](https://img.shields.io/badge/VSCode%20-%23007ACC.svg?&style=for-the-badge&logo=visual-studio-code&logoColor=white)

## Getting Started

Follow these steps to set up the project on your local machine:

1. **Clone the repository and navigate to the project directory:**

    ```sh
    git clone <repository-url>
    cd <project-directory>
    ```
    - Replace `<repository-url>` with the actual URL of this repository.
    - Replace `<project-directory>` with the name of the directory created by cloning this repository.

2. **Activate the virtual environment using Pipenv:**

    ```sh
    pipenv shell
    ```

3. **Install the project dependencies:**

    ```sh
    pipenv install
    ```

4. **Install additional required packages:**

    ```sh
    pip install django-safedelete
    pipenv install pillow
    ```

5. **Set up the database:**

    ```sh
    ./seed_database.sh
    ```
7. **Open the project directory in VS Code**

8. **Open the Command Palette:**
    - Mac: Press <kbd>⌘</kbd> + <kbd>SHIFT</kbd> + <kbd>P</kbd>
    - Windows: Press <kbd>Ctrl</kbd> + <kbd>SHIFT</kbd> + <kbd>P</kbd>

9. **Select Python Interpreter:**
    - In the Command Palette, type and select `Python: Select Interpreter`.
    - Search for `wish` and select the interpreter that starts with those characters. There should only be one to choose from.

10. **Start the Debugger:**
    - Mac: Press <kbd>Shift</kbd> + <kbd>Option</kbd> + <kbd>D</kbd>
    - Windows: Press <kbd>Shift</kbd> + <kbd>Alt</kbd> + <kbd>D</kbd>

11. Ensure that the process starts with no exceptions.

12. If you haven't already, go to the [client-side repository](https://github.com/sgriff22/WishLinker-client) and follow the steps to open the site.
