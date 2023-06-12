from PyQt5.QtWidgets import *
from PyQt5 import uic, QtCore
from search_results import get_search_results, WebsiteRetriever
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtCore import Qt, QUrl, QMetaObject, pyqtSlot, Q_ARG
from PyQt5.QtGui import QPixmap, QMovie, QDesktopServices
from functools import partial
import threading
from search_results import NoResultsException


class MyGUI(QMainWindow):

    def __init__(self):
        super(MyGUI, self).__init__()
        uic.loadUi('my_GUI.ui', self)
        self.show()

        self.searchButton.clicked.connect(self.search_podcasts)
        self.filter_reset_button.clicked.connect(self.reset_filters)
        self.search_line.textChanged.connect(self.check_search_line)

        self.loading_movie = QMovie("loading2.gif")
        self.loading_label = QLabel()
        self.loading_label.setMinimumSize(QtCore.QSize(50, 50))
        self.loading_label.setMaximumSize(QtCore.QSize(50, 50))
        self.loading_label.setMovie(self.loading_movie)
        self.horizontalLayout_12.addWidget(self.loading_label)
        self.loading_label.hide()

        self.searchButton.setEnabled(False)
        self.search_button_blocked = False

        self.error_label = None

        self.sorting_combo_box.addItem("Sort by Title")
        self.sorting_combo_box.addItem("Sort by Author")
        self.apply_sorting.clicked.connect(self.apply_sorting_method)

        self.results = []
        self.selected_categories = []
        self.podcast_widgets = {}
        self.website_retrievers = []

    # Creates all podcast widgets and other UI elements
    def create_podcast_ui_element(self, podcast):
        # If a widget for this podcast already exists, return it
        if podcast in self.podcast_widgets:
            return self.podcast_widgets[podcast]

        # Create a widget to hold the labels
        widget = QWidget()

        # Create a layout for the widget
        layout = QHBoxLayout()

        # Create podcast attribute widgets
        title_label = QLabel(f'<a href="{podcast.pi_link}">{podcast.title}</a>')
        title_label.setOpenExternalLinks(True)
        author_label = QLabel(f'{podcast.author}')
        author_label.setWordWrap(True)
        description_label = QLabel(f'Description: {podcast.description}')
        description_label.setWordWrap(True)
        website_button = QPushButton('Go to website')
        website_retriever = WebsiteRetriever(podcast.pi_link)
        website_retriever.finished.connect(lambda url: QDesktopServices.openUrl(QUrl(url)))
        website_button.clicked.connect(website_retriever.start)
        self.website_retrievers.append(website_retriever)

        # Create a QPixmap for the image
        image_label = QLabel()
        self.load_image(podcast.img_url, image_label)

        # Add the labels to the layout
        layout.addWidget(image_label)
        layout.addWidget(website_button)
        layout.addWidget(title_label)
        layout.addWidget(author_label)
        layout.addWidget(description_label)

        for category in podcast.categories:
            button = QPushButton(category)
            if category in self.selected_categories:
                button.setStyleSheet("background-color: green")
            button.clicked.connect(partial(self.filter_by_category, category))
            layout.addWidget(button)

        # Set the widget's layout
        widget.setLayout(layout)

        # Store the widget in the dictionary
        self.podcast_widgets[podcast] = widget

        return widget

    # Loads the image for a podcast
    def load_image(self, url, label):
        # Set placeholder image
        placeholder_pixmap = QPixmap("placeholder_image.jpg")
        label.setPixmap(placeholder_pixmap.scaled(150, 150, Qt.KeepAspectRatio))

        # QNetworkAccessManager to send network requests and receive replies
        manager = QNetworkAccessManager(self)
        manager.finished.connect(lambda reply, l=label: self.set_image(reply, l))
        manager.get(QNetworkRequest(QUrl(url)))

    # Sets the image for a podcast
    def set_image(self, reply, label):
        # Read data from network reply
        data = reply.readAll()
        pixmap = QPixmap()
        if pixmap.loadFromData(data):
            # Replace the placeholder with the actual image
            label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))

    # Filters podcasts by selected categories
    def filter_by_category(self, category):
        button = self.sender()  # Get the button that was clicked

        if category in self.selected_categories:
            self.selected_categories.remove(category)
            button.setStyleSheet("")  # Remove the color styling
        else:
            self.selected_categories.append(category)
            button.setStyleSheet("background-color: green")  # Add green color styling

        # Iterate over all podcast widgets and set the color of the category buttons
        for podcast, widget in self.podcast_widgets.items():
            for button in widget.findChildren(QPushButton):  # Get all buttons in the widget
                if button.text() == category:  # If the button's text matches the category
                    if category in self.selected_categories:
                        button.setStyleSheet("background-color: green")  # Add green color styling
                    else:
                        button.setStyleSheet("")  # Remove the color styling
        self.display_podcasts()

    # Reset all selected filters
    def reset_filters(self):
        self.selected_categories = []
        # Iterate over all podcast widgets and set the color of the category buttons
        for podcast, widget in self.podcast_widgets.items():
            for button in widget.findChildren(QPushButton):  # Get all buttons in the widget
                button.setStyleSheet("")  # Remove the color styling
        self.display_podcasts()

    # Updates UI for podcast widgets, placing them in their area. Uses @pyqtSlot decorator to work in the Main thread,
    # apart from the network thread
    @pyqtSlot()
    def display_podcasts(self):
        if self.error_label is not None:
            self.error_label.deleteLater()
            self.error_label = None

        # Access the QVBoxLayout from the QWidget
        layout = self.scrollAreaWidgetContents_2.layout()

        # Make all widgets invisible
        for widget in self.podcast_widgets.values():
            widget.setVisible(False)

        # Filter results based on the selected categories
        filtered_results = [podcast for podcast in self.results if
                            all(c in podcast.categories for c in self.selected_categories)]

        # Add new results to the scroll area
        for podcast in filtered_results:
            # Ensure a widget exists for this podcast
            if podcast not in self.podcast_widgets:
                self.create_podcast_ui_element(podcast)
            widget = self.podcast_widgets[podcast]
            layout.addWidget(widget)
            widget.setVisible(True)

    # Calls the function that searches for podcasts, in a separate thread
    def search_podcasts(self):
        self.searchButton.setEnabled(False)
        self.search_button_blocked = True
        self.loading_label.show()
        self.loading_movie.start()
        search_item = self.search_line.text()
        # Start a new thread that runs the get_search_results function
        thread = threading.Thread(target=self.fetch_search_results, args=(search_item,))
        thread.start()

    # Handles all exceptions for the results gotten from the get_search_results function.
    def fetch_search_results(self, search_item):
        try:
            self.results = get_search_results(search_item)
        except NoResultsException as e:
            # Handle NoResultsException
            QMetaObject.invokeMethod(self, "display_error_message", Qt.QueuedConnection,
                                     Q_ARG(str, str(e)))
        except Exception as e:
            # Handling other exceptions here
            # print(f"An error occurred while fetching search results: {e}")
            QMetaObject.invokeMethod(self, "display_error_message", Qt.QueuedConnection,
                                     Q_ARG(str, str(e)))
        else:
            QMetaObject.invokeMethod(self, "display_podcasts", Qt.QueuedConnection)
        finally:
            self.loading_movie.stop()
            self.loading_label.hide()
            self.search_button_blocked = False
            self.searchButton.setEnabled(True)

    # Main thread function for displaying error messages
    @pyqtSlot(str)
    def display_error_message(self, message):
        # Make all podcast widgets invisible
        for widget in self.podcast_widgets.values():
            widget.setVisible(False)

        self.error_label = QLabel(message, self.scrollAreaWidgetContents_2)
        self.scrollAreaWidgetContents_2.layout().addWidget(self.error_label)
        self.error_label.setVisible(True)

    # Disable the 'Find' button when the search bar is empty and when results are loading
    def check_search_line(self, s):

        if not self.search_button_blocked:
            if s:
                self.searchButton.setEnabled(True)
            else:
                self.searchButton.setEnabled(False)

    # Sorts podcasts based either by titles or by authors
    @pyqtSlot()
    def apply_sorting_method(self):
        sorted_results = sorted(self.results, key=lambda podcast: podcast.title)
        sorting_method = self.sorting_combo_box.currentText()
        if sorting_method == "Sort by Title":
            self.results.sort(key=lambda podcast: podcast.title)
        elif sorting_method == "Sort by Author":
            self.results.sort(key=lambda podcast: podcast.author)
        self.display_podcasts()


def main():
    app = QApplication([])
    window = MyGUI()
    # with open("MaterialDark.qss", "r") as file:
    #     app.setStyleSheet(file.read())
    app.exec_()


if __name__ == '__main__':
    main()
