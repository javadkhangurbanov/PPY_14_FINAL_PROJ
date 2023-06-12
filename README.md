# Podcast Search and Filter Tool

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
    1. [Prerequisites](#prerequisites)
    2. [Installing Dependencies](#installing-dependencies)
    3. [Running the Application](#running-the-application)
3. [Functionality](#functionality)
    1. [Search for Podcasts](#search-for-podcasts)
    2. [Filtering](#filtering)
    3. [Sorting](#sorting)
    4. [Go to Website](#go-to-website)
    5. [Loading Animation](#loading-animation)
    6. [Error Handling](#error-handling)
4. [Technical Information](#technical-information)
    1. [Core Modules](#core-modules)
    2. [Threading](#threading)
5. [Key Features](#key-features)
6. [Challenges Faced](#challenges-faced)
7. [Solutions and Approaches Used](#solutions-and-approaches-used)
8. [Future Enhancements](#future-enhancements)

## Introduction
The Podcast Search and Filter Tool is a desktop application designed to make the process of finding podcasts more efficient. The application allows users to search for podcasts by name, filter them based on genre, language, and popularity, and access the podcasts' websites for streaming.

## Getting Started

### Prerequisites
- Python 3.x
- PyQt5
- Selenium
- BeautifulSoup
- Webdriver Manager for Chrome

### Installing Dependencies
Run the following command to install the required dependencies:
1. You will need Python 3.x installed on your system. You can download Python from the official website: Python Downloads.
2. Install the necessary Python libraries and packages by running the following command:

```
pip install PyQt5 selenium beautifulsoup4 webdriver-manager
```


### Running the Application
1. Ensure that `main.py`, `search_results.py`, and `podcast.py` files are in the same directory.
2. In the terminal or command line, navigate to the directory where the files are located.
3. Run the main.py script to start the application:

```
python main.py
```
4. The GUI of the application should open. You can start by typing in the search bar and clicking on the 'Search' button to search for podcasts.


## Functionality

### Search for Podcasts
Users can search for podcasts by entering a query in the search bar and clicking the 'Search' button. The application will then scrape podcast data from 'https://podcastindex.org' and display the results.

### Filtering
The user can filter the podcasts by categories. Each podcast has category buttons, and clicking on a category will filter the podcasts to show only those belonging to the selected categories.

### Sorting
Podcasts can be sorted by either title or author by selecting the appropriate option from the dropdown menu and clicking the 'Apply' button.

### Go to Website
Each podcast entry has a 'Go to Website' button that opens the podcast's webpage in a web browser.

### Loading Animation
When the user performs a search, a loading animation is displayed while the application fetches data.

### Error Handling
If no results are found or an error occurs during the search, an error message will be displayed.

## Technical Information

### Core Modules
The application is built using Python and employs the following modules:
1. `main.py`: Contains the main GUI class (MyGUI) responsible for creating and managing the graphical user interface of the application. This includes handling button clicks, displaying results, and updating the GUI. The script also contains the main function that initializes the QApplication and MyGUI.
2. `search_results.py`: Handles scraping of podcast data from 'https://podcastindex.org' using the Selenium WebDriver and BeautifulSoup. It contains the get_search_results function that takes a search term and returns a list of Podcast objects. It also contains the WebsiteRetriever class, which is a QThread that fetches a podcast's webpage link.
3. `podcast.py`: Contains the `Podcast` class which acts as a data model for podcasts. It holds attributes like title, author, categories, description, image URL, etc.

### Threading
The application uses threading to ensure that the UI remains responsive while fetching data from the web. It fetches search results in a separate thread and updates the UI in the main thread.

## Key Features
1. User-friendly GUI to search for podcasts.
2. Web scraping to fetch podcast data.
3. Category-based filtering of podcasts.
4. Smooth user experience with loading animations and error handling.
5. Sorting by title or author.
6. Direct link to the podcast's webpage.

## Challenges Faced
- Keeping the UI responsive while fetching data.
- Handling dynamic web content using Selenium WebDriver.
- Efficiently scraping and processing data to reduce the wait time for users.
- Designing a clean and intuitive user interface.

## Solutions and Approaches Used
- Implemented multithreading to keep the UI responsive during web scraping.
- Used Selenium WebDriver to handle dynamic content on the webpage and BeautifulSoup for parsing the HTML content efficiently.
- Optimized the web scraping process by selectively fetching required elements and handling network delays.
- Created a simple and clean UI layout using PyQt5, focusing on the usability aspect.

## Future Enhancements
1. Implement pagination or a load more button for viewing additional search results.
2. Allow users to save favorite podcasts within the application.
3. Include additional filters, such as by date, language, or location.
4. Provide an option to listen to a podcast preview within the application.
5. Implement caching for previously searched terms to speed up repeated searches.

